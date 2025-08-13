import pandas as pd

def get_run_details(comparison_obj):
    """
    Generates a summary DataFrame about the comparison run.
    """
    try:
        data = {
            "run_id": [comparison_obj.run_id],
            "Stream": [comparison_obj.stream],
            "new_report_workspace": [f"{comparison_obj.report_new.report_name}_workspace_{comparison_obj.report_new.workspace_name}"],
            "old_report_workspace": [f"{comparison_obj.report_old.report_name}_workspace_{comparison_obj.report_old.workspace_name}"],
            "new_report_refresh_date": [str(comparison_obj.report_new.last_modified_date)],
            "old_report_refresh_date": [str(comparison_obj.report_old.last_modified_date)]
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