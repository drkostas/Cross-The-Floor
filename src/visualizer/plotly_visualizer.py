from typing import *
import logging
import pandas as pd
import plotly
import plotly.graph_objects as go
import seaborn as sns

from .visualizer import AbstractVisualizer

logger = logging.getLogger('PlotlyVisualizer')


class PlotlyVisualizer(AbstractVisualizer):

    def __init__(self, config: dict) -> None:
        """
        Plotly Visualizer
        """
        super().__init__(config=config)

    @staticmethod
    def __generate_node_positions_and_colors__(nodes_list: List,
                                               nodes_count_list: List,
                                               color_palette: List,
                                               grouping: str = 'year') -> Tuple[List, List, List, Dict]:
        # Get the node types based on the year
        node_types: Dict = {node.split('_')[-1]: [] for node in nodes_list}
        # For each node_type assign the equivalent node index
        for ind, node in enumerate(nodes_list):
            node_types[node.split('_')[-1]].append(ind)
        logger.debug("Node types: %s" % str(node_types))
        # Init x, y coordinates and node colors lists
        x_positions: List = [0 for _ in range(len(nodes_list))]
        y_positions: List = [0 for _ in range(len(nodes_list))]
        if grouping == 'year':
            node_color_list = [0 for _ in range(len(nodes_list))]
        elif grouping == 'none':
            node_color_list = color_palette
        else:
            raise Exception("Color grouping %s not supported" % grouping)
        # Fill the lists with values based on the node types
        x_position = 0.1
        for ind_1, key in enumerate(sorted(node_types.keys())):
            y_position = 1.0
            for ind_2, node in sorted(enumerate(node_types[key]), key=lambda row: nodes_count_list[row[1]],
                                      reverse=False):
                x_positions[node] = round(float(x_position), ndigits=3)
                y_positions[node] = round(y_position, ndigits=3)
                if grouping == 'year':
                    node_color_list[node] = color_palette[ind_1]
                y_position -= 1.0 / len(node_types[key])
            x_position += 0.9 / len(node_types.keys())
        logger.debug("x_positions:")
        logger.debug(x_positions)
        logger.debug("y_positions:")
        logger.debug(y_positions)
        logger.debug("node_color_list:")
        logger.debug(node_color_list)

        return x_positions, y_positions, node_color_list, node_types

    @staticmethod
    def __generate_edge_colors__(edges_df: pd.DataFrame, nodes_list: List, color_palette: List,
                                 grouping: str = 'year') -> List:

        source_from_edges_list = edges_df['Target'].to_list()
        if grouping == 'year':
            edge_years = set([node.split('_')[-1] for node in nodes_list])
            edge_types = dict(zip(sorted(edge_years), color_palette))
            logger.debug("Edge types: %s" % str(edge_types))
            edge_color_list = [edge_types[node.split('_')[-1]] for node in source_from_edges_list]
        elif grouping == 'none':
            edge_color_list = [color_palette[nodes_list.index(node)] for node in source_from_edges_list]
        else:
            raise Exception("Color grouping %s not supported" % grouping)

        logger.debug("edge_color_list:")
        logger.debug(edge_color_list)
        return edge_color_list

    @classmethod
    def __generate_sankey_figure__(cls, nodes_df: pd.DataFrame, edges_df: pd.DataFrame,
                                   color_grouping: str = 'year', custom_party_colors: Dict = None,
                                   title: str = 'Sankey Diagram') -> Dict:
        # Get a List with the Nodes and one with the counts
        nodes_list = nodes_df['Node'].tolist()
        nodes_count_list = nodes_df['Count'].tolist()
        # Create a color palette
        if color_grouping == 'year':
            logger.debug("Year Color Grouping is enabled.")
            num_node_types = len(set([node.split('_')[-1] for node in nodes_list]))
            color_palette = list(sns.color_palette(None, num_node_types).as_hex())
        elif color_grouping == 'none':
            logger.debug("Color Grouping is disabled.")
            color_palette = list(sns.color_palette(None, len(nodes_list)).as_hex())
        else:
            raise Exception("Color grouping %s not supported" % color_grouping)
        logger.debug("Color Palette:")
        logger.debug(color_palette)
        # Generate the nodes' positions and colors
        x_positions, y_positions, node_color_list, node_types = \
            cls.__generate_node_positions_and_colors__(nodes_list=nodes_list,
                                                       nodes_count_list=nodes_count_list,
                                                       color_palette=color_palette,
                                                       grouping=color_grouping)
        # Generate the edges' colors
        edge_color_list = cls.__generate_edge_colors__(edges_df=edges_df, nodes_list=nodes_list,
                                                       color_palette=color_palette, grouping=color_grouping)
        # The source and the target of each edge should be the corresponding index of the node
        edges_df['SourceID'] = edges_df['Source'].apply(lambda x: nodes_list.index(x))
        edges_df['TargetID'] = edges_df['Target'].apply(lambda x: nodes_list.index(x))

        # Construct the sankey diagram's figure
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
            title=title,
            font=dict(
                size=10
            )
        )

        fig_dict = dict(data=[data], layout=layout)
        return fig_dict

    def plot(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame, attribute_cols: List, name_col: str):
        logger.debug('Plotly config:')
        logger.debug(self.__config__)
        # Generate Sankey Figure
        fig_dict = self.__generate_sankey_figure__(nodes_df=nodes_df, edges_df=edges_df,
                                                   color_grouping=self.__config__['color_grouping_type'],
                                                   custom_party_colors=self.__config__['custom_party_colors'],
                                                   title=self.__config__['plot_name'])
        # self.logger.debug(fig)
        # Plot it
        logger.info("Plotting..")
        if self.__config__['save_html']:
            html_filepath = "{}/{}.html".format(self.__config__['target_path'], self.__config__['plot_name'])
            logger.info("Saving html as `%s`" % html_filepath)
            plotly.offline.plot(fig_dict, validate=True, filename=html_filepath)
        if self.__config__['save_image']:
            image_filepath = "{}/{}.png".format(self.__config__['target_path'], self.__config__['plot_name'])
            logger.info("Saving image as `%s`" % image_filepath)
            fig = go.Figure(fig_dict)
            fig.write_image(image_filepath)
