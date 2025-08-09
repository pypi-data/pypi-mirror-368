"""TestAPIX Test Data Generators Module.

This module provides intelligent test data generation for API testing. Good test
data is crucial for effective testing - it needs to be:

1. Realistic: Data that looks like real user input finds real bugs
2. Varied: Different patterns expose different issues
3. Contextual: Email fields get emails, not random strings
4. Reproducible: Consistent data for debugging failures

The generators use the Mimesis library to create contextually appropriate data.
This means when you ask for a user's email, you get "john.smith@example.com"
not "abc123xyz". This realism helps find bugs related to data validation,
formatting, and business logic that random strings would miss.

Example usage:
    from testapix.generators import BaseGenerator

    generator = BaseGenerator()
    user_data = generator.generate_user_data()
    # Returns: {
    #     "email": "sarah.johnson@example.com",
    #     "name": "Sarah Johnson",
    #     "phone": "+1-555-234-5678",
    #     ...
    # }

The generator system is designed to be extended for domain-specific needs
while providing sensible defaults out of the box.
"""

from testapix.generators.base import BaseGenerator, DataGenerationError

# Export main interfaces
__all__ = ["BaseGenerator", "DataGenerationError"]

# Module version
__version__ = "0.1.0"
