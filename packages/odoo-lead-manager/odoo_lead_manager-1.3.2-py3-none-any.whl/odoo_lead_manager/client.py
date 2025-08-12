"""
Core Odoo API connection module using xmlrpc.client.

This module provides a robust client for connecting to Odoo instances
and handling authentication, connection pooling, and error handling.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import xmlrpc.client
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class ModelProxy:
    """
    A proxy class for interacting with Odoo models via XML-RPC.
    """
    
    def __init__(self, client: 'OdooClient', model_name: str):
        """
        Initialize the model proxy.
        
        Args:
            client: The OdooClient instance
            model_name: Name of the Odoo model
        """
        self.client = client
        self.model_name = model_name
    
    def search_read(self, domain=None, fields=None, limit=None, offset=0, order=None):
        """
        Search and read records from the model.
        
        Args:
            domain: Search domain/filter
            fields: List of fields to read
            limit: Maximum number of records to return
            offset: Number of records to skip
            order: Sort order
            
        Returns:
            List of dictionaries with record data
        """
        if domain is None:
            domain = []
        if fields is None:
            fields = []
            
        return self.client.object.execute_kw(
            self.client.database,
            self.client.uid,
            self.client.password,
            self.model_name,
            'search_read',
            [domain],
            {'fields': fields, 'limit': limit, 'offset': offset, 'order': order}
        )
    
    def search_count(self, domain=None):
        """
        Count records matching the domain.
        
        Args:
            domain: Search domain/filter
            
        Returns:
            Number of matching records
        """
        if domain is None:
            domain = []
            
        return self.client.object.execute_kw(
            self.client.database,
            self.client.uid,
            self.client.password,
            self.model_name,
            'search_count',
            [domain]
        )
    
    def write(self, record_ids, values):
        """
        Write values to records.
        
        Args:
            record_ids: List of record IDs to update
            values: Dictionary of values to write
            
        Returns:
            True if successful
        """
        return self.client.object.execute_kw(
            self.client.database,
            self.client.uid,
            self.client.password,
            self.model_name,
            'write',
            [record_ids, values]
        )
    
    def create(self, values):
        """
        Create a new record.
        
        Args:
            values: Dictionary of values for the new record
            
        Returns:
            ID of the created record
        """
        return self.client.object.execute_kw(
            self.client.database,
            self.client.uid,
            self.client.password,
            self.model_name,
            'create',
            [values]
        )
    
    def unlink(self, record_ids):
        """
        Delete records.
        
        Args:
            record_ids: List of record IDs to delete
            
        Returns:
            True if successful
        """
        return self.client.object.execute_kw(
            self.client.database,
            self.client.uid,
            self.client.password,
            self.model_name,
            'unlink',
            [record_ids]
        )


class OdooClient:
    """
    A robust client for connecting to Odoo instances using the xmlrpc library.
    
    This class handles authentication, connection management, and provides
    convenient methods for interacting with Odoo models via XML-RPC.
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        protocol: str = "http",
        timeout: int = 120
    ):
        """
        Initialize Odoo client with connection parameters.
        
        Args:
            host: Odoo server hostname or URL (defaults to ODOO_HOST env var)
            port: Odoo server port (optional, defaults to standard port 8069)
            database: Database name (defaults to ODOO_DB env var)
            username: Username (defaults to ODOO_USERNAME env var)
            password: Password (defaults to ODOO_PASSWORD env var)
            protocol: Connection protocol (http/https)
            timeout: Connection timeout in seconds
        """
        # Parse host to handle full URLs
        raw_host = host or os.getenv("ODOO_HOST", "localhost")
        
        # Handle URL parsing if host includes protocol
        if raw_host.startswith(('http://', 'https://')):
            from urllib.parse import urlparse
            parsed = urlparse(raw_host)
            self.host = parsed.hostname
            self.protocol = parsed.scheme
            # Use port from URL only, don't add default port
            self.port = parsed.port
            # If no port in URL, use None (let protocol default handle it)
            if self.port is None and port is None:
                self.port = None
            elif port is not None:
                self.port = port
        else:
            # Handle non-URL host
            self.host = raw_host
            self.port = port or 8069
            self.protocol = protocol
            
        self.database = database or os.getenv("ODOO_DB", "odoo")
        self.username = username or os.getenv("ODOO_USERNAME", "admin")
        self.password = password or os.getenv("ODOO_PASSWORD", "admin")
        self.timeout = timeout
        
        self._common: Optional[xmlrpc.client.ServerProxy] = None
        self._object: Optional[xmlrpc.client.ServerProxy] = None
        self._uid: Optional[int] = None
        
    @property
    def common(self) -> xmlrpc.client.ServerProxy:
        """Get the common XML-RPC endpoint."""
        if self._common is None:
            self.connect()
        return self._common
    
    @property
    def object(self) -> xmlrpc.client.ServerProxy:
        """Get the object XML-RPC endpoint."""
        if self._object is None:
            self.connect()
        return self._object
    
    @property
    def uid(self) -> int:
        """Get the user ID."""
        if self._uid is None:
            self.authenticate()
        return self._uid
    
    def connect(self) -> None:
        """Establish connection to Odoo server."""
        try:
            # Auto-detect protocol based on common Odoo configurations
            protocols_to_try = []
            
            # If protocol was explicitly set or detected from URL, try it first
            if self.protocol in ["http", "https"]:
                protocols_to_try.append(self.protocol)
            else:
                # Common Odoo configurations:
                # - HTTP on 8069 (default)
                # - HTTPS on 443 or custom HTTPS port
                if self.port == 8069:
                    protocols_to_try.append("http")
                elif self.port == 443:
                    protocols_to_try.append("https")
                else:
                    # Try both protocols
                    protocols_to_try.extend(["http", "https"])
            
            # Try each protocol
            last_error = None
            for protocol in protocols_to_try:
                try:
                    base_url = f"{protocol}://{self.host}"
                    # Only add port if it's explicitly provided and not the default for the protocol
                    if self.port is not None and \
                       not (protocol == "http" and self.port == 80) and \
                       not (protocol == "https" and self.port == 443):
                        base_url += f":{self.port}"
                    
                    import socket
                    socket.setdefaulttimeout(self.timeout)
                    
                    if protocol == "https":
                        import ssl
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        
                        common = xmlrpc.client.ServerProxy(
                            f"{base_url}/xmlrpc/2/common", 
                            context=ssl_context,
                            allow_none=True
                        )
                        object = xmlrpc.client.ServerProxy(
                            f"{base_url}/xmlrpc/2/object", 
                            context=ssl_context,
                            allow_none=True
                        )
                    else:
                        common = xmlrpc.client.ServerProxy(f"{base_url}/xmlrpc/2/common", allow_none=True)
                        object = xmlrpc.client.ServerProxy(f"{base_url}/xmlrpc/2/object", allow_none=True)
                    
                    # Test the connection
                    common.version()
                    
                    # Success - set the endpoints
                    self._common = common
                    self._object = object
                    self.protocol = protocol  # Update protocol if we tried both
                    
                    logger.info(f"Connected to Odoo XML-RPC at {base_url}")
                    return
                    
                except Exception as e:
                    last_error = e
                    logger.debug(f"Failed to connect with {protocol}: {e}")
                    continue
            
            # All protocols failed
            raise last_error or ConnectionError("Failed to connect to Odoo")
            
        except Exception as e:
            logger.error(f"Failed to connect to Odoo: {e}")
            raise ConnectionError(f"Failed to connect to Odoo: {e}")
    
    def authenticate(self) -> None:
        """Authenticate with Odoo using provided credentials."""
        try:
            # Use the common endpoint to authenticate
            self._uid = self.common.authenticate(self.database, self.username, self.password, {})
            if not self._uid:
                raise PermissionError("Invalid credentials")
            logger.info(f"Authenticated as user ID: {self._uid}")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise PermissionError(f"Authentication failed: {e}")
    
    def is_connected(self) -> bool:
        """Check if connection to Odoo is active."""
        if self._common is None:
            return False
        try:
            self._common.version()
            return True
        except Exception:
            return False
    
    def get_model(self, model_name: str):
        """Get a model proxy for the specified model."""
        return ModelProxy(self, model_name)
    
    def search_read(
        self,
        model_name: str,
        domain: List[Any] = None,
        fields: List[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search and read records from a model.
        
        Args:
            model_name: Name of the Odoo model
            domain: Search domain/filter
            fields: List of fields to read
            limit: Maximum number of records to return (default: 1000)
            offset: Number of records to skip
            order: Sort order
            
        Returns:
            List of dictionaries with record data
        """
        if domain is None:
            domain = []
        if fields is None:
            fields = []
        if limit is None:
            limit = 1000
            
        try:
            model = self.get_model(model_name)
            records = model.search_read(
                domain=domain,
                fields=fields,
                limit=limit,
                offset=offset,
                order=order
            )
            logger.debug(f"Retrieved {len(records)} records from {model_name}")
            return records
        except Exception as e:
            logger.error(f"Error searching {model_name}: {e}")
            raise RuntimeError(f"Error searching {model_name}: {e}")
    
    def search_count(self, model_name: str, domain: List[Any] = None) -> int:
        """
        Count records matching the domain.
        
        Args:
            model_name: Name of the Odoo model
            domain: Search domain/filter
            
        Returns:
            Number of matching records
        """
        if domain is None:
            domain = []
            
        try:
            model = self.get_model(model_name)
            count = model.search_count(domain)
            return count
        except Exception as e:
            logger.error(f"Error counting {model_name}: {e}")
            raise RuntimeError(f"Error counting {model_name}: {e}")
    
    def write(self, model_name: str, record_ids: List[int], values: Dict[str, Any]) -> bool:
        """
        Write values to records.
        
        Args:
            model_name: Name of the Odoo model
            record_ids: List of record IDs to update
            values: Dictionary of values to write
            
        Returns:
            True if successful
        """
        try:
            model = self.get_model(model_name)
            model.write(record_ids, values)
            logger.debug(f"Updated {len(record_ids)} records in {model_name}")
            return True
        except Exception as e:
            logger.error(f"Error writing to {model_name}: {e}")
            raise RuntimeError(f"Error writing to {model_name}: {e}")
    
    def create(self, model_name: str, values: Dict[str, Any]) -> int:
        """
        Create a new record.
        
        Args:
            model_name: Name of the Odoo model
            values: Dictionary of values for the new record
            
        Returns:
            ID of the created record
        """
        try:
            model = self.get_model(model_name)
            record_id = model.create(values)
            logger.debug(f"Created new record in {model_name} with ID: {record_id}")
            return record_id
        except Exception as e:
            logger.error(f"Error creating record in {model_name}: {e}")
            raise RuntimeError(f"Error creating record in {model_name}: {e}")
    
    def unlink(self, model_name: str, record_ids: List[int]) -> bool:
        """
        Delete records.
        
        Args:
            model_name: Name of the Odoo model
            record_ids: List of record IDs to delete
            
        Returns:
            True if successful
        """
        try:
            model = self.get_model(model_name)
            model.unlink(record_ids)
            logger.debug(f"Deleted {len(record_ids)} records from {model_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting records from {model_name}: {e}")
            raise RuntimeError(f"Error deleting records from {model_name}: {e}")
    
    def get_user_info(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get information about a user.
        
        Args:
            user_id: User ID (defaults to current user)
            
        Returns:
            Dictionary with user information
        """
        if user_id is None:
            user_id = self.uid
            
        return self.search_read(
            "res.users",
            domain=[["id", "=", user_id]],
            fields=["id", "name", "email", "login", "active"]
        )[0]
    
    def _get_config(self) -> Dict[str, Any]:
        """Get configuration details without sensitive credentials."""
        return {
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol,
            'db': self.database,
            'username': self.username,
            'timeout': self.timeout
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        if not self.is_connected():
            self.connect()
            self.authenticate()
        
        try:
            version = self.common.version()
            return {
                'server_version': version.get('server_version', 'Unknown'),
                'server_name': 'Odoo Server'
            }
        except Exception as e:
            logger.error(f"Error getting server info: {e}")
            return {'server_version': 'Unknown', 'server_name': 'Unknown'}
    
    def close(self) -> None:
        """Close the connection to Odoo."""
        self._common = None
        self._object = None
        self._uid = None
        logger.info("Disconnected from Odoo")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()