import asyncio
import gettext
import logging
import os
import sys

from asyncio import (
    FIRST_COMPLETED,
    CancelledError,
    Event,
    Future,
    Lock,
    Task,
    create_task,
    current_task,
    get_event_loop,
    sleep,
    wait,
)
from collections.abc import Hashable
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import StrEnum
from functools import partial, wraps
from inspect import iscoroutine, iscoroutinefunction
from itertools import chain, repeat
from ssl import SSLContext
from typing import Any, Callable, Coroutine, Iterable, Literal, cast
from uuid import uuid4

import aiormq
import aiormq.exceptions
import yarl


gettext.bindtextdomain(
    "rmqaio",
    localedir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales"),
)
gettext.textdomain("rmqaio")
_ = gettext.gettext


logger = logging.getLogger("rmqaio")

log_frmt = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s lineno:%(lineno)4d -- %(message)s")
log_hndl = logging.StreamHandler(stream=sys.stderr)
log_hndl.setFormatter(log_frmt)

logger.addHandler(log_hndl)


def env_var_as_int(env_var_name: str, default: int) -> int:
    value = os.environ.get(env_var_name)
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        raise ValueError(_("invalid value '{}' for environment variable {}").format(value, env_var_name))


def env_var_as_bool(env_var_name: str, default: bool = False) -> bool:
    value = os.environ.get(env_var_name)
    if value is None:
        return default
    if value.lower() in ("1", "true", "yes", "y"):
        return True
    if value.lower() in ("0", "false", "no", "n"):
        return False
    raise ValueError(_("invalid value '{}' for environment variable {}").format(value, env_var_name))


BasicProperties = aiormq.spec.Basic.Properties


@dataclass
class Config:
    connect_timeout: int = field(default_factory=lambda: env_var_as_int("RMQAIO_CONNECT_TIMEOUT", 15))
    """Connection establishment operation timeout."""
    log_sanitize: bool = field(default_factory=lambda: env_var_as_bool("RMQAIO_LOG_SANITIZE", True))
    """Logger data sanitize flag. If `True` user data will be replaces with `<hidden>` message."""


config = Config()


class ExchangeType(StrEnum):
    """Enum for RabbitMQ exchange types."""

    DIRECT = "direct"
    """
    RabbitMQ [direct](https://www.rabbitmq.com/tutorials/amqp-concepts#exchange-direct) exchange.
    """
    FANOUT = "fanout"
    """
    RabbitMQ [fanout](https://www.rabbitmq.com/tutorials/amqp-concepts#exchange-fanout) exchange.
    """
    TOPIC = "topic"
    """
    RabbitMQ [topic](https://www.rabbitmq.com/tutorials/amqp-concepts#exchange-topic) exchange.
    """
    HEADERS = "HEADERS"
    """
    RabbitMQ [headers](https://www.rabbitmq.com/tutorials/amqp-concepts#exchange-headers) exchange.
    """


class QueueType(StrEnum):
    """Enum for RabbitMQ queue types"""

    CLASSIC = "classic"
    """
    RabbitMQ [classic](https://www.rabbitmq.com/docs/classic-queues) queue.
    """

    QUORUM = "quorum"
    """
    RabbitMQ [quorum](https://www.rabbitmq.com/docs/quorum-queues) queue.
    """


def _retry(
    *,
    retry_timeouts: Iterable[int],
    exc_filter: Callable[[Exception], bool],
    msg: str | None = None,
    on_error: Callable[[Exception], Coroutine] | None = None,
):
    """Retry decorator.

    Args:
        retry_timeouts: Retry timeout as iterable of int, for example: `[1, 2, 3]` or `itertools.repeat(5)`.
        exc_filter: Callable to determine whether or not to retry.
        msg: Message to log on retry.
        on_error: Callable to call on error.
    """

    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwds):
            timeouts = iter(retry_timeouts)
            attempt = 0
            while True:
                try:
                    return await fn(*args, **kwds)
                except Exception as e:
                    if not exc_filter(e):
                        raise e
                    try:
                        t = next(timeouts)
                        attempt += 1
                        logger.warning(
                            _("%s (%s %s) retry(%s) in %s second(s)"),
                            msg or fn,
                            e.__class__,
                            e,
                            attempt,
                            t,
                        )
                        if on_error:
                            await on_error(e)
                        await sleep(t)
                    except StopIteration:
                        raise e

        return wrapper

    return decorator


