"""Tests for validation_utils module."""

import pytest
from myutils.validation_utils import (
    is_valid_phone, is_valid_url, is_valid_ip, is_numeric,
    has_required_keys, is_in_range, is_not_empty,
    validate_password_strength, is_strong_password
)


class TestPhoneValidation:
    """Test phone number validation."""
    
    def test_is_valid_phone_us_formats(self):
        """Test valid US phone number formats."""
        valid_phones = [
            "+1-555-123-4567",
            "555-123-4567",
            "(555) 123-4567",
            "555.123.4567",
            "15551234567",
            "+15551234567",
            "1-555-123-4567",
            "(555)123-4567",
            "555 123 4567"
        ]
        
        for phone in valid_phones:
            assert is_valid_phone(phone), f"Expected {phone} to be valid"
    
    def test_is_valid_phone_invalid_formats(self):
        """Test invalid phone number formats."""
        invalid_phones = [
            "",
            "123",
            "555-123",
            "555-123-456",
            "555-123-45678",
            "abc-def-ghij",
            "+44-20-7946-0958",  # UK format (not US)
            "555-CALL-NOW",       # Letters
            "555..123..4567",     # Double dots
            "+1-555-123-4567-890" # Too long
        ]
        
        for phone in invalid_phones:
            assert not is_valid_phone(phone), f"Expected {phone} to be invalid"
    
    def test_is_valid_phone_with_whitespace(self):
        """Test phone validation with various whitespace."""
        # Leading/trailing whitespace should be handled
        assert is_valid_phone("  555-123-4567  ")
        assert is_valid_phone("\t555-123-4567\n")
        
        # Internal whitespace variations
        assert is_valid_phone("555 123 4567")
        assert is_valid_phone("(555) 123-4567")


class TestURLValidation:
    """Test URL validation."""
    
    def test_is_valid_url_http_https(self):
        """Test valid HTTP/HTTPS URLs."""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "https://www.example.com",
            "http://subdomain.example.com",
            "https://example.com/path",
            "https://example.com/path/to/resource",
            "https://example.com/path?query=value",
            "https://example.com/path?query=value&other=param",
            "https://example.com/path#fragment",
            "https://example-domain.com",
            "https://example123.com",
            "https://example.co.uk",
            "https://localhost:8080",
            "http://192.168.1.1:3000"
        ]
        
        for url in valid_urls:
            assert is_valid_url(url), f"Expected {url} to be valid"
    
    def test_is_valid_url_invalid_formats(self):
        """Test invalid URL formats."""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://example.com",      # FTP not supported
            "http://",
            "https://",
            "http://.com",
            "https://example",        # No TLD
            "https://example.",       # Incomplete TLD
            "http://exam ple.com",    # Space in domain
            "https://",
            "://example.com",         # No protocol
            "example.com",            # No protocol
            "www.example.com"         # No protocol
        ]
        
        for url in invalid_urls:
            assert not is_valid_url(url), f"Expected {url} to be invalid"
    
    def test_is_valid_url_edge_cases(self):
        """Test URL validation edge cases."""
        # Case sensitivity
        assert is_valid_url("HTTP://EXAMPLE.COM")
        assert is_valid_url("HTTPS://EXAMPLE.COM")
        
        # Port numbers
        assert is_valid_url("https://example.com:443")
        assert is_valid_url("http://example.com:80")
        assert is_valid_url("https://example.com:8443")


