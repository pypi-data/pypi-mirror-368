import pandas as pd
import numpy as np
import sempy.fabric as sfabric
from .report import FabricAnalyticsReport
import logging 
logger = logging.getLogger(__name__)

class BaseValidator:
    def __init__(
            self, 
            report_new: FabricAnalyticsReport, 
            report_old: FabricAnalyticsReport, 
            all_items: pd.DataFrame, 
            run_id: str, 
            stream: str
        ):
        self.report_new = report_new
        self.report_old = report_old
        self.all_items = all_items
        self.run_id = run_id
        self.stream = stream
    
    def _validate_value(self, new_val, old_val, margin_of_error) -> bool:

        if pd.isna(new_val) or pd.isna(old_val):
            return False

        lower_bound = old_val * (1 - margin_of_error / 100)
        upper_bound = old_val * (1 + margin_of_error / 100)

        return True if lower_bound <= new_val <= upper_bound else False
    
class MeasureValidator(BaseValidator):

    def validate_measure_values(self, margin_of_error=5.0):

        matched_measures = self.all_items[
            (self.all_items['origin'] == 'both') &
            (self.all_items['data_type_new'].str.strip().str.lower() == 'int64') &
            (self.all_items['data_type_old'].str.strip().str.lower() == 'int64')
        ][[
            'field_name_new',
            'field_name_old',
            'data_type_new',
            'data_type_old',
            'expression_old',
            'expression_new',
            'origin',
            'best_score'
        ]].dropna(subset=['field_name_new', 'field_name_old'])

        if matched_measures.empty:
            return pd.DataFrame()

        try:
            new_eval = sfabric.evaluate_measure(
                dataset=self.report_new.datasetid,
                workspace=self.report_new.workspaceid,
                measure=list(matched_measures['field_name_new'])
            )
            old_eval = sfabric.evaluate_measure(
                dataset=self.report_old.datasetid,
                workspace=self.report_old.workspaceid,
                measure=list(matched_measures['field_name_old'])
            )
            new_eval_pivot = new_eval.melt(var_name='field_name_new', value_name='new_report_value')
            old_eval_pivot = old_eval.melt(var_name='field_name_old', value_name='old_report_value')

            merged = pd.merge(matched_measures, new_eval_pivot, on='field_name_new', how='left')
            merged = pd.merge(merged, old_eval_pivot, on='field_name_old', how='left')
            
            merged['value_difference'] = merged['new_report_value'] - merged['old_report_value']
            merged['value_difference_percent'] = np.where(
                (merged['old_report_value'] == 0) |
                (merged['old_report_value'].isna()) |
                (merged['new_report_value'].isna()),
                '<NA>',
                (((merged['new_report_value'] - merged['old_report_value']) * 100) / merged['old_report_value'])
                .round(2).astype(str) + '%'
            )
            merged.loc[(merged['value_difference'] == 0) & (merged['value_difference_percent'] == '<NA>'),'value_difference_percent'] = '0.0%'
            merged['is_value_similar'] = merged.apply(
                lambda row: self._validate_value(row['new_report_value'], row['old_report_value'], margin_of_error), axis=1
            )
            merged['is_data_type_same'] = merged['data_type_new'] == merged['data_type_old']
            merged['is_expression_same'] = merged['expression_new'] == merged['expression_old']
            merged['run_id'] = self.run_id
            merged['Stream'] = self.stream

            final_cols = [
                'run_id', 'Stream', 'field_name_new', 'field_name_old' , 'best_score', 'origin',
                'new_report_value', 'old_report_value',
                'value_difference', 'value_difference_percent',
                'is_value_similar', 'is_data_type_same', 'is_expression_same'
            ]
            return merged[final_cols].astype(str).fillna('Unknown')
        except Exception as e:
            print(f"Error in measure validation: {e}")
            return pd.DataFrame()

class TableValidator(BaseValidator):

    def _get_table_row_count(self, report, table_name) -> int:
        query = f'EVALUATE ROW("RowCount", COUNTROWS(\'{table_name}\'))'
        try:
            df = sfabric.evaluate_dax(dataset=report.datasetid, workspace=report.workspaceid, dax_string=query)
            colname = df.columns[0]
            value = df[colname].iloc[0]
            return 0 if pd.isna(value) else int(value)
        except Exception as e:
            logger.error(f"Error fetching row count for table : {e}")
            return -1

    def validate_row_counts(self, margin_of_error=5.0) -> pd.DataFrame:
        results = []
        matched_tables = self.all_items

        for _, row in matched_tables.iterrows():
            table_new = row['table_name_new']
            table_old = row['table_name_old']

            count_new = self._get_table_row_count(self.report_new, table_new)
            count_old = self._get_table_row_count(self.report_old, table_old)
            
            diff = count_new - count_old
            diff_pct = f"{((diff) / count_old * 100):.2f}%" if count_old != 0 else "∞%"

            results.append({
                'run_id': self.run_id,
                'Stream': self.stream,
                'table_name_new': table_new,
                'table_name_old': table_old,
                'best_score': row['best_score'],
                'origin': 'both',
                'row_count_new': count_new,
                'row_count_old': count_old,
                'row_count_difference': diff,
                'row_count_diff_percentage': diff_pct,
                'is_value_similar': self._validate_value(count_new, count_old, margin_of_error),
            })
        
        return pd.DataFrame(results)

