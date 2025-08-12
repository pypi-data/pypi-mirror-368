# docx-json-replacer

A Python library and CLI tool for replacing template placeholders in DOCX files with JSON data, including support for formatted tables with colors and styling.

## ✨ New in v0.5.0: Table Support!

Create professional Word documents with formatted tables directly from JSON data. Tables support custom colors, backgrounds, bold text, and multiple data formats.

## Installation

```bash
pip install docx-json-replacer
# or
pip3 install docx-json-replacer
```

## Quick Start

### CLI Usage

```bash
# Basic text replacement
docx-json-replacer template.docx data.json

# Specify output file
docx-json-replacer template.docx data.json -o output.docx
```

### Python API

```python
from docx_json_replacer import DocxReplacer

# Create replacer instance
replacer = DocxReplacer("template.docx")

# Replace with JSON data (including tables)
replacer.replace_from_json({
    "name": "John Doe",
    "date": "2025-01-15",
    "sales_table": [
        {"cells": ["Month", "Revenue"], "style": {"bg": "4472C4", "color": "FFFFFF", "bold": True}},
        {"cells": ["January", "$100K"], "style": {"bg": "F2F2F2"}}
    ]
})

# Save the result
replacer.save("output.docx")
```

## 📊 Table Support

### 1. Styled Tables with Colors

```json
{
  "financial_data": [
    {
      "cells": ["Quarter", "Revenue", "Profit"],
      "style": {
        "bg": "1F4788",      // Background color (hex without #)
        "color": "FFFFFF",   // Text color
        "bold": true,        // Bold text
        "italic": false      // Italic text
      }
    },
    {
      "cells": ["Q1 2024", "$2.5M", "$500K"],
      "style": {"bg": "E8F4FD"}
    },
    {
      "cells": ["Q2 2024", "$2.8M", "$600K"],
      "style": {"bg": "FFFFFF"}
    }
  ]
}
```

### 2. Simple List Tables

```json
{
  "product_list": [
    ["Product", "Price", "Stock"],
    ["Laptop", "$999", "15 units"],
    ["Mouse", "$29", "50 units"],
    ["Keyboard", "$79", "32 units"]
  ]
}
```

### 3. Dictionary Tables (Auto-Headers)

Headers are automatically generated from object keys:

```json
{
  "employee_data": [
    {"name": "Alice Johnson", "department": "Engineering", "salary": 95000},
    {"name": "Bob Smith", "department": "Marketing", "salary": 75000},
    {"name": "Carol White", "department": "HR", "salary": 65000}
  ]
}
```

### 4. HTML Table Parsing

```json
{
  "html_report": "<table><tr><th>Metric</th><th>Value</th></tr><tr><td>Users</td><td>1,250</td></tr><tr><td>Revenue</td><td>$50K</td></tr></table>"
}
```

## Template Format

Use `{{key}}` placeholders in your DOCX file:

**template.docx:**
```
Company Report

Company: {{company}}
Date: {{date}}

Financial Summary:
{{financial_table}}

Products:
{{product_list}}
```

**data.json:**
```json
{
  "company": "TechCorp International",
  "date": "2025-01-15",
  "financial_table": [
    {"cells": ["Metric", "Q1", "Q2"], "style": {"bg": "4472C4", "color": "FFFFFF", "bold": true}},
    {"cells": ["Revenue", "$45M", "$52M"], "style": {"bg": "F2F2F2"}},
    {"cells": ["Profit", "$12M", "$15M"], "style": {"bg": "FFFFFF"}}
  ],
  "product_list": [
    ["Product", "Units Sold"],
    ["Software", "500"],
    ["Services", "200"]
  ]
}
```

## Color Reference

Use hex color codes without the `#` symbol:

| Color | Hex Code | Usage |
|-------|----------|-------|
| Dark Blue | `1F4788` | Headers |
| Medium Blue | `4472C4` | Primary headers |
| Light Blue | `E8F4FD` | Alternating rows |
| Green | `D4EDDA` | Success/Positive |
| Yellow | `FFF3CD` | Warning |
| Red | `F8D7DA` | Alert/Negative |
| Light Gray | `F2F2F2` | Alternating rows |
| White | `FFFFFF` | Default/Text on dark |

## Complete Example

### 1. Create Template (template.docx)

```
Annual Business Report

Company: {{company}}
Report Date: {{report_date}}
Prepared by: {{author}}

Executive Summary:
{{summary}}

Department Performance:
{{department_table}}

Risk Assessment:
{{risk_table}}
```

### 2. Prepare Data (data.json)

```json
{
  "company": "Global Tech Solutions",
  "report_date": "2025-01-15",
  "author": "Analytics Team",
  "summary": "Strong performance across all departments with 23% YoY growth.",
  "department_table": [
    {
      "cells": ["Department", "Budget", "Utilization", "Performance"],
      "style": {"bg": "495057", "color": "FFFFFF", "bold": true}
    },
    {
      "cells": ["Engineering", "$2.5M", "94%", "Excellent"],
      "style": {"bg": "D4EDDA"}
    },
    {
      "cells": ["Sales", "$1.8M", "88%", "Very Good"],
      "style": {"bg": "FFFFFF"}
    },
    {
      "cells": ["Operations", "$1.2M", "78%", "Needs Improvement"],
      "style": {"bg": "FFF3CD"}
    }
  ],
  "risk_table": [
    {
      "cells": ["Risk", "Level", "Mitigation"],
      "style": {"bg": "DC3545", "color": "FFFFFF", "bold": true}
    },
    {
      "cells": ["Cybersecurity", "High", "24/7 monitoring"],
      "style": {"bg": "F8D7DA"}
    },
    {
      "cells": ["Market Competition", "Medium", "Innovation focus"],
      "style": {"bg": "FFF3CD"}
    }
  ]
}
```

### 3. Generate Report

```bash
docx-json-replacer template.docx data.json -o report.docx
```

Or with Python:

```python
from docx_json_replacer import DocxReplacer

replacer = DocxReplacer("template.docx")
replacer.replace_from_json_file("data.json")
replacer.save("report.docx")
```

## API Reference

### DocxReplacer Class

```python
class DocxReplacer:
    def __init__(self, docx_path: str)
    """Initialize with template document path"""
    
    def replace_from_json(self, json_data: Dict[str, Any]) -> None
    """Replace placeholders with JSON data"""
    
    def replace_from_json_file(self, json_path: str) -> None
    """Load JSON from file and replace"""
    
    def save(self, output_path: str) -> None
    """Save the modified document"""
```

### Utility Function

```python
replace_docx_template(docx_path: str, json_data: Dict[str, Any], output_path: str) -> None
"""One-line replacement function"""
```

## Local Development

### Run Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_table_handler.py -v
```

### Test Table Features

```bash
# Create a test document with tables
python test_simple.py
```

## Requirements

- Python 3.7+
- python-docx >= 0.8.11
- docxtpl >= 0.20.0

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or feature requests:
- GitHub: https://github.com/liuspatt/docx-json-replacer
- Issues: https://github.com/liuspatt/docx-json-replacer/issues