class _LoopIter:
    """Repeatable iterator.

    Args:
        data: list of items to iterate.
    """

    __slots__ = ("_data", "_i", "_j")

    def __init__(self, data: list):
        self._data = data
        self._i = -1
        self._j = 0

    def __next__(self):
        if self._j == len(self._data):
            self._j = 0
            raise StopIteration
        self._i = (self._i + 1) % len(self._data)
        self._j += 1
        return self._data[self._i]

    def reset(self):
        self._i = max(-1, self._i - 1)
        self._j = 0


class Connection:
    """RabbitMQ smart connection. Single `aiormq` connection per event loop, url(s) and name.

    Args:
        url: RabbitMQ URL or `list` of URLs. See [uri-spec](https://www.rabbitmq.com/docs/uri-spec).
        name: Connection name. Will be generated automatically if not provided as `uuid4().hex[-4:]`.
        ssl_context: SSL context or `list` of SSL contexts according to provided `url` argument.
        retry_timeouts: Iterable of `int`.
        exc_filter: Callable to filter exceptions for retry.

            Default:
                ```python
                lambda e: isinstance(
                    e, (asyncio.TimeoutError, ConnectionError, aiormq.exceptions.AMQPConnectionError)
                )
                ```

    Examples:
        ```python
        >>> Connection("amqp://guest:guest@localhost", name="abc", retry_timeouts=itertools.repeat(5))
        ```

        ```python
        >>> Connection(
                ["amqps://localhost1", "amqps://localhost2"],
                ssl_context=[ssl_context_for_url1, ssl_context_for_url2],
            )
        ```
    """

    __shared: dict = {}

    def __init__(
        self,
        url: str | list[str],
        name: str | None = None,
        ssl_context: SSLContext | list[SSLContext] | None = None,
        retry_timeouts: Iterable[int] | None = None,
        exc_filter: Callable[[Exception], bool] | None = None,
    ):
        if not isinstance(url, (list, tuple, set)):
            urls = [url]
        else:
            urls = list(url)

        if ssl_context is None:
            ssl_contexts = [None] * len(urls)
        elif not isinstance(ssl_context, (list, tuple, set)):
            ssl_contexts = [ssl_context]
        else:
            ssl_contexts = list(ssl_context)

        if ssl_context is not None and len(urls) != len(ssl_contexts):
            raise Exception(_("len(url) not match len(ssl_context)"))

        self.name = name or uuid4().hex[-4:]

        self._open_task: Task | Future = Future()
        self._open_task.set_result(None)

        self._reconnect_task: Task | None = None

        self._watcher_task: Task | None = None
        self._watcher_task_started: Event = Event()

        self._closed: Future = Future()

        self._key: tuple = (name, get_event_loop(), tuple(sorted(urls)))

        if self._key not in self.__shared:
            self.__shared[self._key] = {
                "refs": 0,
                "url": urls[0],
                "ssl_context": ssl_contexts[0],
                "iter": _LoopIter(list(zip(urls, ssl_contexts))),
                "conn": None,
                "connect_lock": Lock(),
                "instances": {},
            }

        shared: dict = self.__shared[self._key]
        shared["instances"][self] = {
            "on_reconnect": {},
            "on_close": {},
            "callback_tasks": {"on_reconnect": {}, "on_close": {}},
        }
        self._shared = shared

        self._channel: aiormq.abc.AbstractChannel | None = None

        self._retry_timeouts = retry_timeouts or []

        self._exc_filter = exc_filter or (
            lambda e: isinstance(e, (asyncio.TimeoutError, ConnectionError, aiormq.exceptions.AMQPConnectionError))
        )

        self._state: ContextVar[str] = ContextVar("state", default="")

    def __del__(self):
        if getattr(self, "_key", None):
            if self._conn and not self.is_closed:
                logger.warning(_("%s unclosed"), self)
            self._shared["instances"].pop(self, None)
            if not self._shared["instances"]:
                self.__shared.pop(self._key, None)

    @property
    def url(self) -> str:
        return self._shared["url"]

    @property
    def ssl_context(self) -> SSLContext | None:
        return self._shared["ssl_context"]

    @property
    def _conn(self) -> aiormq.Connection:
        return self._shared["conn"]

    @_conn.setter
    def _conn(self, value: aiormq.Connection | None):
        self._shared["conn"] = value

    @property
    def _refs(self) -> int:
        return self._shared["refs"]

    @_refs.setter
    def _refs(self, value: int):
        self._shared["refs"] = value

    async def _execute_callbacks(
        self,
        tp: Literal["on_reconnect", "on_close"],
        reraise: bool | None = None,
    ):
        for name, callback in tuple(self._shared["instances"][self][tp].items()):
            logger.debug(_("%s execute callback[tp=%s, name=%s, reraise=%s]"), self, tp, name, reraise)

            self._shared["instances"][self]["callback_tasks"][tp][name] = current_task()
            try:
                if iscoroutinefunction(callback):
                    await callback()
                else:
                    res = callback()
                    if iscoroutine(res):
                        await res
            except Exception as e:
                logger.exception(_("%s callback[tp=%s, name=%s, callback=%s] error"), self, tp, name, callback)
                if reraise:
                    raise e
            finally:
                self._shared["instances"][self]["callback_tasks"][tp].pop(name, None)

    def set_callback(
        self,
        tp: Literal["on_reconnect", "on_close"],
        name: Hashable,
        callback: Callable,
    ):
        if shared := self._shared["instances"].get(self):
            if tp not in shared:
                raise ValueError("invalid callback type")
            shared[tp][name] = callback

    def remove_callback(
        self,
        tp: Literal["on_reconnect", "on_close"],
        name: Hashable,
        cancel: bool | None = None,
    ):
        if shared := self._shared["instances"].get(self):
            if tp not in shared:
                raise ValueError("invalid callback type")
            if name in shared[tp]:
                del shared[tp][name]
            if cancel:
                task = shared["callback_tasks"][tp].get(name)
                if task:
                    task.cancel()

    def remove_callbacks(self, cancel: bool | None = None):
        if shared := self._shared["instances"].get(self):
            if cancel:
                for tp in ("on_reconnect", "on_close"):
                    for task in shared["callback_tasks"][tp].values():
                        task.cancel()
            self._shared["instances"][self] = {
                "on_reconnect": {},
                "on_close": {},
                "callback_tasks": {"on_reconnect": {}, "on_close": {}},
            }

    def __str__(self):
        url = yarl.URL(self.url)
        if url.port:
            return f"{self.__class__.__name__}[{url.host}:{url.port}]#{self.name}"
        return f"{self.__class__.__name__}[{url.host}]#{self.name}"

    def __repr__(self):
        return self.__str__()

    @property
    def is_open(self) -> bool:
        """Returns is connection openned."""

        return self._watcher_task is not None and not (self.is_closed or self._conn is None or self._conn.is_closed)

    @property
    def is_closed(self) -> bool:
        """Returns is connection closed."""

        return self._closed.done()

    async def _watcher(self):
        try:
            self._watcher_task_started.set()
            aws = [self._conn.closing, self._closed]
            while True:
                done, pending = await wait(aws, timeout=5, return_when=FIRST_COMPLETED)
                if done or (self._conn and self._conn.is_connection_was_stuck):
                    break
        except Exception as e:
            logger.exception(e)
            logger.warning("%s %s %s", self, e.__class__, e)

        self._watcher_task = None

        if not self._closed.done():
            logger.warning(_("%s connection lost"), self)
            if self._conn:
                task = asyncio.create_task(self._conn.close())
                await wait([task], timeout=5)
            self._refs -= 1
            token = self._state.set("reconnect")
            try:
                logger.info(_("%s reconnecting..."), self)
                self._reconnect_task = create_task(self.open(retry_timeouts=iter(chain((1, 3), repeat(5)))))
            finally:
                self._state.reset(token)

    async def _connect(self):
        self._shared["url"], self._shared["ssl_context"] = next(self._shared["iter"])
        while not self.is_closed:
            connect_timeout = yarl.URL(self.url).query.get("connection_timeout")
            if connect_timeout is not None:
                connect_timeout = int(connect_timeout) / 1000
            else:
                connect_timeout = config.connect_timeout
            try:
                logger.info(_("%s connecting[timeout=%s]..."), self, connect_timeout)
                async with asyncio.timeout(connect_timeout):
                    self._conn = cast(aiormq.Connection, await aiormq.connect(self.url, context=self.ssl_context))
                logger.info(_("%s connected"), self)
                self._shared["iter"].reset()
                break
            except (
                asyncio.TimeoutError,
                ConnectionError,
                aiormq.exceptions.AMQPConnectionError,
                FileNotFoundError,
            ) as e:
                try:
                    url, ssl_context = next(self._shared["iter"])
                except StopIteration:
                    raise e
                logger.warning("%s %s %s", self, e.__class__, e)
                self._shared["url"] = url
                self._shared["ssl_context"] = ssl_context
            except Exception as e:
                self._shared["iter"].reset()
                raise e

    async def open(
        self,
        retry_timeouts: Iterable[int] | None = None,
        exc_filter: Callable[[Exception], bool] | None = None,
    ):
        """Open connection."""

        if self._state.get() == "on_reconnect":
            return

        if self.is_open:
            return

        if self.is_closed:
            self._closed = Future()

        async with self._shared["connect_lock"]:
            if retry_timeouts is None:
                retry_timeouts = self._retry_timeouts

            if exc_filter is None:
                exc_filter = self._exc_filter

            async def _open():
                if self._conn is None or self._conn.is_closed:
                    self._open_task = create_task(self._connect())
                    await self._open_task
                if self._watcher_task is None:
                    if self._state.get() == "reconnect":
                        token = self._state.set("on_reconnect")
                        try:
                            await self._execute_callbacks("on_reconnect", reraise=True)
                        except Exception as e:
                            await self._conn.close()
                            raise e
                        finally:
                            self._state.reset(token)
                    self._refs += 1
                    self._watcher_task_started.clear()
                    self._watcher_task = create_task(self._watcher())
                    await self._watcher_task_started.wait()

            if retry_timeouts:
                await _retry(retry_timeouts=retry_timeouts, exc_filter=exc_filter)(_open)()
            else:
                await _open()

    async def close(self):
        """Close connection."""

        if self.is_closed:
            return

        if not self._open_task.done():
            self._open_task.cancel()
            self._open_task = Future()

        if self._conn:
            await self._execute_callbacks("on_close")

        self._closed.set_result(None)

        if self._watcher_task:
            self._refs = max(0, self._refs - 1)

        if self._refs == 0:
            if self._conn:
                await self._conn.close()
                self._conn = None
                logger.info(_("%s close underlying connection"), self)

        self.remove_callbacks(cancel=True)

        if self._watcher_task:
            await self._watcher_task
            self._watcher_task = None

        if self._reconnect_task:
            if not self._reconnect_task.done():
                self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except (CancelledError, Exception):
                pass

        logger.info(_("%s closed"), self)

    @_retry(retry_timeouts=[0], exc_filter=lambda e: isinstance(e, aiormq.exceptions.ConnectionClosed))
    async def new_channel(self) -> aiormq.abc.AbstractChannel:
        """Create new channel."""

        await self.open()
        return await self._conn.channel()

    async def channel(self) -> aiormq.abc.AbstractChannel:
        """Get channel. A new channel will be created if one does not exist."""

        if self._channel is None or self._channel.is_closed:
            await self.open()
            if self._channel is None or self._channel.is_closed:
                self._channel = await self.new_channel()
        return self._channel


