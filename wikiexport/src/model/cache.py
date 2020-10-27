from datetime import datetime

from src.utils import repeat_if_exception

class Cache:

    def get_entry(self, dt: datetime) -> str:
        raise NotImplementedError()

    def set_entry(self, dt: datetime) -> None:
        raise NotImplementedError()


class LocalCache(Cache):

    CACHE_FILE_PATH = '/tmp/wikiexporter_cache.txt'
    DATETIME_FORMAT = '%Y%m%dT%H:%M:%S'

    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    @classmethod
    def _remove_instance(cls):
        cls.__instance = None

    def __init__(self):
        if LocalCache.__instance is None:
            self.cache = LocalCache._populate_cache()
            LocalCache.__instance = self
        else:
            raise Exception('Already instanciated')

    def add_entry(self, dt: datetime, file_path):
        self.cache[dt] = file_path

    def get_entry(self, dt: datetime) -> None:
        return self.cache.get(dt, None)

    def __contains__(self, dt: datetime):
        return dt in self.cache

    @classmethod
    @repeat_if_exception(message='Something went wrong when populating the cache', nb_times=3)
    def _populate_cache(cls) -> dict:
        cache = {}

        with open(cls.CACHE_FILE_PATH, 'a+') as file_handle:
            file_handle.seek(0)
            for line in file_handle.readlines():
                dt_str, export_path = line.strip().split(',')
                dt = datetime.strptime(dt_str, cls.DATETIME_FORMAT)
                cache[dt] = export_path

        return cache

    @repeat_if_exception(message='Something went wrong when saving the cache', nb_times=3)
    def _save_cache(self) -> None:
        with open(self.CACHE_FILE_PATH, 'w') as file_handle:
            for dt, export_path in self.cache.items():
                dt_str = dt.strftime(self.DATETIME_FORMAT)
                file_handle.write(f'{dt_str},{export_path}\n')