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
    def crawl(self) -> None:
        pass