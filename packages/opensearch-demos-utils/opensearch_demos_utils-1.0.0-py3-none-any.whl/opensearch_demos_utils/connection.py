"""
Connection utilities for OpenSearch demos optimized for Google Colab.

This module provides connection management for OpenSearch services,
specifically optimized for DataStax Astra managed OpenSearch with
AstraCS token authentication in Google Colab environments.
"""

import json
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

# Import OpenSearch only when needed to avoid import issues
def _get_opensearch():
    """Import OpenSearch only when needed."""
    try:
        from opensearchpy import OpenSearch
        return OpenSearch
    except ImportError:
        print("❌ opensearch-py not installed. Install with: pip install opensearch-py")
        return None


@dataclass
class ColabConnectionConfig:
    """
    Colab-optimized connection configuration for DataStax Astra OpenSearch.
    
    This class provides Astra-specific validation and defaults optimized for
    Google Colab environments. It enforces Astra connection requirements and
    provides helpful validation messages.
    """
    
    host: str
    port: int = 9200
    astra_cs_token: str = ""
    use_ssl: bool = True
    verify_certs: bool = False
    timeout: int = 30
    
    def __post_init__(self):
        """Validate Astra-specific requirements and provide helpful feedback."""
        if not self.host:
            raise ValueError("Host is required for OpenSearch connection")
        
        if not self.astra_cs_token:
            raise ValueError("AstraCS token is required for authentication")
        
        if not self.astra_cs_token.startswith('AstraCS:'):
            raise ValueError("AstraCS token must start with 'AstraCS:'")
        
        if self.port <= 0:
            raise ValueError("Port must be a positive integer")
        
        if self.timeout <= 0:
            raise ValueError("Timeout must be a positive integer")
        
        # Astra-specific validation and warnings
        if not self.host.endswith('.astra.datastax.com'):
            print("⚠️ Warning: Host doesn't appear to be an Astra endpoint")
        
        if self.port != 9200:
            print("⚠️ Warning: Astra typically uses port 9200")
        
        if not self.use_ssl:
            print("⚠️ Warning: Astra requires SSL, enabling SSL automatically")
            self.use_ssl = True
        
        # Validate for Colab environment
        self._validate_for_colab()
    
    def _validate_for_colab(self):
        """Validate configuration specifically for Google Colab environment."""
        # Check for localhost connections (not suitable for Colab)
        localhost_indicators = ['localhost', '127.0.0.1', '::1', '0.0.0.0']
        if any(indicator in self.host.lower() for indicator in localhost_indicators):
            raise ValueError(
                "🚫 Localhost connections don't work in Google Colab. "
                "Please use DataStax Astra managed OpenSearch service."
            )
        
        # Check for private IP ranges (not accessible from Colab)
        if (self.host.startswith('192.168.') or 
            self.host.startswith('10.') or 
            self.host.startswith('172.')):
            raise ValueError(
                "🚫 Private IP addresses are not accessible from Google Colab. "
                "Please use DataStax Astra or another publicly accessible OpenSearch service."
            )
    
    def get_connection_summary(self) -> Dict[str, str]:
        """Get a summary of connection settings for debugging."""
        is_astra = self.host.endswith('.astra.datastax.com')
        
        return {
            'host': self.host,
            'port': str(self.port),
            'use_ssl': str(self.use_ssl),
            'verify_certs': str(self.verify_certs),
            'service_type': 'DataStax Astra' if is_astra else 'Other OpenSearch',
            'protocol': 'HTTPS' if self.use_ssl else 'HTTP',
            'auth_method': 'AstraCS Token',
            'colab_compatible': 'Yes' if is_astra else 'Unknown'
        }
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Returns authentication headers with AstraCS token for Bearer token authentication.
        
        Returns:
            Dict containing Authorization header with Bearer token
        """
        return {"Authorization": f"Bearer {self.astra_cs_token}"}


@dataclass
class ConnectionConfig(ColabConnectionConfig):
    """
    Legacy connection configuration class for backward compatibility.
    
    This class extends ColabConnectionConfig to maintain compatibility with
    existing code while providing the same Colab-optimized functionality.
    """
    
    ca_certs: Optional[str] = None
    
    def __post_init__(self):
        """Call parent validation and add legacy compatibility features."""
        # Call parent validation first
        super().__post_init__()
        
        # Additional legacy compatibility features can be added here if needed


class OpenSearchConnection:
    """
    Manages connection to OpenSearch services optimized for Google Colab.
    
    Provides connection management specifically designed for Google Colab
    environments connecting to managed OpenSearch services like DataStax Astra.
    """
    
    def __init__(self, config: Union[ColabConnectionConfig, ConnectionConfig]):
        """
        Initialize OpenSearch connection with configuration.
        
        Args:
            config: ColabConnectionConfig or ConnectionConfig instance with connection parameters
        """
        self.config = config
        self._client = None
        
        # Configuration validation is handled in the config's __post_init__ method
        print(f"🔧 Initializing connection to {config.host}:{config.port}")
    
    def connect(self):
        """
        Establish connection to OpenSearch using AstraCS token authentication.
        
        Returns:
            OpenSearch client instance
            
        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            # Build connection parameters optimized for Colab
            connection_params = {
                'hosts': [{'host': self.config.host, 'port': self.config.port}],
                'http_auth': None,  # We use custom headers instead
                'use_ssl': self.config.use_ssl,
                'verify_certs': self.config.verify_certs,
                'timeout': self.config.timeout,
                'headers': self.config.get_auth_headers(),
                'max_retries': 3,  # Add retries for network stability in Colab
                'retry_on_timeout': True
            }
            
            # Add CA certs if specified (only available in ConnectionConfig)
            if hasattr(self.config, 'ca_certs') and self.config.ca_certs:
                connection_params['ca_certs'] = self.config.ca_certs
            
            # Create OpenSearch client
            OpenSearch = _get_opensearch()
            if not OpenSearch:
                raise ConnectionError("OpenSearch library not available")
            
            self._client = OpenSearch(**connection_params)
            
            # Test the connection immediately
            if not self.test_connection():
                raise ConnectionError("Connection test failed after client creation")
            
            print("✅ Successfully connected to OpenSearch!")
            return self._client
            
        except Exception as e:
            error_msg = f"Failed to connect to OpenSearch: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Provide Colab-specific troubleshooting hints
            self._print_colab_troubleshooting_hints()
            
            raise ConnectionError(error_msg)
    
    def test_connection(self) -> bool:
        """
        Test connectivity to the OpenSearch cluster.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            if not self._client:
                self.connect()
            
            # Use cluster info for connectivity test
            response = self._client.info()
            success = bool(response and 'cluster_name' in response)
            
            if success:
                cluster_name = response.get('cluster_name', 'Unknown')
                version = response.get('version', {}).get('number', 'Unknown')
                print(f"🔗 Connected to cluster: {cluster_name} (v{version})")
            
            return success
            
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get cluster information for service verification.
        
        Returns:
            Dictionary containing cluster information
            
        Raises:
            ConnectionError: If unable to retrieve cluster information
        """
        try:
            if not self._client:
                self.connect()
            
            # Get cluster info
            cluster_info = self._client.info()
            
            # Get cluster health
            cluster_health = self._client.cluster.health()
            
            return {
                'cluster_info': cluster_info,
                'cluster_health': cluster_health,
                'connection_config': self.config.get_connection_summary()
            }
            
        except Exception as e:
            error_msg = f"Failed to retrieve cluster information: {str(e)}"
            print(f"❌ {error_msg}")
            raise ConnectionError(error_msg)
    
    def _print_colab_troubleshooting_hints(self):
        """Print comprehensive troubleshooting hints specific to Google Colab environment."""
        print("\n🔧 Google Colab Troubleshooting Guide:")
        print("=" * 50)
        
        # Configuration issues
        print("\n📋 Configuration Issues:")
        print("• Verify your Astra cluster is active in the DataStax console")
        print("• Check that your AstraCS token is valid and starts with 'AstraCS:'")
        print("• Ensure your host endpoint is correct (should end with .astra.datastax.com)")
        print("• Confirm you're using port 9200 with SSL enabled for Astra")
        
        # Colab-specific issues
        print("\n🌐 Colab Environment Issues:")
        print("• Restart your Colab runtime if you see import errors")
        print("• Try running the connection test in a separate cell")
        print("• Check if dependencies were installed correctly (run !pip list | grep opensearch)")
        print("• Ensure you're not using localhost or private IP addresses")
        
        # Network and authentication issues
        print("\n🔐 Network & Authentication Issues:")
        print("• Verify your Astra cluster allows connections from external IPs")
        print("• Check if your AstraCS token has expired or been revoked")
        print("• Try generating a new AstraCS token from the DataStax console")
        print("• Ensure your cluster is in an active (not hibernated) state")
        
        # Common fixes
        print("\n🛠️ Common Fixes:")
        print("• Copy-paste your configuration into a fresh cell")
        print("• Restart runtime and re-run all cells from the beginning")
        print("• Check the DataStax Astra console for cluster status")
        print("• Try connecting from a different Colab notebook to isolate issues")
        
        print("=" * 50)


def create_colab_connection(host: str, astra_cs_token: str, 
                           port: int = 9200, **kwargs) -> OpenSearchConnection:
    """
    Convenience function to create a connection optimized for Google Colab.
    
    Args:
        host: OpenSearch host (should be Astra endpoint)
        astra_cs_token: AstraCS authentication token
        port: Port number (default: 9200 for Astra)
        **kwargs: Additional connection parameters
        
    Returns:
        OpenSearchConnection instance ready for use
        
    Example:
        >>> connection = create_colab_connection(
        ...     host="your-cluster.astra.datastax.com",
        ...     astra_cs_token="AstraCS:your-token-here"
        ... )
        >>> client = connection.connect()
    """
    # Set Colab-optimized defaults
    config_params = {
        'host': host,
        'port': port,
        'astra_cs_token': astra_cs_token,
        'use_ssl': True,
        'verify_certs': False,
        'timeout': 30
    }
    
    # Override with any provided kwargs
    config_params.update(kwargs)
    
    config = ColabConnectionConfig(**config_params)
    return OpenSearchConnection(config)