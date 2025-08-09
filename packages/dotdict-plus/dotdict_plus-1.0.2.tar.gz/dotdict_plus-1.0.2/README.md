# dot-dict

A Python library for dot notation access to nested dictionaries.

## Features

- Access nested dictionary values using dot notation
- Automatic creation of nested structures
- Compatible with standard dictionary operations
- JSON serialization support
- Lightweight and efficient

## Installation

```bash
pip install dot-dict
```

## Usage

```python
from dot_dict import Dot

# Create a Dot object from a dictionary
data = {
    "user": {
        "name": "John",
        "age": 30,
        "address": {
            "city": "New York",
            "country": "USA"
        }
    }
}

dot_data = Dot(data)

# Access values using dot notation
print(dot_data.user.name)  # Output: John
print(dot_data.user.address.city)  # Output: New York

# Set values using dot notation
dot_data.user.age = 31
dot_data.user.email = "john@example.com"

# Automatic creation of nested structures
dot_data.settings.theme = "dark"
dot_data.settings.language = "en"

# Convert back to dictionary
dict_data = dot_data.to_dict()

# JSON serialization
print(str(dot_data))
```

## Development

### Setup

```bash
# Clone the repository
git clone https://git.xmov.ai/jiangbin/dot-dict.git
cd dot-dict

# Install development dependencies
pip install -e ".[dev]"
```


## License

MIT License 