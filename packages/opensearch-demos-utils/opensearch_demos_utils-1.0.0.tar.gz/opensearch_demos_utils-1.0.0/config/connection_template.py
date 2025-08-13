"""
Connection configuration template for OpenSearch demos.

This template provides example configuration for connecting to the managed
OpenSearch service using AstraCS token authentication.

To use this template:
1. Copy this file to 'connection_config.py' in the same directory
2. Replace the placeholder values with your actual connection details
3. Obtain your AstraCS token from astra.com following the instructions below

How to obtain AstraCS token from astra.com:
1. Visit https://astra.com and sign in to your account
2. Navigate to your OpenSearch service dashboard
3. Go to the "Connect" or "API Access" section
4. Generate or copy your AstraCS token
5. The token will be in the format: AstraCS:xxxxx...


Security Note:
- Never commit your actual connection configuration with real tokens to version control
- Use environment variables for production deployments
- Keep your AstraCS token secure and rotate it regularly
"""

import os
from utils.connection import ConnectionConfig

# Example configuration using placeholder values
# Replace these with your actual connection details from astra.com

# Option 1: Direct configuration (for development/testing)
EXAMPLE_CONFIG = ConnectionConfig(
    host="your-opensearch-cluster.astra.com",  # Replace with your cluster endpoint
    port=9200,  # Astra always uses port 9200 with HTTPS
    astra_cs_token="AstraCS:your-token-here",  # Replace with your actual AstraCS token
    use_ssl=None,  # Auto-detect based on host/port (None = auto-detect)
    verify_certs=None,  # Auto-detect based on host/port (None = auto-detect)
    timeout=30  # Connection timeout in seconds
)

# Option 1b: Localhost development configuration
LOCALHOST_CONFIG = ConnectionConfig(
    host="localhost",  # Local OpenSearch instance
    port=9200,  # Standard OpenSearch HTTP port
    astra_cs_token="AstraCS:dev-token",  # Use any token for local dev
    use_ssl=False,  # Explicitly disable SSL for localhost
    verify_certs=False,  # Don't verify certificates for localhost
    timeout=30
)

# Option 2: Environment variable configuration (recommended for production)
def get_config_from_env() -> ConnectionConfig:
    """
    Create ConnectionConfig from environment variables.
    
    Required environment variables:
    - OPENSEARCH_HOST: Your OpenSearch cluster endpoint
    - ASTRA_CS_TOKEN: Your AstraCS token from astra.com
    
    Optional environment variables:
    - OPENSEARCH_PORT: Port number (default: 9200)
    - OPENSEARCH_TIMEOUT: Connection timeout in seconds (default: 30)
    - OPENSEARCH_USE_SSL: Enable/disable SSL (true/false, default: auto-detect)
    - OPENSEARCH_VERIFY_CERTS: Verify SSL certificates (true/false, default: auto-detect)
    
    Returns:
        ConnectionConfig instance configured from environment variables
        
    Raises:
        ValueError: If required environment variables are not set
    """
    host = os.getenv('OPENSEARCH_HOST')
    token = os.getenv('ASTRA_CS_TOKEN')
    
    if not host:
        raise ValueError(
            "OPENSEARCH_HOST environment variable is required. "
            "Set it to your OpenSearch cluster endpoint from astra.com"
        )
    
    if not token:
        raise ValueError(
            "ASTRA_CS_TOKEN environment variable is required. "
            "Obtain your token from astra.com and set this environment variable"
        )
    
    # Parse SSL configuration from environment variables
    use_ssl = None
    ssl_env = os.getenv('OPENSEARCH_USE_SSL', '').lower()
    if ssl_env in ['true', '1', 'yes', 'on']:
        use_ssl = True
    elif ssl_env in ['false', '0', 'no', 'off']:
        use_ssl = False
    # If not set or invalid, leave as None for auto-detection
    
    verify_certs = None
    verify_env = os.getenv('OPENSEARCH_VERIFY_CERTS', '').lower()
    if verify_env in ['true', '1', 'yes', 'on']:
        verify_certs = True
    elif verify_env in ['false', '0', 'no', 'off']:
        verify_certs = False
    # If not set or invalid, leave as None for auto-detection
    
    return ConnectionConfig(
        host=host,
        port=int(os.getenv('OPENSEARCH_PORT', '9200')),
        astra_cs_token=token,
        use_ssl=use_ssl,  # Auto-detect if None
        verify_certs=verify_certs,  # Auto-detect if None
        timeout=int(os.getenv('OPENSEARCH_TIMEOUT', '30'))
    )

# Example usage:
# 
# For development (using direct configuration):
# config = EXAMPLE_CONFIG  # After replacing placeholder values
# 
# For production (using environment variables):
# config = get_config_from_env()
# 
# Then create connection:
# from utils.connection import OpenSearchConnection
# connection = OpenSearchConnection(config)
# client = connection.connect()

