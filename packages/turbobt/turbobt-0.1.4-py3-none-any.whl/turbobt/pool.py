from __future__ import annotations

import contextlib
import contextvars
import itertools

import tenacity
import websockets.exceptions

import turbobt.substrate.exceptions
from turbobt.subtensor.client import Subtensor

_subtensor = contextvars.ContextVar[Subtensor]("subtensor")


def retry(func):
    return func







    @tenacity.retry(
        retry=tenacity.retry_if_exception_type((
            turbobt.substrate.exceptions.SubstrateException,
            websockets.exceptions.WebSocketException,
            ConnectionError,
        )),
        stop=tenacity.stop_after_attempt(3),
    )
    async def wrapper(self, *args, **kwargs):
        # TODO actively check `block_hash` in kwargs?

        pool: SubtensorPool = self.client._pool

        try:
            async with pool.lite_node_ctx():
                return await func(self, *args, **kwargs)
        except turbobt.substrate.exceptions.UnknownBlock:
            # TODO already in archive?
            async with pool.archive_node_ctx():
                return await func(self, *args, **kwargs)

    return wrapper


class SubtensorPool:
    def __init__(
        self,
        lite: list[Subtensor],
        lite_backup: list[Subtensor],
        archive: list[Subtensor],
        archive_backup: list[Subtensor],
    ):
        self._lite = lite
        self._lite_backup = lite_backup
        self._archive = archive
        self._archive_backup = archive_backup

    async def get_archive_node(self) -> Subtensor:
        # TODO
        return self._archive[0]

    async def get_lite_node(self) -> Subtensor:
        # TODO
        return self._lite[0]

    @contextlib.asynccontextmanager
    async def lite_node_ctx(self):
        token = None

        try:
            _subtensor.get()
        except LookupError:
            subtensor = await self.get_lite_node()
            token = _subtensor.set(subtensor)

        try:
            yield subtensor
        except Exception as e:
            # TODO
            self._lite = self._lite_backup
            raise
        finally:
            if token:
                _subtensor.reset(token)

    @contextlib.asynccontextmanager
    async def archive_node_ctx(self):
        token = None

        try:
            _subtensor.get()
        except LookupError:
            subtensor = await self.get_archive_node()
            token = _subtensor.set(subtensor)

        try:
            yield subtensor
        finally:
            if token:
                _subtensor.reset(token)

    def get(self) -> Subtensor:
        return _subtensor.get()

    # TODO lazy
    async def __aenter__(self):
        for subtensor in itertools.chain(
            self._lite,
            self._archive,
            self._lite_backup,
            self._archive_backup,
        ):
            await subtensor.__aenter__()

    async def __aexit__(self, *args, **kwargs):
        for subtensor in itertools.chain(
            self._lite,
            self._archive,
            self._lite_backup,
            self._archive_backup,
        ):
            await subtensor.__aexit__(*args, **kwargs)
