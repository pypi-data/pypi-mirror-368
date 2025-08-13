# Connection Configuration Library Documentation

This document provides comprehensive documentation for the standardized connection configuration library used throughout the OpenSearch Demos project.

## Overview

The connection configuration library provides a two-tier approach to OpenSearch connections:

1. **Educational Tier** (`utils.connection`) - Detailed setup for learning
2. **Productivity Tier** (`utils.opensearch_connection`) - Simplified setup for advanced usage

## Library Architecture

### Core Components

```
utils/
├── connection.py              # Educational connection management
├── opensearch_connection.py   # Simplified connection management
└── ...

config/
├── connection_template.py     # Configuration templates
└── ...

env/
└── opensearch_connection.json # Shared configuration storage
```

## Educational Tier - `utils.connection`

### Purpose
- Provides detailed, step-by-step connection setup
- Educational focus with comprehensive error handling
- Used primarily in beginner notebooks for learning

### Key Classes

#### `ConnectionConfig`
```python
@dataclass
class ConnectionConfig:
    host: str
    port: int
    astra_cs_token: str
    use_ssl: bool = True
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    timeout: int = 30
    
    def get_auth_headers(self) -> dict:
        """Returns authentication headers with AstraCS token"""
        return {"Authorization": f"Bearer {self.astra_cs_token}"}
```

#### `OpenSearchConnection`
```python
class OpenSearchConnection:
    def __init__(self, config: ConnectionConfig)
    def connect(self) -> OpenSearch
    def test_connection(self) -> bool
    def get_cluster_info(self) -> dict
```

### Usage Example
```python
from utils.connection import ConnectionConfig, OpenSearchConnection
from config.connection_template import get_config_from_env

# Create configuration
config = get_config_from_env()
connection = OpenSearchConnection(config)
client = connection.connect()

# Test connection with detailed feedback
if connection.test_connection():
    print("✅ Successfully connected to OpenSearch!")
    cluster_info = connection.get_cluster_info()
    print(f"Cluster: {cluster_info['cluster_info']['cluster_name']}")
    print(f"Version: {cluster_info['cluster_info']['version']['number']}")
else:
    print("❌ Connection test failed. Please check your configuration.")
```

## Productivity Tier - `utils.opensearch_connection`

### Purpose
- Provides simplified, one-line connection setup
- Productivity focus with automatic configuration loading
- Used in all intermediate and advanced notebooks

### Key Classes and Functions

#### `OpenSearchConfig`
```python
class OpenSearchConfig:
    def __init__(self, config_path: str = "env/opensearch_connection.json")
    def save(self) -> bool
    def load(self, set_env_vars: bool = True) -> Optional[Dict[str, Any]]
    def get_client(self) -> OpenSearch
```

#### Convenience Functions
```python
def save_connection(config_path: str = None) -> bool
def load_connection(config_path: str = None, set_env_vars: bool = True) -> Optional[Dict[str, Any]]
def get_opensearch_client(config_path: str = None)
def setup_connection(config_path: str = None)  # Main function for notebooks
```

### Usage Example
```python
from utils.opensearch_connection import setup_connection

# One-line connection setup
client = setup_connection()

if client:
    print("✅ Successfully connected to OpenSearch")
    print("🎯 Ready for operations!")
else:
    print("❌ Connection failed")
    print("💡 Run the basic connection notebook (01_basic_connection.ipynb) first")
```

## Configuration Management

### Shared Configuration File

**Location**: `env/opensearch_connection.json`

**Structure**:
```json
{
  "host": "your-cluster-endpoint.astra.datastax.com",
  "port": 9200,
  "use_ssl": true,
  "verify_certs": true,
  "timeout": 30,
  "connection_type": "managed",
  "astra_cs_token": "AstraCS:your-token-here",
  "created_at": "2024-01-01T12:00:00.000000",
  "created_by": "OpenSearchConfig"
}
```

### SSL Auto-Detection Logic

The library includes intelligent SSL detection:

```python
# Determine if this is localhost
is_localhost = host in ['localhost', '127.0.0.1', '::1', '0.0.0.0'] or \
              host.startswith('192.168.') or host.startswith('10.') or host.startswith('172.')

# Auto-detect SSL usage
is_standard_ssl_port = port in [443, 9243]
is_standard_http_port = port in [80, 9200]

if is_localhost and is_standard_http_port:
    use_ssl = False  # Localhost with standard HTTP port
elif is_standard_ssl_port:
    use_ssl = True   # Standard SSL ports
elif is_localhost:
    use_ssl = False  # Localhost with non-standard port
else:
    use_ssl = True   # Remote host - default to SSL
```

