# A1 Huakunjingxiu Billing SDK

Python SDK for interacting with the A1 Huakunjingxiu Billing API.

## 项目结构

```markdown
billing-sdk/
├── billing/                      # 主应用目录
│   ├── product/                 # 产品模块
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── transaction/             # 交易模块
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── __init__.py
│   ├── exceptions.py
│   ├── http.py
│   └── schemas.py
├── tests/                       # 测试目录
│   └── test_transaction_create.py
├── docs/                        # 文档目录
├── examples/                    # 示例目录
│   ├── product/                 # 产品示例
│   │   ├── __init__.py
│   │   └── create_token_example.py
│   ├── transaction/             # 交易示例
│   │   ├── __init__.py
│   │   └── create_transaction_example.py
│   ├── __init__.py
│   └── README.md
├── .clinerules
├── .cursorrules
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

## 运行示例

运行示例代码前需要设置PYTHONPATH环境变量:

```powershell
$env:PYTHONPATH=$PWD
uv run examples/product/create_token_example.py
```

```bash
export PYTHONPATH=$(pwd)
uv run examples/product/create_token_example.py
```

## Installation

```bash
pip install billing-sdk
```

## Usage

```python
from billing import Client

# Initialize client
client = Client(api_key="your_api_key")

# Create an invoice
invoice = client.create_invoice(
    amount=100.00,
    description="Monthly subscription"
)

# Get invoice details
invoice_details = client.get_invoice(invoice["id"])

# List invoices
invoices = client.list_invoices(limit=10)
```

## Error Handling

The SDK provides several exception types:

```python
from billing import (
    BillingError,
    AuthenticationError,
    InvalidRequestError,
    APIError
)

try:
    # API calls
except AuthenticationError as e:
    print("Invalid API key")
except InvalidRequestError as e:
    print("Invalid request parameters")
except APIError as e:
    print("Server error occurred")
except BillingError as e:
    print("General billing error")
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

MIT
