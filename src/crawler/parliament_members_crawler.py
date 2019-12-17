from typing import *
import logging

from .wikipedia_crawler import WikipediaCrawler



class ParliamentMembersCrawler(WikipediaCrawler):
    logger = logging.getLogger('ParliamentMembersCrawler')

    def __init__(self, config: dict) -> None:
        """
        Parliament Members Crawler
        """
        super().__init__(config=config)

    def crawl(self) -> None:
        pass
