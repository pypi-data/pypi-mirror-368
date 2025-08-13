# OpenSearch Demos Utils

A Python package providing utilities for OpenSearch demonstrations and educational content, specifically optimized for Google Colab environments.

## Features

- **🔗 Connection Management**: Easy connection setup for DataStax Astra managed OpenSearch
- **📊 Data Loading**: In-memory sample data generation (no external files needed)
- **📈 Visualization**: Colab-optimized plotting functions for search results and metrics
- **🎯 Sample Datasets**: Pre-built generators for products, articles, and logs data
- **🚀 Colab Ready**: Designed specifically for Google Colab environments

## Installation

```bash
pip install opensearch-demos-utils
```

## Quick Start

### Basic Connection (Google Colab)

```python
from opensearch_demos_utils import ColabConnectionConfig, OpenSearchConnection

# Configure connection for DataStax Astra (Colab-optimized)
config = ColabConnectionConfig(
    host="your-cluster.astra.datastax.com",
    port=9200,
    astra_cs_token="AstraCS:your-token-here",
    use_ssl=True,
    verify_certs=False
)

# Create connection
connection = OpenSearchConnection(config)
client = connection.connect()

# Test the connection
if connection.test_connection():
    print("✅ Connected successfully!")
```

### Quick Connection Helper

```python
from opensearch_demos_utils import create_colab_connection

# One-line connection setup
connection = create_colab_connection(
    host="your-cluster.astra.datastax.com",
    astra_cs_token="AstraCS:your-token-here"
)
client = connection.connect()
```

### Generate Sample Data

```python
from opensearch_demos_utils import prepare_sample_data_for_demo

# Generate sample data
products = prepare_sample_data_for_demo('products', 50)
articles = prepare_sample_data_for_demo('articles', 30)
logs = prepare_sample_data_for_demo('logs', 100)

print(f"Generated {len(products)} products, {len(articles)} articles, {len(logs)} logs")

# Or use embedded sample data (smaller datasets)
embedded_articles = prepare_sample_data_for_demo('articles')  # Uses embedded data
embedded_products = prepare_sample_data_for_demo('products')  # Uses embedded data
embedded_logs = prepare_sample_data_for_demo('logs')  # Uses embedded data
```

### Visualize Search Results

```python
from opensearch_demos_utils.visualization import (
    plot_search_results, 
    create_aggregation_charts,
    create_dashboard_view
)

# Visualize search results
search_response = client.search(index="demo_products", body={"query": {"match_all": {}}})
plot_search_results(search_response, title="Product Search Results")

# Visualize aggregations
agg_response = client.search(
    index="demo_products", 
    body={"aggs": {"categories": {"terms": {"field": "category"}}}}
)
create_aggregation_charts(agg_response["aggregations"], title="Product Categories")

# Create comprehensive dashboard
create_dashboard_view(
    search_results=search_response,
    aggregation_results=agg_response,
    title="OpenSearch Analytics Dashboard"
)
```

## Core Components

### ColabConnectionConfig
Colab-optimized configuration class for OpenSearch connections:
- **Astra Validation**: Auto-validates DataStax Astra endpoints and tokens
- **Colab Environment Checks**: Prevents localhost/private IP connections
- **SSL Auto-Configuration**: Automatically enables SSL for Astra endpoints
- **Helpful Error Messages**: Provides Colab-specific troubleshooting guidance

### ConnectionConfig (Legacy)
Backward-compatible configuration class that extends ColabConnectionConfig:
- Maintains compatibility with existing code
- Includes all Colab optimizations
- Supports additional legacy features like custom CA certificates

### DataLoader
Comprehensive data loading and preparation utilities:
- **In-memory data generation**: No external files needed for Colab
- **String-based loading**: Load JSON/CSV data from strings
- **Data validation and cleaning**: Automatic data sanitization
- **OpenSearch indexing preparation**: Ready-to-index data formatting
- **Bulk operation support**: Efficient bulk indexing format creation

### Sample Data Generation
Advanced sample data management system:
- **Products**: E-commerce catalog with categories, prices, ratings, inventory
- **Articles**: Blog posts with content, metadata, engagement metrics, SEO data
- **Logs**: Application logs with timestamps, levels, metrics, request tracking
- **Embedded datasets**: Pre-built sample data for quick demos
- **Bulk indexing support**: OpenSearch-ready data preparation utilities

### Visualization Functions
Colab-optimized plotting functions with enhanced display features:
- `plot_search_results()`: Visualize search results with score distributions and category breakdowns
- `create_aggregation_charts()`: Chart aggregation results with automatic chart type selection
- `display_cluster_metrics()`: Show comprehensive cluster health, statistics, and storage metrics
- `create_dashboard_view()`: Multi-panel dashboard combining search, aggregation, and cluster data
- `format_search_response_for_display()`: Format results as DataFrame with enhanced Colab display
- `create_comparison_chart()`: Side-by-side comparison visualizations
- `plot_aggregation_results()`: Specialized aggregation plotting with Colab optimization

## Google Colab Optimization

This package is specifically designed for Google Colab environments:

- **No File Dependencies**: All sample data is generated in-memory
- **Colab-Friendly Visualizations**: Plots optimized for notebook display
- **Easy Installation**: Single pip install with all dependencies
- **Astra Integration**: Pre-configured for DataStax Astra managed OpenSearch
- **Error Handling**: Colab-specific troubleshooting messages

## Configuration Templates

### Installation Cell (Colab)
```python
# Install dependencies
import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = [
    "opensearch-py>=2.4.0",
    "opensearch-demos-utils>=1.0.0",
    "pandas>=1.3.0",
    "matplotlib>=3.5.0"
]

for package in packages:
    install_package(package)
    print(f"✅ {package}")
```

### Configuration Cell (Colab)
```python
# OpenSearch Connection Configuration
OPENSEARCH_CONFIG = {
    "host": "your-cluster.astra.datastax.com",
    "port": 9200,
    "astra_cs_token": "AstraCS:your-token-here",
    "use_ssl": True,
    "verify_certs": False
}

from opensearch_demos_utils import ColabConnectionConfig, OpenSearchConnection

config = ColabConnectionConfig(**OPENSEARCH_CONFIG)
connection = OpenSearchConnection(config)
client = connection.connect()

# Or use the convenience function
from opensearch_demos_utils import create_colab_connection
connection = create_colab_connection(**OPENSEARCH_CONFIG)
client = connection.connect()
```

## Requirements

- Python 3.8+
- opensearch-py >= 2.4.0
- pandas >= 1.3.0
- matplotlib >= 3.5.0
- seaborn >= 0.11.0

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- GitHub Issues: [opensearch-demos/issues](https://github.com/opensearch-project/opensearch-demos/issues)
- Documentation: [README](https://github.com/opensearch-project/opensearch-demos)

## Examples

Check out the example notebooks in the [demos](https://github.com/opensearch-project/opensearch-demos/tree/main/demos) directory for complete usage examples.