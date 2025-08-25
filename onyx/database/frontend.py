import asyncio
import json
import logging

from .backend import JsonBackend


class Database(dict):
    def __init__(self, backend, noop=False):
        super().__init__()
        self._noop = noop or backend is None
        self._backend = backend
        self._loading = True
        self._waiter = asyncio.Event()

    def __repr__(self):
        return object.__repr__(self)

    async def init(self):
        if self._backend is None:
            self._loading = False
            self._waiter.set()
            return

        await self._backend.init(self.reload)
        db = await self._backend.do_download()

        if db is not None:
            try:
                self.update(**json.loads(db))
            except Exception:
                pass

        self._loading = False
        self._waiter.set()

    async def close(self):
        try:
            await self.save()
        except Exception:
            logging.info("Database close failed", exc_info=True)

        if self._backend is not None:
            self._backend.close()

    def save(self):
        return asyncio.create_task(self._save())

    def get(self, owner, key, default=None):
        try:
            return self[owner][key]
        except KeyError:
            return default

    def set(self, owner, key, value):
        super().setdefault(owner, {})[key] = value
        return self.save()

    async def _save(self):
        if self._noop:
            return

        if self._loading:
            await self._waiter.wait()

        await self._backend.do_upload(json.dumps(self, indent=4))

    async def reload(self, event):
        if self._noop:
            return

        try:
            self._waiter.clear()
            self._loading = True

            db = await self._backend.do_download()
            self.clear()
            self.update(**json.loads(db))
        finally:
            self._loading = False
            self._waiter.set()

    async def store_asset(self, message):
        return await self._backend.store_asset(message)

    async def fetch_asset(self, message):
        return await self._backend.fetch_asset(message)


def get_db(noop=False):
    return Database(JsonBackend(), noop)