class TestIPValidation:
    """Test IP address validation."""
    
    def test_is_valid_ip_valid_addresses(self):
        """Test valid IPv4 addresses."""
        valid_ips = [
            "0.0.0.0",
            "127.0.0.1",
            "192.168.1.1",
            "10.0.0.1",
            "255.255.255.255",
            "1.2.3.4",
            "203.0.113.1",
            "198.51.100.1"
        ]
        
        for ip in valid_ips:
            assert is_valid_ip(ip), f"Expected {ip} to be valid"
    
    def test_is_valid_ip_invalid_addresses(self):
        """Test invalid IPv4 addresses."""
        invalid_ips = [
            "",
            "256.1.1.1",           # Octet too high
            "1.256.1.1",
            "1.1.256.1",
            "1.1.1.256",
            "192.168.1",           # Missing octet
            "192.168.1.1.1",       # Extra octet
            "192.168.01.1",        # Leading zero
            "192.168.-1.1",        # Negative number
            "192.168.1.1.1",       # Too many octets
            "192.168.1",           # Too few octets
            "abc.def.ghi.jkl",     # Non-numeric
            "192.168.1.1/24",      # CIDR notation
            "::1",                 # IPv6
            "2001:db8::1"          # IPv6
        ]
        
        for ip in invalid_ips:
            assert not is_valid_ip(ip), f"Expected {ip} to be invalid"


class TestNumericValidation:
    """Test numeric validation."""
    
    def test_is_numeric_valid_numbers(self):
        """Test valid numeric strings."""
        valid_numbers = [
            "123",
            "0",
            "-123",
            "3.14159",
            "-3.14159",
            "0.0",
            "1000000",
            "1e10",
            "1.5e-3",
            ".5",
            "5."
        ]
        
        for num in valid_numbers:
            assert is_numeric(num), f"Expected {num} to be numeric"
    
    def test_is_numeric_invalid_numbers(self):
        """Test invalid numeric strings."""
        invalid_numbers = [
            "",
            "abc",
            "12abc",
            "abc12",
            "12.34.56",
            "1,234",
            "$123",
            "123%",
            "NaN",
            "inf",
            "infinity",
            " ",
            "1 2",
            "1-2"
        ]
        
        for num in invalid_numbers:
            assert not is_numeric(num), f"Expected {num} to be non-numeric"


class TestDataStructureValidation:
    """Test data structure validation."""
    
    def test_has_required_keys_all_present(self):
        """Test has_required_keys with all keys present."""
        data = {
            'name': 'John',
            'email': 'john@example.com',
            'age': 30,
            'active': True
        }
        
        # Single key
        assert has_required_keys(data, ['name'])
        
        # Multiple keys
        assert has_required_keys(data, ['name', 'email'])
        assert has_required_keys(data, ['name', 'email', 'age'])
        assert has_required_keys(data, ['name', 'email', 'age', 'active'])
        
        # Empty required keys list
        assert has_required_keys(data, [])
    
    def test_has_required_keys_missing_keys(self):
        """Test has_required_keys with missing keys."""
        data = {
            'name': 'John',
            'email': 'john@example.com'
        }
        
        # Missing single key
        assert not has_required_keys(data, ['age'])
        
        # Some present, some missing
        assert not has_required_keys(data, ['name', 'age'])
        assert not has_required_keys(data, ['name', 'email', 'age'])
        
        # All missing
        assert not has_required_keys(data, ['missing1', 'missing2'])
    
    def test_has_required_keys_edge_cases(self):
        """Test has_required_keys edge cases."""
        # Empty data
        assert has_required_keys({}, [])
        assert not has_required_keys({}, ['key'])
        
        # Keys with None values (should still be considered present)
        data_with_none = {'key': None}
        assert has_required_keys(data_with_none, ['key'])
        
        # Keys with empty string values
        data_with_empty = {'key': ''}
        assert has_required_keys(data_with_empty, ['key'])


