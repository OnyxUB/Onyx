import json
import logging
import os
from .. import main

logger = logging.getLogger(__name__)

ORIGIN = "/".join(main.__file__.split("/")[:-2])
DB_PATH = os.path.join(ORIGIN, "onyx", "database.json")


class JsonBackend:
    def __init__(self, client=None):
        self._db_path = DB_PATH
        if not os.path.exists(self._db_path):
            with open(self._db_path, "w", encoding="utf-8") as f:
                json.dump({}, f)
        self.close = lambda: None

    async def init(self, trigger_refresh=None):
        pass

    async def do_download(self):
        try:
            with open(self._db_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            logger.exception("Failed to read database file!")
            return "{}"

    async def do_upload(self, data):
        try:
            with open(self._db_path, "w", encoding="utf-8") as f:
                f.write(data)
            return True
        except Exception:
            logger.exception("Database save failed!")
            raise

    async def store_asset(self, message):
        raise NotImplementedError

    async def fetch_asset(self, id_):
        raise NotImplementedError