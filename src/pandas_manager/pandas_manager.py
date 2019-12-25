from typing import *
import logging
import re
import pandas as pd
import numpy as np

import sys

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)


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
        # Group by Node and fet Counts
        nodes_df['Count'] = nodes_df['Node'].map(nodes_df['Node'].value_counts())
        nodes_df.drop_duplicates(inplace=True)

        return nodes_df.reset_index().reindex(columns=['Node', 'Count'])

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
        # Replace NaN with nan: str
        edges_df.loc[:, 'value'] = edges_df['value'].fillna('nan')
        edges_df['Source'] = edges_df['value'] + '_' + edges_df['variable']
        # Pair the values (This is why the previous sort is required).
        for ind in range(1, len(plot_cols)):
            # Create len(plot_cols)-1 Target Columns and Name Columns
            current_target_col = 'Target_{}'.format(ind)
            current_name_col = 'Target_{}_{}'.format(ind, name_column)
            edges_df[current_target_col] = edges_df['Source'].shift(-ind).bfill()
            edges_df[current_name_col] = edges_df[name_column].shift(-ind)
        # Set Target=Target_1 if not null and name_col=name_col_1 else Target=Target_2 and so on
        edges_df.loc[:, :] = edges_df.loc[:, :].apply(
            lambda row: cls.__infer_target_col__(row=row, name_col=name_column, num_plot_cols=len(plot_cols)), axis=1)
        edges_df["Target"] = edges_df["Target_1"]
        edges_df["Target_{}".format(name_column)] = edges_df["Target_1_{}".format(name_column)]
        edges_df = edges_df.dropna(subset=['Target'])
        # Remove rows where Source name and Target name don't match.
        mask = edges_df[name_column].eq(edges_df['Target_{}'.format(name_column)])
        edges_df = edges_df.loc[mask]
        # Filter nan that don't match some criteria
        edges_df[['Source', 'Target']] = edges_df[['Source', 'Target']].apply(
            lambda row: cls.__modify_cols_depending_on_null__(row=row, cols=['Source', 'Target'],
                                                              end_year=plot_cols[-1].split()[-1]), axis=1)
        edges_df = edges_df[~edges_df['Source'].str.startswith("nan")]
        # Keep only relevant columns
        edges_df = edges_df.groupby(['Source', 'Target']).size().reset_index(name="Count")

        return edges_df.reset_index().reindex(columns=['Source', 'Target', 'Count'])

    def df_from_generator(self) -> Tuple[pd.DataFrame, List, str]:
        plot_cols = []
        # Get the first DF from the generator
        merged_df, first_name_column, first_attribute_column = next(self.df_generator)
        # Rename Columns
        merged_df = self.__clean_df__(df=merged_df, name_col=first_name_column)
        plot_cols.append(first_attribute_column['name_on_plot'])
        merged_df.loc[:, first_attribute_column['name_on_plot']] = merged_df[first_attribute_column['origin_name']]
        merged_df = merged_df[[first_name_column, first_attribute_column['name_on_plot']]]
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
        # Drop rows with null names
        merged_df.dropna(subset=[first_name_column], inplace=True)
        return merged_df, plot_cols, first_name_column

    @staticmethod
    def __clean_df__(df: pd.DataFrame, name_col: str) -> pd.DataFrame:
        df_obj = df.select_dtypes(['object'])
        # Delete the every character after a [ or ( in the name column
        match_txt_in_brackets = r"([\(\[].*)"
        df_obj.loc[:, name_col] = df_obj[name_col].str.replace(match_txt_in_brackets, "", regex=True)
        # Keep only the first 3 characters of the first word and the last word in the name column
        match_first_2_chars_and_last_word = r"^([a-zA-Z]{3})[a-zA-Z-]+\s+(?:[a-zA-Z-]+\s*\s+)*([a-zA-Z-]+)\s*$"
        df_obj.loc[:, name_col] = df_obj[name_col].str.replace(match_first_2_chars_and_last_word, r"\1 \2", regex=True)
        # Strip and capitalize all columns
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

    @staticmethod
    def __modify_cols_depending_on_null__(row: pd.Series, cols: List, end_year: str):
        """
            Having a size 2 cols List, it modifies the row as follows:
            - If the second col is nan_YYYY and the first one is not then it sets second=first
            - If the first col is nan_YYYY and the second one is not
                  and the second is value_{end_year} then it sets first=second
        """
        new_row = row
        if 'nan' in row[cols[1]] and 'nan' not in row[cols[0]]:
            new_row[cols[1]] = new_row[cols[0]]
        if 'nan' in row[cols[0]] and 'nan' not in row[cols[1]] and end_year in row[cols[1]]:
            new_row[cols[0]] = new_row[cols[1]]
        return new_row

    @staticmethod
    def __infer_target_col__(row: pd.Series, name_col: str, num_plot_cols: int):
        """
            If Source is not nan_YYYY then set Target_1 = Target_n
            where n is the min for which Target_n_{name_col}={name_col} and Target_n is not nan_YYYY
        """
        if 'nan' not in row["Source"]:
            for ind in range(1, num_plot_cols):
                if row[name_col] == row["Target_{}_{}".format(ind, name_col)]:
                    if 'nan' not in row["Target_{}".format(ind)]:
                        row["Target_1"] = row["Target_{}".format(ind)]
                        row["Target_1_{}".format(name_col)] = row["Target_{}_{}".format(ind, name_col)]
                        break
        return row
