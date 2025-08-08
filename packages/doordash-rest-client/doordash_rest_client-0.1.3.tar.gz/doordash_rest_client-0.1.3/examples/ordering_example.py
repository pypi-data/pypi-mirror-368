#!/usr/bin/env python3
"""
Complete ordering flow example.
"""

from doordash_client import DoorDashClient, APIError


def main():
    # You'll need real org_id from your organization
    client = DoorDashClient(
        org_id="your-org-id"
    )
    
    try:
        print("🍕 DoorDash Ordering Example")
        print("=" * 40)
        
        # Step 1: Acquire session
        print("1. Acquiring session...")
        session = client.acquire_session(
            name="Demo Customer",
            phone="555-0123",
            address="123 Main St, New York, NY"
        )
        print(f"   ✓ Session acquired: {session['client_id']}")
        
        # Step 2: Search for restaurants
        print("\n2. Searching for restaurants...")
        restaurants = client.search_restaurants(
            query="italian",
            lat=40.7128,
            lng=-74.0060,
            limit=5
        )
        
        if not restaurants.get("results"):
            print("   ❌ No restaurants found")
            return
        
        print(f"   ✓ Found {len(restaurants['results'])} restaurants")
        
        # Show available restaurants
        for i, restaurant in enumerate(restaurants["results"]):
            print(f"   {i+1}. {restaurant['name']} - {restaurant.get('cuisine_type', 'Unknown')}")
        
        # Step 3: Select first restaurant and get details
        selected_restaurant = restaurants["results"][0]
        store_id = selected_restaurant["id"]
        
        print(f"\n3. Getting menu for {selected_restaurant['name']}...")
        restaurant_details = client.get_restaurant(store_id)
        
        if restaurant_details.get("menu_categories"):
            categories = restaurant_details["menu_categories"]
            print(f"   ✓ Found {len(categories)} menu categories")
            
            # Show first few items from first category
            if categories and categories[0].get("items"):
                items = categories[0]["items"][:3]
                print(f"   Popular items from {categories[0]['name']}:")
                for item in items:
                    print(f"   - {item['name']} (${item['price']})")
        
        # Step 4: Add item to cart (using first available item)
        if restaurant_details.get("menu_categories"):
            first_category = restaurant_details["menu_categories"][0]
            if first_category.get("items"):
                item_to_add = first_category["items"][0]
                item_id = item_to_add["id"]
                
                print(f"\n4. Adding {item_to_add['name']} to cart...")
                add_result = client.add_to_cart(
                    store_id=store_id,
                    item_id=item_id,
                    quantity=1,
                    special_instructions="Extra napkins please"
                )
                print("   ✓ Item added to cart")
        
        # Step 5: View cart
        print("\n5. Viewing cart...")
        cart = client.view_cart()
        
        if cart.get("carts"):
            active_cart = None
            for cart_info in cart["carts"]:
                if cart_info.get("is_active"):
                    active_cart = cart_info
                    break
            
            if active_cart:
                print(f"   Store: {active_cart['store_name']}")
                print(f"   Items: {len(active_cart['items'])}")
                print(f"   Subtotal: ${active_cart['subtotal']}")
                print(f"   Total: ${active_cart['total']}")
                
                # Show items
                for item in active_cart["items"]:
                    print(f"   - {item['name']} x{item['quantity']} = ${item['total_price']}")
        
        # Step 6: Get addresses and payment methods
        print("\n6. Checking addresses and payment methods...")
        addresses = client.get_addresses()
        payments = client.get_payment_methods()
        
        print(f"   Addresses: {len(addresses.get('addresses', []))}")
        print(f"   Payment methods: {len(payments.get('payment_methods', []))}")
        
        # Step 7: Simulate order placement (commented out for safety)
        print("\n7. Order ready for placement...")
        print("   ⚠️  Actual order placement is commented out for safety")
        print("   ⚠️  Uncomment the line below to place a real order (charges money!)")
        
        # UNCOMMENT TO PLACE REAL ORDER (CHARGES MONEY!)
        # order = client.place_order(
        #     tip_amount=5.00,
        #     delivery_instructions="Leave at door, ring bell"
        # )
        # print(f"   ✓ Order placed! ID: {order.get('order_id')}")
        
        print("\n✅ Ordering flow completed successfully!")
        print("💡 To place real orders, uncomment the place_order() call")
        
    except APIError as e:
        print(f"❌ API Error: {e.message}")
        if e.response_data:
            print(f"   Details: {e.response_data}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Always release session
        print("\n🔄 Releasing session...")
        try:
            client.release_session()
            print("   ✓ Session released")
        except:
            print("   ⚠️ Failed to release session")


if __name__ == "__main__":
    main()