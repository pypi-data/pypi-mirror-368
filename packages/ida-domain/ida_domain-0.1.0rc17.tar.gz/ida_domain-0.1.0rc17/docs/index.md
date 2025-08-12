# IDA Domain API

The IDA Domain API provides a **Domain Model** on top of the IDA Python SDK.

This API will not replace the current low level IDA Python SDK, but will progressively increase in coverage to become the **main entry point** for IDA scripting & plugin development.

> **Compatibility:** Requires IDA Pro 9.1.0 or later

## 🚀 Key Features

- **Pure Python implementation** - No compilation required, works with any Python 3.9+
- **Domain-driven design** - APIs mirror how reverse engineers think about binaries
- **Compatibility** - The Domain API is fully compatible and can be used alongside with the IDA Python SDK
- **Comprehensive coverage** - Functions, strings, types, cross-references, and more
- **Easy installation** - Single `pip install` command

## ⚙️ Quick Example

```python
--8<-- "examples/quick_example.py"
```

## 📖 Documentation

- **[Getting Started](getting_started.md)** - Installation and your first script
- **[Examples](examples.md)** - Practical examples for common tasks
- **[API Reference](usage.md)** - Complete API documentation

## 🔗 Additional Resources

- **PyPI Package**: [ida-domain on PyPI](https://pypi.org/project/ida-domain/)
- **Source Code**: [GitHub Repository](https://github.com/HexRaysSA/ida-domain)
- **Issues**: [Bug Reports](https://github.com/HexRaysSA/ida-domain/issues)
- **License**: MIT License
