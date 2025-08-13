"""
Configuration template system for Google Colab OpenSearch demos.

This module provides standardized configuration templates, validation,
and helper functions for setting up OpenSearch connections in Google Colab
notebooks with DataStax Astra managed OpenSearch.
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from .connection import ColabConnectionConfig, OpenSearchConnection


class ConfigurationTemplate:
    """
    Provides standardized configuration templates for Google Colab notebooks.
    
    This class generates copy-paste friendly configuration cells with Astra defaults,
    validation, and clear instructions for users.
    """
    
    @staticmethod
    def get_basic_config_template() -> str:
        """
        Generate basic configuration template cell for Google Colab.
        
        Returns:
            String containing complete configuration cell template
        """
        return '''# 🔧 OpenSearch Connection Configuration for Google Colab
# 
# This cell sets up your connection to DataStax Astra OpenSearch.
# Replace the placeholder values with your actual Astra credentials.
# 
# 📋 How to get your credentials:
# 1. Go to https://astra.datastax.com/
# 2. Select your OpenSearch database
# 3. Go to "Connect" tab
# 4. Copy your endpoint URL and generate an AstraCS token
#
# ⚠️  SECURITY NOTE: Never share notebooks containing real credentials!

# Replace these values with your actual Astra credentials
OPENSEARCH_CONFIG = {
    # Your Astra OpenSearch endpoint (ends with .astra.datastax.com)
    "host": "your-cluster-id.astra.datastax.com",
    
    # Port for Astra OpenSearch (always 9200 with SSL)
    "port": 9200,
    
    # Your AstraCS token (starts with AstraCS:)
    "astra_cs_token": "AstraCS:your-token-here",
    
    # SSL settings (required for Astra)
    "use_ssl": True,
    "verify_certs": False,  # Set to False for development
    
    # Connection timeout in seconds
    "timeout": 30
}

# 🚀 Initialize and test connection
from opensearch_demos_utils import ColabConnectionConfig, OpenSearchConnection

try:
    # Create configuration with validation
    config = ColabConnectionConfig(**OPENSEARCH_CONFIG)
    
    # Create connection manager
    connection = OpenSearchConnection(config)
    
    # Test the connection
    client = connection.connect()
    
    # Display connection summary
    print("\\n📊 Connection Summary:")
    print("=" * 40)
    summary = config.get_connection_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("=" * 40)
    
    print("\\n✅ Configuration successful! You can now run the demo cells below.")
    
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    print("\\n🔧 Please check your credentials and try again.")
    print("💡 Make sure to replace all placeholder values with your actual Astra credentials.")
'''

    @staticmethod
    def get_advanced_config_template() -> str:
        """
        Generate advanced configuration template with additional options.
        
        Returns:
            String containing advanced configuration cell template
        """
        return '''# 🔧 Advanced OpenSearch Connection Configuration for Google Colab
#
# This cell provides advanced configuration options for DataStax Astra OpenSearch.
# Most users should use the basic configuration template instead.

# Advanced configuration with all available options
OPENSEARCH_CONFIG = {
    # Basic connection settings
    "host": "your-cluster-id.astra.datastax.com",
    "port": 9200,
    "astra_cs_token": "AstraCS:your-token-here",
    
    # SSL/TLS settings
    "use_ssl": True,
    "verify_certs": False,  # Set to True for production with proper certificates
    
    # Performance settings
    "timeout": 30,          # Connection timeout in seconds
    
    # Advanced options (usually not needed)
    # "ca_certs": None,     # Path to CA certificate file (if needed)
}

# Additional configuration for specific use cases
ADVANCED_OPTIONS = {
    # Retry settings for unstable networks
    "max_retries": 3,
    "retry_on_timeout": True,
    
    # Connection pool settings (handled automatically)
    "pool_maxsize": 10,
    
    # Request settings
    "request_timeout": 60,  # Individual request timeout
}

# 🚀 Initialize connection with advanced options
from opensearch_demos_utils import ColabConnectionConfig, OpenSearchConnection

try:
    # Create configuration
    config = ColabConnectionConfig(**OPENSEARCH_CONFIG)
    
    # Create connection with advanced options
    connection = OpenSearchConnection(config)
    
    # Connect and test
    client = connection.connect()
    
    # Get detailed cluster information
    cluster_info = connection.get_cluster_info()
    
    print("\\n📊 Detailed Connection Information:")
    print("=" * 50)
    
    # Display cluster info
    if 'cluster_info' in cluster_info:
        info = cluster_info['cluster_info']
        print(f"Cluster Name: {info.get('cluster_name', 'Unknown')}")
        print(f"Version: {info.get('version', {}).get('number', 'Unknown')}")
        print(f"Tagline: {info.get('tagline', 'Unknown')}")
    
    # Display health info
    if 'cluster_health' in cluster_info:
        health = cluster_info['cluster_health']
        print(f"\\nCluster Status: {health.get('status', 'Unknown')}")
        print(f"Number of Nodes: {health.get('number_of_nodes', 'Unknown')}")
        print(f"Active Shards: {health.get('active_shards', 'Unknown')}")
    
    print("=" * 50)
    print("\\n✅ Advanced configuration successful!")
    
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    print("\\n🔧 Troubleshooting steps:")
    print("1. Verify your Astra cluster is active")
    print("2. Check your AstraCS token is valid and not expired")
    print("3. Ensure your endpoint URL is correct")
    print("4. Try the basic configuration template if issues persist")
'''

    @staticmethod
    def get_minimal_config_template() -> str:
        """
        Generate minimal configuration template for quick setup.
        
        Returns:
            String containing minimal configuration cell template
        """
        return '''# ⚡ Quick OpenSearch Configuration for Google Colab
# Replace the two values below with your Astra credentials

# Your Astra endpoint and token
ASTRA_HOST = "your-cluster-id.astra.datastax.com"
ASTRA_TOKEN = "AstraCS:your-token-here"

# Quick setup and connection test
from opensearch_demos_utils import create_colab_connection

try:
    connection = create_colab_connection(
        host=ASTRA_HOST,
        astra_cs_token=ASTRA_TOKEN
    )
    client = connection.connect()
    print("✅ Quick setup successful! Ready to run demos.")
    
except Exception as e:
    print(f"❌ Setup failed: {e}")
    print("💡 Double-check your host and token values above.")
'''

    @staticmethod
    def get_troubleshooting_template() -> str:
        """
        Generate troubleshooting configuration template with diagnostics.
        
        Returns:
            String containing troubleshooting configuration cell template
        """
        return '''# 🔍 OpenSearch Connection Troubleshooting for Google Colab
#
# Use this cell to diagnose connection issues with your Astra OpenSearch setup.
# This template includes comprehensive validation and diagnostic information.

# Your configuration (replace with actual values)
OPENSEARCH_CONFIG = {
    "host": "your-cluster-id.astra.datastax.com",
    "port": 9200,
    "astra_cs_token": "AstraCS:your-token-here",
    "use_ssl": True,
    "verify_certs": False,
    "timeout": 30
}

# 🔍 Comprehensive diagnostics and troubleshooting
from opensearch_demos_utils import ColabConnectionConfig, OpenSearchConnection
import sys

print("🔍 OpenSearch Connection Diagnostics")
print("=" * 50)

# Step 1: Environment check
print("\\n1️⃣ Environment Check:")
print(f"Python version: {sys.version}")

try:
    import opensearchpy
    print(f"✅ opensearch-py version: {opensearchpy.__version__}")
except ImportError:
    print("❌ opensearch-py not installed")
    print("💡 Run: !pip install opensearch-py")

# Step 2: Configuration validation
print("\\n2️⃣ Configuration Validation:")
try:
    config = ColabConnectionConfig(**OPENSEARCH_CONFIG)
    print("✅ Configuration format is valid")
    
    # Display configuration summary
    summary = config.get_connection_summary()
    for key, value in summary.items():
        status = "✅" if value not in ["Unknown", "No"] else "⚠️"
        print(f"{status} {key.replace('_', ' ').title()}: {value}")
        
except Exception as e:
    print(f"❌ Configuration validation failed: {e}")
    print("💡 Check your configuration values above")

# Step 3: Connection test
print("\\n3️⃣ Connection Test:")
try:
    connection = OpenSearchConnection(config)
    client = connection.connect()
    print("✅ Connection established successfully")
    
    # Test basic operations
    info = client.info()
    print(f"✅ Cluster accessible: {info.get('cluster_name', 'Unknown')}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\\n🔧 Troubleshooting suggestions:")
    print("• Verify your Astra cluster is active (not hibernated)")
    print("• Check your AstraCS token hasn't expired")
    print("• Ensure your endpoint URL is correct")
    print("• Try generating a new AstraCS token")
    print("• Restart your Colab runtime and try again")

print("\\n" + "=" * 50)
print("🏁 Diagnostics complete!")
'''


class ConfigurationValidator:
    """
    Validates OpenSearch configuration for Google Colab environment.
    
    Provides comprehensive validation with helpful error messages and
    suggestions for common configuration issues.
    """
    
    @staticmethod
    def validate_config_dict(config_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate configuration dictionary and return validation results.
        
        Args:
            config_dict: Dictionary containing configuration parameters
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Required fields validation
        required_fields = ['host', 'astra_cs_token']
        for field in required_fields:
            if field not in config_dict or not config_dict[field]:
                errors.append(f"❌ Missing required field: {field}")
        
        # Host validation
        if 'host' in config_dict:
            host = config_dict['host']
            if not ConfigurationValidator._validate_host(host):
                errors.append(f"❌ Invalid host format: {host}")
        
        # Token validation
        if 'astra_cs_token' in config_dict:
            token = config_dict['astra_cs_token']
            if not ConfigurationValidator._validate_astra_token(token):
                errors.append(f"❌ Invalid AstraCS token format")
        
        # Port validation
        if 'port' in config_dict:
            port = config_dict['port']
            if not ConfigurationValidator._validate_port(port):
                errors.append(f"❌ Invalid port: {port}")
        
        # SSL validation for Astra
        if 'host' in config_dict and config_dict['host'].endswith('.astra.datastax.com'):
            if config_dict.get('use_ssl') is False:
                errors.append("❌ SSL must be enabled for Astra connections")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_host(host: str) -> bool:
        """Validate host format."""
        if not host or not isinstance(host, str):
            return False
        
        # Check for localhost (not allowed in Colab)
        localhost_patterns = ['localhost', '127.0.0.1', '::1', '0.0.0.0']
        if any(pattern in host.lower() for pattern in localhost_patterns):
            return False
        
        # Basic domain validation
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, host))
    
    @staticmethod
    def _validate_astra_token(token: str) -> bool:
        """Validate AstraCS token format."""
        if not token or not isinstance(token, str):
            return False
        
        return token.startswith('AstraCS:') and len(token) > 10
    
    @staticmethod
    def _validate_port(port: Any) -> bool:
        """Validate port number."""
        try:
            port_int = int(port)
            return 1 <= port_int <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def get_validation_report(config_dict: Dict[str, Any]) -> str:
        """
        Generate a comprehensive validation report for configuration.
        
        Args:
            config_dict: Configuration dictionary to validate
            
        Returns:
            String containing formatted validation report
        """
        is_valid, errors = ConfigurationValidator.validate_config_dict(config_dict)
        
        report = "📋 Configuration Validation Report\n"
        report += "=" * 40 + "\n\n"
        
        if is_valid:
            report += "✅ Configuration is valid!\n\n"
            
            # Add recommendations
            report += "💡 Recommendations:\n"
            
            host = config_dict.get('host', '')
            if host.endswith('.astra.datastax.com'):
                report += "• Using DataStax Astra (recommended for Colab)\n"
                if config_dict.get('port') == 9200:
                    report += "• Port 9200 is correct for Astra\n"
                if config_dict.get('use_ssl') is True:
                    report += "• SSL is properly enabled for Astra\n"
            else:
                report += "• Consider using DataStax Astra for best Colab compatibility\n"
                
        else:
            report += "❌ Configuration has issues:\n\n"
            for error in errors:
                report += f"{error}\n"
            
            report += "\n🔧 How to fix:\n"
            report += "• Check the configuration template examples above\n"
            report += "• Verify your Astra credentials are correct\n"
            report += "• Ensure all required fields are filled\n"
        
        report += "\n" + "=" * 40
        return report


class ConfigurationHelper:
    """
    Helper functions for configuration management in Google Colab.
    
    Provides utilities for generating, validating, and managing
    OpenSearch configurations in Colab notebooks.
    """
    
    @staticmethod
    def create_config_from_template(template_type: str = "basic") -> str:
        """
        Create configuration cell based on template type.
        
        Args:
            template_type: Type of template ("basic", "advanced", "minimal", "troubleshooting")
            
        Returns:
            String containing configuration cell template
        """
        template_map = {
            "basic": ConfigurationTemplate.get_basic_config_template,
            "advanced": ConfigurationTemplate.get_advanced_config_template,
            "minimal": ConfigurationTemplate.get_minimal_config_template,
            "troubleshooting": ConfigurationTemplate.get_troubleshooting_template
        }
        
        if template_type not in template_map:
            raise ValueError(f"Unknown template type: {template_type}")
        
        return template_map[template_type]()
    
    @staticmethod
    def validate_and_connect(config_dict: Dict[str, Any]) -> Tuple[bool, Optional[OpenSearchConnection], str]:
        """
        Validate configuration and attempt connection.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Tuple of (success, connection_object, status_message)
        """
        # First validate the configuration
        is_valid, errors = ConfigurationValidator.validate_config_dict(config_dict)
        
        if not is_valid:
            error_msg = "Configuration validation failed:\n" + "\n".join(errors)
            return False, None, error_msg
        
        # Try to create connection
        try:
            config = ColabConnectionConfig(**config_dict)
            connection = OpenSearchConnection(config)
            client = connection.connect()
            
            success_msg = "✅ Configuration validated and connection established successfully!"
            return True, connection, success_msg
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            return False, None, error_msg
    
    @staticmethod
    def generate_colab_setup_instructions() -> str:
        """
        Generate comprehensive setup instructions for Google Colab.
        
        Returns:
            String containing formatted setup instructions
        """
        return '''# 📚 Google Colab Setup Instructions for OpenSearch Demos

## 🚀 Quick Start Guide

### Step 1: Install Dependencies
Run this cell first to install required packages:

```python
!pip install opensearch-py opensearch-demos-utils pandas matplotlib seaborn
```

### Step 2: Configure Connection
Choose one of the configuration templates below and replace with your credentials:

**Option A: Basic Configuration (Recommended)**
- Use `ConfigurationTemplate.get_basic_config_template()`
- Copy the generated cell and replace placeholder values

**Option B: Quick Setup**
- Use `ConfigurationTemplate.get_minimal_config_template()`
- Just replace host and token values

**Option C: Advanced Configuration**
- Use `ConfigurationTemplate.get_advanced_config_template()`
- For users who need custom settings

### Step 3: Test Connection
After configuration, the template will automatically test your connection.

## 🔧 Getting Your Astra Credentials

1. **Go to DataStax Astra Console**: https://astra.datastax.com/
2. **Select Your Database**: Choose your OpenSearch database
3. **Navigate to Connect Tab**: Click on "Connect" in the left sidebar
4. **Copy Endpoint**: Copy your cluster endpoint URL
5. **Generate Token**: Create a new AstraCS token with appropriate permissions

## 🆘 Troubleshooting

If you encounter issues:

1. **Use Troubleshooting Template**: 
   ```python
   from opensearch_demos_utils.config_templates import ConfigurationTemplate
   print(ConfigurationTemplate.get_troubleshooting_template())
   ```

2. **Common Issues**:
   - Cluster is hibernated (activate it in Astra console)
   - Token has expired (generate a new one)
   - Incorrect endpoint URL (check Astra console)
   - Network connectivity (restart Colab runtime)

3. **Get Help**: Check the troubleshooting section in each template

## 📋 Configuration Reference

### Required Fields
- `host`: Your Astra endpoint (ends with .astra.datastax.com)
- `astra_cs_token`: Your AstraCS token (starts with AstraCS:)

### Optional Fields
- `port`: Port number (default: 9200 for Astra)
- `use_ssl`: Enable SSL (default: True, required for Astra)
- `verify_certs`: Certificate verification (default: False for development)
- `timeout`: Connection timeout in seconds (default: 30)

## 🔒 Security Best Practices

- Never commit notebooks with real credentials to version control
- Use Colab secrets for sensitive data in shared notebooks
- Rotate your AstraCS tokens regularly
- Don't share notebooks containing credentials

## 💡 Tips for Success

- Always run cells in order from top to bottom
- Restart runtime if you encounter import errors
- Use the validation features to check your configuration
- Keep your Astra cluster active during demo sessions
'''


# Convenience functions for easy access
def get_basic_template() -> str:
    """Get basic configuration template."""
    return ConfigurationTemplate.get_basic_config_template()

def get_minimal_template() -> str:
    """Get minimal configuration template."""
    return ConfigurationTemplate.get_minimal_config_template()

def get_advanced_template() -> str:
    """Get advanced configuration template."""
    return ConfigurationTemplate.get_advanced_config_template()

def get_troubleshooting_template() -> str:
    """Get troubleshooting configuration template."""
    return ConfigurationTemplate.get_troubleshooting_template()

def validate_config(config_dict: Dict[str, Any]) -> str:
    """Validate configuration and return report."""
    return ConfigurationValidator.get_validation_report(config_dict)

def create_connection_from_config(config_dict: Dict[str, Any]) -> OpenSearchConnection:
    """Create and test connection from configuration dictionary."""
    success, connection, message = ConfigurationHelper.validate_and_connect(config_dict)
    
    if not success:
        raise ValueError(message)
    
    return connection