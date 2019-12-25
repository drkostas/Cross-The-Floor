from typing import *
import logging
import pandas as pd
import plotly
import seaborn as sns

from .visualizer import AbstractVisualizer


class PlotlyVisualizer(AbstractVisualizer):
    logger = logging.getLogger('PlotlyVisualizer')

    def __init__(self, config: dict) -> None:
        """
        Plotly Visualizer
        """
        super().__init__(config=config)

    @staticmethod
    def __generate_sankey_figure__(nodes_df: pd.DataFrame, edges_df: pd.DataFrame, color_list: List,
                                   title: str = 'Sankey Diagram'):

        # add index for source-target pair
        nodes_list = nodes_df['Node'].tolist()
        nodes_count_list = nodes_df['Count'].tolist()
        node_types = {node.split('_')[-1]: [] for node in nodes_list}
        color_palette = list(sns.color_palette(None, len(node_types.keys())).as_hex())
        for ind, node in enumerate(nodes_list):
            node_types[node.split('_')[-1]].append(ind)
        print(node_types)
        x_positions = [0 for _ in range(len(nodes_list))]
        y_positions = [0 for _ in range(len(nodes_list))]
        node_color_list = [0 for _ in range(len(nodes_list))]
        x_position = 0.0
        for ind_1, key in enumerate(sorted(node_types.keys())):
            y_position = 1.0
            for ind_2, node in sorted(enumerate(node_types[key]), key=lambda row: nodes_count_list[row[1]],
                                      reverse=False):
                node_color_list[node] = color_palette[ind_1]
                x_positions[node] = round(x_position, 3)
                y_positions[node] = round(y_position, 3)
                y_position -= 1.0 / len(node_types[key])
            x_position += 1.0 / len(node_types.keys())


        edges_df['SourceID'] = edges_df['Source'].apply(lambda x: nodes_list.index(x))
        edges_df['TargetID'] = edges_df['Target'].apply(lambda x: nodes_list.index(x))
        # print(edges_df)
        edge_years = set([node.split('_')[-1] for node in nodes_list])
        edge_types = dict(zip(sorted(edge_years), color_palette))
        print(edge_types)
        source_from_edges_list = edges_df['Source'].to_list()
        edge_color_list = [edge_types[node.split('_')[-1]] for node in source_from_edges_list]


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
                label=nodes_list,
                color=node_color_list,
                x=x_positions,
                y=y_positions,
                # groups=list(node_types.values())
            ),
            link=dict(
                source=edges_df['SourceID'],
                target=edges_df['TargetID'],
                value=edges_df['Count'],
                label=edges_df['Count'],
                color=edge_color_list
            ),
            arrangement='freeform'
        )

        layout = dict(
            title='Test Sankey',
            font=dict(
                size=10
            )
        )

        fig = dict(data=[data], layout=layout)
        return fig

    def plot(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame, attribute_cols: List, name_col: str):
        # Generate color palette
        color_palette = list(sns.color_palette(None, nodes_df.count()[0]).as_hex())
        color_list = color_palette
        fig = self.__generate_sankey_figure__(nodes_df=nodes_df, edges_df=edges_df, color_list=color_list,
                                              title=self.__config__['plot_name'])
        self.logger.info(fig)
        filename = "{}/{}.html".format(self.__config__['target_path'], self.__config__['plot_name'])

        plotly.offline.plot(fig, validate=True, filename=filename)
