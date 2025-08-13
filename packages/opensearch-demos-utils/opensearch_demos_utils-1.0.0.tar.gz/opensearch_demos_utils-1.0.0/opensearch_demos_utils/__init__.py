"""
OpenSearch Demos Utils - A Python package for OpenSearch demonstration utilities.

This package provides utilities for connecting to OpenSearch, loading data,
creating visualizations, and working with sample datasets in educational
and demonstration contexts, specifically optimized for Google Colab environments.
"""

__version__ = "1.0.0"
__author__ = "OpenSearch Demos Team"
__email__ = "support@example.com"

# Import main classes and functions for easy access
from .connection import ColabConnectionConfig, ConnectionConfig, OpenSearchConnection, create_colab_connection
from .data_loader import DataLoader, DataValidationError
from .visualization import (
    plot_search_results,
    create_aggregation_charts,
    display_cluster_metrics,
    format_search_response_for_display,
    create_comparison_chart
)
from .sample_datasets import SampleDatasets, DatasetType
from .config_templates import (
    ConfigurationTemplate,
    ConfigurationValidator,
    ConfigurationHelper,
    get_basic_template,
    get_minimal_template,
    get_advanced_template,
    get_troubleshooting_template,
    validate_config,
    create_connection_from_config
)

# Define what gets imported with "from opensearch_demos_utils import *"
__all__ = [
    # Core classes
    'ColabConnectionConfig',
    'ConnectionConfig',
    'OpenSearchConnection',
    'DataLoader',
    'SampleDatasets',
    
    # Configuration template classes
    'ConfigurationTemplate',
    'ConfigurationValidator',
    'ConfigurationHelper',
    
    # Convenience functions
    'create_colab_connection',
    'get_basic_template',
    'get_minimal_template',
    'get_advanced_template',
    'get_troubleshooting_template',
    'validate_config',
    'create_connection_from_config',
    
    # Enums
    'DatasetType',
    
    # Exceptions
    'DataValidationError',
    
    # Visualization functions
    'plot_search_results',
    'create_aggregation_charts', 
    'display_cluster_metrics',
    'format_search_response_for_display',
    'create_comparison_chart',
    
    # Package metadata
    '__version__',
    '__author__',
    '__email__'
]

# Package-level configuration
DEFAULT_TIMEOUT = 30
DEFAULT_SSL_VERIFY = False
DEFAULT_PORT = 9200

# Colab-specific defaults for Astra connections
ASTRA_DEFAULTS = {
    'port': 9200,
    'use_ssl': True,
    'verify_certs': False,
    'timeout': 30
}