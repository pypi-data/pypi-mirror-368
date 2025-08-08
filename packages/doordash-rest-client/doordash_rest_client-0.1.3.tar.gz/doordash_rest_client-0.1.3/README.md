# DoorDash Python Client

A simple Python client for the DoorDash API.

## Installation

```bash
pip install doordash-rest-client
```

## Quick Start

```python
from doordash_client import DoorDashClient

# Initialize client
client = DoorDashClient(
    org_id="your-org-id"
)

# Acquire a session (address required for new users)
client.acquire_session(
    name="John Doe",
    phone="555-1234", 
    address="123 Main St, New York, NY"
)

# Search for restaurants
restaurants = client.search_restaurants(query="pizza", lat=40.7128, lng=-74.0060)

# Add items to cart
client.add_to_cart(store_id=12345, item_id=67890, quantity=2)

# View cart
cart = client.view_cart()

# Place order
order = client.place_order(tip_amount=5.00)

# Release session when done
client.release_session()
```

## API Methods

### Session Management
- `acquire_session(ttl_minutes=60, **kwargs)` - Acquire a session (address required for new users)
- `release_session()` - Release the session (automatically saves address snapshots)
- `health_check()` - Check API health
- `system_status()` - Get system status

### 🏠 Address Isolation System
- **Complete Privacy**: Users never see other users' addresses
- **Automatic Management**: Address isolation happens transparently
- **Perfect Restoration**: Addresses restored exactly as saved across sessions
- **Zero Configuration**: No manual snapshot management required

### Restaurant Search
- `search_restaurants(query=None, lat=None, lng=None, limit=10)` - Search restaurants
- `get_restaurant(store_id)` - Get restaurant details
- `get_menu_item(store_id, item_id)` - Get menu item details

### Cart Management
- `add_to_cart(store_id, item_id, quantity=1, **kwargs)` - Add item to cart
- `view_cart()` - View current cart
- `clear_carts()` - Clear all carts
- `get_bundle_opportunities(cart_id)` - Get multi-store bundle options

### Orders
- `place_order(tip_amount=0.0, **kwargs)` - Place an order

### Addresses
- `get_addresses()` - Get user addresses
- `add_address(street, city, state, zipcode, **kwargs)` - Add new address
- `get_address_suggestions(query)` - Get address suggestions (requires session)
- `get_standalone_address_suggestions(address_input)` - Get address suggestions without session

### Payment Methods
- `get_payment_methods()` - Get payment methods
- `add_payment_method(**kwargs)` - Add payment method
- `get_credit_balance()` - Get account credit balance

### Grocery
- `browse_grocery(store_id)` - Browse grocery store
- `search_grocery(store_id, query)` - Search grocery items

### Snapshots
- `save_snapshot()` - Save session snapshot
- `restore_snapshot()` - Restore session snapshot

## Configuration

The client supports these initialization parameters:

- `org_id` (required): Your organization ID (serves as both ID and API key)
- `base_url`: API base URL (defaults to production)
- `client_id`: Optional client ID (auto-generated if not provided)
- `timeout`: Request timeout in seconds (default: 30.0)

## Error Handling

The client raises these exceptions:

- `APIError`: API returned an error response
- `NetworkError`: Network request failed
- `AuthenticationError`: Authentication failed

```python
from doordash_client import DoorDashClient, APIError, NetworkError

try:
    client = DoorDashClient(org_id="your-org-id")
    result = client.health_check()
except APIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
except NetworkError as e:
    print(f"Network error: {e}")
```

## Examples

### Complete Ordering Flow

