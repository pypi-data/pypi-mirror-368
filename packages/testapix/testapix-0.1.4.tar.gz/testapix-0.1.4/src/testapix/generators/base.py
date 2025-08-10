"""Base Test Data Generator Implementation.

This module provides the foundation for generating realistic test data using
the Mimesis library. The philosophy behind this design is that test data should
mirror real-world usage patterns as closely as possible.

Why realistic test data matters:
1. Validation Logic: APIs often validate that emails look like emails, phones
   like phones, etc. Random strings won't trigger these validations.
2. Business Logic: Many bugs hide in business logic that only triggers with
   realistic data patterns (e.g., timezone handling, currency calculations).
3. Edge Cases: Real data has edge cases (long names, special characters) that
   random generation might miss.
4. Debugging: When a test fails, realistic data makes it easier to understand
   what went wrong and reproduce the issue.

The generator provides both general-purpose methods and specific generators
for common data types, all producing contextually appropriate data.
"""

import random
import string
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, cast

from mimesis import Address, Code, Datetime, Finance, Internet, Numeric, Person, Text
from mimesis.enums import EANFormat, Gender
from mimesis.locales import Locale


def _safe_int(val: int | str | float | None) -> int:
    """Safely cast a value to int, defaulting to 0 if not possible."""
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    if isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            return 0
    return 0


class DataGenerationError(Exception):
    """Custom exception for errors during test data generation."""

    pass


class FakeDataWrapper:
    """Convenience wrapper for common fake data generation methods."""

    def __init__(self, generator: "BaseGenerator") -> None:
        """Initialize wrapper with generator instance."""
        self.generator = generator

    def email(self) -> str:
        """Generate a fake email address."""
        return str(self.generator.person.email())

    def name(self) -> str:
        """Generate a fake full name."""
        return str(self.generator.person.full_name())

    def first_name(self) -> str:
        """Generate a fake first name."""
        return str(self.generator.person.first_name())

    def last_name(self) -> str:
        """Generate a fake last name."""
        return str(self.generator.person.last_name())

    def phone(self) -> str:
        """Generate a fake phone number."""
        return str(self.generator.person.phone_number())

    def company(self) -> str:
        """Generate a fake company name."""
        return str(self.generator.finance.company())

    def text(self, max_nb_chars: int = 200) -> str:
        """Generate fake text up to specified character limit."""
        result = ""
        while len(result) < max_nb_chars:
            result += self.generator.text.sentence() + " "
        return result[:max_nb_chars].strip()

    def uuid(self) -> str:
        """Generate a fake UUID string."""
        return str(uuid.uuid4())

    def boolean(self) -> bool:
        """Generate a random boolean value."""
        return random.choice([True, False])

    def url(self) -> str:
        """Generate a fake URL."""
        return str(self.generator.internet.url())

    def uuid4(self) -> str:
        """Generate a fake UUID string (alias for uuid)."""
        return self.uuid()

    def random_int(self, min_val: int = 1, max_val: int = 1000) -> int:
        """Generate a random integer."""
        return random.randint(min_val, max_val)

    def city(self) -> str:
        """Generate a fake city name."""
        return str(self.generator.address.city())


