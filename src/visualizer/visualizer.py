from abc import ABC, abstractmethod
import logging


class AbstractVisualizer(ABC):
    __slots__ = '__config__'

    __config__: dict

    def __init__(self, config) -> None:
        """
        Abstract Visualizer
        """
        self.__config__ = config

    @abstractmethod
    def create_sankey_diagram(self):
        pass