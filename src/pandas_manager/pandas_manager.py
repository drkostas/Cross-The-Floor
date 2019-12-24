from typing import *
import logging
import pandas as pd
import numpy as np


class PandasManager:
    logger = logging.getLogger('PandasManager')

    def __init__(self, df_generator: Generator) -> None:
        """
        Pandas Manager
        """
        self.df_generator = df_generator

    @classmethod
    def create_nodes_df(cls, merged_df: pd.DataFrame, plot_cols: List) -> pd.DataFrame:
        # Create nodes_df
        tmp_nodes_df = merged_df.copy(deep=True)
        tmp_nodes_df[plot_cols] = tmp_nodes_df[plot_cols].apply(
            lambda row: cls.__change_value_based_on_column_name__(row=row, cols=plot_cols), axis=1)
        nodes_df = tmp_nodes_df.copy(deep=True)
        nodes_df.loc[:, 'Node'] = nodes_df[plot_cols[0]]
        nodes_df = nodes_df.filter(['Node'])
        for col in plot_cols[1:]:
            loop_tmp_df = tmp_nodes_df
            loop_tmp_df.loc[:, 'Node'] = tmp_nodes_df[col]
            loop_tmp_df = tmp_nodes_df.filter(['Node'])
            nodes_df = pd.concat([nodes_df, loop_tmp_df], ignore_index=True).dropna()

        nodes_df['Count'] = nodes_df['Node'].map(nodes_df['Node'].value_counts())
        nodes_df.drop_duplicates(inplace=True)

        return nodes_df.sort_values(by='Count', ascending=False).reset_index()

    @classmethod
    def create_edges_df(cls, merged_df: pd.DataFrame, plot_cols: List, name_column: str) -> pd.DataFrame:
        # Create edges_df
        edges_df = merged_df.copy(deep=True)
        # Melt columns while leaving the others (in this case only name_column) intact.
        edges_df = pd.melt(edges_df, id_vars=[name_column], value_vars=plot_cols)
        # Sort the values by 'name_column' (required).
        edges_df = edges_df.sort_values(by=[name_column, 'variable'])
        # Get the year.
        edges_df['variable'] = edges_df['variable'].str.split(' ').apply(lambda x: x[-1])
        # Drop rows with empty values.
        edges_df = edges_df.dropna()
        edges_df['Source'] = edges_df['value'] + '_' + edges_df['variable']
        # Pair the values (This is why the previous sort is required).
        edges_df['Target'] = edges_df['Source'].shift(-1)
        # Remove rows where the values don't belong to the same name.
        mask = edges_df[name_column].eq(edges_df[name_column].shift(-1).bfill())
        edges_df = edges_df.loc[mask]
        # Keep only relevant columns.
        edges_df = edges_df
        edges_df = edges_df.groupby(['Source', 'Target']).size().reset_index(name="Count")

        return edges_df.reindex(columns=['Source', 'Target', 'Count']).sort_values(by='Count', ascending=False).reset_index()


    def df_from_generator(self) -> Tuple[pd.DataFrame, List, str]:
        plot_cols = []
        merged_df, first_name_column, first_attribute_column = next(self.df_generator)
        merged_df = self.__clean_df__(df=merged_df, name_col=first_name_column)
        merged_df.loc[:, first_attribute_column['name_on_plot']] = merged_df[first_attribute_column['origin_name']]
        merged_df = merged_df[[first_name_column, first_attribute_column['name_on_plot']]]
        plot_cols.append(first_attribute_column['name_on_plot'])
        for df, name_column, attribute_column in self.df_generator:
            # Clean DF, add column name for plot
            df = self.__clean_df__(df=df, name_col=name_column)
            plot_cols.append(attribute_column['name_on_plot'])
            # Rename Columns
            df.loc[:, attribute_column['name_on_plot']] = df[attribute_column['origin_name']]
            df.loc[:, first_name_column] = df[name_column]
            df = df[[first_name_column, attribute_column['name_on_plot']]]
            # Merge DF
            merged_df = pd.merge(merged_df, df, on=first_name_column, how='outer')

        return merged_df, plot_cols, first_name_column

    @staticmethod
    def __clean_df__(df: pd.DataFrame, name_col: str) -> pd.DataFrame:
        df_obj = df.select_dtypes(['object'])
        df_obj.loc[:, name_col] = df_obj[name_col].str.replace(r"([\(\[].*)", "", regex=True)
        df_obj.fillna("_", inplace=True)
        df_obj[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
        df_obj[df_obj.columns] = df_obj.apply(lambda x: x.str.capitalize())
        df[df_obj.columns] = df_obj[df_obj.columns]
        return df

    @staticmethod
    def __change_value_based_on_column_name__(row: pd.Series, cols: List):
        for col in cols:
            if row[col] is not np.NaN:
                row[col] = '{}_{}'.format(row[col], col.split()[-1])
        return row
