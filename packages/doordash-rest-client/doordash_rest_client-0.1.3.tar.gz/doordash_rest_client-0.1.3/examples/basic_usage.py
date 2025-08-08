#!/usr/bin/env python3
"""
Basic usage example for DoorDash Python Client.
"""

from doordash_client import DoorDashClient, APIError, NetworkError


def main():
    # Initialize client (you'll need real org_id)
    client = DoorDashClient(
        org_id="your-org-id"
    )
    
    try:
        print("🚀 DoorDash Client Example")
        print("=" * 40)
        
        # 1. Health check
        print("1. Checking API health...")
        health = client.health_check()
        print(f"   Status: {health.get('status', 'Unknown')}")
        
        # 2. Acquire session
        print("\n2. Acquiring session...")
        session = client.acquire_session(
            ttl_minutes=60,
            name="Demo User",
            phone="555-0123"
        )
        print(f"   Session ID: {session.get('client_id', 'Unknown')}")
        
        # 3. Search for restaurants
        print("\n3. Searching for pizza restaurants...")
        restaurants = client.search_restaurants(
            query="pizza",
            lat=40.7128,  # NYC coordinates
            lng=-74.0060,
            limit=3
        )
        
        if restaurants.get("results"):
            print(f"   Found {len(restaurants['results'])} restaurants:")
            for i, restaurant in enumerate(restaurants["results"][:3]):
                print(f"   {i+1}. {restaurant.get('name', 'Unknown')}")
        
        # 4. Get restaurant details (if we found any)
        if restaurants.get("results"):
            store_id = restaurants["results"][0]["id"]
            print(f"\n4. Getting details for store {store_id}...")
            
            restaurant = client.get_restaurant(store_id)
            print(f"   Name: {restaurant.get('name', 'Unknown')}")
            print(f"   Rating: {restaurant.get('average_rating', 'N/A')}")
        
        # 5. View current cart
        print("\n5. Viewing cart...")
        cart = client.view_cart()
        print(f"   Cart items: {len(cart.get('items', []))}")
        print(f"   Total: ${cart.get('total', 0.0)}")
        
        # 6. Get addresses
        print("\n6. Getting addresses...")
        addresses = client.get_addresses()
        print(f"   Found {len(addresses.get('addresses', []))} addresses")
        
        # 7. Get payment methods
        print("\n7. Getting payment methods...")
        payments = client.get_payment_methods()
        print(f"   Found {len(payments.get('payment_methods', []))} payment methods")
        
        # 8. Save snapshot
        print("\n8. Saving session snapshot...")
        snapshot = client.save_snapshot()
        print(f"   Snapshot saved: {snapshot.get('success', False)}")
        
        print("\n✅ Example completed successfully!")
        
    except APIError as e:
        print(f"❌ API Error: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
    
    except NetworkError as e:
        print(f"❌ Network Error: {e}")
    
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    
    finally:
        # Always release the session
        print("\n🔄 Releasing session...")
        try:
            client.release_session()
            print("   Session released successfully")
        except Exception as e:
            print(f"   Warning: Failed to release session: {e}")


if __name__ == "__main__":
    main()