class BaseGenerator:
    """Base test data generator providing realistic data for API testing.

    This generator uses Mimesis to create contextually appropriate fake data
    that follows real-world patterns. It's designed to be extended for
    domain-specific needs while providing comprehensive defaults.

    The generator supports:
    - Localization: Generate data appropriate for different locales
    - Consistency: Seed support for reproducible data
    - Relationships: Generate related data (e.g., user and their orders)
    - Edge cases: Methods for generating boundary and special case data
    - Invalid data: Intentionally malformed data for negative testing
    """

    def __init__(self, locale: Locale = Locale.EN, seed: int | None = None):
        """Initialize the generator with specified locale and optional seed.

        Args:
        ----
            locale: Locale for generating localized data (names, addresses, etc.)
            seed: Random seed for reproducible data generation

        """
        # Set random seed if provided for reproducibility
        if seed is not None:
            random.seed(seed)

        # Initialize Mimesis providers
        self.person = Person(locale, seed=seed)
        self.text = Text(locale, seed=seed)
        self.internet = Internet(seed=seed)
        self.datetime = Datetime(locale, seed=seed)
        self.address = Address(locale, seed=seed)
        self.finance = Finance(locale, seed=seed)
        self.code = Code(seed=seed)
        self.numeric = Numeric(seed=seed)

        self.locale = locale
        self.seed = seed

        # Create convenience wrapper for common operations
        self.fake = self._create_fake_wrapper()

    def _create_fake_wrapper(self) -> FakeDataWrapper:
        """Create a convenience wrapper for common data generation methods.

        Provides simple access to common data generation methods,
        similar to other popular fake data libraries.
        """
        return FakeDataWrapper(self)

    # User Data Generation

    def generate_user_data(self, **override: Any) -> dict[str, Any]:
        """Generate comprehensive user data with realistic values.

        This method creates a complete user profile with all common fields
        populated with contextually appropriate data. The generated data
        includes proper formatting for emails, phones, addresses, etc.

        Args:
        ----
            **overrides: Specific fields to override with custom values

        Returns:
        -------
            Dictionary containing realistic user data

        Example:
        -------
            user = generator.generate_user_data(role="admin")
            # Returns complete user data with role set to "admin"

        """
        # Generate consistent gender for name generation
        gender = random.choice([Gender.MALE, Gender.FEMALE])

        # Generate basic user information
        first_name = self.person.first_name(gender=gender)
        last_name = self.person.last_name()

        # Create username from name (lowercase, no spaces)
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
        username = username.replace(" ", "").replace("'", "")

        # Generate age and birth date
        age = random.randint(18, 80)
        birth_date = datetime.now() - timedelta(days=age * 365 + random.randint(0, 365))

        data = {
            # Basic information
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "username": username,
            "email": f"{username}@{self.internet.hostname()}",
            # Personal details
            "phone": self.person.phone_number(),
            "mobile": self.person.phone_number(),  # Some APIs distinguish these
            "birth_date": birth_date.date().isoformat(),
            "age": age,
            "gender": gender.value.lower(),
            # Address information
            "address": {
                "street": self.address.street_name(),
                "street_number": self.address.street_number(),
                "city": self.address.city(),
                "state": self.address.state(),
                "postal_code": self.address.postal_code(),
                "country": self.address.country(),
                "country_code": self.address.country_code(),
                "latitude": float(self.address.latitude()),
                "longitude": float(self.address.longitude()),
            },
            # Profile information
            "bio": self.text.text(quantity=2),  # 2 sentences
            "website": self.internet.url(),
            "avatar_url": f"https://api.example.com/avatars/{username}.jpg",
            "locale": self.locale.value,
            "timezone": random.choice(
                [
                    "America/New_York",
                    "America/Los_Angeles",
                    "Europe/London",
                    "Europe/Paris",
                    "Asia/Tokyo",
                    "Australia/Sydney",
                ]
            ),
            # Account metadata
            "role": "user",  # Default role
            "status": "active",
            "email_verified": random.choice([True, True, True, False]),  # 75% verified
            "phone_verified": random.choice([True, False]),
            "two_factor_enabled": random.choice([True, False, False]),  # 33% enabled
            # Timestamps
            "created_at": self._generate_past_datetime(days=365).isoformat(),
            "updated_at": self._generate_past_datetime(days=30).isoformat(),
            "last_login": self._generate_past_datetime(days=7).isoformat(),
            # Preferences (common user settings)
            "preferences": {
                "notifications": {
                    "email": True,
                    "sms": random.choice([True, False]),
                    "push": random.choice([True, False]),
                },
                "privacy": {
                    "profile_visible": True,
                    "email_visible": False,
                    "phone_visible": False,
                },
                "theme": random.choice(["light", "dark", "auto"]),
                "language": self.locale.value,
            },
        }

        # Apply any overrides
        self._deep_update(data, override)
        return data

    # Product/Item Data Generation

    def generate_product_data(self, **overrides: Any) -> dict[str, Any]:
        """Generate realistic product/item data for e-commerce or inventory APIs.

        Creates complete product information including pricing, inventory,
        descriptions, and metadata that mirrors real product data.

        Args:
        ----
            **overrides: Specific fields to override

        Returns:
        -------
            Dictionary containing product data

        """
        # Generate product categorization
        categories = [
            ("Electronics", ["Smartphones", "Laptops", "Tablets", "Accessories"]),
            ("Clothing", ["Men's", "Women's", "Kids", "Shoes"]),
            ("Home & Garden", ["Furniture", "Decor", "Kitchen", "Garden"]),
            ("Books", ["Fiction", "Non-fiction", "Technical", "Children's"]),
            ("Sports", ["Equipment", "Apparel", "Footwear", "Accessories"]),
        ]

        main_category, subcategories = random.choice(categories)
        subcategory = random.choice(subcategories)

        # Generate product name based on category
        product_words = self.text.words(quantity=random.randint(2, 4))
        product_name = " ".join(word.title() for word in product_words)

        # Generate SKU
        sku = f"{main_category[:3].upper()}-{self.code.pin(mask='####-####')}"

        # Generate pricing
        base_price = Decimal(str(random.uniform(9.99, 999.99))).quantize(
            Decimal("0.01")
        )
        discount_percent = random.choice(
            [0, 0, 0, 10, 15, 20, 25, 30]
        )  # Most items not on sale

        data = {
            # Basic information
            "name": product_name,
            "slug": product_name.lower().replace(" ", "-"),
            "sku": sku,
            "barcode": self.code.ean(fmt=EANFormat.EAN13),
            # Categorization
            "category": main_category,
            "subcategory": subcategory,
            "tags": self._generate_product_tags(main_category),
            # Description and details
            "description": self.text.text(quantity=3),
            "short_description": self.text.text(quantity=1),
            "features": [self.text.sentence() for _ in range(random.randint(3, 6))],
            # Pricing
            "price": float(base_price),
            "currency": "USD",
            "discount_percent": discount_percent,
            "sale_price": (
                float(base_price * Decimal(1 - discount_percent / 100))
                if discount_percent > 0
                else None
            ),
            "tax_rate": 0.08,  # 8% tax
            # Inventory
            "in_stock": random.choice([True, True, True, False]),  # 75% in stock
            "stock_quantity": random.randint(0, 1000) if random.random() > 0.25 else 0,
            "low_stock_threshold": 10,
            "backorder_allowed": random.choice([True, False]),
            # Physical properties
            "weight": round(random.uniform(0.1, 50.0), 2),
            "weight_unit": "kg",
            "dimensions": {
                "length": round(random.uniform(5, 100), 1),
                "width": round(random.uniform(5, 100), 1),
                "height": round(random.uniform(5, 50), 1),
                "unit": "cm",
            },
            # Images
            "images": [
                {
                    "url": f"https://api.example.com/products/{sku}/image-{i}.jpg",
                    "alt_text": f"{product_name} - Image {i}",
                    "is_primary": i == 0,
                }
                for i in range(random.randint(1, 5))
            ],
            # Ratings and reviews
            "rating": round(random.uniform(3.0, 5.0), 1),
            "review_count": random.randint(0, 500),
            # Metadata
            "brand": self.finance.company(),
            "manufacturer": self.finance.company(),
            "model": self.code.pin(mask="XX-####"),
            "status": random.choice(
                ["active", "active", "active", "discontinued", "coming_soon"]
            ),
            "visibility": random.choice(["public", "public", "public", "private"]),
            # Timestamps
            "created_at": self._generate_past_datetime(days=730).isoformat(),
            "updated_at": self._generate_past_datetime(days=7).isoformat(),
            "published_at": self._generate_past_datetime(days=365).isoformat(),
        }

        self._deep_update(data, overrides)
        return data

    # Order/Transaction Data Generation

    def generate_order_data(
        self, user_id: str | None = None, **overrides: Any
    ) -> dict[str, Any]:
        """Generate realistic order/transaction data.

        Creates complete order information including items, pricing, shipping,
        and payment details that mirror real e-commerce transactions.

        Args:
        ----
            user_id: Optional user ID to associate with order
            **overrides: Specific fields to override

        Returns:
        -------
            Dictionary containing order data

        """
        # Generate order ID
        order_id = f"ORD-{self.code.pin(mask='########')}"

        # Generate order items
        num_items = random.randint(1, 5)
        items: list[dict[str, object]] = []
        subtotal = Decimal("0")

        for i in range(num_items):
            quantity = random.randint(1, 3)
            unit_price = Decimal(str(random.uniform(9.99, 199.99))).quantize(
                Decimal("0.01")
            )
            line_total = unit_price * quantity

            item = {
                "id": str(uuid.uuid4()),
                "product_id": str(uuid.uuid4()),
                "product_name": " ".join(self.text.words(quantity=3)).title(),
                "sku": f"SKU-{self.code.pin(mask='####')}",
                "quantity": quantity,
                "unit_price": float(unit_price),
                "line_total": float(line_total),
                "discount": 0.0,
                "tax": float(line_total * Decimal("0.08")),  # 8% tax
            }
            items.append(item)
            subtotal += line_total

        # Calculate totals
        tax_rate = Decimal("0.08")
        shipping_fee = Decimal("9.99") if subtotal < 50 else Decimal("0")
        tax_amount = (subtotal + shipping_fee) * tax_rate
        total = subtotal + shipping_fee + tax_amount

        # Generate shipping address
        shipping_address = {
            "recipient_name": self.person.full_name(),
            "street": f"{self.address.street_number()} {self.address.street_name()}",
            "street2": random.choice(["", "", f"Apt {random.randint(1, 500)}"]),
            "city": self.address.city(),
            "state": self.address.state(),
            "postal_code": self.address.postal_code(),
            "country": self.address.country(),
            "country_code": self.address.country_code(),
            "phone": self.person.phone_number(),
        }

        # Order status progression
        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        status = random.choice(statuses)

        data = {
            # Order identification
            "id": order_id,
            "order_number": order_id,
            "user_id": user_id or str(uuid.uuid4()),
            # Items
            "items": items,
            "item_count": sum(
                _safe_int(cast(int | str | float | None, item["quantity"]))
                for item in items
            ),
            # Pricing
            "subtotal": float(subtotal),
            "shipping_fee": float(shipping_fee),
            "tax_amount": float(tax_amount),
            "tax_rate": float(tax_rate),
            "discount_amount": 0.0,
            "total": float(total),
            "currency": "USD",
            # Shipping
            "shipping_address": shipping_address,
            "billing_address": shipping_address,
            "shipping_method": random.choice(["standard", "express", "overnight"]),
            "tracking_number": (
                f"1Z{self.code.pin(mask='#########')}"
                if status in ["shipped", "delivered"]
                else None
            ),
            # Payment
            "payment_method": {
                "type": random.choice(["credit_card", "debit_card", "paypal"]),
                "last_four": str(random.randint(1000, 9999)),
                "brand": random.choice(["visa", "mastercard", "amex", "discover"]),
            },
            "payment_status": "paid" if status != "cancelled" else "refunded",
            # Status and metadata
            "status": status,
            "notes": random.choice(
                ["", "", "Please leave at door", "Gift wrap requested"]
            ),
            # Timestamps
            "created_at": self._generate_past_datetime(days=30).isoformat(),
            "updated_at": self._generate_past_datetime(days=1).isoformat(),
            "paid_at": (
                self._generate_past_datetime(days=30).isoformat()
                if status != "cancelled"
                else None
            ),
            "shipped_at": (
                self._generate_past_datetime(days=7).isoformat()
                if status in ["shipped", "delivered"]
                else None
            ),
            "delivered_at": (
                self._generate_past_datetime(days=1).isoformat()
                if status == "delivered"
                else None
            ),
        }

        self._deep_update(data, overrides)
        return data

    # API-Specific Data Generation

    def generate_api_key_data(self, **overrides: Any) -> dict[str, Any]:
        """Generate API key/token data for authentication testing.

        Creates realistic API credential data including scopes, rate limits,
        and metadata commonly found in API key management systems.
        """
        key_id = f"key_{self.code.pin(mask='###################')}"

        data = {
            "id": key_id,
            "key": f"sk_{''.join(random.choices(string.ascii_letters + string.digits, k=32))}",
            "name": f"{self.text.word().title()} API Key",
            "description": f"API key for {self.text.word()} integration",
            # Permissions
            "scopes": random.sample(
                [
                    "read:users",
                    "write:users",
                    "read:orders",
                    "write:orders",
                    "read:products",
                    "write:products",
                    "admin:all",
                    "analytics:read",
                ],
                random.randint(1, 4),
            ),
            # Rate limiting
            "rate_limit": random.choice([100, 1000, 5000, 10000]),
            "rate_limit_window": "hour",
        }
        self._deep_update(data, overrides)
        return data

    def generate_edge_case_data(self, data_type: str, edge_case: str) -> dict[str, Any]:
        """Generate edge case data for boundary testing.

        This generates valid but boundary-case data that often reveals bugs
        in API validation, business logic, and data handling.

        Args:
        ----
            data_type: Type of data to generate (user, product, order)
            edge_case: Specific edge case (max_length, unicode, numeric_edge, etc.)

        Returns:
        -------
            Dictionary containing edge case data

        """
        if data_type == "user":
            if edge_case == "max_length":
                return {
                    "first_name": "A" * 255,  # Very long name
                    "last_name": "B" * 255,
                    "email": f"{'a' * 240}@example.com",  # Near email limit
                    "phone": "+1" + "9" * 18,  # Maximum phone length
                    "bio": "Long bio content. " * 200,  # Very long bio
                    "username": "user" + "x" * 60,  # Long username
                    "address": {
                        "street": "Very Long Street Name That Goes On And On" * 5,
                        "city": "Supercalifragilisticexpialidocious" * 3,
                    },
                }
            elif edge_case == "unicode":
                return {
                    "first_name": "José María",  # Accented characters
                    "last_name": "李小明",  # Chinese characters
                    "email": "tëst.用户@example.com",  # Unicode in email
                    "bio": "🚀 User with emojis 🎉 and unicode ñäñö",
                    "address": {
                        "street": "Rue de la Résistance",
                        "city": "北京市",  # Beijing in Chinese
                        "country": "España",
                    },
                }
            elif edge_case == "minimal":
                return {
                    "first_name": "A",  # Single character
                    "last_name": "B",
                    "email": "a@b.co",  # Minimal valid email
                    "phone": "+15551234567",  # Minimal phone
                    "age": 18,  # Minimum age
                    "bio": "",  # Empty optional field
                }
            elif edge_case == "special_chars":
                return {
                    "first_name": "John-Paul",  # Hyphenated name
                    "last_name": "O'Connor",  # Apostrophe
                    "email": "user+tag@sub.example.com",  # Plus and subdomain
                    "username": "user_name.123",  # Mixed characters
                    "bio": "Bio with \"quotes\" and 'apostrophes' & ampersands",
                    "address": {
                        "street": "123 1/2 Main St., Apt. #4B",  # Complex address
                        "postal_code": "12345-6789",  # Extended zip
                    },
                }

        elif data_type == "product":
            product_cases = {
                "max_price": {
                    "name": "Luxury Item",
                    "price": 999999.99,  # Very high price
                    "stock_quantity": 999999,  # Very high stock
                    "weight": 1000.00,  # Heavy item
                    "dimensions": {"length": 999.9, "width": 999.9, "height": 999.9},
                },
                "min_price": {
                    "name": "Free Sample",
                    "price": 0.01,  # Minimum price
                    "stock_quantity": 1,  # Single item
                    "weight": 0.1,  # Very light
                    "dimensions": {"length": 0.1, "width": 0.1, "height": 0.1},
                },
                "precision": {
                    "name": "Precision Test Item",
                    "price": 19.999,  # 3 decimal places
                    "weight": 1.23456789,  # High precision
                    "tax_rate": 0.08675,  # Complex tax rate
                    "discount_percent": 12.5,  # Half percent
                },
            }
            if edge_case in product_cases:
                return product_cases[edge_case]

        elif data_type == "order":
            if edge_case == "large_order":
                # Generate order with many items
                items = []
                for i in range(100):  # Large number of items
                    items.append(
                        {
                            "id": str(uuid.uuid4()),
                            "product_name": f"Product {i + 1}",
                            "quantity": 1,
                            "unit_price": 1.00,
                            "line_total": 1.00,
                        }
                    )
                return {
                    "items": items,
                    "item_count": 100,
                    "subtotal": 100.00,
                    "total": 108.00,  # With tax
                }
            elif edge_case == "high_value":
                return {
                    "items": [
                        {
                            "id": str(uuid.uuid4()),
                            "product_name": "Expensive Item",
                            "quantity": 1,
                            "unit_price": 50000.00,
                            "line_total": 50000.00,
                        }
                    ],
                    "subtotal": 50000.00,
                    "total": 54000.00,  # Very high total
                    "currency": "USD",
                }

        # Default case - return minimal valid data
        return {"edge_case": edge_case, "data_type": data_type}

    def generate_invalid_data(self, data_type: str) -> dict[str, Any]:
        """Generate intentionally invalid data for negative testing.

        This helps test error handling and validation logic by providing
        data that should be rejected by the API.

        Args:
        ----
            data_type: Type of invalid data to generate

        Returns:
        -------
            Dictionary containing invalid data

        """
        if data_type == "user":
            return {
                "email": random.choice(
                    [
                        "not-an-email",
                        "@example.com",
                        "user@",
                        "user..name@example.com",
                        "user name@example.com",  # Space in email
                        "user@domain@com",  # Multiple @
                        "user@.com",  # Starts with dot
                        "user@domain.",  # Ends with dot
                        "a" * 300 + "@example.com",  # Too long
                        "",  # Empty email
                        None,  # Null email
                    ]
                ),
                "username": random.choice(
                    [
                        "",  # Empty
                        "a",  # Too short
                        "user name",  # Contains space
                        "user@name",  # Contains @
                        "123",  # Only numbers
                        "🚀emoji",  # Starts with emoji
                        "user/name",  # Contains slash
                        "user\nname",  # Contains newline
                        "a" * 100,  # Too long
                        None,  # Null
                        123,  # Wrong type
                    ]
                ),
                "phone": random.choice(
                    [
                        "not-a-phone",
                        "123",  # Too short
                        "+1234567890123456789",  # Too long
                        "555-CALL-NOW",  # Letters
                        "++15551234567",  # Double plus
                        "1-800-FLOWERS",  # Text number
                        "",  # Empty
                        None,  # Null
                        123456789,  # Wrong type (int)
                    ]
                ),
                "age": random.choice(
                    [
                        -5,  # Negative
                        0,  # Zero age
                        150,  # Too old
                        "twenty",  # String instead of number
                        3.14,  # Float instead of int
                        None,  # Null
                        float("inf"),  # Infinity
                        float("nan"),  # NaN
                    ]
                ),
                "birth_date": random.choice(
                    [
                        "invalid-date",
                        "2099-01-01",  # Future date
                        "32/13/2020",  # Invalid format
                        "2020-13-01",  # Invalid month
                        "2020-01-32",  # Invalid day
                        "1800-01-01",  # Too old
                        "",  # Empty
                        None,  # Null
                        "2020/01/01T10:30:00",  # Wrong format
                        123456789,  # Wrong type
                    ]
                ),
                "first_name": random.choice(
                    [
                        "",  # Empty required field
                        None,  # Null
                        123,  # Wrong type
                        "a" * 500,  # Too long
                        "\n\t",  # Whitespace only
                        "<script>",  # Potential XSS
                    ]
                ),
                "last_name": random.choice(
                    [
                        "",  # Empty required field
                        None,  # Null
                        [],  # Wrong type
                        "SELECT * FROM users",  # SQL injection attempt
                    ]
                ),
            }

        elif data_type == "product":
            return {
                "name": random.choice(
                    [
                        "",  # Empty required field
                        None,  # Null
                        123,  # Wrong type
                        "a" * 1000,  # Too long
                        "\n\t  ",  # Whitespace only
                        "<script>alert('xss')</script>",  # XSS attempt
                        "'; DROP TABLE products;--",  # SQL injection
                    ]
                ),
                "price": random.choice(
                    [
                        -10.99,  # Negative price
                        0,  # Zero price
                        "free",  # String instead of number
                        float("inf"),  # Infinity
                        float("nan"),  # NaN
                        None,  # Null
                        [],  # Wrong type
                        "99.99.99",  # Invalid decimal
                        1e100,  # Extremely large number
                    ]
                ),
                "stock_quantity": random.choice(
                    [
                        -5,  # Negative stock
                        "unlimited",  # String instead of number
                        1.5,  # Fractional quantity
                        None,  # Null
                        float("inf"),  # Infinity
                        {},  # Wrong type
                        "1,000",  # Formatted number
                    ]
                ),
                "sku": random.choice(
                    [
                        "",  # Empty
                        None,  # Null
                        "SKU WITH SPACES",  # Invalid format
                        "sku@#$%",  # Special characters
                        "sku\nwith\nnewlines",  # Contains newlines
                        "a" * 200,  # Too long
                        123,  # Wrong type
                        "SKU/with/slashes",  # Invalid chars
                    ]
                ),
                "category": random.choice(
                    [
                        "nonexistent_category",
                        "",  # Empty
                        None,  # Null
                        123,  # Wrong type
                        [],  # Wrong type
                        "category\nwith\nnewlines",
                        "a" * 500,  # Too long
                    ]
                ),
                "weight": random.choice(
                    [
                        -1.5,  # Negative weight
                        0,  # Zero weight (might be invalid)
                        "heavy",  # String instead of number
                        None,  # Null
                        float("inf"),  # Infinity
                        float("nan"),  # NaN
                        [],  # Wrong type
                        "1.5kg",  # With units
                    ]
                ),
                "dimensions": random.choice(
                    [
                        "10x5x2",  # String instead of object
                        [],  # Array instead of object
                        None,  # Null
                        {
                            "length": -5,  # Negative dimension
                            "width": "wide",  # String instead of number
                            "height": None,  # Null dimension
                        },
                        {"invalid": "dimensions"},  # Missing required fields
                    ]
                ),
            }

        elif data_type == "order":
            return {
                "items": random.choice(
                    [
                        [],  # Empty items
                        "not-an-array",  # Wrong type
                        None,  # Null
                        [{"quantity": 0}],  # Zero quantity
                        [{"quantity": -1}],  # Negative quantity
                        [{"quantity": "two"}],  # String quantity
                        [{"quantity": float("inf")}],  # Infinite quantity
                        [{}],  # Empty item object
                        ["not-an-object"],  # Non-object in array
                        [
                            {
                                "quantity": 1,
                                "unit_price": -50.00,  # Negative price
                                "product_id": None,  # Null product ID
                            }
                        ],
                    ]
                ),
                "total": random.choice(
                    [
                        -100.00,  # Negative total
                        0,  # Zero total
                        "one hundred",  # String
                        None,  # Null
                        float("inf"),  # Infinity
                        float("nan"),  # NaN
                        [],  # Wrong type
                        "$100.00",  # With currency symbol
                        "100.00.00",  # Invalid decimal
                    ]
                ),
                "user_id": random.choice(
                    [
                        "",  # Empty
                        "invalid-uuid",  # Not a UUID
                        123,  # Wrong type
                        None,  # Null
                        [],  # Wrong type
                        "user-id-with-too-many-characters-" + "x" * 100,  # Too long
                        "user\nwith\nnewlines",  # Invalid characters
                    ]
                ),
                "status": random.choice(
                    [
                        "invalid_status",
                        "",  # Empty
                        None,  # Null
                        123,  # Wrong type
                        "status with spaces",  # Invalid format
                        "UPPERCASE_STATUS",  # Wrong case
                        "status\nwith\nnewlines",  # Invalid characters
                    ]
                ),
                "shipping_address": random.choice(
                    [
                        {},  # Empty object
                        "123 Main St",  # String instead of object
                        None,  # Null
                        [],  # Array instead of object
                        {
                            "street": None,  # Null required field
                            "city": 123,  # Wrong type
                            "postal_code": "INVALID-ZIP-FORMAT",
                        },
                        {"invalid_field": "value"},  # Missing required fields
                    ]
                ),
                "payment_method": random.choice(
                    [
                        "cash",  # Invalid payment method
                        "",  # Empty
                        None,  # Null
                        123,  # Wrong type
                        {"type": "invalid_type"},  # Invalid nested type
                        [],  # Wrong type
                    ]
                ),
            }

        elif data_type == "xss":
            # Cross-Site Scripting payloads for security testing
            return {
                "malicious_script": random.choice(
                    [
                        "<script>alert('XSS')</script>",
                        "<img src=x onerror=alert('XSS')>",
                        "javascript:alert('XSS')",
                        "<svg onload=alert('XSS')>",
                        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
                        "<body onload=alert('XSS')>",
                        "<input onfocus=alert('XSS') autofocus>",
                        "<select onfocus=alert('XSS') autofocus>",
                    ]
                ),
                "script_in_attribute": 'value" onmouseover="alert(\'XSS\')" "',
                "encoded_script": "%3Cscript%3Ealert('XSS')%3C/script%3E",
                "nested_script": "<div><script>alert('XSS')</script></div>",
            }

        elif data_type == "sql_injection":
            # SQL injection payloads for security testing
            return {
                "union_attack": random.choice(
                    [
                        "' UNION SELECT username, password FROM users--",
                        "1' OR '1'='1",
                        "'; DROP TABLE users; --",
                        "admin'--",
                        "' OR 1=1--",
                        "1'; DELETE FROM products; --",
                        "' UNION SELECT 1,2,3,4,5--",
                    ]
                ),
                "boolean_injection": "1' AND '1'='1",
                "time_based": "1'; WAITFOR DELAY '00:00:10'--",
                "comment_injection": "admin'/*",
                "stacked_queries": "1'; INSERT INTO logs VALUES('hacked'); --",
            }

        elif data_type == "path_traversal":
            # Path traversal payloads for security testing
            return {
                "directory_traversal": random.choice(
                    [
                        "../../../etc/passwd",
                        "..\\..\\..\\windows\\system32\\config\\sam",
                        "....//....//....//etc/passwd",
                        "..%2F..%2F..%2Fetc%2Fpasswd",
                        "..%252f..%252f..%252fetc%252fpasswd",
                        "../../../../../../etc/shadow",
                    ]
                ),
                "null_byte": "../../../etc/passwd%00.txt",
                "unicode_bypass": "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
                "double_encoding": "..%255c..%255c..%255cetc%255cboot.ini",
            }

        elif data_type == "overflow":
            # Buffer overflow payloads for security testing
            long_string = "A" * 10000
            return {
                "buffer_overflow": long_string,
                "format_string": "%s%s%s%s%s%s%s%s%s%s" * 100,
                "extremely_long": "B" * 50000,
                "nested_overflow": {"field": "C" * 20000},
                "array_overflow": ["D" * 1000] * 100,
            }

        elif data_type == "format_attack":
            # Format string attack payloads
            return {
                "format_specifiers": random.choice(
                    [
                        "%x%x%x%x%x%x%x%x%x%x",
                        "%s%s%s%s%s%s%s%s%s%s",
                        "%n%n%n%n%n%n%n%n%n%n",
                        "%08x" * 20,
                        "%p%p%p%p%p%p%p%p",
                    ]
                ),
                "stack_reading": "%08x." * 50,
                "memory_leak": "%s" * 100,
                "write_attack": "%n" * 10,
            }

        else:
            # Generic invalid data
            return {
                "null_field": None,
                "empty_string": "",
                "negative_number": -1,
                "invalid_boolean": "yes",  # String instead of boolean
                "invalid_date": "not-a-date",
                "invalid_array": "not-an-array",
                "invalid_object": "not-an-object",
                "type_mismatch": ["array", "when", "expecting", "string"],
            }

    # Helper Methods

    def _generate_past_datetime(self, days: int = 30, hours: int = 0) -> datetime:
        """Generate a datetime in the past within specified range."""
        total_seconds = (days * 24 * 60 * 60) + (hours * 60 * 60)
        random_seconds = random.randint(0, total_seconds)
        return datetime.now(UTC) - timedelta(seconds=random_seconds)

    def _generate_product_tags(self, category: str) -> list[str]:
        """Generate relevant tags based on product category."""
        common_tags = ["new", "popular", "sale", "featured", "limited"]

        category_tags = {
            "Electronics": [
                "wireless",
                "portable",
                "smart",
                "rechargeable",
                "bluetooth",
            ],
            "Clothing": ["cotton", "comfortable", "stylish", "casual", "formal"],
            "Home & Garden": [
                "modern",
                "durable",
                "eco-friendly",
                "decorative",
                "functional",
            ],
            "Books": [
                "bestseller",
                "educational",
                "entertaining",
                "classic",
                "new-release",
            ],
            "Sports": [
                "professional",
                "beginner-friendly",
                "lightweight",
                "durable",
                "performance",
            ],
        }

        tags = random.sample(common_tags, random.randint(0, 2))
        if category in category_tags:
            tags.extend(random.sample(category_tags[category], random.randint(1, 3)))

        return list(set(tags))  # Remove duplicates

    def _deep_update(self, base: dict[str, Any], updates: dict[str, Any]) -> None:
        """Recursively update nested dictionaries."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    # Convenience Methods for Quick Data Generation

    def email(self) -> str:
        """Generate a random email address."""
        return self.fake.email()

    def name(self) -> str:
        """Generate a random full name."""
        return self.fake.name()

    def phone(self) -> str:
        """Generate a random phone number."""
        return self.fake.phone()

    def uuid(self) -> str:
        """Generate a random UUID."""
        return str(uuid.uuid4())

    def boolean(self) -> bool:
        """Generate a random boolean."""
        return random.choice([True, False])

    def date_between(self, start_date: str, end_date: str) -> str:
        """Generate a random date between two dates.

        Args:
        ----
            start_date: Start date in ISO format
            end_date: End date in ISO format

        Returns:
        -------
            Random date in ISO format

        """
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            if start >= end:
                raise DataGenerationError(
                    f"Start date {start_date} must be before end date {end_date}"
                )

            random_timestamp = random.uniform(start.timestamp(), end.timestamp())
            random_date = datetime.fromtimestamp(random_timestamp, tz=UTC)

            return random_date.date().isoformat()
        except ValueError as e:
            raise DataGenerationError(f"Invalid date format: {e}") from e

    def number_between(
        self, min_value: float, max_value: float, decimals: int = 2
    ) -> float:
        """Generate a random number between min and max with specified decimal places."""
        if min_value >= max_value:
            raise DataGenerationError(
                f"min_value ({min_value}) must be less than max_value ({max_value})"
            )
        if decimals < 0:
            raise DataGenerationError("decimals must be non-negative")

        value = random.uniform(min_value, max_value)
        return round(value, decimals)

    def generate_security_test_data(self, attack_type: str) -> dict[str, Any]:
        """Generate data for security testing.

        This generates potentially malicious payloads to test API security.
        Use with caution and only against systems you own or have permission to test.

        Args:
        ----
            attack_type: Type of security test (xss, sql_injection, path_traversal, etc.)

        Returns:
        -------
            Dictionary containing security test payloads

        """
        security_payloads = {
            "xss": {
                "basic_xss": "<script>alert('XSS')</script>",
                "img_xss": "<img src=x onerror=alert('XSS')>",
                "svg_xss": "<svg onload=alert('XSS')>",
                "encoded_xss": "%3Cscript%3Ealert('XSS')%3C/script%3E",
                "js_event": "onclick=alert('XSS')",
                "iframe_xss": "<iframe src=javascript:alert('XSS')></iframe>",
            },
            "sql_injection": {
                "basic_sqli": "'; DROP TABLE users;--",
                "union_sqli": "' UNION SELECT * FROM users--",
                "boolean_sqli": "' OR '1'='1",
                "time_sqli": "'; WAITFOR DELAY '00:00:05'--",
                "error_sqli": "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
                "comment_sqli": "/* comment */ SELECT * FROM users",
            },
            "path_traversal": {
                "basic_traversal": "../../../etc/passwd",
                "encoded_traversal": "..%2F..%2F..%2Fetc%2Fpasswd",
                "double_encoded": "..%252F..%252F..%252Fetc%252Fpasswd",
                "windows_traversal": "..\\..\\..\\windows\\system32\\config\\sam",
                "null_byte": "../../../etc/passwd%00",
                "url_encoded": "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            },
            "command_injection": {
                "basic_cmd": "; ls -la",
                "pipe_cmd": "| whoami",
                "backtick_cmd": "`whoami`",
                "dollar_cmd": "$(whoami)",
                "and_cmd": "&& cat /etc/passwd",
                "or_cmd": "|| ping -c 4 127.0.0.1",
            },
            "ldap_injection": {
                "basic_ldap": "*)(uid=*))(|(uid=*",
                "bypass_ldap": "admin)(&(password=*)",
                "wildcard_ldap": "*",
                "null_ldap": "%00",
            },
            "header_injection": {
                "crlf_injection": "value\r\nX-Injected-Header: malicious",
                "response_splitting": "value\r\n\r\n<script>alert('XSS')</script>",
                "host_header": "evil.com",
                "x_forwarded": "127.0.0.1\r\nX-Injected: header",
            },
        }

        return security_payloads.get(
            attack_type,
            {
                "generic_payload": f"test_payload_for_{attack_type}",
                "long_string": "A" * 10000,
                "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
                "unicode_chars": "ñáéíóúü测试数据🚀",
                "null_bytes": "\x00\x01\x02\x03",
                "format_strings": "%s%d%x%n",
            },
        )

    def generate_boundary_values(self, data_type: str, field: str = "") -> list[Any]:
        """Generate boundary values for specific field types.

        Args:
        ----
            data_type: Type of data (integer, string, date, etc.)
            field: Specific field name for context (currently unused but reserved for future field-specific logic)

        Returns:
        -------
            List of boundary values to test

        """
        # Note: field parameter reserved for future field-specific boundary logic
        _ = field  # Acknowledge parameter to avoid unused warning

        boundary_values: dict[str, list[Any]] = {
            "integer": [
                -2147483648,  # 32-bit int min
                -1,  # Negative boundary
                0,  # Zero
                1,  # Positive boundary
                2147483647,  # 32-bit int max
                9223372036854775807,  # 64-bit int max
            ],
            "string": [
                "",  # Empty string
                "a",  # Single character
                "A" * 255,  # Common max length
                "A" * 256,  # Just over common max
                "A" * 1000,  # Very long
                "A" * 65535,  # 16-bit max
                "🚀",  # Unicode emoji
                "テスト",  # Multi-byte unicode
                "\n\r\t",  # Whitespace characters
            ],
            "email": [
                "a@b.co",  # Minimal valid
                "user@example.com",  # Standard
                "user+tag@example.com",  # With tag
                f"{'a' * 64}@example.com",  # Max local part
                f"user@{'a' * 253}.com",  # Max domain
                "user@sub.domain.example.com",  # Subdomain
            ],
            "price": [
                0.01,  # Minimum price
                0.99,  # Common low price
                1.00,  # Dollar boundary
                999.99,  # Common high price
                999999.99,  # Very high price
                0.001,  # Sub-cent (might be invalid)
            ],
            "date": [
                "1900-01-01",  # Very old date
                "1970-01-01",  # Unix epoch
                "2000-01-01",  # Y2K
                "2023-02-28",  # Non-leap year Feb
                "2024-02-29",  # Leap year Feb
                "2099-12-31",  # Future date
            ],
        }

        return boundary_values.get(data_type, ["boundary_value_unknown_type"])
