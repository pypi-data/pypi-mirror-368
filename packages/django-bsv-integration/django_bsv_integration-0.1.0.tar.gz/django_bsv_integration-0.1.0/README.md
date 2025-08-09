# Django BSV Integration

A Django package for Bitcoin SV (BSV) blockchain integration using the py-bsv SDK.

## Features

- BSV wallet management with Django models
- Transaction creation and broadcasting
- 1sat ordinal support
- Image processing for blockchain storage
- UTXO management
- Integration with WhatsOnChain and GorillaPool APIs

## Installation

```bash
pip install django-bsv-integration
```

## Quick Start

1. Add "bsv_integration" to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    'bsv_integration',
]
```

2. Run migrations:

```bash
python manage.py migrate bsv_integration
```

3. Create a BSV wallet:

```python
from bsv_integration.models import BSVWallet

# Create wallet
wallet = BSVWallet.objects.create(
    user=request.user,
    name="My BSV Wallet",
    # ... other fields
)

# Send transaction
result = await wallet.send_transaction(
    recipient_address="1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
    amount=1000,  # satoshis
    op_return_message="Hello BSV!"
)
```

## Requirements

- Django 3.2+
- Python 3.8+
- py-bsv SDK
- aiohttp for async operations

## License

MIT License
