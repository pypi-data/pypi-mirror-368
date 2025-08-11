"""
Key Vault SDK - Python SDK for accessing Key Vault API keys and values

Usage:
    from key_vault_sdk import KeyVault
    
    kv = KeyVault(api_url="https://yourdomain.com/api", token="your-api-token")
    keys = kv.list_keys(folder_id="folder-id")
    key_value = kv.get_key_value(key_id="key-id")
"""

from .client import KeyVault, KeyVaultError, KeyVaultAuthError, KeyVaultNotFoundError

__version__ = "1.0.2"
__all__ = ["KeyVault", "KeyVaultError", "KeyVaultAuthError", "KeyVaultNotFoundError"] 