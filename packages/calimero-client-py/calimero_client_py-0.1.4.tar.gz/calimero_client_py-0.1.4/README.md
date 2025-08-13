# Calimero Network Python Client SDK

The **Calimero Python Client SDK** helps developers interact with decentralized apps by handling server communication. It simplifies the process, letting you focus on building your app while the SDK manages the technical details.

## Features

- JSON-RPC client for sending queries and updates to Calimero nodes
- WebSocket client for real-time subscriptions
- Authentication handling with Ed25519 keypairs
- Configuration management
- Type hints and comprehensive documentation

## Installation

```bash
pip install calimero-client-py==0.1.2
```

## Quick Start

Here's a complete example of using the SDK to interact with a key-value store:

```python
import asyncio
import toml
import os
from pathlib import Path
from calimero import JsonRpcClient, Ed25519Keypair

async def main():
    # Load keypair from config file
    config_path = os.path.expanduser("~/.calimero/node1/config.toml")
    try:
        with open(config_path, 'r') as f:
            config_data = toml.load(f)
            keypair_value = config_data.get('identity', {}).get('keypair')
            if not keypair_value:
                raise ValueError("'keypair' not found in [identity] section")
            keypair = Ed25519Keypair.from_base58(keypair_value)
    except Exception as e:
        raise ValueError(f"Failed to load keypair from config: {str(e)}")

    # Initialize the client
    client = JsonRpcClient(
        base_url="http://localhost:2428",
        endpoint="/jsonrpc",
        keypair=keypair
    )

    # Example: Set a key-value pair
    set_params = {
        "applicationId": "your_application_id",
        "method": "set",
        "argsJson": {"key": "my_key", "value": "my_value"}
    }
    set_response = await client.mutate(set_params)
    print("Set response:", set_response)

    # Example: Get a value
    get_params = {
        "applicationId": "your_application_id",
        "method": "get",
        "argsJson": {"key": "my_key"}
    }
    get_response = await client.query(get_params)
    print("Get response:", get_response)

if __name__ == "__main__":
    asyncio.run(main())
```

### WebSocket Example

Here's how to use the WebSocket client for real-time updates:

```python
import asyncio
import toml
import os
from pathlib import Path
from calimero import WsSubscriptionsClient, Ed25519Keypair

async def main():
    # Load keypair from config file
    config_path = os.path.expanduser("~/.calimero/node1/config.toml")
    try:
        with open(config_path, 'r') as f:
            config_data = toml.load(f)
            keypair_value = config_data.get('identity', {}).get('keypair')
            if not keypair_value:
                raise ValueError("'keypair' not found in [identity] section")
            keypair = Ed25519Keypair.from_base58(keypair_value)
    except Exception as e:
        raise ValueError(f"Failed to load keypair from config: {str(e)}")

    # Initialize the client
    client = WsSubscriptionsClient(
        base_url="http://localhost:2428",
        endpoint="/ws",
        keypair=keypair
    )

    # Connect and subscribe
    await client.connect()
    client.subscribe(["your_application_id"])

    # Add callback for received messages
    def callback(data):
        print("Received update:", data)

    client.add_callback(callback)

    # Keep the connection alive
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

For detailed documentation, please visit [our documentation site](https://docs.calimero.network).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 

## Development

### Setting Up Development Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[test]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=calimero

# Run specific test file
pytest tests/test_keypair.py
```

### Building and Publishing

```bash
# Install build tools
pip install --upgrade build twine

# Build the package
python -m build

# Publish to PyPI
twine upload dist/*
``` 