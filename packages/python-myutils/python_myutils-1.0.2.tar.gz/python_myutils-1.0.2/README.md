# 🐍 MyUtils - Python Utility Library

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-119_passed-green.svg)](https://github.com/quocln-tech/python-myutils/actions)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/quocln-tech/python-myutils)
[![Code Quality](https://img.shields.io/badge/code_quality-A-brightgreen.svg)](https://github.com/quocln-tech/python-myutils)

A comprehensive, production-ready Python utility library that provides essential tools for file operations, string manipulation, date/time handling, validation, and AI integrations. Built with modern Python practices and extensive test coverage.

## ✨ Features

### 🔧 Core Utilities
- **File Operations**: JSON, CSV handling, directory management, file utilities
- **String Processing**: Case conversion, cleaning, validation, formatting, pluralization  
- **Date/Time**: Parsing, formatting, calculations, human-readable timestamps
- **Validation**: Phone, URL, IP, email, password strength, data structure validation

### 🤖 AI & Integration Managers
- **AI Manager**: OpenRouter API integration with request handling
- **Database Manager**: Supabase operations with full CRUD support
- **Sentry Manager**: Error tracking and event capture with custom context
- **AI Embed Manager**: OpenAI embeddings with intelligent caching and rate limiting

### 🛡️ Production Ready
- **100% Test Coverage**: 119 comprehensive tests covering all functionality
- **Type Hints**: Full type annotation support for better IDE experience
- **Error Handling**: Robust error handling with detailed logging
- **Configuration**: Flexible, configuration-driven initialization
- **Performance**: Optimized with caching and rate limiting where needed

## 🚀 Quick Start

### Basic Usage

```python
from myutils import *

# File operations
data = {"name": "John", "age": 30}
write_json(data, "user.json")
user_data = read_json("user.json")

# String utilities
snake_case = camel_to_snake("MyVariableName")  # "my_variable_name"
clean_name = clean_filename("my<file>name.txt")  # "myfilename.txt"
is_valid = is_email("user@example.com")  # True

# Date utilities
formatted = format_datetime(datetime.now(), "%Y-%m-%d")
time_str = time_since(datetime.now() - timedelta(hours=2))  # "2 hours ago"

# Validation
phone_valid = is_valid_phone("555-123-4567")  # True
strong_pwd = is_strong_password("MyP@ssw0rd123")  # True
```

## 📚 Comprehensive Documentation

### File Utilities

```python
from myutils.file_utils import *

# JSON operations
data = {"users": [{"name": "John", "age": 30}]}
write_json(data, "data.json", indent=2)
result = read_json("data.json")

# CSV operations  
csv_data = read_csv_as_dicts("users.csv")
for user in csv_data:
    print(f"Name: {user['name']}, Age: {user['age']}")

# Directory management
ensure_dir_exists("logs/2024")
if file_exists("config.json"):
    size = get_file_size("config.json")
```

### String Processing

```python
from myutils.string_utils import *

# Case conversion
camel_case = snake_to_camel("user_name")  # "UserName"
snake_case = camel_to_snake("UserName")   # "user_name"

# Text processing
cleaned = remove_extra_spaces("  Hello    world  ")  # "Hello world"
truncated = truncate_string("Long text here", 10)    # "Long te..."
numbers = extract_numbers("Price: $123.45")         # ["123", "45"]

# Validation & formatting
valid_email = is_email("user@domain.com")           # True
safe_name = clean_filename("file<name>.txt")        # "filename.txt"
plural_form = plural("item", 5)                     # "items"
```

### Date & Time Operations

```python
from myutils.date_utils import *

# Date formatting and parsing
now = datetime.now()
formatted = format_datetime(now, "%B %d, %Y")       # "August 08, 2024"
parsed = parse_datetime("2024-08-08", "%Y-%m-%d")

# Date calculations
past_date = days_ago(7)                              # 7 days ago
future_date = days_from_now(14)                      # 14 days from now
age = get_age_in_years(datetime(1990, 5, 15))       # Current age

# Human-readable time
time_str = time_since(datetime.now() - timedelta(minutes=30))  # "30 minutes ago"
weekend = is_weekend(datetime.now())                           # True/False
```

### Validation Functions

```python
from myutils.validation_utils import *

# Contact validation
phone_valid = is_valid_phone("(555) 123-4567")      # True
url_valid = is_valid_url("https://example.com")     # True
ip_valid = is_valid_ip("192.168.1.1")              # True

# Data validation
numeric = is_numeric("123.45")                       # True
in_range = is_in_range(25, 18, 65)                 # True
not_empty = is_not_empty("  content  ")            # True
has_keys = has_required_keys({"name": "John"}, ["name"])  # True

# Password validation
strength = validate_password_strength("MyP@ssw0rd123")
# {"min_length": True, "has_uppercase": True, "has_lowercase": True, 
#  "has_digit": True, "has_special": True}
strong = is_strong_password("MyP@ssw0rd123")        # True
```

## 🤖 AI & Integration Managers

### AI Manager (OpenRouter Integration)

```python
from myutils.ai_manager_utils import AIManager

config = {
    "api_key": "your-openrouter-api-key",
    "model": "google/gemini-2.0-flash-001",
    "base_url": "https://openrouter.ai/api/v1"
}

ai = AIManager(config)

# Make AI requests
response = ai.request("chat/completions", {
    "messages": [{"role": "user", "content": "Hello, AI!"}],
    "max_tokens": 100
})

# Verify connectivity
if ai.verify_connectivity():
    print("AI service is available")
```

### Database Manager (Supabase Integration)

```python
from myutils.database_manager_utils import DatabaseManager

config = {
    "url": "your-supabase-url",
    "key": "your-supabase-key"
}

db = DatabaseManager(config)

# CRUD operations
user = db.insert({"name": "John", "email": "john@example.com"}, "users")
users = db.select("users", {"active": True})
updated = db.update({"name": "John Doe"}, {"id": user["id"]}, "users")
deleted = db.delete({"id": user["id"]}, "users")
```

### Sentry Manager (Error Tracking)

```python
from myutils.sentry_manager_utils import SentryManager

config = {
    "dsn": "your-sentry-dsn",
    "environment": "production",
    "version": "1.0.0"
}

sentry = SentryManager(config)

# Capture events
sentry.capture({"message": "User login", "user_id": 123}, "info")
sentry.capture({"error": "Database connection failed"}, "error")
sentry.capture({"metric": "api_response_time", "value": 250}, "performance")

# Verify connectivity
if sentry.verify_connectivity():
    print("Sentry tracking is active")
```

### AI Embed Manager (OpenAI Embeddings)

```python
from myutils.ai_embed_manager_utils import AIEmbedManager

config = {
    "api_key": "your-openai-api-key",
    "model": "text-embedding-3-small",
    "cache_duration": 3600  # 1 hour cache
}

embedder = AIEmbedManager(config)

# Generate embeddings (with automatic caching)
embedding = embedder.get_embedding("Hello, world!")
print(f"Embedding dimensions: {len(embedding)}")

# Batch processing
embeddings = embedder.get_embedding_batch([
    "First text", "Second text", "Third text"
])

# Cache management
stats = embedder.get_cache_stats()
print(f"Cache entries: {stats['total_entries']}")
embedder.clear_cache()  # Clear when needed
```

## 🔧 Advanced Usage

### Configuration Management

All managers support flexible configuration:

```python
# Environment variables
import os
from myutils import AIManager, DatabaseManager

ai_config = {
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "model": os.getenv("AI_MODEL", "google/gemini-2.0-flash-001")
}

db_config = {
    "url": os.getenv("SUPABASE_URL"),
    "key": os.getenv("SUPABASE_KEY")
}

ai = AIManager(ai_config)
db = DatabaseManager(db_config)
```

### Error Handling

```python
from myutils import *

try:
    data = read_json("nonexistent.json")
except FileNotFoundError:
    data = {"default": True}

# Graceful degradation
ai = AIManager({"api_key": ""})  # No key provided
if not ai.client_available:
    print("AI features disabled - no API key")
```

### Integration Example

```python
from myutils import *
from datetime import datetime

# Complete workflow example
def process_user_data(user_input):
    # Validate and clean input
    if not is_email(user_input.get('email', '')):
        return {"error": "Invalid email"}
    
    # Process and format data
    user_data = {
        "name": remove_extra_spaces(user_input['name']),
        "email": user_input['email'].lower().strip(),
        "phone": user_input.get('phone', '').strip(),
        "registered": datetime.now().isoformat(),
        "age": get_age_in_years(parse_datetime(user_input['birth_date'], "%Y-%m-%d"))
    }
    
    # Validate phone if provided
    if user_data['phone'] and not is_valid_phone(user_data['phone']):
        return {"error": "Invalid phone number"}
    
    # Save to database
    db = DatabaseManager({"url": "...", "key": "..."})
    result = db.insert(user_data, "users")
    
    # Log to Sentry
    sentry = SentryManager({"dsn": "..."})
    sentry.capture({"message": "User registered", "user_id": result["id"]}, "info")
    
    return {"success": True, "user": result}
```

## 📊 Testing & Quality

- **119 Tests**: Comprehensive test suite covering all functionality
- **100% Pass Rate**: All tests passing with robust error handling
- **Type Safety**: Full type hints for better development experience  
- **Mock Testing**: External API dependencies properly mocked
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Optimized for speed and memory usage

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=myutils --cov-report=html

# Run specific test module
pytest tests/test_string_utils.py -v
```

## 🛠️ Requirements

- **Python**: 3.10 or higher
- **Dependencies**: requests, supabase, sentry-sdk, python-dotenv
- **Optional**: pytest, pytest-cov, pytest-mock (for development)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Setup

```bash
# Clone using SSH (recommended)
git clone git@github.com:quocln-tech/python-myutils.git
cd python-myutils
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
pytest  # Run tests
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Why MyUtils?

### ✅ Production Ready
- Extensively tested with 100% test coverage
- Used in production environments
- Robust error handling and graceful degradation
- Type-safe with comprehensive type hints

### ⚡ Performance Optimized
- Intelligent caching for expensive operations
- Rate limiting to respect API constraints
- Memory-efficient implementations
- Async-ready architecture

### 🔧 Developer Friendly
- Intuitive API design
- Comprehensive documentation
- Clear error messages
- IDE-friendly with full type support

### 🎯 Comprehensive
- Core utilities + AI integrations in one package
- Consistent API patterns across all modules
- Configuration-driven architecture
- Mock-friendly for easy testing

---

**Built with ❤️ by [quocln](https://github.com/quocln)**

*Making Python development more efficient, one utility at a time.*