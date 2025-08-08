"""
Simple DoorDash API client.
"""

import uuid
from typing import Any, Dict, Optional

import httpx

from .exceptions import APIError, NetworkError


class DoorDashClient:
    """Simple client for the DoorDash API."""
    
    def __init__(
        self,
        org_id: str,
        base_url: str = "https://apparel-scraper--doordash-session-system-fastapi-app.modal.run",
        client_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the DoorDash client.
        
        Args:
            org_id: Organization ID for API access (serves as both ID and API key)
            base_url: Base URL for the DoorDash API
            client_id: Optional client ID (will be generated if not provided)
            timeout: Request timeout in seconds
        """
        self.org_id = org_id
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id or str(uuid.uuid4())
        self.timeout = timeout
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "X-Org-ID": self.org_id,
            "Content-Type": "application/json",
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response.json() if response.content else {}
            except httpx.HTTPStatusError as e:
                raise APIError(f"API error: {e.response.text}", e.response.status_code)
            except httpx.RequestError as e:
                raise NetworkError(f"Network error: {str(e)}")
    
    # Session Management
    def acquire_session(self, ttl_minutes: int = 5, **kwargs) -> Dict[str, Any]:
        """Acquire a session."""
        data = {"client_id": self.client_id, "ttl_minutes": ttl_minutes, **kwargs}
        return self._request("POST", "/sessions/acquire", json=data)
    
    def release_session(self) -> Dict[str, Any]:
        """Release the session."""
        return self._request("POST", f"/sessions/{self.client_id}/release")
    
    # Health & Status
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        return self._request("GET", "/health")
    
    def system_status(self) -> Dict[str, Any]:
        """Get system status."""
        return self._request("GET", "/system/status")
    
    # Restaurant Search
    def search_restaurants(self, query: Optional[str] = None, lat: Optional[float] = None, 
                          lng: Optional[float] = None, limit: int = 10) -> Dict[str, Any]:
        """Search for restaurants."""
        data = {"client_id": self.client_id}
        if query: data["query"] = query
        if lat: data["lat"] = lat  
        if lng: data["lng"] = lng
        if limit: data["limit"] = limit
        return self._request("POST", f"/sessions/{self.client_id}/restaurants/search", json=data)
    
    def get_restaurant(self, store_id: int) -> Dict[str, Any]:
        """Get restaurant details."""
        return self._request("GET", f"/sessions/{self.client_id}/restaurants/{store_id}")
    
    def get_menu_item(self, store_id: int, item_id: int) -> Dict[str, Any]:
        """Get menu item details."""
        return self._request("GET", f"/sessions/{self.client_id}/restaurants/{store_id}/items/{item_id}")
    
    # Cart Management  
    def add_to_cart(self, store_id: int, item_id: int, quantity: int = 1, **kwargs) -> Dict[str, Any]:
        """Add item to cart."""
        data = {"store_id": store_id, "item_id": item_id, "quantity": quantity, **kwargs}
        return self._request("POST", f"/sessions/{self.client_id}/cart/add", json=data)
    
    def view_cart(self) -> Dict[str, Any]:
        """View current cart."""
        return self._request("GET", f"/sessions/{self.client_id}/cart")
    
    def clear_carts(self) -> Dict[str, Any]:
        """Clear all carts."""
        return self._request("POST", f"/sessions/{self.client_id}/clear-carts")
    
    def get_bundle_opportunities(self, cart_id: str) -> Dict[str, Any]:
        """Get multi-store bundle opportunities."""
        return self._request("GET", f"/sessions/{self.client_id}/cart/{cart_id}/bundle-opportunities")
    
    # Orders
    def place_order(self, tip_amount: float = 0.0, **kwargs) -> Dict[str, Any]:
        """Place an order."""
        data = {"client_id": self.client_id, "tip_amount": tip_amount, **kwargs}
        return self._request("POST", f"/sessions/{self.client_id}/orders/place", json=data)
    
    # Addresses
    def get_addresses(self) -> Dict[str, Any]:
        """Get user addresses (user-level endpoint)."""
        return self._request("GET", f"/users/{self.client_id}/addresses")
    
    def add_address(self, street: str, city: str, state: str, zipcode: str, **kwargs) -> Dict[str, Any]:
        """Add a new address."""
        data = {"street": street, "city": city, "state": state, "zipcode": zipcode, **kwargs}
        return self._request("POST", f"/users/{self.client_id}/addresses", json=data)
    
    def get_address_suggestions(self, query: str) -> Dict[str, Any]:
        """Get address suggestions."""
        data = {"query": query}
        return self._request("POST", f"/sessions/{self.client_id}/address/suggestions", json=data)
    
    def get_standalone_address_suggestions(self, address_input: str) -> Dict[str, Any]:
        """Get standalone address suggestions without requiring an active session.
        
        This endpoint is designed for use during user registration to help users
        find and validate their addresses before creating an account.
        
        Args:
            address_input: Partial address input (e.g., "123 Main St, San Francisco")
            
        Returns:
            Dict containing suggestions with formatted addresses, coordinates, and market info
        """
        data = {"address_input": address_input}
        return self._request("POST", "/address/suggestions", json=data)
    
    # Payment Methods
    def get_payment_methods(self) -> Dict[str, Any]:
        """Get payment methods."""
        return self._request("GET", f"/users/{self.client_id}/payment_methods")
    
    def add_payment_method(self, **kwargs) -> Dict[str, Any]:
        """Add payment method."""
        return self._request("POST", f"/users/{self.client_id}/payment_methods", json=kwargs)
    
    def get_credit_balance(self) -> Dict[str, Any]:
        """Get account credit balance."""
        return self._request("GET", f"/users/{self.client_id}/credit-balance")
    
    # Grocery 
    def browse_grocery(self, store_id: int) -> Dict[str, Any]:
        """Browse grocery store."""
        return self._request("GET", f"/sessions/{self.client_id}/grocery/{store_id}/browse")
    
    def search_grocery(self, store_id: int, query: str) -> Dict[str, Any]:
        """Search grocery items."""
        data = {"query": query}
        return self._request("POST", f"/sessions/{self.client_id}/grocery/{store_id}/search", json=data)
    
    # Snapshots
    def save_snapshot(self) -> Dict[str, Any]:
        """Save session snapshot."""
        return self._request("POST", f"/sessions/{self.client_id}/snapshot/save")
    
    def restore_snapshot(self) -> Dict[str, Any]:
        """Restore session snapshot."""
        return self._request("POST", f"/sessions/{self.client_id}/snapshot/restore")