@dataclass(slots=True, frozen=True)
class ForeignExchange:
    """
    Foreign exchange. Declaration not allowed.
    May be used as RabbitMQ [default exchange](https://www.rabbitmq.com/tutorials/amqp-concepts#exchange-default)
    or foreign exchange.

    Args:
        name: Exchange name.
        timeout: Default timeout for network operations.
        conn: `rmqaio.Connection` instance.
        conn_factory: `rmqaio.Connection` instance factroy.

    Warning:
        One of the parameters `conn` or `conn_factory` is required.

    Examples:
        >>> ForeignExchange(conn_factory=lambda: Connection("amqp://localhost"))

        Or

        >>> conn = Connection("amqp://localhost")
        >>> ForeignExchange(conn=conn)
    """

    name: str = ""
    timeout: int | None = None
    conn: Connection = None  # type: ignore
    conn_factory: Callable[[], Connection] = field(default=None, repr=False)  # type: ignore

    def __post_init__(self):
        if all((self.conn, self.conn_factory)):
            raise Exception("conn and conn_factory are incompatible")
        if not any((self.conn, self.conn_factory)):
            raise Exception("conn or conn_factory is requried")
        if self.conn_factory:
            object.__setattr__(self, "conn", self.conn_factory())

    async def close(self):
        """Close exchange."""

        logger.info(_("close %s"), self)
        try:
            if self.conn_factory:
                self.conn.remove_callbacks(cancel=True)
        finally:
            if self.conn_factory:
                await self.conn.close()

    async def publish(
        self,
        data: bytes,
        routing_key: str,
        properties: dict | None = None,
        timeout: int | None = None,
    ):
        """
        Publish data to exchange.

        Args:
            data: Data to publish.
            routing_key: Routing key.
            properties: RabbitMQ message properties.
            timeout: Operation timeout. If `None` `self.timeout` will be used.
        """

        channel = await self.conn.channel()

        logger.debug(
            _("exchange[name='%s'] channel[%s] publish[routing_key='%s'] %s"),
            self.name,
            channel,
            routing_key,
            data if not config.log_sanitize else "<hidden>",
        )

        await channel.basic_publish(
            data,
            exchange=self.name,
            routing_key=routing_key,
            properties=BasicProperties(**(properties or {})),
            timeout=timeout or self.timeout,
        )


