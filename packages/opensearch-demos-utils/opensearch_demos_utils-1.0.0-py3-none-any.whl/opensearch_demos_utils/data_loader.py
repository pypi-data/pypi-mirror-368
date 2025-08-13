"""
Data loading and preparation utilities optimized for Google Colab.

This module provides utilities for loading various data formats and preparing
them for indexing in OpenSearch, with in-memory sample data generation
capabilities for Google Colab environments.
"""

import json
import csv
import logging
import random
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import uuid
from io import StringIO

logger = logging.getLogger(__name__)


# Sample data embedded directly in the module for Colab compatibility
EMBEDDED_SAMPLE_ARTICLES = [
    {
        "id": "article_001",
        "title": "Getting Started with OpenSearch 3.0",
        "author": "Jane Smith",
        "category": "Technology",
        "content": "OpenSearch 3.0 introduces significant improvements in search performance and new features for developers. This comprehensive guide covers the key enhancements including improved vector search capabilities, enhanced query DSL, and better integration options.",
        "tags": ["opensearch", "search", "technology", "tutorial"],
        "published_date": "2024-03-01T08:00:00Z",
        "word_count": 1250,
        "reading_time": 5,
        "views": 15420,
        "likes": 342
    },
    {
        "id": "article_002",
        "title": "Machine Learning in Modern Search Systems",
        "author": "Dr. Michael Chen",
        "category": "AI & Machine Learning",
        "content": "Explore how machine learning algorithms are revolutionizing search systems. From relevance scoring to personalized results, ML techniques are making search more intelligent and user-centric than ever before.",
        "tags": ["machine-learning", "ai", "search", "algorithms"],
        "published_date": "2024-03-05T12:30:00Z",
        "word_count": 2100,
        "reading_time": 8,
        "views": 8750,
        "likes": 198
    },
    {
        "id": "article_003",
        "title": "Best Practices for Data Indexing",
        "author": "Sarah Johnson",
        "category": "Data Management",
        "content": "Learn the essential best practices for indexing data efficiently. This article covers mapping strategies, field types, analyzers, and performance optimization techniques for large-scale data indexing.",
        "tags": ["indexing", "data-management", "performance", "best-practices"],
        "published_date": "2024-03-10T14:45:00Z",
        "word_count": 1800,
        "reading_time": 7,
        "views": 12300,
        "likes": 267
    },
    {
        "id": "article_004",
        "title": "Vector Search and Semantic Understanding",
        "author": "Alex Rodriguez",
        "category": "Technology",
        "content": "Dive deep into vector search capabilities and how they enable semantic understanding in search applications. Learn about embedding models, similarity search, and practical implementation strategies.",
        "tags": ["vector-search", "semantic-search", "embeddings", "similarity"],
        "published_date": "2024-03-15T10:15:00Z",
        "word_count": 2400,
        "reading_time": 9,
        "views": 6890,
        "likes": 156
    },
    {
        "id": "article_005",
        "title": "Monitoring and Observability in Search Systems",
        "author": "Emma Wilson",
        "category": "DevOps",
        "content": "Comprehensive guide to monitoring search system performance, setting up alerts, and maintaining observability. Covers key metrics, logging strategies, and troubleshooting common issues.",
        "tags": ["monitoring", "observability", "devops", "performance"],
        "published_date": "2024-03-20T16:00:00Z",
        "word_count": 1650,
        "reading_time": 6,
        "views": 9420,
        "likes": 223
    }
]

