from datetime import datetime
from abc import ABC, abstractmethod

from src.utils import repeat_if_exception

class Cache(ABC):
    """
    An abstract base class for cache capabilities
    """

    @abstractmethod
    def get_entry(self, dt: datetime) -> str:
        """ An abstract method to get the result of dt's (datetime) request

        :param dt: datetime of the request
        :return: path to the CSV result file
        """

        pass


    @abstractmethod
    def set_entry(self, dt: datetime) -> None:
        """ An abstract method to set the path of dt's (datetime) request result

        :param dt: datetime of the request
        :return: None
        """

        pass



class LocalCache(Cache):
    """
    A simple local cache based on a file saved in CACHE_FILE_PATH. It's a singleton class.
    File content is loaded once the first instance is instantiated.
    """

    CACHE_FILE_PATH = '/tmp/wikiexporter_cache.txt'
    DATETIME_FORMAT = '%Y%m%dT%H:%M:%S'

    __instance = None

    @classmethod
    def get_instance(cls) -> 'LocalCache':
        """Get the only instance of LocalCache, instantiate it if needed

        :return: The only instance of LocalCache
        """

        if cls.__instance is None:
            cls()

        return cls.__instance


    @classmethod
    def _remove_instance(cls) -> None:
        """ Clear the only instance of this class

        :return: None
        """

        cls.__instance = None


    def __init__(self) -> None:
        """ Populate the cache the first time the only instance is instantiated
        """

        if LocalCache.__instance is None:
            self.cache = self._populate_cache()
            LocalCache.__instance = self
        else:
            raise Exception('Already instantiated')


    def set_entry(self, dt: datetime, file_path: str):
        """ Add an Entry in the cache (in Memory) and replaces a previously set entry with the same key

        :param dt: datetime of the request
        :param file_path: path where the CSV file is saved
        :return: None
        """

        self.cache[dt] = file_path


    def get_entry(self, dt: datetime) -> str:
        """ Get the path to CSV file of the request if any saved in cache

        :param dt: datetime of the request
        :return: path to the CSV file
        """

        return self.cache.get(dt, None)


    def __contains__(self, dt: datetime) -> bool:
        """ inclusion test that relies on the __contains__ magic method.
        LocalCache can be used with the in operator: datetime.now() in cache

        :param dt: datetime of the request
        :return: True if datetime in cache, false otherwise
        """

        return dt in self.cache


    @repeat_if_exception(message='Something went wrong when populating the cache', nb_times=3)
    def _populate_cache(self) -> dict:
        """ private method used to populate the cache from local storage. It creates the file when the application is
        started for the first time (the file doesn't exist

        :return: dict(datetime -> str) where the key a datetime object and the value is the path to CSV file
        """

        cache = {}

        with open(self.CACHE_FILE_PATH, 'a+') as file_handle:
            file_handle.seek(0)
            for line in file_handle.readlines():
                dt_str, export_path = line.strip().split(',')
                dt = datetime.strptime(dt_str, self.DATETIME_FORMAT)
                cache[dt] = export_path

        return cache


    @repeat_if_exception(message='Something went wrong when saving the cache', nb_times=3)
    def save_cache(self) -> None:
        """ Commits the cache to secondary storage in LocalCache.CACHE_FILE_PATH

        :return: None
        """

        with open(self.CACHE_FILE_PATH, 'w') as file_handle:
            for dt, export_path in self.cache.items():
                dt_str = dt.strftime(self.DATETIME_FORMAT)
                file_handle.write(f'{dt_str},{export_path}\n')
