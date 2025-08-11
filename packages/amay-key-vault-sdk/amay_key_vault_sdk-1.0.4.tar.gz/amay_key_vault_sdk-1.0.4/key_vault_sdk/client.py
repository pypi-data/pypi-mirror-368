"""
Key Vault Client - Main client for interacting with the Key Vault API
"""

import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urljoin


class KeyVaultError(Exception):
    """Base exception for Key Vault SDK errors"""
    pass


class KeyVaultAuthError(KeyVaultError):
    """Authentication error"""
    pass


class KeyVaultNotFoundError(KeyVaultError):
    """Resource not found error"""
    pass


class KeyVault:
    """
    Key Vault SDK Client
    
    Provides a simple interface for accessing Key Vault API keys and folders.
    This SDK is read-only: key and folder creation, update, and deletion must be performed
    via the Key Vault web platform.
    """
    
    def __init__(self, api_url: str, token: str, timeout: int = 30):
        """
        Initialize the Key Vault client
        
        Args:
            api_url: Base URL of the Key Vault API (e.g., https://yourdomain.com/api)
            token: Your API token for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'User-Agent': f'KeyVault-Python-SDK/1.0.0'
        })
        self.permissions = None  # Cache for user permissions
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the Key Vault API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            API response as dictionary
            
        Raises:
            KeyVaultError: For API errors
            KeyVaultAuthError: For authentication errors
            KeyVaultNotFoundError: For not found errors
        """
        # Fix URL construction to preserve the /api path
        if endpoint.startswith('/'):
            url = self.api_url + endpoint
        else:
            url = self.api_url + '/' + endpoint
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Handle different response status codes
            if response.status_code == 401:
                raise KeyVaultAuthError("Invalid API token or token expired")
            elif response.status_code == 404:
                raise KeyVaultNotFoundError("Resource not found")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f'HTTP {response.status_code}')
                except:
                    error_msg = f'HTTP {response.status_code}: {response.text}'
                raise KeyVaultError(error_msg)
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError:
                raise KeyVaultError(f"Invalid JSON response: {response.text}")
                
        except requests.exceptions.Timeout:
            raise KeyVaultError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise KeyVaultError("Connection error")
        except requests.exceptions.RequestException as e:
            raise KeyVaultError(f"Request failed: {str(e)}")
    
    def list_keys(self, folder_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        List keys in a folder
        
        Args:
            folder_id: Folder ID to list keys from
            limit: Number of keys to return (default: 20, max: 100)
            offset: Number of keys to skip (default: 0)
            
        Returns:
            Dictionary containing keys list and pagination info
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> result = kv.list_keys(folder_id="folder-123", limit=50)
            >>> print(f"Found {len(result['keys'])} keys")
        """
        params = {
            'folderId': folder_id,
            'limit': min(limit, 100),  # Cap at 100
            'offset': offset
        }
        
        response = self._make_request('GET', '/keys', params=params)
        
        if not response.get('success', True):
            raise KeyVaultError(response.get('error', 'Failed to list keys'))
        
        return {
            'keys': response.get('keys', []),
            'total': response.get('total', 0),
            'limit': response.get('limit', limit),
            'offset': response.get('offset', offset)
        }
    
    def get_key(self, key_id: str, include_value: bool = False) -> Dict[str, Any]:
        """
        Get a key by ID
        
        Args:
            key_id: The key's ID
            include_value: If True, include the decrypted key value
            
        Returns:
            Key object with metadata and optionally the value
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> key = kv.get_key(key_id="key-123", include_value=True)
            >>> print(f"Key: {key['name']}, Value: {key['value']}")
        """
        params = {'includeValue': str(include_value).lower()}
        
        response = self._make_request('GET', f'/keys/{key_id}', params=params)
        
        if not response.get('success', True):
            raise KeyVaultError(response.get('error', 'Failed to fetch key'))
        
        return response.get('key', {})
    
    def get_key_by_name(self, folder_id: str, key_name: str) -> str:
        """
        Get a key's value by name (convenience method)
        
        Args:
            folder_id: Folder containing the key
            key_name: Name of the key to retrieve
            
        Returns:
            The decrypted key value as string
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> api_key = kv.get_key_by_name(folder_id="folder-123", key_name="stripe-secret-key")
            >>> print(f"API Key: {api_key}")
        """
        # First, list keys to find the one we want
        result = self.list_keys(folder_id=folder_id, limit=100)
        
        # Find the key by name
        key = next((k for k in result['keys'] if k['name'] == key_name), None)
        
        if not key:
            raise KeyVaultNotFoundError(f"Key '{key_name}' not found in folder")
        
        # Get the key with value
        key_with_value = self.get_key(key_id=key['id'], include_value=True)
        
        return key_with_value.get('value', '')
    
    def get_multiple_keys(self, folder_id: str, key_names: List[str]) -> Dict[str, str]:
        """
        Get multiple keys by name
        
        Args:
            folder_id: Folder containing the keys
            key_names: List of key names to retrieve
            
        Returns:
            Dictionary mapping key names to their values
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> keys = kv.get_multiple_keys(
            ...     folder_id="folder-123", 
            ...     key_names=["stripe-key", "database-password", "api-secret"]
            ... )
            >>> print(f"Retrieved {len(keys)} keys")
        """
        # Get all keys from the folder
        result = self.list_keys(folder_id=folder_id, limit=100)
        folder_keys = {k['name']: k for k in result['keys']}
        
        # Get values for requested keys
        keys_dict = {}
        for key_name in key_names:
            if key_name in folder_keys:
                key_with_value = self.get_key(
                    key_id=folder_keys[key_name]['id'], 
                    include_value=True
                )
                keys_dict[key_name] = key_with_value.get('value', '')
            else:
                keys_dict[key_name] = None  # Key not found
        
        return keys_dict

    def list_folders(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List all folders with hierarchical structure
        
        Args:
            project_id: If provided, only return folders within this project
            
        Returns:
            Dictionary containing folders list with hierarchical structure
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> # Get all folders
            >>> all_folders = kv.list_folders()
            >>> # Get folders within a specific project
            >>> project_folders = kv.list_folders(project_id="project-123")
            >>> print(f"Found {len(all_folders['folders'])} root folders")
        """
        if project_id:
            response = self._make_request('GET', f'/folders/tree?projectId={project_id}')
        else:
            response = self._make_request('GET', '/folders/tree')
        
        return {
            'folders': response.get('folders', [])
        }

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List only root folders (projects)
        
        Returns:
            List of project folders
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> projects = kv.list_projects()
            >>> for project in projects:
            ...     print(f"Project: {project['name']} (ID: {project['id']})")
        """
        response = self._make_request('GET', '/folders')
        return response.get('folders', [])

    def get_folder(self, folder_id: str) -> Dict[str, Any]:
        """
        Get a specific folder with its contents
        
        Args:
            folder_id: The folder's ID
            
        Returns:
            Dictionary containing folder object and its keys
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> folder_data = kv.get_folder(folder_id="folder-123")
            >>> print(f"Folder: {folder_data['folder']['name']}")
            >>> print(f"Contains {len(folder_data['keys'])} keys")
        """
        response = self._make_request('GET', f'/folders/{folder_id}')
        
        return {
            'folder': response.get('folder', {}),
            'keys': response.get('keys', [])
        }

    def search_keys(self, search: str, key_type: Optional[str] = None, 
                   favorite: Optional[bool] = None, limit: int = 20, 
                   offset: int = 0) -> Dict[str, Any]:
        """
        Search for keys across all folders
        
        Args:
            search: Search term
            key_type: Filter by key type (e.g., 'API_KEY', 'PASSWORD')
            favorite: Filter by favorite status
            limit: Number of keys to return (default: 20)
            offset: Number of keys to skip (default: 0)
            
        Returns:
            Dictionary containing search results and pagination info
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> results = kv.search_keys(search="database", key_type="PASSWORD")
            >>> print(f"Found {len(results['keys'])} database passwords")
        """
        params = {
            'search': search,
            'limit': limit,
            'offset': offset
        }
        
        if key_type:
            params['type'] = key_type
        if favorite is not None:
            params['favorite'] = str(favorite).lower()
        
        response = self._make_request('GET', '/keys', params=params)
        
        return {
            'keys': response.get('keys', []),
            'total': response.get('total', 0),
            'limit': response.get('limit', limit),
            'offset': response.get('offset', offset)
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get folder and key statistics
        
        Returns:
            Dictionary containing statistics about keys and folders
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> stats = kv.get_stats()
            >>> print(f"Total keys: {stats['totalKeys']}")
            >>> print(f"Total folders: {stats['folders']}")
        """
        response = self._make_request('GET', '/stats')
        return response.get('stats', {})

    def navigate_folder_tree(self, project_id: str) -> Dict[str, Any]:
        """
        Navigate through folder tree structure (convenience method)
        
        Args:
            project_id: The project ID to navigate
            
        Returns:
            Dictionary with folder tree and navigation helpers
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> tree = kv.navigate_folder_tree(project_id="project-123")
            >>> # Print folder structure
            >>> def print_tree(folders, level=0):
            ...     for folder in folders:
            ...         print("  " * level + f"📁 {folder['name']}")
            ...         if folder.get('children'):
            ...             print_tree(folder['children'], level + 1)
            >>> print_tree(tree['folders'])
        """
        folders = self.list_folders(project_id=project_id)
        
        def find_folder_by_name(folder_list, name):
            """Find a folder by name in the tree"""
            for folder in folder_list:
                if folder['name'] == name:
                    return folder
                if folder.get('children'):
                    found = find_folder_by_name(folder['children'], name)
                    if found:
                        return found
            return None
        
        def get_folder_path(folder_list, target_id, path=None):
            """Get the path to a folder"""
            if path is None:
                path = []
            
            for folder in folder_list:
                current_path = path + [folder]
                if folder['id'] == target_id:
                    return current_path
                if folder.get('children'):
                    found_path = get_folder_path(folder['children'], target_id, current_path)
                    if found_path:
                        return found_path
            return None
        
        return {
            'folders': folders['folders'],
            'find_folder_by_name': lambda name: find_folder_by_name(folders['folders'], name),
            'get_folder_path': lambda folder_id: get_folder_path(folders['folders'], folder_id)
        }
    
    def test_connection(self) -> bool:
        """
        Test the connection to the Key Vault API
        
        Returns:
            True if connection is successful
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> if kv.test_connection():
            ...     print("Connection successful!")
            ... else:
            ...     print("Connection failed!")
        """
        try:
            # Try to list folders as a connection test
            self.list_folders()
            return True
        except Exception:
            return False

    # RBAC Methods

    def load_permissions(self) -> List[str]:
        """
        Load user permissions from the server
        
        Returns:
            List of permission strings
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> permissions = kv.load_permissions()
            >>> print(f"User has {len(permissions)} permissions")
        """
        try:
            response = self._make_request('GET', '/auth/permissions')
            if response.get('permissions'):
                self.permissions = set(response['permissions'])
                return list(self.permissions)
            else:
                self.permissions = set()
                return []
        except Exception as e:
            print(f"Warning: Failed to load permissions: {e}")
            self.permissions = set()
            return []

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            permission: Permission to check (e.g., 'keys:read')
            
        Returns:
            True if user has permission
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> if kv.has_permission('keys:read'):
            ...     print("User can read keys")
            ... else:
            ...     print("User cannot read keys")
        """
        if self.permissions is None:
            self.load_permissions()
        return permission in self.permissions or '*' in self.permissions

    def has_any_permission(self, permissions: List[str]) -> bool:
        """
        Check if user has any of the specified permissions
        
        Args:
            permissions: List of permissions to check
            
        Returns:
            True if user has any of the permissions
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> if kv.has_any_permission(['keys:read', 'keys:write']):
            ...     print("User can read or write keys")
        """
        if self.permissions is None:
            self.load_permissions()
        return any(p in self.permissions or '*' in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: List[str]) -> bool:
        """
        Check if user has all of the specified permissions
        
        Args:
            permissions: List of permissions to check
            
        Returns:
            True if user has all permissions
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> if kv.has_all_permissions(['keys:read', 'keys:write']):
            ...     print("User can read and write keys")
        """
        if self.permissions is None:
            self.load_permissions()
        return all(p in self.permissions or '*' in self.permissions for p in permissions)

    def get_permissions(self) -> List[str]:
        """
        Get user's current permissions
        
        Returns:
            List of permission strings
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> permissions = kv.get_permissions()
            >>> for perm in permissions:
            ...     print(f"- {perm}")
        """
        if self.permissions is None:
            self.load_permissions()
        return list(self.permissions)

    def get_roles(self) -> List[Dict[str, Any]]:
        """
        Get user's roles
        
        Returns:
            List of role objects
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> roles = kv.get_roles()
            >>> for role in roles:
            ...     print(f"Role: {role['name']} - {role['description']}")
        """
        response = self._make_request('GET', '/auth/roles')
        return response.get('roles', [])

    def list_keys(self, folder_id: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        List keys in a folder (with RBAC permission check)
        
        Args:
            folder_id: Folder ID to list keys from
            limit: Number of keys to return (default: 20, max: 100)
            offset: Number of keys to skip (default: 0)
            
        Returns:
            Dictionary containing keys list and pagination info
            
        Raises:
            KeyVaultError: If user lacks 'keys:read' permission
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> result = kv.list_keys(folder_id="folder-123", limit=50)
            >>> print(f"Found {len(result['keys'])} keys")
        """
        # Check permission before making request
        if not self.has_permission('keys:read'):
            raise KeyVaultError("Insufficient permissions: keys:read required")

        params = {
            'folderId': folder_id,
            'limit': min(limit, 100),  # Cap at 100
            'offset': offset
        }
        
        response = self._make_request('GET', '/keys', params=params)
        
        if not response.get('success', True):
            raise KeyVaultError(response.get('error', 'Failed to list keys'))
        
        return {
            'keys': response.get('keys', []),
            'total': response.get('total', 0),
            'limit': response.get('limit', limit),
            'offset': response.get('offset', offset)
        }

    def get_key(self, key_id: str, include_value: bool = False) -> Dict[str, Any]:
        """
        Get a key by ID (with RBAC permission check)
        
        Args:
            key_id: The key's ID
            include_value: If True, include the decrypted key value
            
        Returns:
            Key object with metadata and optionally the value
            
        Raises:
            KeyVaultError: If user lacks 'keys:read' permission
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> key = kv.get_key(key_id="key-123", include_value=True)
            >>> print(f"Key: {key['name']}, Value: {key['value']}")
        """
        # Check permission before making request
        if not self.has_permission('keys:read'):
            raise KeyVaultError("Insufficient permissions: keys:read required")

        params = {'includeValue': str(include_value).lower()}
        
        response = self._make_request('GET', f'/keys/{key_id}', params=params)
        
        if not response.get('success', True):
            raise KeyVaultError(response.get('error', 'Failed to fetch key'))
        
        return response.get('key', {})

    def get_folder(self, folder_id: str) -> Dict[str, Any]:
        """
        Get a specific folder with its contents (with RBAC permission check)
        
        Args:
            folder_id: The folder's ID
            
        Returns:
            Dictionary containing folder object and its keys
            
        Raises:
            KeyVaultError: If user lacks 'folders:read' permission
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> folder_data = kv.get_folder(folder_id="folder-123")
            >>> print(f"Folder: {folder_data['folder']['name']}")
            >>> print(f"Contains {len(folder_data['keys'])} keys")
        """
        # Check permission before making request
        if not self.has_permission('folders:read'):
            raise KeyVaultError("Insufficient permissions: folders:read required")

        response = self._make_request('GET', f'/folders/{folder_id}')
        
        return {
            'folder': response.get('folder', {}),
            'keys': response.get('keys', [])
        }

    def get_keys_by_path(self, path: str, environment: Optional[str] = None, 
                         limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get keys by path (most user-friendly method)
        
        Args:
            path: Path like 'ProjectName/Subfolder' or 'ProjectName'
            environment: Filter by environment (DEVELOPMENT, STAGING, PRODUCTION, etc.)
            limit: Number of keys to return (default: 100)
            offset: Number of keys to skip (default: 0)
            
        Returns:
            Dictionary containing keys, total count, folder info, and path
            
        Raises:
            KeyVaultError: If path not found or other errors
            
        Example:
            >>> kv = KeyVault(api_url="https://yourdomain.com/api", token="your-token")
            >>> result = kv.get_keys_by_path('MyApp/Production')
            >>> print(f"Found {len(result['keys'])} keys in {result['path']}")
        """
        try:
            # Parse the path and find the target folder
            target_folder = self._resolve_path_to_folder(path)
            
            if not target_folder:
                raise KeyVaultError(f"Path not found: {path}")

            # Build query parameters
            params = {
                'folderId': target_folder['id'],
                'limit': min(limit, 100),
                'offset': offset
            }
            
            if environment:
                params['environment'] = environment.upper()

            # Fetch keys from the resolved folder
            response = self._make_request('GET', '/keys', params=params)
            
            if not response.get('success', True):
                raise KeyVaultError(response.get('error', 'Failed to fetch keys'))

            return {
                'keys': response.get('keys', []),
                'total': response.get('total', 0),
                'folder': target_folder,
                'path': path
            }

        except Exception as e:
            raise KeyVaultError(f"Failed to get keys by path '{path}': {str(e)}")

    def _resolve_path_to_folder(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to resolve a path to a folder object
        
        Args:
            path: Path like 'ProjectName/Subfolder/SubSubfolder'
            
        Returns:
            Folder object or None if not found
        """
        if not path or not isinstance(path, str):
            raise KeyVaultError("Path must be a non-empty string")

        path_parts = [part.strip() for part in path.split('/') if part.strip()]
        
        if not path_parts:
            raise KeyVaultError("Invalid path format")

        try:
            # First, get all projects to find the root project
            projects = self.list_projects()
            root_project = next((p for p in projects if 
                               p['name'].lower() == path_parts[0].lower()), None)

            if not root_project:
                raise KeyVaultError(f"Project not found: {path_parts[0]}")

            # If it's just a project name, return the project
            if len(path_parts) == 1:
                return root_project

            # Navigate through the path to find the target folder
            current_folder = root_project
            
            for i in range(1, len(path_parts)):
                part = path_parts[i]
                
                # Get subfolders of current folder
                folders_data = self.list_folders(project_id=root_project['id'])
                
                # Find the next folder in the path
                next_folder = self._find_folder_in_tree(folders_data.get('folders', []), part)
                
                if not next_folder:
                    raise KeyVaultError(f"Subfolder not found: {part} in path {path}")
                
                current_folder = next_folder

            return current_folder

        except Exception as e:
            raise KeyVaultError(f"Path resolution failed: {str(e)}")

    def _find_folder_in_tree(self, folders: List[Dict[str, Any]], folder_name: str) -> Optional[Dict[str, Any]]:
        """
        Helper method to find a folder by name in a folder tree
        
        Args:
            folders: Array of folders to search in
            folder_name: Name of the folder to find
            
        Returns:
            Found folder or None
        """
        for folder in folders:
            if folder['name'].lower() == folder_name.lower():
                return folder
            
            # Search in children recursively
            if 'children' in folder and folder['children']:
                found = self._find_folder_in_tree(folder['children'], folder_name)
                if found:
                    return found
        
        return None

    def get_project_keys(self, project_name: str, environment: Optional[str] = None, 
                        limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get keys from a project by name (convenience method)
        
        Args:
            project_name: Name of the project
            environment: Filter by environment
            limit: Number of keys to return
            offset: Number of keys to skip
            
        Returns:
            Same as get_keys_by_path
        """
        return self.get_keys_by_path(project_name, environment, limit, offset)

    def get_environment_keys(self, project_name: str, environment: str, 
                           limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get keys from a specific environment in a project (convenience method)
        
        Args:
            project_name: Name of the project
            environment: Environment name (DEVELOPMENT, STAGING, PRODUCTION, etc.)
            limit: Number of keys to return
            offset: Number of keys to skip
            
        Returns:
            Same as get_keys_by_path with environment filter
        """
        return self.get_keys_by_path(project_name, environment, limit, offset) 