"""
FinToolsAP: A Comprehensive Python Package for Financial Data Analysis
====================================================================

FinToolsAP is a comprehensive Python package designed for researchers and data analysts 
in economics and finance. It provides streamlined tools for managing, processing, and 
querying large datasets using a local SQLite database, as well as convenient data 
manipulation utilities compatible with both pandas and polars.

Modules
-------
LocalDatabase : module
    Local SQLite database management and querying tools
WebData : module
    WRDS data downloading and processing utilities
UtilityFunctions : module
    Common data manipulation and analysis functions
FactorModels : module
    Financial factor model implementations and portfolio optimization
Decorators : module
    Performance monitoring and notification decorators
LaTeXBuilder : module
    LaTeX document generation from tables and figures
MertonModel : module
    Merton structural credit risk model implementation

Example
-------
>>> import FinToolsAP as ft
>>> # Initialize a local database
>>> db = ft.LocalDatabase('/path/to/database')
>>> # Download data from WRDS
>>> wd = ft.WebData('your_username')
>>> data = wd.getData(['AAPL', 'MSFT'], fields=['prc', 'ret'])

Notes
-----
This package requires appropriate database permissions for WRDS data access.
Some modules may require additional system dependencies (e.g., LaTeX for LaTeXBuilder).

Author: Andrew Maurice Perry
Email: Andrewpe@berkeley.edu
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Andrew Maurice Perry"
__email__ = "Andrewpe@berkeley.edu"

# Import main modules
from . import LocalDatabase
from . import WebData  
from . import UtilityFunctions
from . import FactorModels
from . import Decorators
from . import LaTeXBuilder
from . import MertonModel

# Import commonly used functions for convenience
from .FactorModels import tangency_portfolio, minimum_variance_portfolio, create_efficient_frontier, FamaMacBeth
from .UtilityFunctions import df_normalize, group_avg, group_nunique
from .Decorators import Performance

__all__ = [
    # Modules
    'LocalDatabase',
    'WebData', 
    'UtilityFunctions',
    'FactorModels',
    'Decorators',
    'LaTeXBuilder',
    'MertonModel',
    # Commonly used functions
    'tangency_portfolio',
    'minimum_variance_portfolio', 
    'create_efficient_frontier',
    'FamaMacBeth',
    'df_normalize',
    'group_avg',
    'group_nunique',
    'Performance'
]