class ColumnValidator(BaseValidator):

    def _read_table(self,table_name) -> None:
        self._new_tables_data = {}
        try:
            self._new_tables_data[table_name] = sfabric.read_table(
                dataset=self.report_new.datasetid,
                workspace=self.report_new.workspaceid,
                table=table_name
            )
        except Exception as e:
            logger.warning(f"Error reading new table '{table_name}': {e}")
            self._new_tables_data[table_name] = pd.DataFrame()

    def _generate_distinct_count_dax(self,columns: list[str],table_name) -> str:
        rows = []
        for col in columns:
            row = f'ROW("ColumnName", "{col}", "DistinctCount", COUNTROWS(SUMMARIZE(\'{table_name}\', \'{table_name}\'[{col}])))'
            rows.append(row)
        return  "EVALUATE\nUNION(\n    " + ",\n    ".join(rows) + "\n)"
        
    def _get_column_distinct_counts(self, table_name: str, columns: list[str], report: FabricAnalyticsReport) -> pd.DataFrame | None:
        """
        Executes a DAX query to fetch distinct counts for the given columns and table.
        """
        if not columns:
            logging.warning(f"No columns provided for table '{table_name}' in dataset {report.datasetid}.")
            return None
            
        dax_query = self._generate_distinct_count_dax(columns=columns, table_name=table_name)
        if dax_query is None:
            return None
            
        try:
            df = sfabric.evaluate_dax(
                dataset=report.datasetid,
                workspace=report.workspaceid,
                dax_string=dax_query
            )
            # Standardize column names from DAX result
            df.columns = ["ColumnName", "DistinctCount"]
            if(len(df) == 0):
                logging.warning(f"No row count returned for columns in table '{table_name}'")
            return df
        except Exception as e:
            logging.error(f"Error fetching distinct row count for columns in table '{table_name}': {e}")
            return None

    def validate_distinct_counts(self, margin_of_error: float = 5.0) -> pd.DataFrame:
        """
        Validates the distinct count of values for all common columns across all common tables.

        Args:
            margin_of_error (float): The allowed percentage difference between old and new counts.

        Returns:
            pd.DataFrame: A dataframe containing the validation results for each column,
                          including new/old counts and whether the validation passed.
        """
        validation_results = []
        
        # Find common tables based on the mapping in all_items
        common_tables = self.all_items[['table_name_new', 'table_name_old']].drop_duplicates()

        for _, row in common_tables.iterrows():
            table_name_new = row['table_name_new']
            table_name_old = row['table_name_old']

            logging.info(f"Validating distinct counts for table: '{table_name_new}' (new) vs '{table_name_old}' (old)")

            # Filter columns for the current table pair
            table_columns_map = self.all_items[
                (self.all_items['table_name_new'] == table_name_new) &
                (self.all_items['table_name_old'] == table_name_old)
            ]

            cols_new = table_columns_map['field_name_new'].unique().tolist()
            cols_old = table_columns_map['field_name_old'].unique().tolist()

            # Fetch distinct counts for both new and old reports
            df_new = self._get_column_distinct_counts(table_name_new, cols_new, self.report_new)
            df_old = self._get_column_distinct_counts(table_name_old, cols_old, self.report_old)

            if df_new is None or df_old is None:
                logging.warning(f"Could not retrieve data for one or both tables: {table_name_new}, {table_name_old}. Skipping.")
                continue

            # Rename columns for merging
            df_new = df_new.rename(columns={"ColumnName": "field_name_new", "DistinctCount": "distinct_count_new"})
            df_old = df_old.rename(columns={"ColumnName": "field_name_old", "DistinctCount": "distinct_count_old"})
            
            # Merge results based on the column mapping
            merged_df = pd.merge(table_columns_map, df_new, on="field_name_new")
            merged_df = pd.merge(merged_df, df_old, on="field_name_old")

            # Perform validation for each column
            merged_df['is_value_similar'] = merged_df.apply(
                lambda r: self._validate_value(r['distinct_count_new'], r['distinct_count_old'], margin_of_error),
                axis=1
            )
            merged_df['value_difference'] = merged_df['distinct_count_new'] - merged_df['distinct_count_old']
            merged_df['value_difference_percent'] = np.where(
                (merged_df['distinct_count_new'] == 0) |
                (merged_df['distinct_count_new'].isna()) |
                (merged_df['distinct_count_old'].isna()),
                '<NA>',
                (((merged_df['distinct_count_old'] - merged_df['distinct_count_new']) * 100) / merged_df['distinct_count_new'])
                .round(2).astype(str) + '%'
            )
            merged_df.loc[(merged_df['value_difference'] == 0) & (merged_df['value_difference_percent'] == '<NA>'),'value_difference_percent'] = '0.0%'
            merged_df['is_data_type_same'] = merged_df['data_type_new'] == merged_df['data_type_old']
            validation_results.append(merged_df)

        if not validation_results:
            return pd.DataFrame() 

        return pd.concat(validation_results, ignore_index=True)
    
