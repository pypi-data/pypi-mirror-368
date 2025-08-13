"""
Sample datasets utility optimized for Google Colab environments.

This module provides access to generated sample datasets for different demo scenarios,
eliminating the need for external files and making it perfect for Google Colab usage.
"""

import logging
import random
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timedelta
import uuid

from .data_loader import DataLoader, DataValidationError, generate_sample_articles, generate_sample_products, generate_sample_logs

logger = logging.getLogger(__name__)


class DatasetType(Enum):
    """Enumeration of available dataset types."""
    PRODUCTS = "products"
    ARTICLES = "articles"
    LOGS = "logs"


class SampleDatasets:
    """
    Utility class for managing and generating sample datasets for Google Colab.
    
    Provides easy access to various types of generated sample data for OpenSearch demos,
    including products, articles, and log data. All data is generated in-memory,
    making it perfect for Google Colab environments.
    """
    
    def __init__(self):
        """Initialize the SampleDatasets utility."""
        self.data_loader = DataLoader()
        
        # Dataset configuration with generation parameters
        self.datasets = {
            DatasetType.PRODUCTS: {
                "description": "E-commerce product catalog with categories, prices, and ratings",
                "generator": generate_sample_products,
                "default_count": 30,
                "fields": ["id", "name", "category", "brand", "price", "description", "tags", "rating"],
                "use_cases": ["product search", "faceted search", "aggregations", "price filtering"]
            },
            DatasetType.ARTICLES: {
                "description": "Blog articles with content, metadata, and engagement metrics",
                "generator": generate_sample_articles,
                "default_count": 50,
                "fields": ["id", "title", "author", "category", "content", "tags", "published_date"],
                "use_cases": ["full-text search", "content analysis", "semantic search", "date filtering"]
            },
            DatasetType.LOGS: {
                "description": "Application log entries with timestamps, levels, and metrics",
                "generator": generate_sample_logs,
                "default_count": 100,
                "fields": ["id", "timestamp", "level", "service", "message", "user_id", "response_time_ms"],
                "use_cases": ["log analysis", "time-series data", "monitoring dashboards", "error tracking"]
            }
        }
    
    def list_available_datasets(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available datasets.
        
        Returns:
            Dictionary mapping dataset names to their metadata
        """
        available = {}
        
        for dataset_type, config in self.datasets.items():
            available[dataset_type.value] = {
                "description": config["description"],
                "generator": config["generator"].__name__,
                "default_count": config["default_count"],
                "fields": config["fields"],
                "use_cases": config["use_cases"],
                "source": "Generated in-memory (Colab-optimized)"
            }
        
        return available
    
    def load_dataset(self, dataset_type: DatasetType, 
                    count: Optional[int] = None,
                    prepare_for_index: bool = False,
                    index_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate and load a specific dataset.
        
        Args:
            dataset_type: Type of dataset to generate
            count: Number of records to generate (uses default if None)
            prepare_for_index: Whether to prepare data for OpenSearch indexing
            index_name: Index name to use if preparing for indexing
            
        Returns:
            List of dictionaries containing the dataset
            
        Raises:
            ValueError: If dataset type is invalid
            DataValidationError: If data generation fails
        """
        if dataset_type not in self.datasets:
            available_types = [dt.value for dt in DatasetType]
            raise ValueError(f"Invalid dataset type. Available: {available_types}")
        
        config = self.datasets[dataset_type]
        
        # Use default count if not specified
        if count is None:
            count = config["default_count"]
        
        if count <= 0:
            raise ValueError("Count must be a positive integer")
        
        try:
            # Generate data using the appropriate generator function
            generator_func = config["generator"]
            data = generator_func(count)
            
            if not data:
                raise DataValidationError(f"Generator returned empty data for {dataset_type.value}")
            
            # Prepare for indexing if requested
            if prepare_for_index:
                if not index_name:
                    index_name = f"demo_{dataset_type.value}"
                data = self.data_loader.prepare_for_indexing(data, index_name)
            
            logger.info(f"Generated {len(data)} records for {dataset_type.value} dataset")
            print(f"✅ Generated {len(data)} {dataset_type.value} records")
            
            return data
            
        except Exception as e:
            error_msg = f"Failed to generate {dataset_type.value} dataset: {str(e)}"
            logger.error(error_msg)
            raise DataValidationError(error_msg)
    
    def load_products(self, count: int = 30, prepare_for_index: bool = False, 
                     index_name: str = "demo_products") -> List[Dict[str, Any]]:
        """
        Generate and load the products dataset.
        
        Args:
            count: Number of products to generate
            prepare_for_index: Whether to prepare data for OpenSearch indexing
            index_name: Index name to use if preparing for indexing
            
        Returns:
            List of product dictionaries
        """
        return self.load_dataset(DatasetType.PRODUCTS, count, prepare_for_index, index_name)
    
    def load_articles(self, count: int = 50, prepare_for_index: bool = False,
                     index_name: str = "demo_articles") -> List[Dict[str, Any]]:
        """
        Generate and load the articles dataset.
        
        Args:
            count: Number of articles to generate
            prepare_for_index: Whether to prepare data for OpenSearch indexing
            index_name: Index name to use if preparing for indexing
            
        Returns:
            List of article dictionaries
        """
        return self.load_dataset(DatasetType.ARTICLES, count, prepare_for_index, index_name)
    
    def load_logs(self, count: int = 100, prepare_for_index: bool = False,
                 index_name: str = "demo_logs") -> List[Dict[str, Any]]:
        """
        Generate and load the logs dataset.
        
        Args:
            count: Number of log entries to generate
            prepare_for_index: Whether to prepare data for OpenSearch indexing
            index_name: Index name to use if preparing for indexing
            
        Returns:
            List of log entry dictionaries
        """
        return self.load_dataset(DatasetType.LOGS, count, prepare_for_index, index_name)
    
    def get_dataset_info(self, dataset_type: DatasetType) -> Dict[str, Any]:
        """
        Get detailed information about a specific dataset.
        
        Args:
            dataset_type: Type of dataset to get info for
            
        Returns:
            Dictionary containing dataset metadata
            
        Raises:
            ValueError: If dataset type is invalid
        """
        if dataset_type not in self.datasets:
            available_types = [dt.value for dt in DatasetType]
            raise ValueError(f"Invalid dataset type. Available: {available_types}")
        
        config = self.datasets[dataset_type]
        
        info = {
            "name": dataset_type.value,
            "description": config["description"],
            "generator_function": config["generator"].__name__,
            "default_count": config["default_count"],
            "expected_fields": config["fields"],
            "use_cases": config["use_cases"],
            "source": "Generated in-memory",
            "colab_optimized": True
        }
        
        # Generate a small sample to show structure
        try:
            sample_data = config["generator"](3)  # Generate 3 samples
            if sample_data:
                info["sample_record"] = sample_data[0]
                info["actual_fields"] = list(sample_data[0].keys())
                info["generation_successful"] = True
            else:
                info["generation_successful"] = False
                info["error"] = "Generator returned empty data"
                
        except Exception as e:
            info["generation_successful"] = False
            info["error"] = str(e)
            logger.warning(f"Could not generate sample for {dataset_type.value}: {e}")
        
        return info
    
    def validate_all_datasets(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all available dataset generators.
        
        Returns:
            Dictionary mapping dataset names to validation results
        """
        results = {}
        
        for dataset_type in DatasetType:
            try:
                info = self.get_dataset_info(dataset_type)
                
                validation_result = {
                    "valid": info.get("generation_successful", False),
                    "generator_available": True,
                    "error": info.get("error"),
                    "colab_ready": True
                }
                
                # Check if expected fields are present in generated data
                if "actual_fields" in info and "expected_fields" in info:
                    expected_fields = set(info["expected_fields"])
                    actual_fields = set(info["actual_fields"])
                    validation_result["missing_fields"] = list(expected_fields - actual_fields)
                    validation_result["extra_fields"] = list(actual_fields - expected_fields)
                
                results[dataset_type.value] = validation_result
                
            except Exception as e:
                results[dataset_type.value] = {
                    "valid": False,
                    "generator_available": False,
                    "error": str(e),
                    "colab_ready": False
                }
        
        return results
    
    def create_mixed_dataset(self, products_count: int = 20, articles_count: int = 30, 
                           logs_count: int = 50, prepare_for_index: bool = False,
                           index_name: str = "demo_mixed") -> Dict[str, List[Dict[str, Any]]]:
        """
        Create a mixed dataset with multiple data types for complex demos.
        
        Args:
            products_count: Number of products to generate
            articles_count: Number of articles to generate
            logs_count: Number of log entries to generate
            prepare_for_index: Whether to prepare data for OpenSearch indexing
            index_name: Base index name (will be suffixed with data type)
            
        Returns:
            Dictionary containing all generated datasets
        """
        mixed_data = {}
        
        try:
            # Generate products
            if products_count > 0:
                products_index = f"{index_name}_products" if prepare_for_index else None
                mixed_data['products'] = self.load_products(
                    products_count, prepare_for_index, products_index
                )
            
            # Generate articles
            if articles_count > 0:
                articles_index = f"{index_name}_articles" if prepare_for_index else None
                mixed_data['articles'] = self.load_articles(
                    articles_count, prepare_for_index, articles_index
                )
            
            # Generate logs
            if logs_count > 0:
                logs_index = f"{index_name}_logs" if prepare_for_index else None
                mixed_data['logs'] = self.load_logs(
                    logs_count, prepare_for_index, logs_index
                )
            
            total_records = sum(len(data) for data in mixed_data.values())
            print(f"✅ Generated mixed dataset with {total_records} total records")
            print(f"   📦 Products: {len(mixed_data.get('products', []))}")
            print(f"   📄 Articles: {len(mixed_data.get('articles', []))}")
            print(f"   📊 Logs: {len(mixed_data.get('logs', []))}")
            
            return mixed_data
            
        except Exception as e:
            error_msg = f"Failed to create mixed dataset: {str(e)}"
            logger.error(error_msg)
            raise DataValidationError(error_msg)
    
    def get_sample_queries(self, dataset_type: DatasetType) -> Dict[str, str]:
        """
        Get sample OpenSearch queries for a specific dataset type.
        
        Args:
            dataset_type: Type of dataset to get queries for
            
        Returns:
            Dictionary of sample queries with descriptions
        """
        if dataset_type == DatasetType.PRODUCTS:
            return {
                "match_all": '{"query": {"match_all": {}}}',
                "category_filter": '{"query": {"term": {"category": "Electronics"}}}',
                "price_range": '{"query": {"range": {"price": {"gte": 50, "lte": 200}}}}',
                "text_search": '{"query": {"match": {"name": "smartphone"}}}',
                "aggregation": '{"aggs": {"categories": {"terms": {"field": "category"}}}}'
            }
        
        elif dataset_type == DatasetType.ARTICLES:
            return {
                "match_all": '{"query": {"match_all": {}}}',
                "content_search": '{"query": {"match": {"content": "technology"}}}',
                "author_filter": '{"query": {"term": {"author": "Alice Johnson"}}}',
                "date_range": '{"query": {"range": {"published_date": {"gte": "2023-01-01"}}}}',
                "aggregation": '{"aggs": {"authors": {"terms": {"field": "author"}}}}'
            }
        
        elif dataset_type == DatasetType.LOGS:
            return {
                "match_all": '{"query": {"match_all": {}}}',
                "error_logs": '{"query": {"term": {"level": "ERROR"}}}',
                "service_filter": '{"query": {"term": {"service": "auth-service"}}}',
                "time_range": '{"query": {"range": {"timestamp": {"gte": "now-1h"}}}}',
                "aggregation": '{"aggs": {"log_levels": {"terms": {"field": "level"}}}}'
            }
        
        else:
            return {"match_all": '{"query": {"match_all": {}}}'}


# Convenience functions for quick access
def quick_products(count: int = 30) -> List[Dict[str, Any]]:
    """Quick function to generate product data."""
    return generate_sample_products(count)


def quick_articles(count: int = 50) -> List[Dict[str, Any]]:
    """Quick function to generate article data."""
    return generate_sample_articles(count)


def quick_logs(count: int = 100) -> List[Dict[str, Any]]:
    """Quick function to generate log data."""
    return generate_sample_logs(count)