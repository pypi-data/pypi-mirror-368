# knnpy/__init__.py
"""
The knnpy package for Power BI report comparison and validation.
"""

# Import key classes/functions to make them directly accessible from the package
from .base import (
    ReportCompare,
    ReportComparison
)
from .token_provider import initializeToken
from .report import FabricAnalyticsReport
from .utils import (
    get_raw_measure_details,
    get_raw_table_details,
    get_run_details
)

# Define __all__ for explicit imports
__all__ = [
    "FabricAnalyticsReport",
    "initializeToken",
    "ReportCompare"
]

import logging
logger = logging.getLogger(__name__)


# logger.setLevel(logging.INFO)

# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# console_handler.setFormatter(formatter)
# if not logger.handlers:
#     logger.addHandler(console_handler)