from abc import abstractmethod
from typing import *

from .crawler import AbstractCrawler


class WikipediaCrawler(AbstractCrawler):

    @abstractmethod
    def __init__(self, config: dict) -> None:
        """
        Wikipedia Crawler
        """
        super().__init__(config=config)


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

