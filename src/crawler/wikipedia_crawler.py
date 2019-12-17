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
    def crawl(self) -> None:
        pass