SimpleExchange = ForeignExchange  # backward compatibility


@dataclass(slots=True, frozen=True)
class DefaultExchange(ForeignExchange):
    """
    RabbitMQ [default exchange](https://www.rabbitmq.com/tutorials/amqp-concepts#exchange-default).
    Declaration not allowed.

    Args:
        timeout: Default timeout for network operations.
        conn: `rmqaio.Connection` instance.
        conn_factory: `rmqaio.Connection` instance factroy.

    Warning:
        One of the parameters `conn` or `conn_factory` is required.

    Examples:
        >>> DefaultExchange(conn_factory=lambda: Connection("amqp://localhost"))

        Or

        >>> conn = Connection("amqp://localhost")
        >>> DefaultExchange(conn=conn)
    """

    name: str = field(default="", init=False)


@dataclass(slots=True, frozen=True)
class Exchange:
    """
    RabbitMQ exchange.

    Args:
        name: Exchange name.
        type: RabbitMQ exchange [type](https://www.rabbitmq.com/tutorials/amqp-concepts#exchanges).
        durable: Durable or transient exchange.
        auto_delete: Exchange auto-delete parameter.
        timeout: Default timeout for network operations.
        conn: `rmqaio.Connection` instance.
        conn_factory: `rmqaio.Connection` instance factroy.

    Warning:
        One of the parameters `conn` or `conn_factory` is required.
    """

    name: str = ""
    type: ExchangeType = ExchangeType.DIRECT
    durable: bool = False
    auto_delete: bool = False
    timeout: int | None = None
    conn: Connection = None  # type: ignore
    conn_factory: Callable[[], Connection] = field(default=None, repr=False)  # type: ignore

    def __post_init__(self):
        if all((self.conn, self.conn_factory)):
            raise Exception("conn and conn_factory are incompatible")
        if not any((self.conn, self.conn_factory)):
            raise Exception("conn or conn_factory is requried")
        if self.conn_factory:
            object.__setattr__(self, "conn", self.conn_factory())

    async def close(self, delete: bool | None = None, timeout: int | None = None):
        """
        Close exchange.

        Args:
            delete: Delete exchnage on close.
            timeout: Operation timeout. If `None` `self.timeout` will be used.
        """

        if self.conn.is_closed:
            raise Exception("already closed")

        logger.info(_("close[delete=%s] %s"), delete, self)

        try:
            if self.conn_factory:
                self.conn.remove_callbacks(cancel=True)
            else:
                self.conn.remove_callback(
                    "on_reconnect",
                    f"on_reconnect_exchange_[{self.name}]_declare",
                    cancel=True,
                )
            if delete and self.name != "":
                channel = await self.conn.channel()
                try:
                    await channel.exchange_delete(self.name, timeout=timeout or self.timeout)
                except aiormq.exceptions.AMQPError:
                    pass
        finally:
            if self.conn_factory:
                await self.conn.close()

    async def declare(
        self,
        timeout: int | None = None,
        restore: bool | None = None,
        force: bool | None = None,
    ):
        """
        Declare exchange.

        Args:
            timeout: Operation timeout. If `None` `self.timeout` will be used.
            restore: Restore exchange on connection issue.
            force: Force redeclare exchange if it has already been declared with different parameters.
        """

        if self.name == "":
            return

        logger.info(_("declare[restore=%s, force=%s] %s"), restore, force, self)

        async def fn():
            channel = await self.conn.channel()
            await channel.exchange_declare(
                self.name,
                exchange_type=self.type,
                durable=self.durable,
                auto_delete=self.auto_delete,
                timeout=timeout or self.timeout,
            )

        if force:

            async def on_error(e):
                channel = await self.conn.channel()
                logger.info(_("delete[on_error] %s"), self)
                await channel.exchange_delete(self.name)

            await _retry(
                retry_timeouts=[0],
                exc_filter=lambda e: isinstance(e, aiormq.ChannelPreconditionFailed),
                on_error=on_error,
            )(fn)()

        else:
            await fn()

        if restore:
            self.conn.set_callback(
                "on_reconnect",
                f"on_reconnect_exchange_[{self.name}]_declare",
                partial(
                    self.declare,
                    timeout=timeout,
                    restore=restore,
                    force=force,
                ),
            )

    async def publish(
        self,
        data: bytes,
        routing_key: str,
        properties: dict | None = None,
        timeout: int | None = None,
    ):
        """
        Publish data to exchange.

        Args:
            data: Data to publish.
            routing_key: Routing key.
            properties: RabbitMQ message properties.
            timeout: Operation timeout. If `None` `self.timeout` will be used.
        """

        channel = await self.conn.channel()

        logger.debug(
            _("exchange[name='%s'] channel[%s] publish[routing_key='%s'] %s"),
            self.name,
            channel,
            routing_key,
            data if not config.log_sanitize else "<hidden>",
        )

        await channel.basic_publish(
            data,
            exchange=self.name,
            routing_key=routing_key,
            properties=BasicProperties(**(properties or {})),
            timeout=timeout or self.timeout,
        )


