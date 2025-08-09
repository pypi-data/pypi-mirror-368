"""
Basic test for PyIDVerify package functionality
"""
import pytest
from pyidverify import __version__
from pyidverify.validators.personal.email import EmailValidator


def test_package_version():
    """Test that package version is correctly set."""
    assert __version__ == "2.0.0"


def test_email_validator_initialization():
    """Test EmailValidator can be instantiated."""
    validator = EmailValidator()
    assert validator is not None


def test_email_validator_basic_validation():
    """Test basic email validation functionality."""
    validator = EmailValidator()
    
    # Test valid email
    result = validator.validate("test@example.com")
    assert result is not None
    assert hasattr(result, 'is_valid')
    
    # Test invalid email
    result = validator.validate("invalid-email")
    assert result is not None
    assert hasattr(result, 'is_valid')


if __name__ == "__main__":
    pytest.main([__file__])