class TestRangeValidation:
    """Test range validation."""
    
    def test_is_in_range_integers(self):
        """Test range validation with integers."""
        # Within range
        assert is_in_range(5, 1, 10)
        assert is_in_range(1, 1, 10)  # At minimum
        assert is_in_range(10, 1, 10)  # At maximum
        
        # Outside range
        assert not is_in_range(0, 1, 10)
        assert not is_in_range(11, 1, 10)
        assert not is_in_range(-5, 1, 10)
    
    def test_is_in_range_floats(self):
        """Test range validation with floats."""
        # Within range
        assert is_in_range(5.5, 1.0, 10.0)
        assert is_in_range(1.0, 1.0, 10.0)
        assert is_in_range(10.0, 1.0, 10.0)
        
        # Outside range
        assert not is_in_range(0.5, 1.0, 10.0)
        assert not is_in_range(10.1, 1.0, 10.0)
    
    def test_is_in_range_mixed_types(self):
        """Test range validation with mixed int/float types."""
        assert is_in_range(5, 1.0, 10.0)
        assert is_in_range(5.0, 1, 10)
        assert is_in_range(5.5, 1, 10)
    
    def test_is_in_range_edge_cases(self):
        """Test range validation edge cases."""
        # Single point range
        assert is_in_range(5, 5, 5)
        assert not is_in_range(4, 5, 5)
        assert not is_in_range(6, 5, 5)
        
        # Negative ranges
        assert is_in_range(-5, -10, -1)
        assert not is_in_range(0, -10, -1)


class TestStringValidation:
    """Test string validation."""
    
    def test_is_not_empty_valid_strings(self):
        """Test is_not_empty with valid strings."""
        valid_strings = [
            "hello",
            "a",
            "123",
            "hello world",
            "\t\tcontent\t\t",  # Has non-whitespace content
        ]
        
        for s in valid_strings:
            assert is_not_empty(s), f"Expected '{s}' to be not empty"
    
    def test_is_not_empty_invalid_strings(self):
        """Test is_not_empty with invalid strings."""
        invalid_strings = [
            "",
            "   ",
            "\t\t",
            "\n\n",
            "\r\n",
            "\t \n \r"
        ]
        
        for s in invalid_strings:
            assert not is_not_empty(s), f"Expected '{s}' to be empty"


