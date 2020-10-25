from datetime import datetime


class Cache: #todo make this an abstract class
    pass

class LocalCache: #todo make this a singleton
    """
    file
    date in %y%M
    """

    CACHE_FILE_PATH = '/tmp/wikiexporter_cache.txt'
    DATETIME_FORMAT = '%Y%m%dT%H:%M:%S'

    def __init__(self):
        self.cache = self._populate_cache()


    def add_entry(self, dt: datetime, file_path):
        self.cache[dt] = file_path

    def get_entry(self, dt: datetime):
        return self.cache.get(dt, None)

    def __contains__(self, dt: datetime):
        return dt in self.cache

    @classmethod
    def _populate_cache(cls) -> dict:
        cache = {}

        with open(cls.CACHE_FILE_PATH, 'a+') as file_handle:

            for line in file_handle.readlines():
                dt_str, export_path = line.split(',')
                dt = datetime.strptime(dt_str, cls.DATETIME_FORMAT)
                cache[dt] = export_path

        return cache

    def _save_cache(self) -> None:
        with open(self.CACHE_FILE_PATH, 'w') as file_handle:
            for dt, export_path in self.cache.items():
                dt_str = dt.strftime(self.DATETIME_FORMAT)
                file_handle.write(f'{dt_str},{export_path}')
