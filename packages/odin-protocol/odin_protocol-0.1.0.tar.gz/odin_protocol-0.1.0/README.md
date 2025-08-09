# ODIN Protocol Python SDK

Python SDK for the ODIN AI state interchange protocol.

## Installation

```bash
pip install odin-protocol
```

## Quick Start

```python
from odin_protocol import create_odin_file, pack_odin, unpack_odin

# Create an ODIN file
odin_file = create_odin_file(
    content_type="text/plain",
    data="Hello, ODIN Protocol!",
    creator="your-app",
    description="Example ODIN file"
)

# Pack to binary format
packed_data = pack_odin(odin_file)

# Unpack back to OdinFile
unpacked_file = unpack_odin(packed_data)
```

## Features

- Complete ODIN v1.0 format implementation
- Deterministic msgpack serialization
- zlib compression with CRC32C checksums
- Ed25519 and RSA-PSS digital signatures
- ChaCha20-Poly1305 encryption
- HTTP client for ODIN service endpoints
- Comprehensive test suite

## API Reference

### Core Functions

- `pack_odin()` - Pack ODIN file to binary format
- `unpack_odin()` - Unpack binary ODIN file
- `sign_odin()` - Sign ODIN file data
- `verify_odin()` - Verify ODIN file signature
- `encrypt_odin()` - Encrypt ODIN file fields
- `decrypt_odin()` - Decrypt ODIN file
- `open_chain()` - Open .odin.chain files

### HTTP Client

```python
from odin_protocol import OdinClient

client = OdinClient(
    base_url="https://api.odin.ai",
    api_key="your-api-key"
)

# Submit files to mediator
result = client.mediator_submit([packed_data])

# Evaluate rules
result = client.rules_evaluate("rule-id", {"input": "data"})

# Registry operations
client.registry_put("key", packed_data)
data = client.registry_get("key")
```

## Development

```bash
git clone https://github.com/odin-ai/odin-protocol
cd python/odin-protocol
pip install -e .
pytest
```

## License

MIT License - see LICENSE file for details.