EMBEDDED_SAMPLE_PRODUCTS = [
    {
        "id": "prod_001",
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "brand": "TechSound",
        "price": 89.99,
        "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life.",
        "tags": ["wireless", "bluetooth", "headphones", "noise-cancellation"],
        "in_stock": True,
        "rating": 4.5,
        "reviews_count": 1247,
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": "prod_002",
        "name": "Organic Coffee Beans",
        "category": "Food & Beverages",
        "brand": "Mountain Roast",
        "price": 24.99,
        "description": "Premium organic coffee beans sourced from sustainable farms in Colombia.",
        "tags": ["organic", "coffee", "beans", "fair-trade", "colombian"],
        "in_stock": True,
        "rating": 4.8,
        "reviews_count": 892,
        "created_at": "2024-01-20T14:15:00Z"
    },
    {
        "id": "prod_003",
        "name": "Yoga Mat Premium",
        "category": "Sports & Fitness",
        "brand": "FlexFit",
        "price": 45.00,
        "description": "Non-slip yoga mat made from eco-friendly materials, perfect for all yoga practices.",
        "tags": ["yoga", "mat", "fitness", "eco-friendly", "non-slip"],
        "in_stock": False,
        "rating": 4.3,
        "reviews_count": 567,
        "created_at": "2024-02-01T09:45:00Z"
    },
    {
        "id": "prod_004",
        "name": "Smart Home Security Camera",
        "category": "Electronics",
        "brand": "SecureView",
        "price": 129.99,
        "description": "WiFi-enabled security camera with night vision, motion detection, and mobile app control.",
        "tags": ["security", "camera", "smart-home", "wifi", "night-vision"],
        "in_stock": True,
        "rating": 4.2,
        "reviews_count": 2103,
        "created_at": "2024-02-10T16:20:00Z"
    },
    {
        "id": "prod_005",
        "name": "Stainless Steel Water Bottle",
        "category": "Home & Kitchen",
        "brand": "HydroLife",
        "price": 19.99,
        "description": "Insulated stainless steel water bottle that keeps drinks cold for 24 hours or hot for 12 hours.",
        "tags": ["water-bottle", "stainless-steel", "insulated", "eco-friendly"],
        "in_stock": True,
        "rating": 4.6,
        "reviews_count": 1456,
        "created_at": "2024-02-15T11:30:00Z"
    }
]

EMBEDDED_SAMPLE_LOGS_CSV = """timestamp,level,service,message,user_id,request_id,duration_ms
2024-03-01T08:00:00Z,INFO,api-gateway,Request received,user_123,req_001,45
2024-03-01T08:00:01Z,INFO,auth-service,User authenticated successfully,user_123,req_001,12
2024-03-01T08:00:02Z,INFO,search-service,Search query executed,user_123,req_001,234
2024-03-01T08:00:03Z,INFO,api-gateway,Response sent,user_123,req_001,5
2024-03-01T08:01:15Z,WARN,search-service,Slow query detected,user_456,req_002,1250
2024-03-01T08:01:16Z,ERROR,database,Connection timeout,user_456,req_002,5000
2024-03-01T08:01:17Z,INFO,api-gateway,Request failed,user_456,req_002,2
2024-03-01T08:02:30Z,INFO,api-gateway,Request received,user_789,req_003,38
2024-03-01T08:02:31Z,INFO,auth-service,User authenticated successfully,user_789,req_003,8
2024-03-01T08:02:32Z,INFO,search-service,Search query executed,user_789,req_003,156
2024-03-01T08:02:33Z,INFO,api-gateway,Response sent,user_789,req_003,4
2024-03-01T08:03:45Z,DEBUG,cache-service,Cache hit,user_123,req_004,2
2024-03-01T08:03:46Z,INFO,search-service,Cached result returned,user_123,req_004,15
2024-03-01T08:04:00Z,ERROR,auth-service,Invalid credentials,user_999,req_005,25
2024-03-01T08:04:01Z,INFO,api-gateway,Authentication failed,user_999,req_005,1"""


class DataValidationError(Exception):
    """Raised when data validation fails."""
    pass


