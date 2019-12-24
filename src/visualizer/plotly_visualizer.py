from typing import *
import logging
import pandas as pd
import numpy as np
import plotly

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)
pd.set_option('display.width', 1000)

from .visualizer import AbstractVisualizer


class PlotlyVisualizer(AbstractVisualizer):
    logger = logging.getLogger('PlotlyVisualizer')

    def __init__(self, config: dict) -> None:
        """
        Plotly Visualizer
        """
        super().__init__(config=config)

    @staticmethod
    def __generate_sankey__(df: pd.DataFrame, cat_cols=None, value_cols: str = '', title: str = 'Sankey Diagram'):
        # maximum of 6 value cols -> 6 colors
        if cat_cols is None:
            cat_cols = []
        colorPalette = ['#4B8BBE', '#306998', '#646464', '#FFD43B', '#FFE873']
        labelList = []
        colorNumList = []
        for catCol in cat_cols:
            labelListTemp = list(set(df[catCol].values))
            colorNumList.append(len(labelListTemp))
            labelList = labelList + labelListTemp

        # remove duplicates from labelList
        labelList = list(dict.fromkeys(labelList))
        print(labelList)
        import sys
        # sys.exit()

        # define colors based on number of levels
        colorList = []
        for idx, colorNum in enumerate(colorNumList):
            colorList = colorList + [colorPalette[idx]] * colorNum

        # transform df into a source-target pair
        sourceTargetDf = df[[cat_cols[0], cat_cols[1], value_cols]]
        print("Generate sankey 1")
        print(sourceTargetDf.head(20))
        sourceTargetDf.columns = ['source', 'target', 'count']
        for i in range(1, len(cat_cols) - 1):
            for j in range(1, i+1):
                tempDf = df[[cat_cols[j], cat_cols[i + 1], value_cols]]
                tempDf.columns = ['source', 'target', 'count']
                sourceTargetDf = pd.concat([sourceTargetDf, tempDf])
                sourceTargetDf = sourceTargetDf.groupby(['source', 'target']).agg({'count': 'sum'}).reset_index()
        print("Generate sankey 2")
        print(sourceTargetDf.head(20))

        # add index for source-target pair
        sourceTargetDf["sourceID"] = sourceTargetDf["source"].apply(lambda x: labelList.index(x))
        sourceTargetDf["targetID"] = sourceTargetDf["target"].apply(lambda x: labelList.index(x))
        print("Generate sankey 3")
        print(sourceTargetDf.head(20))
        # import sys;sys.exit()
        # creating the sankey diagram
        data = dict(
            type='sankey',
            node=dict(
                hoverinfo="all",
                pad=15,
                thickness=20,
                line=dict(
                    color="black",
                    width=0.5
                ),
                label=labelList,
                color=colorList
            ),
            link=dict(
                source=sourceTargetDf['sourceID'],
                target=sourceTargetDf['targetID'],
                value=sourceTargetDf['count']
            )
        )

        layout = dict(
            title=title,
            font=dict(
                size=10
            )
        )

        fig = dict(data=[data], layout=layout)
        return fig

    @staticmethod
    def transform_row(row, cols):
        # Fix first column
        row[cols[0]] = 'Total(300)'
        # if row[cols[1]] == '_':
        #     row[cols[0]] = np.NaN
        for ind in range(1, len(cols) - 1):
            # if row[cols[ind + 1]] == '_' or row[cols[ind]] == '_':
            #     row[cols[ind]] = np.NaN
            # else:
            row[cols[ind]] = row[cols[ind]] + '({})'.format(cols[ind].split()[-1])
        if row[cols[-1]] == '_':
            row[cols[-1]] = np.NaN
        else:
            row[cols[-1]] = row[cols[-1]] + '({})'.format(cols[-1].split()[-1])
        return row

    def create_sankey_diagram(self, data_df: pd.DataFrame, attribute_cols: List, name_col: str,
                              plot_name: Optional[str] = 'Sankey Diagram'):
        data_df = data_df.groupby(attribute_cols).count().reset_index()
        print("Create sankey 1")
        print(data_df)
        data_df[attribute_cols] = data_df[attribute_cols].apply(
            lambda row: self.transform_row(row=row, cols=attribute_cols), axis=1)
        print("Create sankey 2")
        print(data_df)
        import sys
        # sys.exit(1)
        fig = self.__generate_sankey__(df=data_df, cat_cols=attribute_cols, value_cols=name_col, title=plot_name)
        plotly.offline.plot(fig, validate=True)
