from typing import List, Tuple
import pandas as pd
from IPython.display import HTML, display
from notebookutils import mssparkutils
from .config import config
from pyspark.sql import SparkSession
import logging 
logger = logging.getLogger(__name__)

def get_run_details(comparison_obj):
    """
    Generates a summary DataFrame about the comparison run.
    """
    try:
        data = {
            "run_id": [comparison_obj.run_id],
            "Stream": [comparison_obj.stream],
            "new_model_workspace": [f"{comparison_obj.model_new.model_name}_workspace_{comparison_obj.model_new.workspace_name}"],
            "old_model_workspace": [f"{comparison_obj.model_old.model_name}_workspace_{comparison_obj.model_old.workspace_name}"],
            "new_model_refresh_date": [str(comparison_obj.model_new.last_modified_date)],
            "old_model_refresh_date": [str(comparison_obj.model_old.last_modified_date)]
        }
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error generating run details: {e}")
        return pd.DataFrame()

def get_raw_table_details(comparison_obj):
    """
    Returns all table comparison details with a run ID.
    """
    try:
        df = comparison_obj._all_tables.copy()
        df["run_id"] = comparison_obj.run_id
        return df
    except Exception as e:
        print(f"Error retrieving raw table details: {e}")
        return pd.DataFrame()

def get_raw_measure_details(comparison_obj):
    """
    Returns all measure comparison details with a run ID.
    """
    try:
        df = comparison_obj._all_measures.copy()
        df["run_id"] = comparison_obj.run_id
        return df
    except Exception as e:
        print(f"Error retrieving raw measure details: {e}")
        return pd.DataFrame()

def render_dataframe_tabs(df_list: List[Tuple[str, pd.DataFrame]]) -> HTML:
    """
    Render multiple DataFrames as scrollable tabs in Fabric notebook.
    Adds green/red dot icons in 'is_value_similar' column.

    Parameters:
    - df_list: List of (title, DataFrame) tuples

    Returns:
    - HTML display or raw string
    """
    style = """
    <style>
        .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
        .tab button { background-color: inherit; float: left; border: none; outline: none;
                      cursor: pointer; padding: 10px 14px; transition: 0.3s; }
        .tab button:hover { background-color: #ddd; }
        .tab button.active { background-color: #ccc; }
        .tabcontent { display: none; border: 1px solid #ccc; border-top: none;
                      padding: 10px; overflow: auto; max-height: 500px; }
        .tabcontent.active { display: block; }
        table { border-collapse: collapse; width: 100%; }
        th, td { text-align: center; padding: 8px; border: 1px solid #ddd; }
    </style>
    """

    script = """
    <script>
    function openTab(evt, tabName) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
    }
    </script>
    """

    tab_buttons = '<div class="tab">'
    tab_contents = ''

    greenSymbol = '🟢'
    redSymbol = '🔴'

    for i, (title, df) in enumerate(df_list):
        tab_id = f"tab{i}"
        active_class = "active" if i == 0 else ""
        df = df.copy()

        if title == "Measure Validation results":
            df['Pass_Fail'] = df.apply(
                lambda row: greenSymbol if row['is_value_similar'] and row['is_data_type_same'] and row['is_expression_same'] else redSymbol,
                axis=1
            )
        elif title == "Table Validation results":
            df['Pass_Fail'] = df['is_value_similar'].apply(lambda x: greenSymbol if x else redSymbol)

        elif title == "Column Validation results":
            df['Pass_Fail'] = df.apply(
                lambda row: greenSymbol if row['is_value_similar'] and row['is_data_type_same'] else redSymbol,
                axis=1
            )
        elif title == "Relationship Validation results":
            df['Pass_Fail'] = df.apply(
                lambda row: greenSymbol if row['is_cross_filtering_behavior_match'] and row['is_active_status_match'] and row['is_multiplicity_match'] and row['data_type_match'] and row['is_column_name_exactly_matched'] else redSymbol,
                axis=1
            )

        tab_buttons += f'<button class="tablinks {active_class}" onclick="openTab(event, \'{tab_id}\')">{title}</button>'
        df_html = df.to_html(escape=False, index=False)
        tab_contents += f'<div id="{tab_id}" class="tabcontent {active_class}">{df_html}</div>'
        
    tab_buttons += '</div>'
    html = style + tab_buttons + tab_contents + script
    return display(HTML(html))

def export_validation_results( results: List[Tuple[str, pd.DataFrame]], lakehouse_config: dict = config.get_lakehouse_config()):
    """
    Exports validation results to a specified location (e.g., lakehouse).

    Args:
        results (List[Tuple[str, pd.DataFrame]]): The validation results to export.
    """
    try:
        logger.info("Starting export process...")
        spark = SparkSession.builder.getOrCreate()

        # Determine Lakehouse path
        if lakehouse_config and "lakehouse_id" in lakehouse_config and "workspace_id" in lakehouse_config:
            lakehouse_id = lakehouse_config["lakehouse_id"]
            workspace_id = lakehouse_config["workspace_id"]
            base_path = f"abfss://{workspace_id}@msit-onelake.dfs.fabric.microsoft.com/{lakehouse_id}/Tables"
            logger.info(f"Exporting using provided lakehouse_config: workspace_id={workspace_id}, lakehouse_id={lakehouse_id}")
        else:
            try:
                mounts = mssparkutils.fs.mounts()
                default_mount = next((m for m in mounts if m.mountPoint == "/default"), None)
                if not default_mount:
                    logger.error("Export requested but no lakehouse_config provided and no attached Lakehouse found.")
                base_path = f"{default_mount.source}/Tables"
                logger.info(f"Exporting using attached Lakehouse: source={default_mount.source}")
            except Exception as e:
                logger.error("Error while accessing attached Lakehouse mounts.", e)

                # Write each result to Lakehouse
        for name, result in results:
            try:
                logger.info(f"Exporting result: {name}")
                df = pd.DataFrame(result)
                spark_df = spark.createDataFrame(df)
                df.replace('NA', None, inplace=True)
                table_path = name.replace(" ", "_").lower()
                full_path = f"{base_path}/{table_path}"
                spark_df.write.mode("overwrite").format("delta").option("mergeSchema", "true").save(full_path)
                logger.info(f"Successfully exported '{name}' to: {full_path}")
            except Exception as e:
                logger.error(f"Failed to export '{name}'", e)
        return render_dataframe_tabs(results)
    except Exception as e:
        logger.error("Unexpected error occurred during export process.", e)