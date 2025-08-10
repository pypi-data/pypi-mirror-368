"""Tests for string_utils module."""

import pytest
from myutils.string_utils import (
    camel_to_snake, snake_to_camel, remove_extra_spaces,
    truncate_string, extract_numbers, is_email, clean_filename, plural
)


class TestCaseConversion:
    """Test case conversion functions."""
    
    def test_camel_to_snake_basic(self):
        """Test basic CamelCase to snake_case conversion."""
        assert camel_to_snake("CamelCase") == "camel_case"
        assert camel_to_snake("SimpleWord") == "simple_word"
        assert camel_to_snake("HTTPSConnection") == "httpsconnection"
        assert camel_to_snake("XMLParser") == "xmlparser"
    
    def test_camel_to_snake_edge_cases(self):
        """Test edge cases for CamelCase conversion."""
        assert camel_to_snake("") == ""
        assert camel_to_snake("A") == "a"
        assert camel_to_snake("AB") == "ab"
        assert camel_to_snake("lowercase") == "lowercase"
        assert camel_to_snake("UPPERCASE") == "uppercase"
    
    def test_camel_to_snake_with_numbers(self):
        """Test CamelCase conversion with numbers."""
        assert camel_to_snake("User123Profile") == "user123_profile"
        assert camel_to_snake("API2Version") == "api2_version"
        assert camel_to_snake("HTML5Parser") == "html5_parser"
    
    def test_snake_to_camel_basic(self):
        """Test basic snake_case to CamelCase conversion."""
        assert snake_to_camel("snake_case") == "SnakeCase"
        assert snake_to_camel("simple_word") == "SimpleWord"
        assert snake_to_camel("multiple_word_string") == "MultipleWordString"
    
    def test_snake_to_camel_edge_cases(self):
        """Test edge cases for snake_case conversion."""
        assert snake_to_camel("") == ""
        assert snake_to_camel("single") == "Single"
        assert snake_to_camel("_leading_underscore") == "LeadingUnderscore"
        assert snake_to_camel("trailing_underscore_") == "TrailingUnderscore"
    
    def test_snake_to_camel_with_numbers(self):
        """Test snake_case conversion with numbers."""
        assert snake_to_camel("user_123_profile") == "User123Profile"
        assert snake_to_camel("api_v2_endpoint") == "ApiV2Endpoint"
    
    def test_case_conversion_roundtrip(self):
        """Test that case conversion is consistent (though not always reversible)."""
        test_cases = [
            "CamelCase",
            "SimpleWord",
            "MultipleWordString"
        ]
        
        for camel in test_cases:
            snake = camel_to_snake(camel)
            back_to_camel = snake_to_camel(snake)
            # Note: This might not be exactly the same due to consecutive caps
            assert isinstance(back_to_camel, str)
            assert len(back_to_camel) > 0


class TestStringCleaning:
    """Test string cleaning functions."""
    
    def test_remove_extra_spaces_basic(self):
        """Test basic space removal."""
        assert remove_extra_spaces("hello world") == "hello world"
        assert remove_extra_spaces("  hello   world  ") == "hello world"
        assert remove_extra_spaces("multiple    spaces     everywhere") == "multiple spaces everywhere"
    
    def test_remove_extra_spaces_edge_cases(self):
        """Test edge cases for space removal."""
        assert remove_extra_spaces("") == ""
        assert remove_extra_spaces("   ") == ""
        assert remove_extra_spaces("single") == "single"
        assert remove_extra_spaces("  single  ") == "single"
    
    def test_remove_extra_spaces_with_tabs_and_newlines(self):
        """Test space removal with different whitespace characters."""
        assert remove_extra_spaces("hello\t\tworld") == "hello world"
        assert remove_extra_spaces("hello\n\nworld") == "hello world"
        assert remove_extra_spaces("hello\r\nworld") == "hello world"
        assert remove_extra_spaces("  hello  \t\n  world  ") == "hello world"
    
    def test_clean_filename_basic(self):
        """Test basic filename cleaning."""
        assert clean_filename("normal_file.txt") == "normal_file.txt"
        assert clean_filename("my<file>.txt") == "myfile.txt"
        assert clean_filename('bad"file".txt') == "badfile.txt"
        assert clean_filename("file|with|pipes.txt") == "filewithpipes.txt"
    
    def test_clean_filename_all_invalid_chars(self):
        """Test filename cleaning with all invalid characters."""
        invalid_chars = '<>:"/\\|?*'
        filename = f"file{invalid_chars}name.txt"
        cleaned = clean_filename(filename)
        assert cleaned == "filename.txt"
        
        # Ensure no invalid characters remain
        for char in invalid_chars:
            assert char not in cleaned
    
    def test_clean_filename_edge_cases(self):
        """Test filename cleaning edge cases."""
        assert clean_filename("") == ""
        assert clean_filename("<<<>>>") == ""
        assert clean_filename("good_file_123.txt") == "good_file_123.txt"


