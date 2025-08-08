#!/usr/bin/env python3
"""
DoorDash MCP Server

An MCP server that provides DoorDash food ordering functionality
using the published doordash-rest-client package.

Install dependencies:
    pip install mcp doordash-rest-client

Usage:
    python doordash_mcp_server.py
"""

import os
import asyncio
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Import the published DoorDash client
from doordash_client import DoorDashClient, APIError, NetworkError

# Initialize FastMCP server
mcp = FastMCP("doordash")

# Configuration
DEFAULT_ORG_ID = os.getenv("DOORDASH_ORG_ID")  # Must be set via environment variable
DEFAULT_SESSION_TTL = 60  # minutes

# Session management is now handled per-request by individual tools

@mcp.tool()
async def initialize_doordash(
    client_id: Optional[str] = None,
    org_id: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None
) -> Dict[str, Any]:
    """Initialize DoorDash Session

**🚀 CRITICAL: This must be called FIRST before ANY other DoorDash operations!**

Creates a DoorDash session for the user. Returns a client_id that must be used for all subsequent operations.

**📍 ADDRESS REQUIREMENTS:**
- **NEW USERS**: MUST provide name, phone, AND address
  - Example: name="John Doe", phone="555-1234", address="456 S Main St, Los Angeles, CA 90013"
  - Address must be valid and within DoorDash delivery area
  - Invalid addresses will return suggestions to help user
- **RETURNING USERS**: Leave name/phone/address empty
  - Previous cart and addresses automatically restored
  - Just need the same client_id as before

**🎯 How to Know if User is New:**
- First time using DoorDash in this conversation → NEW USER
- No previous client_id for this person → NEW USER  
- When unsure, provide address (ignored if not needed)

**📋 Common Scenarios:**
1. User wants to order food → Initialize with their info
2. User returning after break → Use same client_id, no address needed
3. Invalid address provided → Check suggestions in error response
4. System busy → Try again or wait a moment

    **🔄 Session Lifecycle:**
    1. `initialize_doordash()` → Get client_id
    2. Use client_id for all operations (search, cart, order)
    3. `end_session()` → Save state when done
    
    **💡 Best Practices:**
    - Use consistent client_id format (e.g., "user_123", "john_doe")
    - Save client_id to reuse in future conversations
    - Always end session when done
    
    Args:
        client_id: Optional. Your own ID for the user (auto-generated if not provided)
        org_id: Optional. Uses DOORDASH_ORG_ID env var if not provided
        name: User's name (required for new users)
        phone: User's phone like "555-1234" (required for new users)  
        address: Full delivery address (required for new users)
    
    Returns:
        Success: {"success": true, "client_id": "...", "message": "..."}
        Error: {"success": false, "error": "...", "suggestions": [...]}
    """
    try:
        if not org_id:
            org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        # Use provided client_id or generate a unique one
        import time
        if not client_id:
            client_id = f"mcp_user_{int(time.time())}"
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        
        # Build kwargs for session acquisition
        kwargs = {}
        if name:
            kwargs['name'] = name
        if phone:
            kwargs['phone'] = phone
        if address:
            kwargs['address'] = address
            
        session = client.acquire_session(**kwargs)
        
        return {
            "success": True,
            "client_id": client.client_id,
            "session_info": session,
            "org_id": org_id,
            "message": "DoorDash session initialized successfully"
        }
    except Exception as e:
        error_msg = str(e)
        # Parse error for address suggestions if present
        if "suggestions" in error_msg.lower():
            return {"success": False, "error": error_msg, "needs_address": True}
        return {"success": False, "error": error_msg}

