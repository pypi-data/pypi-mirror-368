# Key Vault Python SDK

A Python SDK for securely accessing your Key Vault API keys and secrets.

## Installation

```bash
pip install amay-key-vault-sdk
```

## Quick Start

```python
from key_vault_sdk import KeyVault

# Initialize the SDK
kv = KeyVault(
    api_url="https://yourdomain.com/api",
    token="your-api-token"
)

# Get a key by name
api_key = kv.get_key_by_name("folder-id", "stripe-secret-key")
print(f"API Key: {api_key}")

# List all keys in a folder
result = kv.list_keys(folder_id="folder-id", limit=50)
print(f"Found {len(result['keys'])} keys")

# Get multiple keys at once
keys = kv.get_multiple_keys(
    folder_id="folder-id",
    key_names=["stripe-key", "database-password", "api-secret"]
)
print(f"Retrieved {len(keys)} keys")
```

## Features

- 🔐 **Secure Access**: All keys are encrypted and securely transmitted
- 📁 **Folder Support**: Organize keys in hierarchical folders
- 🔍 **Search & Filter**: Find keys by name, type, or tags
- 📊 **Statistics**: Get usage statistics and folder information
- 🔄 **Auto Refresh**: Automatic token refresh handling
- 🛡️ **Error Handling**: Comprehensive error handling with specific exceptions

## API Reference

### Authentication

```python
from key_vault_sdk import KeyVault

kv = KeyVault(
    api_url="https://yourdomain.com/api",
    token="your-api-token",
    timeout=30  # Optional: request timeout in seconds
)
```

### Key Operations

#### Get Key by Name
```python
# Get a key's value by name (convenience method)
api_key = kv.get_key_by_name("folder-id", "stripe-secret-key")
```

#### Get Key by ID
```python
# Get key metadata only
key = kv.get_key("key-id")

# Get key with decrypted value
key_with_value = kv.get_key("key-id", include_value=True)
print(f"Key: {key_with_value['name']}, Value: {key_with_value['value']}")
```

#### List Keys
```python
# List keys in a folder with pagination
result = kv.list_keys(
    folder_id="folder-id",
    limit=20,  # Number of keys to return
    offset=0   # Number of keys to skip
)

print(f"Found {result['total']} keys")
for key in result['keys']:
    print(f"- {key['name']} ({key['type']})")
```

#### Get Multiple Keys
```python
# Get multiple keys by name
keys = kv.get_multiple_keys(
    folder_id="folder-id",
    key_names=["stripe-key", "database-password", "api-secret"]
)

for name, value in keys.items():
    if value:
        print(f"{name}: {value}")
    else:
        print(f"{name}: Not found")
```

### Folder Operations

#### List Folders
```python
# List all folders with hierarchical structure
folders = kv.list_folders()
print(f"Found {len(folders['folders'])} root folders")

# List folders within a specific project
project_folders = kv.list_folders(project_id="project-id")
```

#### List Projects
```python
# List only root folders (projects)
projects = kv.list_projects()
for project in projects:
    print(f"Project: {project['name']} (ID: {project['id']})")
```

#### Get Folder Details
```python
# Get a specific folder with its contents
folder_data = kv.get_folder("folder-id")
print(f"Folder: {folder_data['folder']['name']}")
print(f"Contains {len(folder_data['keys'])} keys")
```

### Search Operations

#### Search Keys
```python
# Search for keys across all folders
results = kv.search_keys(
    search="database",
    key_type="PASSWORD",
    favorite=True,
    limit=20
)

print(f"Found {len(results['keys'])} database passwords")
```

### Utility Methods

#### Test Connection
```python
# Test the connection to the Key Vault API
if kv.test_connection():
    print("Connection successful!")
else:
    print("Connection failed!")
```

#### Get Statistics
```python
# Get folder and key statistics
stats = kv.get_stats()
print(f"Total keys: {stats['totalKeys']}")
print(f"Total folders: {stats['folders']}")
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from key_vault_sdk import KeyVaultError, KeyVaultAuthError, KeyVaultNotFoundError

try:
    key = kv.get_key("key-id")
except KeyVaultAuthError:
    print("Authentication failed - check your token")
except KeyVaultNotFoundError:
    print("Key not found")
except KeyVaultError as e:
    print(f"API error: {e}")
```

## Examples

### Complete Example
```python
from key_vault_sdk import KeyVault

def main():
    # Initialize SDK
    kv = KeyVault(
        api_url="https://yourdomain.com/api",
        token="your-api-token"
    )
    
    try:
        # Test connection
        if not kv.test_connection():
            print("Failed to connect to Key Vault")
            return
        
        # List projects
        projects = kv.list_projects()
        print(f"Available projects: {len(projects)}")
        
        # Get keys from first project
        if projects:
            project_id = projects[0]['id']
            result = kv.list_keys(folder_id=project_id, limit=10)
            
            print(f"Keys in {projects[0]['name']}:")
            for key in result['keys']:
                print(f"- {key['name']} ({key['type']})")
                
                # Get key value if needed
                if key['type'] == 'API_KEY':
                    key_with_value = kv.get_key(key['id'], include_value=True)
                    print(f"  Value: {key_with_value['value']}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
```

## Development

### Local Testing
For local development, use the local server URL:

```python
kv = KeyVault(
    api_url="http://localhost:3000/api",
    token="your-local-token"
)
```

### Running Tests
```bash
cd python-sdk
python -m pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: https://github.com/amaykorade/key-vault/issues
- Documentation: https://github.com/amaykorade/key-vault#readme 