## API Reference

### `utils.opensearch_connection` Module

#### `setup_connection(config_path: str = None) -> OpenSearch`

**Purpose**: Main function for notebook connections - provides one-line setup

**Parameters**:
- `config_path` (optional): Path to configuration file. Defaults to `env/opensearch_connection.json`

**Returns**: 
- `OpenSearch` client instance if successful
- `None` if connection fails

**Example**:
```python
client = setup_connection()
if client:
    # Use client for operations
    info = client.info()
```

#### `save_connection(config_path: str = None) -> bool`

**Purpose**: Save current environment variables to configuration file

**Parameters**:
- `config_path` (optional): Path to save configuration. Auto-detects project root if None

**Returns**: 
- `True` if saved successfully
- `False` if save failed

**Environment Variables Used**:
- `OPENSEARCH_HOST`
- `OPENSEARCH_PORT`
- `ASTRA_CS_TOKEN`
- `OPENSEARCH_USE_SSL` (optional)
- `OPENSEARCH_VERIFY_CERTS` (optional)

**Example**:
```python
import os
os.environ['OPENSEARCH_HOST'] = 'your-endpoint.astra.datastax.com'
os.environ['OPENSEARCH_PORT'] = '9200'
os.environ['ASTRA_CS_TOKEN'] = 'AstraCS:your-token'

success = save_connection()
```

#### `load_connection(config_path: str = None, set_env_vars: bool = True) -> Optional[Dict[str, Any]]`

**Purpose**: Load connection configuration from file

**Parameters**:
- `config_path` (optional): Path to configuration file
- `set_env_vars` (optional): Whether to set environment variables from config

**Returns**: 
- Configuration dictionary if successful
- `None` if load failed

**Example**:
```python
config = load_connection(set_env_vars=False)  # Load without setting env vars
print(f"Host: {config['host']}")
```

#### `get_opensearch_client(config_path: str = None) -> OpenSearch`

**Purpose**: Get configured OpenSearch client (used internally by `setup_connection`)

**Parameters**:
- `config_path` (optional): Path to configuration file

**Returns**: 
- `OpenSearch` client instance if successful
- `None` if client creation failed

### `OpenSearchConfig` Class

#### `__init__(self, config_path: str = "env/opensearch_connection.json")`

**Purpose**: Initialize configuration manager

**Parameters**:
- `config_path`: Path to configuration file

#### `save(self) -> bool`

**Purpose**: Save current environment variables to configuration file

**Returns**: 
- `True` if saved successfully
- `False` if save failed

**Features**:
- Intelligent SSL auto-detection
- Localhost vs managed service detection
- Comprehensive error handling
- Detailed logging of configuration decisions

#### `load(self, set_env_vars: bool = True) -> Optional[Dict[str, Any]]`

**Purpose**: Load configuration from file

**Parameters**:
- `set_env_vars`: Whether to update environment variables

**Returns**: 
- Configuration dictionary if successful
- `None` if load failed

#### `get_client(self) -> OpenSearch`

**Purpose**: Create OpenSearch client from configuration

**Returns**: 
- `OpenSearch` client instance if successful
- `None` if client creation failed

## Usage Patterns by Notebook Type

### Beginner Notebooks

**Pattern**: Detailed educational setup

```python
# Step-by-step connection with full explanation
from utils.connection import ConnectionConfig, OpenSearchConnection
from config.connection_template import get_config_from_env

# Create and configure connection
config = get_config_from_env()
connection = OpenSearchConnection(config)
client = connection.connect()

# Test with detailed feedback
if connection.test_connection():
    print("✅ Successfully connected to OpenSearch!")
    
    # Save configuration for other notebooks
    from utils.opensearch_connection import save_connection
    save_connection()
    
    # Show cluster information
    cluster_info = connection.get_cluster_info()
    print(f"Cluster: {cluster_info['cluster_info']['cluster_name']}")
else:
    print("❌ Connection test failed")
    print("🔧 Troubleshooting steps:")
    print("1. Check your AstraCS token")
    print("2. Verify cluster is running")
    print("3. Check network connectivity")
```

### Intermediate/Advanced Notebooks

**Pattern**: Simplified productive setup