class TestPasswordValidation:
    """Test password validation."""
    
    def test_validate_password_strength_criteria(self):
        """Test password strength validation criteria."""
        # Test each criterion individually
        
        # Length criterion
        short_pass = "Ab1!"
        long_pass = "Ab1!5678"
        assert not validate_password_strength(short_pass)['min_length']
        assert validate_password_strength(long_pass)['min_length']
        
        # Uppercase criterion
        no_upper = "ab1!5678"
        with_upper = "Ab1!5678"
        assert not validate_password_strength(no_upper)['has_uppercase']
        assert validate_password_strength(with_upper)['has_uppercase']
        
        # Lowercase criterion
        no_lower = "AB1!5678"
        with_lower = "Ab1!5678"
        assert not validate_password_strength(no_lower)['has_lowercase']
        assert validate_password_strength(with_lower)['has_lowercase']
        
        # Digit criterion
        no_digit = "Ab!bcdef"
        with_digit = "Ab1!5678"
        assert not validate_password_strength(no_digit)['has_digit']
        assert validate_password_strength(with_digit)['has_digit']
        
        # Special character criterion
        no_special = "Ab123456"
        with_special = "Ab1!5678"
        assert not validate_password_strength(no_special)['has_special']
        assert validate_password_strength(with_special)['has_special']
    
    def test_validate_password_strength_combinations(self):
        """Test password strength with various combinations."""
        # Weak passwords (missing multiple criteria)
        weak_passwords = [
            "password",      # No uppercase, digits, or special chars
            "PASSWORD",      # No lowercase, digits, or special chars
            "12345678",      # No letters or special chars
            "Pass123",       # No special chars, might be too short
            "Pass!"          # Too short
        ]
        
        for pwd in weak_passwords:
            strength = validate_password_strength(pwd)
            criteria_met = sum(strength.values())
            assert criteria_met < 5, f"Password '{pwd}' should not meet all criteria"
        
        # Strong passwords (meeting all criteria)
        strong_passwords = [
            "MyP@ssw0rd123",
            "Str0ng!P@ss2024",
            "C0mpl3x_P@ssw0rd",
            "S3cur3#P@ssw0rd!"
        ]
        
        for pwd in strong_passwords:
            strength = validate_password_strength(pwd)
            criteria_met = sum(strength.values())
            assert criteria_met == 5, f"Password '{pwd}' should meet all criteria: {strength}"
    
    def test_is_strong_password(self):
        """Test is_strong_password function."""
        # Strong passwords
        strong_passwords = [
            "MyP@ssw0rd123",
            "Str0ng!P@ss2024",
            "C0mpl3x_P@ssw0rd"
        ]
        
        for pwd in strong_passwords:
            assert is_strong_password(pwd), f"Expected '{pwd}' to be strong"
        
        # Weak passwords
        weak_passwords = [
            "password",
            "Password123",  # No special chars
            "Pass!",        # Too short
            "PASSWORD!123", # No lowercase
            "password!123"  # No uppercase
        ]
        
        for pwd in weak_passwords:
            assert not is_strong_password(pwd), f"Expected '{pwd}' to be weak"
    
    def test_password_validation_special_characters(self):
        """Test password validation with various special characters."""
        special_chars = "!@#$%^&*(),.?\":{}|<>"
        
        for char in special_chars:
            password = f"Passw0rd{char}"
            strength = validate_password_strength(password)
            assert strength['has_special'], f"Character '{char}' should be recognized as special"
            assert is_strong_password(password), f"Password with '{char}' should be strong"


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple validation functions."""
    
    def test_user_registration_validation(self):
        """Test complete user registration validation."""
        user_data = [
            {
                'name': 'John Doe',
                'email': 'john@example.com',
                'phone': '555-123-4567',
                'website': 'https://johndoe.com',
                'age': 30,
                'password': 'MyStr0ng!P@ss'
            },
            {
                'name': '',  # Invalid: empty name
                'email': 'invalid.email',  # Invalid: bad email
                'phone': '555-123',  # Invalid: bad phone
                'website': 'not-a-url',  # Invalid: bad URL
                'age': 150,  # Invalid: age out of range
                'password': 'weak'  # Invalid: weak password
            }
        ]
        
        validation_results = []
        for user in user_data:
            result = {
                'name_valid': is_not_empty(user['name']),
                'phone_valid': is_valid_phone(user['phone']),
                'website_valid': is_valid_url(user['website']),
                'age_valid': is_in_range(user['age'], 18, 120),
                'password_strong': is_strong_password(user['password']),
                'has_required': has_required_keys(user, ['name', 'email', 'phone'])
            }
            validation_results.append(result)
        
        # First user should be valid
        assert all(validation_results[0].values())
        
        # Second user should have validation failures
        assert not validation_results[1]['name_valid']
        assert not validation_results[1]['phone_valid']
        assert not validation_results[1]['website_valid']
        assert not validation_results[1]['age_valid']
        assert not validation_results[1]['password_strong']
        # Should still have required keys
        assert validation_results[1]['has_required']
    
    def test_api_input_validation(self):
        """Test API input validation scenario."""
        api_requests = [
            {
                'endpoint': 'https://api.example.com/users',
                'user_id': '123',
                'data': {'name': 'John', 'active': True},
                'ip_address': '192.168.1.1'
            },
            {
                'endpoint': 'invalid-url',
                'user_id': 'abc',  # Should be numeric
                'data': {},  # Missing required fields
                'ip_address': '256.1.1.1'  # Invalid IP
            }
        ]
        
        for i, request in enumerate(api_requests):
            validation = {
                'endpoint_valid': is_valid_url(request['endpoint']),
                'user_id_numeric': is_numeric(request['user_id']),
                'has_required_data': has_required_keys(request['data'], ['name']),
                'ip_valid': is_valid_ip(request['ip_address'])
            }
            
            if i == 0:  # First request should be valid
                assert validation['endpoint_valid']
                assert validation['user_id_numeric']
                assert validation['has_required_data']
                assert validation['ip_valid']
            else:  # Second request should have failures
                assert not validation['endpoint_valid']
                assert not validation['user_id_numeric']
                assert not validation['has_required_data']
                assert not validation['ip_valid']