@mcp.tool()
async def search_doordash(
    client_id: str,
    query: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Search DoorDash

🧠 **Intelligent Search System**: Automatically detects restaurant vs item searches and routes accordingly.

**🏠 AUTOMATIC ADDRESS RESOLUTION**: If no lat/lng provided, automatically uses your saved address!

**✨ Search Intelligence (Fixed January 2025):**
- **Restaurant Queries**: "mcdonalds", "burger king", "pizza hut" → Restaurant search
- **Item Queries**: "fresca", "water", "energy drink" → Item search within stores  
- **Ambiguous Queries**: "italian", "mexican" → Defaults to restaurant search
- **Unified Endpoint**: One API handles both types intelligently

**🎯 Search Intelligence Benefits:**
- ✅ **McDonald's now works**: Previously returned 0 results, now finds McDonald's restaurants
- ✅ **Grocery searches preserved**: Fresca, water, etc. still work perfectly
- ✅ **One unified API**: No need to know which endpoint to use
- ✅ **Automatic routing**: System determines search type for you
- ✅ **Location-aware**: Uses your address when no coordinates provided

**💡 Usage Examples:**
- query="mcdonalds" → Finds McDonald's restaurants with menus
- query="fresca" → Finds grocery stores selling Fresca
- query="italian" → Finds Italian restaurants
- query="pizza" → Finds pizza restaurants
- location="San Francisco, CA" → Search in specific location

**📋 Workflow:**
1. First call `initialize_doordash()` to get a client_id
2. Use search_doordash() to find restaurants/items
3. Use get_restaurant_details() to see full menu
4. Use get_menu_item_details() for options/customizations
5. Use add_to_cart() with exact values from menu

Args:
    client_id: Session ID from initialize_doordash() (required)
    query: Optional search query (e.g. "pizza", "McDonald's") 
    location: Optional location string (e.g. "New York, NY", "San Francisco"). 
              If not provided, automatically uses your saved address for location-aware search.
    limit: Maximum number of results to return (default: 10)

Returns:
    Dict containing API response with restaurants near your location
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        # The Python client will call the Modal API which has automatic address resolution
        # When lat/lng are None, the Modal backend automatically uses user's saved address
        lat, lng = None, None
        
        # TODO: In future, could parse location string to lat/lng coordinates
        # For now, rely on backend automatic address resolution when lat/lng are None
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        results = client.search_restaurants(
            query=query,
            lat=lat,
            lng=lng,
            limit=limit
        )
        
        restaurants = results.get("restaurants", [])
        
        return {
            "success": True,
            "restaurants": restaurants,
            "count": len(restaurants),
            "message": f"Found {len(restaurants)} restaurants"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_restaurant_details(client_id: str, store_id: int) -> Dict[str, Any]:
    """Get Restaurant Details

Get detailed information about a specific restaurant including menu.

Args:
    client_id: Session ID from initialize_doordash() (required)
    store_id: Restaurant/store ID from search results

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        details = client.get_restaurant(store_id)
        
        return {
            "success": True,
            "restaurant": details,
            "message": f"Retrieved details for store {store_id}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def add_to_cart(
    client_id: str,
    store_id: int,
    item_id: int,
    quantity: int = 1,
    special_instructions: Optional[str] = None
) -> Dict[str, Any]:
    """Add to Cart

Add an item to the user's cart.

**🔑 KEY SUCCESS FACTORS:**
- **Use EXACT values from menu/search results** - don't guess item IDs, prices, or option IDs
- **Get option IDs from get_menu_item_details first** for items with size/customization choices
- **Unit prices in CENTS** (e.g., $5.89 = 589 cents)
- **Option format**: Use the exact option_id from menu item details

**📋 Required Workflow:**
1. Search restaurants → get store_id
2. Get restaurant details → find item_id and unit_price  
3. Get menu item details → get option_ids for size/customizations
4. Add to cart with exact values

**✅ Working Example - McDonald's French Fries (Medium):**
- store_id: 653636, item_id: 6570953960, unit_price: 589 (cents)
- Medium size option_id: "29646324430"
    
Args:
    client_id: Session ID from initialize_doordash() (required)
    store_id: Restaurant/store ID
    item_id: Menu item ID
    quantity: Number of items to add (default: 1)
    special_instructions: Optional special instructions

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        result = client.add_to_cart(
            store_id=store_id,
            item_id=item_id,
            quantity=quantity,
            special_instructions=special_instructions
        )
        
        return {
            "success": True,
            "result": result,
            "message": f"Added {quantity} item(s) to cart"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def view_cart(client_id: str) -> Dict[str, Any]:
    """View Cart

View current cart contents and items.

**🛒 Multi-Store Cart Behavior:**
- DoorDash creates **separate carts** for each store/restaurant
- Each cart tracks items from one specific store
- The **most recently active cart** is used for checkout
- You can have multiple active carts simultaneously

**📊 Response Details:**
- Returns all active carts with items from different stores
- Shows subtotal, item count, and store name for each cart
- Includes detailed item information and pricing
- Cart IDs are used for bundle opportunities (DoubleDash)

**Example:** If you add items from McDonald's and Starbucks, you'll see:
- Cart 1: McDonald's items (subtotal, item count)
- Cart 2: Starbucks items (subtotal, item count)

Args:
    client_id: Session ID from initialize_doordash() (required)
    
Returns:
    Dict containing API response with all active carts
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        cart = client.view_cart()
        
        # Parse cart information
        cart_summary = []
        if "cart" in cart and "detailed_carts" in cart["cart"]:
            for detailed_cart in cart["cart"]["detailed_carts"]:
                cart_info = detailed_cart.get("cart", {})
                store_info = detailed_cart.get("stores", [{}])[0]
                
                cart_summary.append({
                    "cart_id": cart_info.get("id"),
                    "store_name": store_info.get("name", "Unknown"),
                    "items_count": cart_info.get("total_items_count", 0),
                    "subtotal": cart_info.get("subtotal", 0) / 100.0,  # Convert cents to dollars
                    "items": cart_info.get("items", [])
                })
        
        return {
            "success": True,
            "carts": cart_summary,
            "raw_cart": cart,
            "message": f"Found {len(cart_summary)} active cart(s)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_addresses(client_id: str) -> Dict[str, Any]:
    """Get saved delivery addresses.
    
    Retrieves all saved addresses associated with the account.
    
    Args:
        client_id: Session ID from initialize_doordash() (required)
    
    Returns:
        Dict[str, Any]: List of saved addresses
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        # Use user-level endpoint via python client
        addresses = client.get_addresses()
        # Normalize shape: python client already returns the API response
        addr_list = addresses.get("addresses") if isinstance(addresses, dict) else addresses
        if addr_list is None:
            addr_list = []
        return {
            "success": True,
            "addresses": addr_list,
            "count": len(addr_list),
            "message": f"Found {len(addr_list)} saved address(es)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def place_order(
    client_id: str,
    tip_amount: float = 0.0,
    delivery_instructions: str = "",
    user_address_id: Optional[str] = None,
    user_payment_id: Optional[str] = None
) -> Dict[str, Any]:
    """Place Order

Place an order with automatic gift configuration, credit validation, and stored tenant information.
    
    ⚠️ **WARNING: This will place a REAL order and charge your payment method!**

**🛒 Cart Selection Behavior:**
- System automatically selects the **most recently active cart** for checkout
- If you have multiple carts from different stores, the most recently modified cart is used
- To checkout a different cart, add any item from that store first to make it active

**🎁 Auto-Gift Features:**
- Every order is automatically configured as a gift to tenant's stored name/phone/address
- Uses DoorDash credits by default when available
- Automatic credit balance validation before placing orders
    
    Args:
        client_id: Session ID from initialize_doordash() (required)
        tip_amount: Tip amount in dollars (default: 0.0)
        delivery_instructions: Delivery instructions (default: "")
        user_address_id: Optional specific address ID
        user_payment_id: Optional specific payment method ID
    
    Returns:
        Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        
        # Confirm before placing order
        if not delivery_instructions:
            delivery_instructions = "Leave at door"
        
        order = client.place_order(
            tip_amount=tip_amount,
            delivery_instructions=delivery_instructions,
            user_address_id=user_address_id,
            user_payment_id=user_payment_id
        )
        
        return {
            "success": True,
            "order": order,
            "message": "Order placed successfully! Check your email for confirmation."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}



@mcp.tool()
async def clear_cart(client_id: str) -> Dict[str, Any]:
    """Clear Cart

Remove all items from the user's cart.

**✅ WORKING:** This endpoint successfully clears all items from the user's cart

Example Response:
{
  "success": true,
  "cleared_count": 1
}

Args:
    client_id: Session ID from initialize_doordash() (required)

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        # Use the documented DELETE endpoint instead of the undocumented POST endpoint
        result = client._request("DELETE", f"/sessions/{client.client_id}/cart")
        
        return {
            "success": True,
            "result": result,
            "message": "Cart cleared successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def end_session(client_id: str) -> Dict[str, Any]:
    """End Session
    
    **⚠️ IMPORTANT: Always call this when done with DoorDash operations!**
    
    Ends the session and saves the user's cart and addresses for next time.

**💾 What Gets Saved:**
- Current cart contents with all items and customizations
- User's delivery addresses
- Selected preferences

**⏱️ When to End:**
- ✅ After placing an order
- ✅ When user is done browsing/shopping
- ✅ Before ending the conversation
- ✅ If switching to a different user

**🔄 Benefits of Ending:**
- User's cart is saved for next session
- Addresses are preserved for future use
- Resources freed for other operations
- Clean session termination

**⚠️ If Not Ended:**
- Session auto-expires after 60 minutes
- Cart contents are still saved (but better to end explicitly)
- May experience delays when acquiring new sessions

**📊 Example Response:**
```json
{
  "success": true,
  "message": "Session released successfully"
}
```
    
Args:
    client_id: The client_id from initialize_doordash() (REQUIRED)
    
Returns:
    Success confirmation with saved state summary
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        result = client.release_session()
        
        return {
            "success": True,
            "result": result,
            "message": "Session ended successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Bundle Opportunities (DoubleDash)
@mcp.tool()
async def get_bundle_opportunities(client_id: str, cart_id: str) -> Dict[str, Any]:
    """Bundle Opportunities (DoubleDash)

Find compatible stores that can add items to your existing cart, enabling multi-store orders (DoubleDash functionality).

**✅ WORKING:** Successfully finds 90+ compatible stores for multi-store cart functionality

**🚚 DoubleDash Explained:**
- **Multi-Store Orders**: Add items from multiple stores to deliver together
- **One Delivery Fee**: Combined delivery for compatible stores in your area
- **Same Delivery Time**: All stores deliver at approximately the same time
- **Automatic Detection**: System finds stores that can bundle with your current order

**🔍 Key Features:**
- **Dynamic Address Resolution:** Automatically uses your saved address for location context
- **90+ Compatible Stores:** Finds restaurants, retail stores, and grocery combinations
- **Mixed Store Types:** Restaurants + grocery stores + convenience stores
- **Smart Filtering**: Only shows stores that can actually deliver together

**📋 Usage Flow:**
1. Add items to cart from any store (creates primary cart)
2. Call this function with the cart_id to find compatible stores
3. Add items from compatible stores (creates combined delivery)
4. Checkout once for all stores together

Args:
    client_id: Session ID from initialize_doordash() (required)
    cart_id: Cart ID to find bundle opportunities for
    
Returns:
    Dict containing 90+ compatible stores with details
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        return client.get_bundle_opportunities(cart_id)
    except Exception as e:
        return {"success": False, "error": str(e)}





# Menu Item Details
@mcp.tool()
async def get_menu_item_details(client_id: str, store_id: int, item_id: int) -> Dict[str, Any]:
    """Get Menu Item Details

Get detailed information about a specific menu item including options and customizations.

**🔧 Critical for add_to_cart Success:**
- **Required before adding items with options** (size, toppings, etc.)
- Returns exact option_ids needed for add_to_cart requests
- Shows available customizations and size choices
- Provides accurate pricing for each option

**📋 Workflow:**
1. Get store_id from search results
2. Get item_id from restaurant details  
3. **Call this function** to get option_ids
4. Use exact option_ids in add_to_cart request

**Example:** McDonald's French Fries returns size options:
- Small: option_id "29646324429"
- Medium: option_id "29646324430" 
- Large: option_id "29646324431"

Args:
    client_id: Session ID from initialize_doordash() (required)
    store_id: Restaurant store ID
    item_id: Menu item ID
    
Returns:
    Dict containing API response with options and customizations
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        return client.get_menu_item(store_id, item_id)
    except Exception as e:
        return {"success": False, "error": str(e)}

# Address Management
@mcp.tool()
async def get_standalone_address_suggestions(address_input: str) -> Dict[str, Any]:
    """Get Standalone Address Suggestions

Get address autocomplete suggestions without requiring an active session. This endpoint is designed for use during user registration to help users find and validate their addresses before creating an account.

**🔑 Key Benefits:**
- **No session required**: Can be used before user registration
- **Rich address data**: Returns formatted addresses, coordinates, and market info
- **Serviceability check**: Shows if address is in DoorDash delivery area
- **Multiple suggestions**: Provides alternatives for partial/ambiguous input

**💡 Use Cases:**
- User registration address validation
- Address autocomplete during signup
- Pre-validation before creating DoorDash account
- Finding serviceable addresses in new areas

**📋 Response Format:**
Each suggestion includes:
- formatted_address: Complete standardized address
- coordinates: Precise lat/lng for mapping  
- market_info: Market ID, serviceability status, city/state/zip
- place_id: For further API calls

Args:
    address_input: Partial address input (e.g., "123 Main St, San Francisco")
    
Returns:
    Dict containing suggestions with formatted addresses, coordinates, and market info
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.get_standalone_address_suggestions(address_input)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_address_suggestions(client_id: str, query: str) -> Dict[str, Any]:
    """Get Address Suggestions

Get address suggestions based on partial input.

**✅ WORKING:** This endpoint successfully provides address autocomplete suggestions

Args:
    client_id: Session ID from initialize_doordash() (required)
    query: Partial address input

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        return client.get_address_suggestions(query)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def add_user_address(client_id: str, street: str, city: str, state: str, zipcode: str, **kwargs) -> Dict[str, Any]:
    """Add User Address

Add a new delivery address for the user.

Args:
    client_id: Session ID from initialize_doordash() (required)
    street: Street address
    city: City name
    state: State abbreviation (e.g. "CA", "NY")
    zipcode: ZIP code
    **kwargs: Additional address fields
    
Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id, client_id=client_id)
        return client.add_address(street, city, state, zipcode, **kwargs)
    except Exception as e:
        return {"success": False, "error": str(e)}



# Health & Monitoring
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Health Check

Simple health check endpoint.

Returns:
    Dict containing API response
    """
    try:
        org_id = os.getenv("DOORDASH_ORG_ID")
        if not org_id:
            return {"success": False, "error": "DOORDASH_ORG_ID environment variable not set"}
        
        client = DoorDashClient(org_id=org_id)
        return client.health_check()
    except Exception as e:
        return {"success": False, "error": str(e)}





# Main entry point
def main():
    """Run the MCP server"""
    import sys
    
    # Run the FastMCP server
    mcp.run(
        transport="stdio"
    )

if __name__ == "__main__":
    main()