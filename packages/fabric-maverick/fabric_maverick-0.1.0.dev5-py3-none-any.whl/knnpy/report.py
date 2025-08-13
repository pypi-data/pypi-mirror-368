import pandas as pd
import sempy.fabric as sfabric
import logging 
logger = logging.getLogger(__name__)

class FabricAnalyticsReport:
    """
    Represents a Power BI report in Microsoft Fabric, providing methods
    to extract metadata like tables, columns, and measures.
    """
    def __init__(self, report_name: str, workspace_name: str) -> None:
        """
        Initializes the FabricAnalyticsReport object.

        Args:
            report_name (str): The name of the Power BI report.
            workspace_name (str): The name of the workspace containing the report.
        
        Raises:
            RuntimeError: If workspace or dataset resolution fails.
        """
        self.report_name = report_name
        self.workspace_name = workspace_name

        try:
            self.workspaceid = sfabric.resolve_workspace_id(workspace_name)
        except Exception as e:
            logger.error(f"Failed to resolve workspace ID for '{workspace_name}': {e}")
            raise RuntimeError(f"Workspace resolution failed for: {workspace_name}")

        try:
            self.datasetid = sfabric.resolve_dataset_id(workspace=self.workspaceid, dataset_name=report_name)
        except Exception as e:
            logger.error(f"Failed to resolve dataset ID for report '{report_name}' in workspace '{workspace_name}': {e}")
            raise RuntimeError(f"Dataset resolution failed for: {report_name} in {workspace_name}")

        self.measures = self.__getMeasures()
        self.columns = self.__getAttributes()
        self.tables = self.__getTables()
        self.last_modified_date = self.__getLastModifiedDate()

    def __getMeasures(self) -> pd.DataFrame:
        """
        Retrieves all measures from the dataset.
        
        Returns:
            pd.DataFrame: A DataFrame of measures with standardized column names.
        """
        try:
            df = sfabric.list_measures(dataset=self.datasetid, workspace=self.workspaceid)

            if df is None or df.empty:
                logger.warning("Measure list is empty or dataset might not contain any measures.")
                return pd.DataFrame()
            return df[['Table Name', 'Measure Name', 'Measure Expression', 'Measure Data Type']].rename(columns={
                'Table Name': 'table_name',
                'Measure Name': 'field_name',
                'Measure Expression': 'expression',
                'Measure Data Type': 'data_type'
            }) 
        except Exception as e:
            logger.error(f"Error fetching measures for report '{self.report_name}' in workspace '{self.workspace_name}': {e}")
            return pd.DataFrame()

    def __getAttributes(self) -> pd.DataFrame:
        """
        Retrieves all columns (attributes) from the dataset.

        Returns:
            pd.DataFrame: A DataFrame of columns with standardized column names.
        """
        try:
            df = sfabric.list_columns(dataset=self.datasetid, workspace=self.workspaceid)

            if df is None or df.empty:
                logger.warning("Attribute list is empty or dataset might not contain any columns.")
                return pd.DataFrame()
            return df[['Table Name', 'Column Name', 'Data Type']].rename(columns={
                'Table Name': 'table_name',
                'Column Name': 'field_name',
                'Data Type': 'data_type'
            })
        except Exception as e:
            logger.error(f"Error fetching attributes (columns) for report '{self.report_name}' in workspace '{self.workspace_name}': {e}")
            return pd.DataFrame()

    def __getTables(self) -> pd.DataFrame:
        """
        Retrieves all tables from the dataset.

        Returns:
            pd.DataFrame: A DataFrame of tables.
        """
        try:
            df = sfabric.list_tables(dataset=self.datasetid, workspace=self.workspaceid)

            if df is None or df.empty:
                logger.warning("Table list is empty or dataset might not contain any tables.")
                return pd.DataFrame()
            return df[['Name']].rename(columns={'Name': 'table_name'})
        except Exception as e:
            logger.error(f"Error fetching tables for report '{self.report_name}' in workspace '{self.workspace_name}': {e}")
            return pd.DataFrame()

    def __getLastModifiedDate(self) -> str:
        """
        Retrieves the last refresh date of the dataset.

        Returns:
            str: The last modified date as a formatted string.
        """
        try:
            refresh_details = sfabric.list_refresh_requests(dataset=self.datasetid, workspace=self.workspaceid)
            if refresh_details.empty:
                logger.warning(f"No refresh history found. Using placeholder date for report '{self.report_name}' in workspace '{self.workspace_name}'.")
                return '01/01/1999 01:01'
            refresh_end = refresh_details[refresh_details['Status'] == 'Completed'] \
                .sort_values('End Time', ascending=False).iloc[0]['End Time']
            return refresh_end.strftime('%m/%d/%Y %H:%M') if refresh_end else '01/01/1999 01:01'
        except Exception as e:
            logger.error(f"Error retrieving last modified date: {e}, putting a placeholder - 01/01/1999")
            return '01/01/1999 01:01'