```python
from doordash_client import DoorDashClient

client = DoorDashClient(org_id="your-org-id")

try:
    # 1. Acquire session (address required for new users)
    session = client.acquire_session(
        name="John Doe", 
        phone="555-555-1234",
        address="123 Main St, New York, NY"
    )
    
    # 2. Search for restaurants
    restaurants = client.search_restaurants(
        query="mexican food",
        lat=40.7128,
        lng=-74.0060,
        limit=5
    )
    
    # 3. Get restaurant details
    store_id = restaurants["results"][0]["id"]
    restaurant = client.get_restaurant(store_id)
    
    # 4. Add items to cart
    client.add_to_cart(
        store_id=store_id,
        item_id=12345,
        quantity=2,
        special_instructions="Extra spicy please"
    )
    
    # 5. View cart
    cart = client.view_cart()
    print(f"Cart total: ${cart['total']}")
    
    # 6. Place order
    order = client.place_order(
        tip_amount=8.00,
        delivery_instructions="Leave at door"
    )
    
    print(f"Order placed! ID: {order['order_id']}")
    
finally:
    # Always release session
    client.release_session()
```

### Using Address Management

```python
# Get standalone address suggestions (no session required)
standalone_suggestions = client.get_standalone_address_suggestions("123 Main St, San Francisco")
print(f"Found {len(standalone_suggestions['suggestions'])} suggestions")
for suggestion in standalone_suggestions['suggestions']:
    print(f"- {suggestion['formatted_address']}")
    print(f"  Serviceable: {suggestion['market_info']['serviceable']}")

# Get address suggestions (requires active session)
suggestions = client.get_address_suggestions("123 Main St, New York")

# Add a new address
address = client.add_address(
    street="123 Main Street",
    city="New York", 
    state="NY",
    zipcode="10001",
    delivery_instructions="Apartment 4B"
)

# Get all addresses
addresses = client.get_addresses()
```

### Multi-Store Ordering (DoubleDash)

```python
# Add items from first restaurant
client.add_to_cart(store_id=111, item_id=1, quantity=1)

# View cart to get cart_id
cart = client.view_cart()
cart_id = cart["id"]

# Get bundle opportunities (other compatible stores)
opportunities = client.get_bundle_opportunities(cart_id)

# Add items from compatible store
client.add_to_cart(store_id=222, item_id=2, quantity=1)

# Place combined order
order = client.place_order(tip_amount=10.00)
```

## 🏠 Address Isolation System

### Complete Privacy & Security

The DoorDash Python Client includes a sophisticated Address Isolation System that ensures complete privacy between users while maintaining seamless address persistence.

### Key Features

- **🔒 Complete Isolation**: Users never see other users' addresses
- **💾 Automatic Restoration**: Addresses automatically restored across sessions
- **🛡️ Zero Contamination**: Address validation doesn't pollute tenant accounts
- **⚡ Transparent Operation**: Works automatically without configuration

### How It Works

```python
# First time user - address required
client = DoorDashClient(org_id="your-org-id")
session = client.acquire_session(
    name="New User",
    phone="555-1234",
    address="123 Main St, San Francisco, CA"  # Required for new users
)

# Address is validated and stored securely
# Session work...
client.release_session()  # Address automatically saved to snapshot

# Later - existing user
session = client.acquire_session(
    name="New User",
    phone="555-1234"
    # No address needed - automatically restored from snapshot
)
# User's addresses are automatically restored exactly as they were
```

### Address Management

```python
# Validate addresses before registration (no session required)
suggestions = client.get_standalone_address_suggestions("123 Main St, SF")
for suggestion in suggestions['suggestions']:
    print(f"Address: {suggestion['formatted_address']}")
    print(f"Serviceable: {suggestion['market_info']['serviceable']}")

# Session-based address management
client.acquire_session(name="User", phone="555-1234", address="Valid Address")

# Get all user addresses
addresses = client.get_addresses()

# Add additional addresses
client.add_address(
    street="456 Oak Ave",
    city="San Francisco", 
    state="CA",
    zipcode="94102"
)
```

### Privacy Guarantees

- ✅ **Zero Cross-Pollution**: Users never see addresses from other users
- ✅ **Tenant Protection**: System default addresses never exposed to users
- ✅ **Clean Validation**: Address validation uses read-only operations only
- ✅ **Perfect Restoration**: Addresses restored exactly as saved
- ✅ **Automatic Cleanup**: User addresses removed from tenant during session release

## License

MIT License