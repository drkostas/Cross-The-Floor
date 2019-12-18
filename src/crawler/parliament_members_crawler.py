from typing import *
import sys
import logging
import urllib.request, urllib.error, urllib.parse
import re
import pandas as pd

from .wikipedia_crawler import WikipediaCrawler


class ParliamentMembersCrawler(WikipediaCrawler):
    logger = logging.getLogger('ParliamentMembersCrawler')

    def __init__(self, config: dict) -> None:
        """
        Parliament Members Crawler
        """
        super().__init__(config=config)

    @staticmethod
    def __retrieve_html__(url):
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0'}
            req = urllib.request.Request(url, headers=header)
            page = urllib.request.urlopen(req).read()
        except Exception as e:
            print(e)
            page = 'None'
        if type(page) is not str:
            page = page.decode('utf-8')
        return page

    @classmethod
    def __parse_html__(cls, source):
        html = cls.__retrieve_html__(source['link'])
        html = html.replace('\n', '', sys.maxsize)
        regex_str = "({table_header}.*?)</{enclosing_tag}>".format(table_header=source["table_header"],
                                                                  enclosing_tag=source["enclosing_tag"])
        pattern = re.compile(regex_str)
        return "<table>{}</table>".format(pattern.findall(html)[0])

    def get_table(cls, source):
        table = cls.__parse_html__(source)
        df_table = pd.read_html(table)[0]
        df_table.drop(source["ignore_cols"], axis=1)
        return df_table

    def get_tables(self):
        for source in self.__config__['sources']:
            yield self.get_table(source)

    def __iter__(self):
        return self.get_tables()

