from abc import ABC, abstractmethod
from typing import *


class AbstractCrawler(ABC):
    __slots__ = '__config__'

    __config__: dict

    @abstractmethod
    def __init__(self, config: dict) -> None:
        """
        Abstract Crawler
        """
        self.__config__ = config

    @abstractmethod
    def __retrieve_html__(self, **kwargs):
        pass

    @abstractmethod
    def __parse_html__(self, **kwargs):
        pass

    @abstractmethod
    def get_table(self, **kwargs):
        pass

    @abstractmethod
    def get_tables(self, **kwargs):
        pass