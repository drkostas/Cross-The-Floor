from typing import *
import logging
import pandas as pd

from .visualizer import AbstractVisualizer


class PlotlyVisualizer(AbstractVisualizer):
    logger = logging.getLogger('PlotlyVisualizer')

    def __init__(self, config: dict) -> None:
        """
        Plotly Visualizer
        """
        super().__init__(config=config)

    def create_sankey_diagram(self, data_df: pd.DataFrame):
        pass