# Environment variable setup examples:
# 
# Linux/macOS:
# export OPENSEARCH_HOST="your-cluster.astra.com"
# export ASTRA_CS_TOKEN="AstraCS:your-actual-token-here"
# export OPENSEARCH_PORT="9200"  # Optional: defaults to 9200 (Astra always uses 9200 with HTTPS)
# 
# Windows:
# set OPENSEARCH_HOST=your-cluster.astra.com
# set ASTRA_CS_TOKEN=AstraCS:your-actual-token-here
# set OPENSEARCH_PORT=9200
# 
# Python script:
# import os
# os.environ['OPENSEARCH_HOST'] = 'your-cluster.astra.com'
# os.environ['ASTRA_CS_TOKEN'] = 'AstraCS:your-actual-token-here'
# os.environ['OPENSEARCH_PORT'] = '9200'  # Optional

# SSL Configuration Examples:
# 
# For localhost development (disable SSL):
# export OPENSEARCH_HOST="localhost"
# export OPENSEARCH_PORT="9200"
# export OPENSEARCH_USE_SSL="false"
# export OPENSEARCH_VERIFY_CERTS="false"
# export ASTRA_CS_TOKEN="AstraCS:dev-token"  # Any token for local dev
# 
# For managed services (auto-detect SSL - recommended):
# export OPENSEARCH_HOST="your-cluster.astra.com"
# export OPENSEARCH_PORT="9200"
# export ASTRA_CS_TOKEN="AstraCS:your-actual-token"
# # SSL settings auto-detected based on host/port
# 
# For custom SSL configuration:
# export OPENSEARCH_USE_SSL="true"   # Force SSL on
# export OPENSEARCH_VERIFY_CERTS="false"  # Disable cert verification (not recommended for production)

# Port Configuration Guide:
# 
# Common OpenSearch ports:
# - 9200: Standard OpenSearch HTTP port (default) / Astra HTTPS port
# - 9243: Standard OpenSearch HTTPS port
# - 9300: OpenSearch transport port (for node-to-node communication)
# 
# For DataStax Astra managed services: always use port 9200 with HTTPS
# For self-hosted OpenSearch clusters: use port 9200 (HTTP) or 9243 (HTTPS)
# 
# Set the port using environment variable:
# export OPENSEARCH_PORT="9200"  # For Astra managed services (with HTTPS)
# export OPENSEARCH_PORT="9200"  # For self-hosted (HTTP, default)
# export OPENSEARCH_PORT="9243"  # For self-hosted (HTTPS)

# Troubleshooting common issues:
# 
# 1. Authentication Error (401):
#    - Verify your AstraCS token is correct and not expired
#    - Ensure the token includes the "AstraCS:" prefix
#    - Check that your token has the necessary permissions
# 
# 2. Connection Timeout:
#    - Verify your host endpoint is correct
#    - Check your network connectivity and port accessibility
#    - Try increasing the timeout value
#    - Ensure you're using the correct port (9200 for Astra managed, 9200/9243 for self-hosted)
# 
# 3. SSL Certificate Error:
#    - Ensure use_ssl=True for managed OpenSearch
#    - Verify verify_certs=True for production use
#    - Check if your network has SSL inspection that might interfere
# 
# 4. Host Not Found:
#    - Double-check your cluster endpoint from astra.com
#    - Ensure the endpoint doesn't include protocol (https://) prefix
#    - Verify your cluster is active and accessible
# 
# 5. Port Connection Issues:
#    - Verify the correct port for your OpenSearch service
#    - Check firewall settings allow connections to the specified port
#    - For Astra managed services, always use port 9200 with HTTPS
#    - For self-hosted clusters, typically use port 9200 (HTTP) or 9243 (HTTPS)

# SSL Auto-Detection Behavior:
# 
# The ConnectionConfig class automatically detects appropriate SSL settings:
# 
# 1. Localhost Detection:
#    - Hosts: localhost, 127.0.0.1, ::1, 0.0.0.0, 192.168.x.x, 10.x.x.x, 172.x.x.x
#    - Default: use_ssl=False, verify_certs=False
# 
# 2. Standard Ports:
#    - Port 443, 9243: use_ssl=True (HTTPS ports)
#    - Port 80, 9200: use_ssl=False for localhost, True for remote hosts
# 
# 3. Override Options:
#    - Set use_ssl=True/False to override auto-detection
#    - Set verify_certs=True/False to override certificate verification
#    - Use environment variables for flexible configuration
# 
# Examples of auto-detection:
# - localhost:9200 → use_ssl=False, verify_certs=False
# - localhost:443 → use_ssl=True, verify_certs=False
# - remote-host.com:9200 → use_ssl=True, verify_certs=True
# - remote-host.com:443 → use_ssl=True, verify_certs=True