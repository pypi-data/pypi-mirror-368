"""
Basic tests for DoorDash client.
"""

import pytest
from unittest.mock import Mock, patch
from doordash_client import DoorDashClient, APIError, NetworkError


def test_client_initialization():
    """Test client initialization."""
    client = DoorDashClient(org_id="test-org")
    
    assert client.org_id == "test-org"
    assert client.base_url == "https://apparel-scraper--doordash-session-system-fastapi-app.modal.run"
    assert client.timeout == 30.0
    assert client.client_id is not None


def test_client_custom_params():
    """Test client with custom parameters.""" 
    client = DoorDashClient(
        org_id="test-org",
        base_url="https://custom.example.com",
        client_id="custom-id",
        timeout=60.0
    )
    
    assert client.org_id == "test-org"
    assert client.base_url == "https://custom.example.com"
    assert client.client_id == "custom-id"
    assert client.timeout == 60.0


@patch('httpx.Client')
def test_health_check_success(mock_client):
    """Test successful health check."""
    # Mock response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"status": "healthy"}
    mock_response.content = b'{"status": "healthy"}'
    
    mock_client_instance = Mock()
    mock_client_instance.request.return_value = mock_response
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    client = DoorDashClient(org_id="test-org")
    result = client.health_check()
    
    assert result == {"status": "healthy"}
    mock_client_instance.request.assert_called_once_with(
        "GET",
        "https://apparel-scraper--doordash-session-system-fastapi-app.modal.run/health",
        headers={
            "X-Org-ID": "test-org",
            "Content-Type": "application/json"
        }
    )


@patch('httpx.Client')
def test_api_error_handling(mock_client):
    """Test API error handling."""
    # Mock HTTP error
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    from httpx import HTTPStatusError, Request
    mock_request = Mock(spec=Request)
    
    mock_client_instance = Mock()
    mock_client_instance.request.side_effect = HTTPStatusError(
        "Bad Request", request=mock_request, response=mock_response
    )
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    client = DoorDashClient(org_id="test-org")
    
    with pytest.raises(APIError) as exc_info:
        client.health_check()
    
    assert "API error" in str(exc_info.value)
    assert exc_info.value.status_code == 400


@patch('httpx.Client')
def test_network_error_handling(mock_client):
    """Test network error handling."""
    from httpx import RequestError
    
    mock_client_instance = Mock()
    mock_client_instance.request.side_effect = RequestError("Connection failed")
    mock_client.return_value.__enter__.return_value = mock_client_instance
    
    client = DoorDashClient(org_id="test-org")
    
    with pytest.raises(NetworkError) as exc_info:
        client.health_check()
    
    assert "Network error" in str(exc_info.value)


def test_search_restaurants_params():
    """Test restaurant search parameter building."""
    client = DoorDashClient(org_id="test-org")
    
    with patch.object(client, '_request') as mock_request:
        mock_request.return_value = {"results": []}
        
        client.search_restaurants(
            query="pizza",
            lat=40.7128,
            lng=-74.0060,
            limit=5
        )
        
        mock_request.assert_called_once_with(
            "POST",
            f"/sessions/{client.client_id}/restaurants/search",
            json={
                "client_id": client.client_id,
                "query": "pizza",
                "lat": 40.7128,
                "lng": -74.0060,
                "limit": 5
            }
        )


def test_add_to_cart_params():
    """Test add to cart parameter building."""
    client = DoorDashClient(org_id="test-org")
    
    with patch.object(client, '_request') as mock_request:
        mock_request.return_value = {"success": True}
        
        client.add_to_cart(
            store_id=123,
            item_id=456,
            quantity=2,
            special_instructions="No onions"
        )
        
        mock_request.assert_called_once_with(
            "POST", 
            f"/sessions/{client.client_id}/cart/add",
            json={
                "store_id": 123,
                "item_id": 456,
                "quantity": 2,
                "special_instructions": "No onions"
            }
        )