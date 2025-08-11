
import os


class Config(object):
    def __init__(self):
        self._endpoint = os.getenv("YDB_ENDPOINT")
        self._database = os.getenv("YDB_DATABASE")

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def database(self):
        return self._database


ydb_configuration = Config()
