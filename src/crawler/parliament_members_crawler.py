from typing import *
import sys
import logging
import urllib.request, urllib.error, urllib.parse
import re
import pandas as pd

from .wikipedia_crawler import WikipediaCrawler

logger = logging.getLogger('ParliamentMembersCrawler')


class ParliamentMembersCrawler(WikipediaCrawler):

    def __init__(self, config: dict) -> None:
        """
        Parliament Members Crawler
        """
        super().__init__(config=config)

    @staticmethod
    def __retrieve_html__(url: str) -> str:
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0'}
            req = urllib.request.Request(url, headers=header)
            page = urllib.request.urlopen(req).read()
        except Exception as e:
            logger.warning(str(e))
            page = 'None'
        if type(page) is not str:
            page = page.decode('utf-8')
        return page

    @classmethod
    def __parse_html__(cls, source: dict) -> str:
        html = cls.__retrieve_html__(source['link'])
        html = html.replace('\n', '', sys.maxsize)
        regex_str = "({table_header}.*?)</{enclosing_tag}>".format(table_header=source["table_header"],
                                                                   enclosing_tag=source["enclosing_tag"])
        logger.debug("regex_str:")
        logger.debug(regex_str)
        pattern = re.compile(regex_str)
        logger.debug("pattern:")
        logger.debug(pattern)
        pattern_match = pattern.findall(html)
        logger.debug("pattern_match:")
        logger.debug(pattern_match)
        table = "<table>{}</table>".format(pattern_match[0])
        return table

    def get_table(self, source: dict) -> pd.DataFrame:
        table = self.__parse_html__(source)
        df_table = pd.read_html(table)[0]
        if "ignore_cols" in source:
            df_table.drop(source["ignore_cols"], axis=1)
            logger.debug("Dropping column(s): %s for %s" % (str(source["ignore_cols"]), str(source['attr_col']['name_on_plot'])))
        return df_table

    def get_tables(self) -> Iterator[Tuple[pd.DataFrame, str, dict]]:
        for source in self.__config__['sources']:
            logger.debug("Crawling source:")
            logger.debug(source)
            yield self.get_table(source), source['name_col'], source['attr_col']
