# DoorDash MCP Server

An MCP (Model Context Protocol) server that provides DoorDash food ordering functionality to Claude Desktop.

## Important: Authentication Required

This MCP server requires a valid DoorDash organization ID to function. You must set the `DOORDASH_ORG_ID` environment variable before using this server.

To obtain an organization ID, you need to register with the DoorDash API platform.

## Features

### 🔍 **Intelligent Search System**
- **McDonald's now works**: Previously returned 0 results, now finds McDonald's restaurants
- **Automatic detection**: Restaurant vs item searches routed intelligently
- **Location-aware**: Uses your saved address when no coordinates provided
- **Unified API**: One search endpoint handles restaurants, grocery items, and more

### 🛒 **Advanced Cart Management**
- **Multi-store carts**: Separate carts for each restaurant/store
- **DoubleDash support**: Combine orders from 90+ compatible stores
- **Automatic cart selection**: Most recently active cart used for checkout
- **Smart pricing**: Unit prices in cents, exact option IDs required

### 🎁 **Auto-Gift Orders**
- **Every order is a gift**: Automatically configured with tenant information
- **Credit validation**: Checks balance before placing orders
- **Saved payment methods**: Uses stored payment information
- **Smart delivery options**: Standard and scheduled delivery

### 🔧 **Session Management**
- **Credential pool management**: Automatic assignment of available credentials
- **Cart persistence**: Previous cart contents restored automatically
- **Address isolation**: Complete address privacy between users with automatic restoration
- **Multi-tenant support**: Isolated sessions for different users
- **TTL management**: Sessions expire after 60 minutes by default

### 🏠 **Address Isolation System**
- **Complete Privacy**: Users never see other users' addresses
- **Automatic Management**: Address isolation happens transparently during session lifecycle
- **Perfect Restoration**: Addresses restored exactly as saved across sessions
- **Zero Configuration**: No manual snapshot management required
- **Clean Validation**: Address validation uses read-only operations to prevent contamination

## Installation

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/doordash-automation/doordash-mcp.git
cd doordash-mcp

# Install dependencies
pip install -r requirements.txt

# Install the MCP server
pip install -e .
```

### Option 2: Install from PyPI

```bash
pip install doordash-mcp
```

## Configuration

### 1. Set up your DoorDash Organization ID

You must obtain a valid DoorDash organization ID for API access. This is required and the server will not function without it.

Set it as an environment variable:

```bash
export DOORDASH_ORG_ID="your-org-id-here"
```

**Note**: Replace `your-org-id-here` with your actual DoorDash organization ID.

### 2. Configure Claude Desktop

Add the DoorDash MCP server to your Claude Desktop configuration.

**On macOS:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows:**
Edit `%APPDATA%\Claude\claude_desktop_config.json`

Add the following to the `mcpServers` section:

```json
{
  "mcpServers": {
    "doordash": {
      "command": "python",
      "args": ["-m", "doordash_mcp"],
      "env": {
        "DOORDASH_ORG_ID": "your-org-id-here"
      }
    }
  }
}
```

Or if you installed from source:

```json
{
  "mcpServers": {
    "doordash": {
      "command": "python",
      "args": ["/path/to/doordash-mcp/doordash_mcp_server.py"],
      "env": {
        "DOORDASH_ORG_ID": "your-org-id-here"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## Usage

Once configured, you can use DoorDash tools in Claude Desktop:

### Initialize Session
```
Use the initialize_doordash tool to start a session
Note: New users must provide a valid address during first session
```

### Search for Restaurants
```
Search for "pizza" restaurants near me using the search_restaurants tool
```

### View Restaurant Menu
```
Get details for restaurant with store_id 12345 using get_restaurant_details
```

### Complete Ordering Workflow
```
Step 1: Initialize a session
Step 2: Search for "McDonald's" restaurants  
Step 3: Get restaurant details for store ID 653636
Step 4: Get menu item details for French Fries (item ID 6570953960)
Step 5: Add French Fries to cart with Medium size option
Step 6: View my cart to confirm items
Step 7: Place order with $3 tip
Step 8: Release session when done
```

### Multi-Store Orders (DoubleDash)
```
Step 1: Add items from McDonald's to cart
Step 2: Get bundle opportunities for the cart
Step 3: Search for compatible Starbucks stores
Step 4: Add Starbucks items to the same order
Step 5: Checkout once for combined delivery
```

## Available Tools

### Session Management
- `initialize_doordash` - Initialize client and acquire session
- `release_session` - Release session when done

### Restaurant Operations
- `search_restaurants` - Search for restaurants by query or location
- `get_restaurant_details` - Get full restaurant info including menu

### Cart Operations
- `add_to_cart` - Add items to cart
- `view_cart` - View all active carts
- `clear_carts` - Clear all carts

### Order Operations
- `place_order` - Place order (charges real money!)
- `get_addresses` - Get saved delivery addresses
- `get_payment_methods` - Get saved payment methods

### Address Management
- `get_standalone_address_suggestions` - Get address suggestions without session (for registration)
- `get_address_suggestions` - Get address suggestions (requires session)
- `add_user_address` - Add new delivery address

## Important Notes

⚠️ **WARNING**: The `place_order` tool will place REAL orders and charge your payment method! Only use it when you actually want to order food.

### 🔑 Critical Success Factors

**For add_to_cart:**
- ✅ **Use EXACT values** from menu/search results - don't guess item IDs or prices
- ✅ **Unit prices in CENTS** (e.g., $5.89 = 589 cents, not 5.89)
- ✅ **Get option IDs first** from get_menu_item_details for items with size/customization
- ✅ **Follow the workflow**: search → restaurant details → menu item details → add to cart

**Common Mistakes to Avoid:**
- ❌ Don't guess item IDs - always get them from search/menu results
- ❌ Don't use dollars for unit_price - use cents (589 not 5.89)  
- ❌ Don't skip getting option IDs for items with size choices
- ❌ Don't forget to release sessions when done

**Cart Behavior:**
- Each restaurant has its own separate cart in DoorDash
- The most recently updated cart is used for checkout
- To checkout a different cart, add any item from that store first
- Sessions expire after 60 minutes - always release when done

## Development

### Running locally

```bash
# Install in development mode
pip install -e .

# Run the server
python doordash_mcp_server.py
```

### Testing with MCP

```bash
# Test the server with mcp dev tools
mcp dev doordash_mcp_server.py
```

## Troubleshooting

### Session Issues
- Make sure your organization ID is valid
- Check that you have network connectivity
- Verify the API endpoint is accessible

### Cart Issues  
- DoorDash maintains separate carts per restaurant
- Clear carts if you're having issues
- Add an item from a restaurant to make its cart active

### Order Issues
- Verify you have a valid payment method
- Check delivery address is correct
- Ensure items are still available

## License

MIT License - See LICENSE file for details