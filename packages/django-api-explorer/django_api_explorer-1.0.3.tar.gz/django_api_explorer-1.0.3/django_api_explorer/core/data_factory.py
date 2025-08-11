"""
Data factory for generating realistic sample data for API endpoints.
This module generates context-aware sample data for cURL commands.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from .models import APIEndpoint


class DataFactory:
    """Factory for generating realistic sample data for API endpoints."""

    def __init__(self):
        self._init_sample_data()

    def _init_sample_data(self):
        """Initialize sample data dictionaries."""
        self.names = [
            "John Doe",
            "Jane Smith",
            "Michael Johnson",
            "Emily Davis",
            "David Wilson",
            "Sarah Brown",
            "James Miller",
            "Lisa Garcia",
            "Robert Martinez",
            "Jennifer Anderson",
        ]

        self.emails = [
            "john.doe@example.com",
            "jane.smith@example.com",
            "michael.johnson@example.com",
            "emily.davis@example.com",
            "david.wilson@example.com",
            "sarah.brown@example.com",
        ]

        self.companies = [
            "Acme Corp",
            "Tech Solutions",
            "Global Industries",
            "Innovation Labs",
            "Digital Dynamics",
            "Future Systems",
            "Smart Solutions",
            "Next Gen Tech",
        ]

        self.cities = [
            "New York",
            "Los Angeles",
            "Chicago",
            "Houston",
            "Phoenix",
            "Philadelphia",
            "San Antonio",
            "San Diego",
            "Dallas",
            "San Jose",
        ]

        self.countries = [
            "United States",
            "Canada",
            "United Kingdom",
            "Germany",
            "France",
            "Japan",
            "Australia",
            "Brazil",
            "India",
            "China",
        ]

        self.phone_formats = [
            "+1-{area}-{prefix}-{line}",
            "+44 {area} {prefix} {line}",
            "+49 {area} {prefix} {line}",
            "+33 {area} {prefix} {line}",
            "+81 {area} {prefix} {line}",
        ]

    def generate_sample_data(
        self, endpoint: APIEndpoint, method: str
    ) -> Dict[str, Any]:
        """
        Generate realistic sample data for an endpoint based on its context.

        Args:
            endpoint: The API endpoint object
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)

        Returns:
            Dictionary containing sample data
        """
        if method.upper() in ["GET", "DELETE"]:
            return {}  # No body needed for GET/DELETE

        # Analyze the endpoint to determine the type of data needed
        endpoint_type = self._analyze_endpoint_type(endpoint)

        if endpoint_type == "user":
            return self._generate_user_data(endpoint, method)
        elif endpoint_type == "product":
            return self._generate_product_data(endpoint, method)
        elif endpoint_type == "order":
            return self._generate_order_data(endpoint, method)
        elif endpoint_type == "article":
            return self._generate_article_data(endpoint, method)
        elif endpoint_type == "auth":
            return self._generate_auth_data(endpoint, method)
        elif endpoint_type == "file":
            return self._generate_file_data(endpoint, method)
        else:
            return self._generate_generic_data(endpoint, method)

    def _analyze_endpoint_type(self, endpoint: APIEndpoint) -> str:
        """Analyze the endpoint to determine what type of data it expects."""
        path_lower = endpoint.path.lower()

        # User-related endpoints
        if any(word in path_lower for word in ["user", "users", "profile", "account"]):
            return "user"

        # Product-related endpoints
        if any(
            word in path_lower
            for word in ["product", "products", "item", "items", "goods"]
        ):
            return "product"

        # Order-related endpoints
        if any(
            word in path_lower
            for word in ["order", "orders", "purchase", "cart", "checkout"]
        ):
            return "order"

        # Article/blog endpoints
        if any(
            word in path_lower
            for word in ["article", "articles", "post", "posts", "blog"]
        ):
            return "article"

        # Authentication endpoints
        if any(
            word in path_lower
            for word in ["auth", "login", "register", "token", "password"]
        ):
            return "auth"

        # File upload endpoints
        if any(
            word in path_lower
            for word in ["upload", "file", "files", "image", "document"]
        ):
            return "file"

        return "generic"

    def _generate_user_data(self, endpoint: APIEndpoint, method: str) -> Dict[str, Any]:
        """Generate realistic user data."""
        if method.upper() == "POST":  # Create user
            return {
                "username": f"user_{random.randint(1000, 9999)}",
                "email": random.choice(self.emails),
                "first_name": random.choice(self.names).split()[0],
                "last_name": random.choice(self.names).split()[-1],
                "password": "SecurePassword123!",
                "phone": self._generate_phone(),
                "date_of_birth": self._generate_date(1980, 2000),
                "is_active": True,
                "profile": {
                    "bio": "Software developer passionate about creating amazing applications.",
                    "location": random.choice(self.cities),
                    "website": "https://example.com",
                    "social_links": {
                        "twitter": "@johndoe",
                        "linkedin": "linkedin.com/in/johndoe",
                        "github": "github.com/johndoe",
                    },
                },
            }
        elif method.upper() in ["PUT", "PATCH"]:  # Update user
            return {
                "first_name": random.choice(self.names).split()[0],
                "last_name": random.choice(self.names).split()[-1],
                "email": random.choice(self.emails),
                "phone": self._generate_phone(),
                "profile": {
                    "bio": "Updated bio with new information.",
                    "location": random.choice(self.cities),
                },
            }

        return {}

    def _generate_product_data(
        self, endpoint: APIEndpoint, method: str
    ) -> Dict[str, Any]:
        """Generate realistic product data."""
        if method.upper() == "POST":  # Create product
            return {
                "name": (
                    f"Product {random.choice(['Premium', 'Standard', 'Basic'])} "
                    f"{random.randint(100, 999)}"
                ),
                "description": "High-quality product designed for modern needs.",
                "price": round(random.uniform(10.0, 1000.0), 2),
                "currency": "USD",
                "category": random.choice(
                    ["Electronics", "Clothing", "Home", "Sports", "Books"]
                ),
                "brand": random.choice(self.companies),
                "sku": f"SKU-{random.randint(10000, 99999)}",
                "in_stock": random.choice([True, False]),
                "stock_quantity": random.randint(0, 1000),
                "tags": ["featured", "popular", "trending"],
                "specifications": {
                    "weight": f"{random.randint(1, 50)} kg",
                    "dimensions": (
                        f"{random.randint(10, 100)}x{random.randint(10, 100)}x"
                        f"{random.randint(5, 50)} cm"
                    ),
                    "color": random.choice(["Black", "White", "Blue", "Red", "Green"]),
                },
            }
        elif method.upper() in ["PUT", "PATCH"]:  # Update product
            return {
                "name": f"Updated Product {random.randint(100, 999)}",
                "price": round(random.uniform(10.0, 1000.0), 2),
                "description": "Updated product description with new features.",
                "in_stock": True,
                "stock_quantity": random.randint(10, 500),
            }

        return {}

    def _generate_order_data(
        self, endpoint: APIEndpoint, method: str
    ) -> Dict[str, Any]:
        """Generate realistic order data."""
        if method.upper() == "POST":  # Create order
            return {
                "customer_id": random.randint(1000, 9999),
                "items": [
                    {
                        "product_id": random.randint(1, 100),
                        "quantity": random.randint(1, 5),
                        "unit_price": round(random.uniform(10.0, 200.0), 2),
                    },
                    {
                        "product_id": random.randint(1, 100),
                        "quantity": random.randint(1, 3),
                        "unit_price": round(random.uniform(20.0, 150.0), 2),
                    },
                ],
                "shipping_address": {
                    "street": f"{random.randint(100, 9999)} Main Street",
                    "city": random.choice(self.cities),
                    "state": "CA",
                    "zip_code": f"{random.randint(10000, 99999)}",
                    "country": random.choice(self.countries),
                },
                "payment_method": random.choice(
                    ["credit_card", "paypal", "bank_transfer"]
                ),
                "notes": "Please deliver during business hours.",
            }
        elif method.upper() in ["PUT", "PATCH"]:  # Update order
            return {
                "status": random.choice(
                    ["processing", "shipped", "delivered", "cancelled"]
                ),
                "tracking_number": f"TRK{random.randint(100000000, 999999999)}",
                "estimated_delivery": self._generate_future_date(7, 14),
            }

        return {}

    def _generate_article_data(
        self, endpoint: APIEndpoint, method: str
    ) -> Dict[str, Any]:
        """Generate realistic article/blog post data."""
        if method.upper() == "POST":  # Create article
            return {
                "title": f"Amazing Article About {random.choice(['Technology', 'Science', 'Business', 'Health', 'Travel'])}",
                "content": "This is a comprehensive article about the latest developments in the field. It covers various aspects and provides valuable insights for readers.",
                "excerpt": "A brief summary of the article content that captures the main points.",
                "author_id": random.randint(1, 100),
                "category": random.choice(
                    ["Technology", "Science", "Business", "Health", "Travel"]
                ),
                "tags": ["featured", "trending", "insights"],
                "status": "published",
                "featured_image": "https://example.com/images/article.jpg",
                "meta_description": "SEO-friendly description for search engines.",
                "published_at": self._generate_date(2020, 2024),
            }
        elif method.upper() in ["PUT", "PATCH"]:  # Update article
            return {
                "title": f"Updated Article About {random.choice(['Technology', 'Science', 'Business'])}",
                "content": "Updated content with new information and insights.",
                "status": "published",
                "updated_at": datetime.now().isoformat(),
            }

        return {}

    def _generate_auth_data(self, endpoint: APIEndpoint, method: str) -> Dict[str, Any]:
        """Generate realistic authentication data."""
        if method.upper() == "POST":
            if "login" in endpoint.path.lower():
                return {
                    "username": "johndoe",
                    "password": "SecurePassword123!",
                    "remember_me": True,
                }
            elif "register" in endpoint.path.lower():
                return {
                    "username": f"user_{random.randint(1000, 9999)}",
                    "email": random.choice(self.emails),
                    "password": "SecurePassword123!",
                    "password_confirm": "SecurePassword123!",
                    "first_name": random.choice(self.names).split()[0],
                    "last_name": random.choice(self.names).split()[-1],
                }
            elif "password" in endpoint.path.lower():
                return {
                    "email": random.choice(self.emails),
                    "current_password": "OldPassword123!",
                    "new_password": "NewSecurePassword456!",
                    "new_password_confirm": "NewSecurePassword456!",
                }

        return {}

    def _generate_file_data(self, endpoint: APIEndpoint, method: str) -> Dict[str, Any]:
        """Generate realistic file upload data."""
        if method.upper() == "POST":
            return {
                "file": "path/to/sample/file.pdf",
                "description": "Sample file for testing purposes",
                "category": random.choice(["document", "image", "video", "audio"]),
                "tags": ["sample", "test", "upload"],
                "metadata": {
                    "size": random.randint(1024, 10485760),  # 1KB to 10MB
                    "format": random.choice(["pdf", "jpg", "png", "mp4", "mp3"]),
                    "uploaded_by": random.randint(1, 100),
                },
            }

        return {}

    def _generate_generic_data(
        self, endpoint: APIEndpoint, method: str
    ) -> Dict[str, Any]:
        """Generate generic sample data for unknown endpoint types."""
        if method.upper() == "POST":
            return {
                "name": f"Sample {random.choice(['Item', 'Object', 'Entity'])} {random.randint(1, 100)}",
                "description": "This is a sample data object for testing purposes.",
                "value": random.randint(1, 1000),
                "active": True,
                "created_at": datetime.now().isoformat(),
                "metadata": {
                    "type": "sample",
                    "version": "1.0",
                    "tags": ["test", "sample", "demo"],
                },
            }
        elif method.upper() in ["PUT", "PATCH"]:
            return {
                "name": f"Updated Sample {random.randint(1, 100)}",
                "description": "Updated description for the sample object.",
                "active": random.choice([True, False]),
                "updated_at": datetime.now().isoformat(),
            }

        return {}

    def _generate_phone(self) -> str:
        """Generate a realistic phone number."""
        area = random.randint(200, 999)
        prefix = random.randint(200, 999)
        line = random.randint(1000, 9999)
        format_template = random.choice(self.phone_formats)
        return format_template.format(area=area, prefix=prefix, line=line)

    def _generate_date(self, start_year: int, end_year: int) -> str:
        """Generate a random date between start_year and end_year."""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date.strftime("%Y-%m-%d")

    def _generate_future_date(self, min_days: int, max_days: int) -> str:
        """Generate a future date between min_days and max_days from now."""
        days_ahead = random.randint(min_days, max_days)
        future_date = datetime.now() + timedelta(days=days_ahead)
        return future_date.strftime("%Y-%m-%d")

    def generate_sample_value_for_param(self, param: Dict[str, str]) -> str:
        """Generate a sample value for a URL parameter."""
        param_name = param.get("name", "").lower()
        param_type = param.get("type", "string")

        # Generate based on parameter name
        if "id" in param_name or "pk" in param_name:
            return str(random.randint(1, 9999))
        elif "uuid" in param_name:
            return str(uuid.uuid4())
        elif "email" in param_name:
            return random.choice(self.emails)
        elif "name" in param_name:
            return random.choice(self.names)
        elif "slug" in param_name:
            return f"sample-{param_name}-{random.randint(1, 100)}"
        elif "date" in param_name:
            return self._generate_date(2020, 2024)
        elif "count" in param_name or "limit" in param_name:
            return str(random.randint(1, 100))
        elif "page" in param_name:
            return str(random.randint(1, 10))

        # Generate based on parameter type
        if param_type == "integer":
            return str(random.randint(1, 1000))
        elif param_type == "string":
            return f"sample_{param_name}_{random.randint(1, 100)}"
        elif param_type == "uuid":
            return str(uuid.uuid4())
        elif param_type == "email":
            return random.choice(self.emails)
        elif param_type == "date":
            return self._generate_date(2020, 2024)

        # Default fallback
        return f"sample_{param_name}"


# Global instance for easy access
data_factory = DataFactory()