```python
# One-line connection setup
from utils.opensearch_connection import setup_connection

client = setup_connection()

if client:
    print("✅ Successfully connected to OpenSearch")
    print("🎯 Ready for advanced operations!")
else:
    print("❌ Connection failed")
    print("💡 Run the basic connection notebook (01_basic_connection.ipynb) first")
    print("💡 Make sure you've completed the connection setup from previous demos.")
```

## Error Handling Patterns

### Standard Error Messages

All notebooks should use consistent error messages:

```python
# Connection success
print("✅ Successfully connected to OpenSearch")

# Connection failure
print("❌ Connection failed")
print("💡 Run the basic connection notebook (01_basic_connection.ipynb) first")
print("💡 Make sure you've completed the connection setup from previous demos.")

# Configuration not found
print("📋 No saved connection found")
print("💡 Complete the basic connection setup first")

# Authentication failure
print("🔐 Authentication failed")
print("💡 Check your AstraCS token")
print("💡 Generate a new token if needed")
```

### Exception Handling

```python
try:
    client = setup_connection()
    if client:
        print("✅ Connected successfully")
    else:
        print("❌ Connection failed")
        print("💡 Check troubleshooting guide")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running from the correct directory")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print("💡 Check CONNECTION_TROUBLESHOOTING.md for help")
```

## Testing and Validation

### Connection Validation

Use the validation script to check all notebooks:

```bash
python validate_connection_consistency.py
```

### Automated Tests

Run the test suite:

```bash
python tests/test_connection_config_validation.py
```

### Manual Testing

Test individual components:

```python
# Test configuration saving
from utils.opensearch_connection import save_connection
success = save_connection()
print(f"Save successful: {success}")

# Test configuration loading
from utils.opensearch_connection import load_connection
config = load_connection()
print(f"Config loaded: {config is not None}")

# Test client creation
from utils.opensearch_connection import get_opensearch_client
client = get_opensearch_client()
print(f"Client created: {client is not None}")
```

## Migration Guide

### From Old Connection Approach

If you have notebooks using the old connection approach:

**Old Pattern**:
```python
from utils.connection import OpenSearchConnection, ConnectionConfig
from config.connection_template import get_connection_config

config = get_connection_config()
connection = OpenSearchConnection(config)
client = connection.connect()
```

**New Pattern** (for intermediate/advanced notebooks):
```python
from utils.opensearch_connection import setup_connection

client = setup_connection()
```

### Updating Existing Notebooks

1. **Replace imports**:
   ```python
   # Old
   from utils.connection import OpenSearchConnection, ConnectionConfig
   from config.connection_template import get_connection_config
   
   # New
   from utils.opensearch_connection import setup_connection
   ```

2. **Replace connection setup**:
   ```python
   # Old
   config = get_connection_config()
   connection = OpenSearchConnection(config)
   client = connection.connect()
   
   # New
   client = setup_connection()
   ```

3. **Update error handling**:
   ```python
   # Old
   if connection.test_connection():
       print("Connected")
   else:
       print("Failed")
   
   # New
   if client:
       print("✅ Successfully connected to OpenSearch")
   else:
       print("❌ Connection failed")
       print("💡 Run the basic connection notebook (01_basic_connection.ipynb) first")
   ```

## Best Practices

### For Library Users

1. **Use appropriate tier**: Educational for learning, productivity for advanced work
2. **Start with basic connection**: Always complete `01_basic_connection.ipynb` first
3. **Handle errors gracefully**: Include proper error messages and troubleshooting guidance
4. **Test connections**: Verify connectivity before proceeding with operations

### For Library Developers

1. **Maintain consistency**: Use standard error messages and patterns
2. **Provide clear feedback**: Include helpful troubleshooting information
3. **Handle edge cases**: Account for different environments and configurations
4. **Document changes**: Update this documentation when modifying the library

### Security Considerations

1. **Never commit tokens**: Use environment variables or gitignored config files
2. **Use SSL by default**: Auto-detection should prefer secure connections
3. **Validate certificates**: Only disable verification for development/testing
4. **Rotate tokens regularly**: Generate new AstraCS tokens periodically

## Troubleshooting

For detailed troubleshooting information, see [CONNECTION_TROUBLESHOOTING.md](../CONNECTION_TROUBLESHOOTING.md).

Common issues:
- Configuration file not found → Run basic connection notebook
- Import errors → Check Python path and working directory
- SSL errors → Update certificates or check corporate network settings
- Authentication failures → Verify AstraCS token format and permissions