class DataLoader:
    """
    Utility class for loading and preparing data for OpenSearch indexing.
    
    Optimized for Google Colab environments with support for both file-based
    data loading and in-memory sample data generation.
    """
    
    def __init__(self):
        """Initialize the DataLoader."""
        self.supported_formats = ['.json', '.csv']
    
    def load_json_from_string(self, json_string: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSON string (useful for Colab environments).
        
        Args:
            json_string: JSON data as string
            
        Returns:
            List of dictionaries containing the loaded data
            
        Raises:
            json.JSONDecodeError: If the JSON is invalid
            DataValidationError: If the data format is invalid
        """
        try:
            data = json.loads(json_string)
            
            # Ensure data is a list of dictionaries
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise DataValidationError("JSON data must be a dictionary or list of dictionaries")
            
            # Validate that all items are dictionaries
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    raise DataValidationError(f"Item at index {i} is not a dictionary")
            
            logger.info(f"Successfully loaded {len(data)} records from JSON string")
            return data
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON string: {e.msg}", e.doc, e.pos)
    
    def load_csv_from_string(self, csv_string: str, delimiter: str = ',') -> List[Dict[str, Any]]:
        """
        Load data from a CSV string (useful for Colab environments).
        
        Args:
            csv_string: CSV data as string
            delimiter: CSV delimiter (default: ',')
            
        Returns:
            List of dictionaries containing the loaded data
            
        Raises:
            DataValidationError: If the CSV format is invalid
        """
        try:
            data = []
            csv_file = StringIO(csv_string)
            reader = csv.DictReader(csv_file, delimiter=delimiter)
            
            if not reader.fieldnames:
                raise DataValidationError("CSV string has no headers")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                # Remove empty values and strip whitespace
                cleaned_row = {k: v.strip() if isinstance(v, str) else v 
                             for k, v in row.items() if v is not None and v != ''}
                
                if cleaned_row:  # Only add non-empty rows
                    data.append(cleaned_row)
            
            if not data:
                raise DataValidationError("CSV string contains no valid data rows")
            
            logger.info(f"Successfully loaded {len(data)} records from CSV string")
            return data
            
        except csv.Error as e:
            raise DataValidationError(f"CSV parsing error: {e}")
    
    def prepare_for_indexing(self, data: List[Dict[str, Any]], index_name: str, 
                           id_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Prepare data for OpenSearch indexing by adding metadata and validation.
        
        Args:
            data: List of dictionaries to prepare
            index_name: Name of the target OpenSearch index
            id_field: Field to use as document ID (if None, generates UUIDs)
            
        Returns:
            List of dictionaries ready for OpenSearch indexing
            
        Raises:
            DataValidationError: If data validation fails
        """
        if not isinstance(data, list):
            raise DataValidationError("Data must be a list of dictionaries")
        
        if not data:
            raise DataValidationError("Data list cannot be empty")
        
        if not index_name or not isinstance(index_name, str):
            raise DataValidationError("Index name must be a non-empty string")
        
        prepared_data = []
        current_time = datetime.utcnow().isoformat()
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise DataValidationError(f"Item at index {i} is not a dictionary")
            
            # Create a copy to avoid modifying original data
            prepared_item = item.copy()
            
            # Add or validate document ID
            if id_field and id_field in prepared_item:
                doc_id = str(prepared_item[id_field])
                if not doc_id:
                    raise DataValidationError(f"Empty ID field '{id_field}' at index {i}")
            else:
                doc_id = str(uuid.uuid4())
                prepared_item['_generated_id'] = doc_id
            
            # Add indexing metadata
            prepared_item['_index_metadata'] = {
                'index_name': index_name,
                'indexed_at': current_time,
                'document_id': doc_id
            }
            
            # Ensure all string values are properly encoded
            prepared_item = self._clean_string_values(prepared_item)
            
            prepared_data.append(prepared_item)
        
        logger.info(f"Prepared {len(prepared_data)} documents for indexing in '{index_name}'")
        return prepared_data
    
    def _clean_string_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean string values in the data dictionary.
        
        Args:
            data: Dictionary to clean
            
        Returns:
            Dictionary with cleaned string values
        """
        cleaned = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Strip whitespace and handle empty strings
                cleaned_value = value.strip()
                cleaned[key] = cleaned_value if cleaned_value else None
            elif isinstance(value, dict):
                # Recursively clean nested dictionaries
                cleaned[key] = self._clean_string_values(value)
            elif isinstance(value, list):
                # Clean list items
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        cleaned_item = item.strip()
                        if cleaned_item:
                            cleaned_list.append(cleaned_item)
                    elif isinstance(item, dict):
                        cleaned_list.append(self._clean_string_values(item))
                    else:
                        cleaned_list.append(item)
                cleaned[key] = cleaned_list
            else:
                cleaned[key] = value
        
        return cleaned
    
    def validate_data_structure(self, data: List[Dict[str, Any]], 
                              required_fields: Optional[List[str]] = None) -> bool:
        """
        Validate the structure of loaded data.
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Returns:
            True if validation passes
            
        Raises:
            DataValidationError: If validation fails
        """
        if not isinstance(data, list):
            raise DataValidationError("Data must be a list")
        
        if not data:
            raise DataValidationError("Data list cannot be empty")
        
        required_fields = required_fields or []
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise DataValidationError(f"Item at index {i} is not a dictionary")
            
            # Check required fields
            for field in required_fields:
                if field not in item:
                    raise DataValidationError(f"Required field '{field}' missing at index {i}")
                
                if item[field] is None or (isinstance(item[field], str) and not item[field].strip()):
                    raise DataValidationError(f"Required field '{field}' is empty at index {i}")
        
        logger.info(f"Data validation passed for {len(data)} records")
        return True


def generate_sample_articles(count: int = 50) -> List[Dict[str, Any]]:
    """
    Generate sample article data for demonstrations.
    
    Args:
        count: Number of articles to generate
        
    Returns:
        List of article dictionaries
    """
    categories = ['Technology', 'Science', 'Business', 'Health', 'Sports', 'Entertainment']
    authors = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown', 'Frank Miller']
    
    sample_titles = [
        "The Future of Artificial Intelligence",
        "Climate Change and Renewable Energy",
        "Digital Transformation in Healthcare",
        "The Rise of Remote Work",
        "Quantum Computing Breakthroughs",
        "Sustainable Business Practices",
        "Mental Health in the Digital Age",
        "The Evolution of E-commerce",
        "Space Exploration Updates",
        "Cybersecurity Best Practices"
    ]
    
    sample_content_snippets = [
        "This comprehensive analysis explores the latest developments in",
        "Recent research has shown significant progress in",
        "Industry experts predict that the next decade will bring",
        "New innovations are transforming the way we approach",
        "The impact of these changes extends far beyond",
        "Organizations worldwide are adapting to",
        "Key findings from recent studies indicate",
        "The integration of advanced technologies is enabling",
        "Market trends suggest a growing demand for",
        "Stakeholders are increasingly focused on"
    ]
    
    articles = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(count):
        article_id = f"article_{i+1:03d}"
        title = f"{random.choice(sample_titles)} - Part {i+1}"
        author = random.choice(authors)
        category = random.choice(categories)
        
        # Generate content
        content_parts = random.sample(sample_content_snippets, 3)
        content = f"{content_parts[0]} {category.lower()}. {content_parts[1]} this field. {content_parts[2]} significant improvements in efficiency and effectiveness."
        
        # Generate tags
        tags = random.sample(['innovation', 'research', 'analysis', 'trends', 'future', 'technology', 'development'], 3)
        
        # Generate publication date
        pub_date = base_date + timedelta(days=random.randint(0, 365))
        
        article = {
            'id': article_id,
            'title': title,
            'author': author,
            'category': category,
            'content': content,
            'tags': tags,
            'published_date': pub_date.isoformat(),
            'word_count': len(content.split()),
            'reading_time': max(1, len(content.split()) // 200),  # Approximate reading time in minutes
            'views': random.randint(100, 10000),
            'likes': random.randint(10, 500)
        }
        
        articles.append(article)
    
    return articles


def generate_sample_products(count: int = 30) -> List[Dict[str, Any]]:
    """
    Generate sample product data for demonstrations.
    
    Args:
        count: Number of products to generate
        
    Returns:
        List of product dictionaries
    """
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Beauty']
    brands = ['TechCorp', 'StyleBrand', 'BookHouse', 'HomeMax', 'SportsPro', 'BeautyPlus']
    
    product_names = {
        'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Tablet', 'Smart Watch'],
        'Clothing': ['T-Shirt', 'Jeans', 'Sneakers', 'Jacket', 'Dress'],
        'Books': ['Programming Guide', 'Science Fiction Novel', 'History Book', 'Cookbook', 'Biography'],
        'Home & Garden': ['Coffee Maker', 'Plant Pot', 'Lamp', 'Cushion', 'Tool Set'],
        'Sports': ['Running Shoes', 'Yoga Mat', 'Dumbbells', 'Tennis Racket', 'Water Bottle'],
        'Beauty': ['Face Cream', 'Shampoo', 'Lipstick', 'Perfume', 'Moisturizer']
    }
    
    products = []
    
    for i in range(count):
        category = random.choice(categories)
        product_name = random.choice(product_names[category])
        brand = random.choice(brands)
        
        product_id = f"prod_{i+1:03d}"
        name = f"{brand} {product_name} {random.choice(['Pro', 'Elite', 'Classic', 'Premium', 'Standard'])}"
        
        # Generate price based on category
        price_ranges = {
            'Electronics': (50, 1500),
            'Clothing': (20, 200),
            'Books': (10, 50),
            'Home & Garden': (15, 300),
            'Sports': (25, 400),
            'Beauty': (10, 100)
        }
        
        min_price, max_price = price_ranges[category]
        price = round(random.uniform(min_price, max_price), 2)
        
        # Generate description
        descriptions = [
            f"High-quality {product_name.lower()} from {brand}",
            f"Premium {product_name.lower()} designed for everyday use",
            f"Professional-grade {product_name.lower()} with advanced features",
            f"Stylish and functional {product_name.lower()}",
            f"Durable {product_name.lower()} built to last"
        ]
        
        description = random.choice(descriptions)
        
        # Generate tags
        base_tags = [category.lower(), brand.lower(), product_name.lower().replace(' ', '-')]
        additional_tags = random.sample(['popular', 'bestseller', 'new', 'premium', 'eco-friendly'], 2)
        tags = base_tags + additional_tags
        
        product = {
            'id': product_id,
            'name': name,
            'category': category,
            'brand': brand,
            'price': price,
            'description': description,
            'tags': tags,
            'rating': round(random.uniform(3.0, 5.0), 1),
            'review_count': random.randint(5, 500),
            'in_stock': random.choice([True, True, True, False]),  # 75% in stock
            'stock_quantity': random.randint(0, 100) if random.choice([True, False]) else 0
        }
        
        products.append(product)
    
    return products


def generate_sample_logs(count: int = 100) -> List[Dict[str, Any]]:
    """
    Generate sample log data for demonstrations.
    
    Args:
        count: Number of log entries to generate
        
    Returns:
        List of log entry dictionaries
    """
    log_levels = ['INFO', 'WARN', 'ERROR', 'DEBUG']
    services = ['auth-service', 'user-service', 'payment-service', 'notification-service', 'api-gateway']
    users = [f'user_{i:03d}' for i in range(1, 21)]  # 20 different users
    
    message_templates = {
        'INFO': [
            'User login successful',
            'Request processed successfully',
            'Service started',
            'Database connection established',
            'Cache updated'
        ],
        'WARN': [
            'High memory usage detected',
            'Slow query detected',
            'Rate limit approaching',
            'Deprecated API used',
            'Connection timeout retry'
        ],
        'ERROR': [
            'Database connection failed',
            'Authentication failed',
            'Payment processing error',
            'Service unavailable',
            'Invalid request format'
        ],
        'DEBUG': [
            'Processing request',
            'Validating input parameters',
            'Executing database query',
            'Sending notification',
            'Updating user session'
        ]
    }
    
    logs = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(count):
        log_id = f"log_{i+1:04d}"
        level = random.choice(log_levels)
        service = random.choice(services)
        user_id = random.choice(users)
        
        # Generate timestamp (spread over last 24 hours)
        timestamp = base_time + timedelta(seconds=random.randint(0, 86400))
        
        # Generate message
        message_template = random.choice(message_templates[level])
        message = f"{message_template} for {user_id}"
        
        # Generate additional metrics
        response_time = random.randint(10, 2000) if level != 'ERROR' else random.randint(1000, 5000)
        status_code = 200
        if level == 'ERROR':
            status_code = random.choice([400, 401, 403, 404, 500, 502, 503])
        elif level == 'WARN':
            status_code = random.choice([200, 201, 202, 429])
        
        log_entry = {
            'id': log_id,
            'timestamp': timestamp.isoformat(),
            'level': level,
            'service': service,
            'message': message,
            'user_id': user_id,
            'response_time_ms': response_time,
            'status_code': status_code,
            'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            'request_id': str(uuid.uuid4())[:8]
        }
        
        logs.append(log_entry)
    
    # Sort by timestamp
    logs.sort(key=lambda x: x['timestamp'])
    
    return logs


def load_embedded_sample_articles() -> List[Dict[str, Any]]:
    """
    Load the embedded sample articles data.
    
    Returns:
        List of sample article dictionaries
    """
    return EMBEDDED_SAMPLE_ARTICLES.copy()


def load_embedded_sample_products() -> List[Dict[str, Any]]:
    """
    Load the embedded sample products data.
    
    Returns:
        List of sample product dictionaries
    """
    return EMBEDDED_SAMPLE_PRODUCTS.copy()


def load_embedded_sample_logs() -> List[Dict[str, Any]]:
    """
    Load the embedded sample logs data.
    
    Returns:
        List of sample log entry dictionaries
    """
    loader = DataLoader()
    return loader.load_csv_from_string(EMBEDDED_SAMPLE_LOGS_CSV)


def prepare_sample_data_for_demo(data_type: str, count: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Prepare sample data for demonstration purposes.
    
    Args:
        data_type: Type of data to generate ('articles', 'products', 'logs')
        count: Number of items to generate (uses defaults if None)
        
    Returns:
        List of prepared sample data
        
    Raises:
        ValueError: If data_type is not supported
    """
    if data_type == 'articles':
        if count is None:
            return load_embedded_sample_articles()
        else:
            return generate_sample_articles(count)
    elif data_type == 'products':
        if count is None:
            return load_embedded_sample_products()
        else:
            return generate_sample_products(count)
    elif data_type == 'logs':
        if count is None:
            return load_embedded_sample_logs()
        else:
            return generate_sample_logs(count)
    else:
        raise ValueError(f"Unsupported data type: {data_type}. Supported types: 'articles', 'products', 'logs'")


def create_bulk_index_data(data: List[Dict[str, Any]], index_name: str, 
                          id_field: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Create bulk indexing data format for OpenSearch.
    
    Args:
        data: List of documents to prepare
        index_name: Name of the target index
        id_field: Field to use as document ID
        
    Returns:
        List of bulk operation dictionaries ready for OpenSearch bulk API
    """
    loader = DataLoader()
    prepared_data = loader.prepare_for_indexing(data, index_name, id_field)
    
    bulk_data = []
    for doc in prepared_data:
        # Create index operation
        doc_id = doc.get('_index_metadata', {}).get('document_id', str(uuid.uuid4()))
        
        # Remove internal metadata before indexing
        clean_doc = {k: v for k, v in doc.items() if not k.startswith('_')}
        
        bulk_data.append({
            "index": {
                "_index": index_name,
                "_id": doc_id
            }
        })
        bulk_data.append(clean_doc)
    
    return bulk_data


def get_sample_data_info() -> Dict[str, Dict[str, Any]]:
    """
    Get information about available sample datasets.
    
    Returns:
        Dictionary with information about each sample dataset
    """
    return {
        'articles': {
            'description': 'Sample articles with titles, authors, content, and metadata',
            'embedded_count': len(EMBEDDED_SAMPLE_ARTICLES),
            'fields': ['id', 'title', 'author', 'category', 'content', 'tags', 'published_date', 'word_count', 'reading_time', 'views', 'likes'],
            'use_cases': ['Full-text search', 'Categorization', 'Content analysis']
        },
        'products': {
            'description': 'Sample product catalog with prices, ratings, and inventory',
            'embedded_count': len(EMBEDDED_SAMPLE_PRODUCTS),
            'fields': ['id', 'name', 'category', 'brand', 'price', 'description', 'tags', 'rating', 'reviews_count', 'in_stock'],
            'use_cases': ['E-commerce search', 'Filtering and faceting', 'Recommendation systems']
        },
        'logs': {
            'description': 'Sample application logs with timestamps, levels, and metrics',
            'embedded_count': len(EMBEDDED_SAMPLE_LOGS_CSV.split('\n')) - 1,  # Subtract header
            'fields': ['timestamp', 'level', 'service', 'message', 'user_id', 'request_id', 'duration_ms'],
            'use_cases': ['Log analysis', 'Time-series data', 'Monitoring and alerting']
        }
    }