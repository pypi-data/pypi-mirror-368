# dotquery - A Universal Proxy Class for Python

`dotquery` provides a versatile `Proxy` class that wraps Python objects (dictionaries, lists, strings, and more) to allow for unified, chainable, dot-notation access to their elements.

It is particularly useful for navigating complex, nested data structures, such as those found in API responses or configuration files, without verbose key/index lookups.

## Features

- **Unified Dot-Notation Access**: Access dictionary keys, list indices, and object attributes with the same `.` syntax (e.g., `proxy.key`, `getattr(proxy, '0')`, `proxy.attribute`).
- **Automatic String Parsing**: When a string is proxied, `dotquery` automatically tries to parse it in the following order:
    1.  **JSON**: Deserializes a JSON string into a navigable object.
    2.  **URL**: Parses an absolute or relative URL string into its components (scheme, path, query, fragment, etc.).
    3.  **URL Query String**: Parses a query string (e.g., `key=value&a=b`) into a dictionary.
- **Recursive & Chainable**: Every element accessed from a `Proxy` object is wrapped in another `Proxy` instance, allowing for deep, uninterrupted chaining (e.g., `proxy.data.user.name`).
- **Handles Complex Objects**: Seamlessly works with objects like `requests.PreparedRequest`, allowing you to inspect the URL, headers, and body with the same dot-notation syntax.
- **Underlying Object Access**: You can retrieve the original, unwrapped object at any point in the chain using the `._` property (e.g., `proxy.data.user.id._`).

## Installation

This is a single-file utility. Simply place `dotquery.py` in your project. It has one external dependency, `requests`.

```bash
pip install requests
```

## Usage

### Basic Example: Dictionary and List

```python
from dotquery import Proxy

data = {"user": {"name": "Alex", "tags": ["dev", "test"]}, "status": "active"}
p_data = Proxy(data)

# Access nested dictionary keys
print(p_data.user.name)  # Output: Proxy('Alex')

# Access the raw value
print(p_data.user.name._) # Output: Alex

# Access list elements (using getattr for numeric keys)
tag = getattr(p_data.user.tags, '1')
print(tag._) # Output: 'test'

# Accessing a non-existent key returns a Proxy of None
print(p_data.user.address._) # Output: None
```

### String Parsing Examples

`Proxy` automatically detects and parses strings.

#### JSON String

```python
json_str = '{"success": true, "data": {"id": 123}}'
p_json = Proxy(json_str)

print(p_json.data.id._) # Output: 123
```

#### URL and Nested Fragment Parsing

`Proxy` can parse a URL and recursively parse its components, like the fragment.

```python
# The fragment itself is a URL-like string
url_str = "https://example.com/api?key=value#/profile?user=test"
p_url = Proxy(url_str)

print(p_url.scheme._)         # Output: 'https'
print(p_url.path._)           # Output: '/api'
print(p_url.query.key._)      # Output: 'value'

# The fragment is parsed recursively
print(p_url.fragment.path._)         # Output: '/profile'
print(p_url.fragment.query.user._)   # Output: 'test'
```

### Advanced Example: `requests.Request`

`dotquery` makes inspecting `requests` objects incredibly simple.

```python
import requests
from dotquery import Proxy, assert_eq

# 1. Create a request
url = "https://example.com/api#/profile?user=test"
req = requests.Request(
    method='POST',
    url=url,
    json={"user": {"name": "Alex"}},
    headers={"Content-Type": "application/json"}
)
prepared_req = req.prepare()

# 2. Wrap it in a Proxy
p_req = Proxy(prepared_req)

# 3. Access everything with dot notation
assert p_req.url.scheme == "https"
assert p_req.url.fragment.path == "/profile"
assert p_req.url.fragment.query.user == "test"
assert p_req.body.user.name == "Alex"
assert p_req.headers['Content-Type'] == "application/json"
```

## Limitations

### Numeric Property Access

Due to Python's syntax rules, you cannot access numeric indices directly with dot notation (e.g., `proxy.0` is a `SyntaxError`). You must use the built-in `getattr()` function for this purpose, which `dotquery` fully supports.

```python
p_list = Proxy(["apple", "banana"])

# Correct way
second_item = getattr(p_list, '1')
print(second_item._) # Output: 'banana'

# Incorrect way
# p_list.1 # This will raise a SyntaxError
```
