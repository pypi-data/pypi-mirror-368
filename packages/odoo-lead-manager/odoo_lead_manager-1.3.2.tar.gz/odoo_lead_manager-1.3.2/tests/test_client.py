"""
Tests for OdooClient class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from odoorpc import ODOO
from odoo_lead_manager.client import OdooClient


class TestOdooClient:
    """Test cases for OdooClient."""
    
    def test_initialization_with_parameters(self):
        """Test client initialization with provided parameters."""
        client = OdooClient(
            host="test.example.com",
            port=8069,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        
        assert client.host == "test.example.com"
        assert client.port == 8069
        assert client.database == "test_db"
        assert client.username == "test_user"
        assert client.password == "test_pass"
    
    def test_initialization_with_env_vars(self):
        """Test client initialization with environment variables."""
        with patch.dict('os.environ', {
            'ODOO_HOST': 'env.example.com',
            'ODOO_PORT': '8080',
            'ODOO_DB': 'env_db',
            'ODOO_USERNAME': 'env_user',
            'ODOO_PASSWORD': 'env_pass'
        }):
            client = OdooClient()
            
            assert client.host == "env.example.com"
            assert client.port == 8080
            assert client.database == "env_db"
            assert client.username == "env_user"
            assert client.password == "env_pass"
    
    def test_default_initialization(self):
        """Test client initialization with default values."""
        client = OdooClient()
        
        assert client.host == "localhost"
        assert client.port == 8069
        assert client.database == "odoo"
        assert client.username == "admin"
        assert client.password == "admin"
    
    @patch('odoo_lead_manager.client.odoorpc.ODOO')
    def test_connect_success(self, mock_odoo_class):
        """Test successful connection to Odoo."""
        mock_odoo = Mock()
        mock_odoo_class.return_value = mock_odoo
        
        client = OdooClient()
        client.connect()
        
        mock_odoo_class.assert_called_once_with(
            host="localhost",
            port=8069,
            protocol="jsonrpc",
            timeout=120
        )
        assert client._odoo == mock_odoo
    
    @patch('odoo_lead_manager.client.odoorpc.ODOO')
    def test_authenticate_success(self, mock_odoo_class):
        """Test successful authentication."""
        mock_odoo = Mock()
        mock_odoo.login.return_value = 42
        mock_odoo_class.return_value = mock_odoo
        
        client = OdooClient()
        client.authenticate()
        
        mock_odoo.login.assert_called_once_with("odoo", "admin", "admin")
        assert client._uid == 42
    
    def test_is_connected_true(self, mock_odoo_client):
        """Test is_connected returns True when connected."""
        mock_odoo = Mock()
        mock_odoo.version.return_value = "15.0"
        mock_odoo_client._odoo = mock_odoo
        
        assert mock_odoo_client.is_connected() is True
    
    def test_is_connected_false(self, mock_odoo_client):
        """Test is_connected returns False when not connected."""
        mock_odoo_client._odoo = None
        assert mock_odoo_client.is_connected() is False
        
        # Test with exception
        mock_odoo = Mock()
        mock_odoo.version.side_effect = Exception("Connection error")
        mock_odoo_client._odoo = mock_odoo
        assert mock_odoo_client.is_connected() is False
    
    def test_get_model(self, mock_odoo_client):
        """Test getting a model proxy."""
        mock_model = Mock()
        mock_odoo_client.odoo.env = {"res.partner": mock_model}
        
        result = mock_odoo_client.get_model("res.partner")
        assert result == mock_model
    
    def test_search_read(self, mock_odoo_client):
        """Test search_read method."""
        mock_model = Mock()
        mock_model.search_read.return_value = [
            {"id": 1, "name": "Test Lead"},
            {"id": 2, "name": "Test Lead 2"}
        ]
        mock_odoo_client.get_model.return_value = mock_model
        
        result = mock_odoo_client.search_read(
            "res.partner",
            domain=[["status", "=", "new"]],
            fields=["id", "name"],
            limit=10
        )
        
        mock_model.search_read.assert_called_once_with(
            domain=[["status", "=", "new"]],
            fields=["id", "name"],
            limit=10,
            offset=0,
            order=None
        )
        
        assert len(result) == 2
        assert result[0]["name"] == "Test Lead"
    
    def test_search_count(self, mock_odoo_client):
        """Test search_count method."""
        mock_model = Mock()
        mock_model.search_count.return_value = 42
        mock_odoo_client.get_model.return_value = mock_model
        
        result = mock_odoo_client.search_count("res.partner", [["status", "=", "new"]])
        
        mock_model.search_count.assert_called_once_with([["status", "=", "new"]])
        assert result == 42
    
    def test_write(self, mock_odoo_client):
        """Test write method."""
        mock_model = Mock()
        mock_model.write.return_value = True
        mock_odoo_client.get_model.return_value = mock_model
        
        result = mock_odoo_client.write("res.partner", [1, 2], {"status": "won"})
        
        mock_model.write.assert_called_once_with([1, 2], {"status": "won"})
        assert result is True
    
    def test_create(self, mock_odoo_client):
        """Test create method."""
        mock_model = Mock()
        mock_model.create.return_value = 123
        mock_odoo_client.get_model.return_value = mock_model
        
        result = mock_odoo_client.create("res.partner", {"name": "New Lead"})
        
        mock_model.create.assert_called_once_with({"name": "New Lead"})
        assert result == 123
    
    def test_unlink(self, mock_odoo_client):
        """Test unlink method."""
        mock_model = Mock()
        mock_model.unlink.return_value = True
        mock_odoo_client.get_model.return_value = mock_model
        
        result = mock_odoo_client.unlink("res.partner", [1, 2, 3])
        
        mock_model.unlink.assert_called_once_with([1, 2, 3])
        assert result is True
    
    def test_get_user_info(self, mock_odoo_client):
        """Test get_user_info method."""
        mock_odoo_client.search_read.return_value = [
            {"id": 1, "name": "Test User", "email": "test@example.com", "login": "test", "active": True}
        ]
        
        result = mock_odoo_client.get_user_info(1)
        
        mock_odoo_client.search_read.assert_called_once_with(
            "res.users",
            domain=[["id", "=", 1]],
            fields=["id", "name", "email", "login", "active"]
        )
        
        assert result["name"] == "Test User"
        assert result["email"] == "test@example.com"
    
    def test_close(self, mock_odoo_client):
        """Test close method."""
        mock_odoo = Mock()
        mock_odoo_client._odoo = mock_odoo
        
        mock_odoo_client.close()
        
        mock_odoo.logout.assert_called_once()
        assert mock_odoo_client._odoo is None
        assert mock_odoo_client._uid is None
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with patch('odoo_lead_manager.client.odoorpc.ODOO') as mock_odoo_class:
            mock_odoo = Mock()
            mock_odoo_class.return_value = mock_odoo
            
            with OdooClient() as client:
                assert client.is_connected() is True
            
            mock_odoo.logout.assert_called_once()
    
    def test_connection_error_handling(self):
        """Test error handling during connection."""
        with patch('odoo_lead_manager.client.odoorpc.ODOO') as mock_odoo_class:
            mock_odoo_class.side_effect = Exception("Connection failed")
            
            client = OdooClient()
            with pytest.raises(ConnectionError):
                client.connect()
    
    def test_authentication_error_handling(self):
        """Test error handling during authentication."""
        with patch('odoo_lead_manager.client.odoorpc.ODOO') as mock_odoo_class:
            mock_odoo = Mock()
            mock_odoo.login.side_effect = Exception("Authentication failed")
            mock_odoo_class.return_value = mock_odoo
            
            client = OdooClient()
            with pytest.raises(PermissionError):
                client.authenticate()