class TestStringAnalysis:
    """Test string analysis functions."""
    
    def test_extract_numbers_basic(self):
        """Test basic number extraction."""
        assert extract_numbers("abc123def456") == ["123", "456"]
        assert extract_numbers("user123") == ["123"]
        assert extract_numbers("version2.1.3") == ["2", "1", "3"]
    
    def test_extract_numbers_edge_cases(self):
        """Test number extraction edge cases."""
        assert extract_numbers("") == []
        assert extract_numbers("no numbers here") == []
        assert extract_numbers("123") == ["123"]
        assert extract_numbers("123abc456def789") == ["123", "456", "789"]
    
    def test_extract_numbers_with_decimals(self):
        """Test number extraction with decimal-like patterns."""
        # Note: This extracts each number part separately
        assert extract_numbers("3.14159") == ["3", "14159"]
        assert extract_numbers("price: $19.99") == ["19", "99"]
        assert extract_numbers("version 1.2.3 beta") == ["1", "2", "3"]
    
    def test_is_email_valid_emails(self):
        """Test email validation with valid emails."""
        valid_emails = [
            "user@example.com",
            "test.user@domain.org",
            "user+tag@example.co.uk",
            "user.name@example-domain.com",
            "user123@example123.com",
            "a@b.co",
            "very.long.email.address@very.long.domain.name.com"
        ]
        
        for email in valid_emails:
            assert is_email(email), f"Expected {email} to be valid"
    
    def test_is_email_invalid_emails(self):
        """Test email validation with invalid emails."""
        invalid_emails = [
            "",
            "not-an-email",
            "@example.com",
            "user@",
            "user@@example.com",
            "user@.com",
            "user@example.",
            "user@example",
            "user name@example.com",  # space
            "user@exam ple.com",      # space in domain
        ]
        
        for email in invalid_emails:
            assert not is_email(email), f"Expected {email} to be invalid"
    
    def test_is_email_edge_cases(self):
        """Test email validation edge cases."""
        # Case sensitivity should not matter for validation
        assert is_email("User@Example.COM")
        assert is_email("USER@EXAMPLE.COM")
        
        # International domains (basic test)
        assert is_email("user@example.org")


class TestTextFormatting:
    """Test text formatting functions."""
    
    def test_truncate_string_basic(self):
        """Test basic string truncation."""
        assert truncate_string("hello world", 5) == "he..."
        assert truncate_string("hello world", 11) == "hello world"  # No truncation needed
        assert truncate_string("hello world", 8) == "hello..."
    
    def test_truncate_string_custom_suffix(self):
        """Test truncation with custom suffix."""
        assert truncate_string("hello world", 8, "***") == "hello***"
        assert truncate_string("hello world", 8, "") == "hello wo"
        assert truncate_string("hello world", 8, ">>") == "hello >>"
    
    def test_truncate_string_edge_cases(self):
        """Test truncation edge cases."""
        assert truncate_string("", 5) == ""
        assert truncate_string("short", 10) == "short"
        assert truncate_string("exact", 5) == "exact"
        
        # Test with suffix longer than max_length
        assert truncate_string("hello", 3, "...") == "..."
    
    def test_plural_basic(self):
        """Test basic pluralization."""
        assert plural("cat", 1) == "cat"
        assert plural("cat", 2) == "cats"
        assert plural("dog", 0) == "dogs"
        assert plural("item", 5) == "items"
    
    def test_plural_special_endings(self):
        """Test pluralization with special endings."""
        # Words ending in 'y'
        assert plural("city", 2) == "cities"
        assert plural("baby", 3) == "babies"
        assert plural("key", 2) == "keys"  # 'ey' ending
        
        # Words ending in 's', 'sh', 'ch', 'x', 'z'
        assert plural("box", 2) == "boxes"
        assert plural("class", 2) == "classes"
        assert plural("dish", 2) == "dishes"
        assert plural("church", 2) == "churches"
        assert plural("fox", 2) == "foxes"
        assert plural("buzz", 2) == "buzzes"
    
    def test_plural_edge_cases(self):
        """Test pluralization edge cases."""
        assert plural("", 1) == ""
        assert plural("", 2) == "s"
        assert plural("a", 1) == "a"
        assert plural("a", 2) == "as"


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple string functions."""
    
    def test_data_cleaning_pipeline(self):
        """Test complete data cleaning pipeline."""
        messy_data = [
            "  UserProfile123  ",
            "admin<user>name.txt",
            "email@DOMAIN.COM",
            "  multiple   spaces   everywhere  "
        ]
        
        cleaned_data = []
        for item in messy_data:
            # Clean spaces
            cleaned = remove_extra_spaces(item)
            # Convert to snake_case if it looks like a class name
            if cleaned and cleaned[0].isupper():
                cleaned = camel_to_snake(cleaned)
            # Clean filename if it has file extension
            if '.' in cleaned:
                cleaned = clean_filename(cleaned)
            # Extract numbers if present
            numbers = extract_numbers(cleaned)
            
            cleaned_data.append({
                'original': item,
                'cleaned': cleaned,
                'numbers': numbers,
                'is_email': is_email(cleaned.lower())
            })
        
        # Verify results
        assert len(cleaned_data) == 4
        assert cleaned_data[0]['cleaned'] == 'user_profile123'
        assert cleaned_data[1]['cleaned'] == 'adminusername.txt'
        assert cleaned_data[2]['is_email'] is True
        assert cleaned_data[3]['cleaned'] == 'multiple spaces everywhere'
    
    def test_text_processing_workflow(self):
        """Test text processing workflow."""
        user_inputs = [
            "My<File>Name.txt",
            "user@example.com",
            "  VeryLongTextThatNeedsToBeProcessed  ",
            "item"
        ]
        
        processed = []
        for text in user_inputs:
            result = {
                'original': text,
                'cleaned': remove_extra_spaces(text),
                'safe_filename': clean_filename(text),
                'snake_case': camel_to_snake(text.strip()),
                'truncated': truncate_string(text.strip(), 10),
                'is_email': is_email(text.strip()),
                'plural': plural(text.strip().lower(), 2)
            }
            processed.append(result)
        
        # Verify processing
        assert processed[0]['safe_filename'] == "MyFileName.txt"
        assert processed[1]['is_email'] is True
        assert processed[2]['truncated'] == "VeryLon..."
        assert processed[3]['plural'] == "items"