@dataclass(slots=True, frozen=True)
class Consumer:
    """
    Class to store Consumer data.

    Attributes:
        channel: Consumer channel.
        consumer_tag: Consumer tag.
    """

    channel: aiormq.abc.AbstractChannel
    consumer_tag: str

    async def close(self):
        """Close consumer channel."""

        logger.info(_("close %s"), self)
        await self.channel.close()


@dataclass(slots=True, frozen=True)
class Queue:
    """
    RabbitMQ queue.

    Args:
        name: Queue name.
        type: Queue type.
        durable: Queue durable [option](https://www.rabbitmq.com/docs/queues#durability).
        exclusive: Queue exclusive [option](https://www.rabbitmq.com/docs/queues#exclusive-queues).
        auto_delete: Queue auto-delete option.
        prefetch_count: RabbitMQ channel [prefecth count](https://www.rabbitmq.com/docs/confirms#channel-qos-prefetch).
        max_priority: Max [priority](https://www.rabbitmq.com/docs/priority) for `QueueType.CLASSIC` queue.
        expires: In seconds. Used for [`x-expires`](https://www.rabbitmq.com/docs/ttl#queue-ttl) option.
        msg_ttl: Message TTL in seconds. Used fo [`message-ttl`](https://www.rabbitmq.com/docs/ttl#per-queue-message-ttl) option.
        timeout: Default timeout for network operations.
        conn: `rmqaio.Connection` instance.
        conn_factory: `rmqaio.Connection` instance factroy.

    Warning:
        One of the parameters `conn` or `conn_factory` is required.
    """

    name: str
    type: QueueType = QueueType.CLASSIC
    durable: bool = False
    exclusive: bool = False
    auto_delete: bool = False
    prefetch_count: int | None = 1
    max_priority: int | None = None
    expires: int | None = None
    msg_ttl: int | None = None
    dead_letter_exchange: str | None = None
    arguments: dict[str, Any] | None = None
    timeout: int | None = None
    conn: Connection = None  # type: ignore
    conn_factory: Callable[[], Connection] = field(default=None, repr=False)  # type: ignore
    consumer: Consumer | None = field(default=None, init=False)
    bindings: list[tuple[ForeignExchange | DefaultExchange | Exchange, str]] = field(default_factory=list, init=False)

    def __post_init__(self):
        if all((self.conn, self.conn_factory)):
            raise Exception("conn and conn_factory are incompatible")
        if not any((self.conn, self.conn_factory)):
            raise Exception("conn or conn_factory is requried")
        if self.conn_factory:
            object.__setattr__(self, "conn", self.conn_factory())
        self.conn.set_callback(
            "on_reconnect",
            f"on_reconnect_queue_[{self.name}]_cleanup_consumer",
            lambda: object.__setattr__(self, "consumer", None),
        )
        self.conn.set_callback(
            "on_close",
            f"on_close_queue_[{self.name}]_cleanup_consumer",
            lambda: object.__setattr__(self, "consumer", None),
        )

    async def close(self, delete: bool | None = None, timeout: int | None = None):
        """
        Close queue.

        Args:
            delete: Delete queue on close.
            timeout: Operation timeout. If `None` `self.timeout` will be used.
        """

        if self.conn.is_closed:
            raise Exception("already closed")

        logger.info(_("close[delete=%s] %s"), delete, self)

        try:
            await self.stop_consume()
            if self.conn_factory:
                self.conn.remove_callbacks(cancel=True)
            else:
                self.conn.remove_callback(
                    "on_reconnect",
                    f"on_reconnect_queue_[{self.name}]_declare",
                    cancel=True,
                )
            if delete:
                channel = await self.conn.channel()
                try:
                    await channel.queue_delete(self.name, timeout=timeout or self.timeout)
                except aiormq.exceptions.AMQPError as e:
                    logger.warning(e)
        finally:
            if self.conn_factory:
                await self.conn.close()

    async def declare(
        self,
        timeout: int | None = None,
        restore: bool | None = None,
        force: bool | None = None,
    ):
        """
        Declare queue.

        Args:
            timeout: Operation timeout. If `None` `self.timeout` will be used.
            restore: Restore this binding on connection issue.
            force: Force redeclare queue if it has already been declared with different parameters.
        """

        logger.info(_("declare[restore=%s, force=%s] %s"), restore, force, self)

        async def fn():
            channel = await self.conn.channel()
            arguments = self.arguments.copy() if self.arguments else {}
            arguments["x-queue-type"] = self.type
            if self.max_priority:
                arguments["x-max-priority"] = self.max_priority
            if self.expires:
                arguments["x-expires"] = int(self.expires) * 1000
            if self.msg_ttl:
                arguments["x-message-ttl"] = int(self.msg_ttl) * 1000
            if self.dead_letter_exchange:
                arguments["x-dead-letter-exchange"] = self.dead_letter_exchange
            await channel.queue_declare(
                self.name,
                durable=self.durable,
                exclusive=self.exclusive,
                auto_delete=self.auto_delete,
                arguments=arguments,
                timeout=timeout or self.timeout,
            )

        if force:

            async def on_error(e):
                channel = await self.conn.channel()
                logger.info(_("delete[on_error] %s"), self)
                await channel.queue_delete(self.name)

            await _retry(
                retry_timeouts=[0],
                exc_filter=lambda e: isinstance(e, aiormq.ChannelPreconditionFailed),
                on_error=on_error,
            )(fn)()

        else:
            await fn()

        if restore:
            self.conn.set_callback(
                "on_reconnect",
                f"on_reconnect_queue_[{self.name}]_declare",
                partial(
                    self.declare,
                    timeout=timeout,
                    restore=restore,
                    force=force,
                ),
            )

    async def bind(
        self,
        exchange: ForeignExchange | DefaultExchange | Exchange,
        routing_key: str,
        timeout: int | None = None,
        restore: bool | None = None,
    ):
        """
        Bind queue to exchange.

        Args:
            exchange: RabbitMQ exchange to bind.
            routing_key: Routing key to bind.
            timeout: Operation timeout. If `None` `self.timeout` will be used.
            restore: Restore this binding on connection issue.
        """

        logger.info(
            _("bind queue '%s' to exchange '%s' with routing_key '%s'"),
            self.name,
            exchange.name,
            routing_key,
        )

        channel = await self.conn.channel()
        await channel.queue_bind(
            self.name,
            exchange.name,
            routing_key=routing_key,
            timeout=timeout or self.timeout,
        )

        if (exchange, routing_key) not in self.bindings:
            self.bindings.append((exchange, routing_key))

        if restore:
            self.conn.set_callback(
                "on_reconnect",
                f"on_reconnect_queue_[{self.name}]_bind_[{exchange.name}]_[{routing_key}]",
                partial(
                    self.bind,
                    exchange,
                    routing_key,
                    timeout=timeout,
                    restore=restore,
                ),
            )

    async def unbind(
        self,
        exchange: ForeignExchange | DefaultExchange | Exchange,
        routing_key: str,
        timeout: int | None = None,
    ):
        """
        Unbind queue.

        Args:
            exchange: Echange to unbind from.
            routing_key: Routing key to unbind.
            timeout: Operation timeout. If `None` `self.timeout` will be used.
        """

        if self.bindings:
            logger.info(
                _("unbind queue '%s' from exchange '%s' for routing_key '%s'"),
                self.name,
                exchange.name,
                routing_key,
            )

            if (exchange, routing_key) in self.bindings:
                self.bindings.remove((exchange, routing_key))

                channel = await self.conn.channel()
                await channel.queue_unbind(
                    self.name,
                    exchange.name,
                    routing_key=routing_key,
                    timeout=timeout or self.timeout,
                )

                self.conn.remove_callback(
                    "on_reconnect",
                    f"on_reconnect_queue_[{self.name}]_bind_[{exchange.name}]_[{routing_key}]",
                    cancel=True,
                )

    async def consume(
        self,
        callback: Callable[[aiormq.abc.AbstractChannel, aiormq.abc.DeliveredMessage], Coroutine],
        prefetch_count: int | None = None,
        timeout: int | None = None,
        retry_timeout: int = 5,
    ) -> Consumer:
        """
        Consume queue.

        Args:
            callback: Async callback to call on incoming `aiormq.abc.DeliveredMessage`.
            prefetch_count: RabbitMQ channel [prefecth count](https://www.rabbitmq.com/docs/confirms#channel-qos-prefetch).
                If `None` `self.prefetch_count` will be used.
            timeout: Operation timeout. If `None` `self.timeout` will be used.
            retry_timeout: Timeout for retry. Used as argument for `itertools.repeat` function.
        """

        if self.consumer is None:
            channel = await self.conn.new_channel()
            await channel.basic_qos(
                prefetch_count=prefetch_count or self.prefetch_count,
                timeout=timeout or self.timeout,
            )

            object.__setattr__(
                self,
                "consumer",
                Consumer(
                    channel=channel,
                    consumer_tag=(  # type: ignore
                        await channel.basic_consume(
                            self.name,
                            partial(callback, channel),
                            timeout=timeout or self.timeout,
                        )
                    ).consumer_tag,
                ),
            )

            logger.info(_("consume %s"), self)

            self.conn.set_callback(
                "on_reconnect",
                f"on_reconnect_queue_[{self.name}]_consume",
                partial(
                    self.consume,
                    callback,
                    prefetch_count=prefetch_count,
                    timeout=timeout,
                ),
            )

        return cast(Consumer, self.consumer)

    async def stop_consume(self, timeout: int | None = None):
        """
        Stop consume queue.

        Args:
            timeout: Operation timeout. If `None` `self.timeout` will be used.
        """

        self.conn.remove_callback(
            "on_reconnect",
            f"on_reconnect_queue_[{self.name}]_consume",
            cancel=True,
        )

        if self.consumer and not self.consumer.channel.is_closed:
            logger.info(_("stop consume %s"), self)

            await self.consumer.channel.basic_cancel(self.consumer.consumer_tag, timeout=timeout)
            await self.consumer.close()
            object.__setattr__(self, "consumer", None)
