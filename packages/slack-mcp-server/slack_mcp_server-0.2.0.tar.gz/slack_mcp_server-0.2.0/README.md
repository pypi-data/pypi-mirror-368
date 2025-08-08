# Slack MCP Server

A Model Context Protocol (MCP) server for Slack workspace integration using FastMCP with HTTP transport and multiuser support.

## Features

### Tools (8 Unified Tools - 65% Reduction from 23 Original Tools!)

#### **🔄 Unified Messaging**
- **conversations** - All messaging operations (history, bulk_history, replies, search, permalink)
- **conversations_add_message** - Post messages to channels/DMs (safety disabled by default)

#### **🏢 Unified Channel Management**  
- **channels** - All channel operations (list, detailed, info, members, bulk_info)
- **channels_manage** - Channel settings (topic, purpose, both)

#### **👥 Unified User Management**
- **users** - All user operations (info, list, presence, bulk_presence)

#### **🌐 Unified Workspace**
- **workspace** - All workspace operations (info, analytics, files, permissions)

#### **💾 Unified Cache**
- **cache** - All cache operations (info, initialize, clear)

#### **⚡ Interactive Features**
- **add_reaction** - Add emoji reactions to messages

### Resources
- **slack://workspace/channels** - CSV directory of all channels with metadata
- **slack://workspace/users** - CSV directory of all users with metadata

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Required Environment Variables
- `SLACK_MCP_XOXP_TOKEN` - Slack bot token (xoxb-) or user token (xoxp-)

### Optional Environment Variables
- `SLACK_MCP_ADD_MESSAGE_TOOL` - Enable message posting:
  - Not set = disabled (default for safety)
  - `true` or `1` = enabled for all channels
  - Comma-separated channel IDs = enabled only for specific channels
- `SLACK_MCP_USERS_CACHE` - Path to users cache file (default: `~/slack-cache/users_cache.json`)
- `SLACK_MCP_CHANNELS_CACHE` - Path to channels cache file (default: `~/slack-cache/channels_cache_v2.json`)

## Usage

### Start HTTP Server
```bash
python slack_mcp_server.py
```

Server runs on `http://0.0.0.0:8000/mcp` by default.

### Authentication
For multiuser support, pass the Slack token in request headers:
```
SLACK_MCP_XOXP_TOKEN: xoxb-your-slack-token
```

Optional message posting control via headers:
```
SLACK_MCP_ADD_MESSAGE_TOOL: true
```

Alternatively, set `SLACK_MCP_XOXP_TOKEN` environment variable for single-user mode.

## API Examples

### Get Messages from Multiple Channels (Efficient Bulk Operation)
```json
{
  "method": "conversations",
  "params": {
    "operation": "bulk_history",
    "channel_ids": "#general, #random, #project-alpha",
    "limit": "1d",
    "filter_user": "@chris"
  }
}
```

### Get All Channels with Details (Single Efficient Call)
```json
{
  "method": "channels",
  "params": {
    "operation": "detailed",
    "channel_types": "public_channel,private_channel",
    "sort": "popularity"
  }
}
```

### Get Info for Multiple Users
```json
{
  "method": "users",
  "params": {
    "operation": "info",
    "user_ids": "@john, @jane, U123456789"
  }
}
```

### Get Channels Directory
```json
{
  "method": "resource",
  "params": {
    "uri": "slack://myworkspace/channels"
  }
}
```

## Slack Permissions

Required scopes for your Slack app:
- **channels:history** - Read public channel messages
- **groups:history** - Read private channel messages  
- **im:history** - Read direct messages
- **mpim:history** - Read group direct messages
- **channels:read** - List public channels
- **groups:read** - List private channels
- **users:read** - List workspace users
- **chat:write** - Post messages (if enabled)

## Enhanced Features

### Intelligent Caching
- **User Cache**: Automatically caches user information to avoid repeated API calls
- **Channel Cache**: Caches channel metadata with configurable refresh intervals  
- **Performance**: Significantly reduces API rate limit usage and improves response times
- **Cache-First**: `user_info` and `channel_info` tools default to cache for instant responses
- **Fallback**: Graceful fallback to API if cache miss or explicitly requested

### Smart Name Resolution
The server now accepts user-friendly names in addition to IDs:

**Channel References:**
- `#general` → resolves to channel ID (C1234567890)
- `#project-alpha` → resolves to channel ID
- `@john_dm` → opens/finds DM with user "john"

**User References:**
- `@john` → resolves to user ID (U1234567890)
- `john.doe` → resolves using display name or real name
- `John Doe` → resolves using real name

**Examples:**
```json
// Get messages from #general channel with user details
{
  "method": "conversations_history",
  "params": {
    "channel_id": "#general",
    "limit": "1d",
    "include_user_details": true
  }
}

// Get workspace analytics from cache (instant)
{
  "method": "workspace",
  "params": {
    "operation": "analytics",
    "date_range": "30d"
  }
}

// Search messages across channels with filters
{
  "method": "conversations",
  "params": {
    "operation": "search",
    "search_query": "deployment status",
    "filter_in_channel": "#devops",
    "filter_users_from": "@admin"
  }
}

// Manage channel settings efficiently
{
  "method": "channels_manage",
  "params": {
    "operation": "both",
    "channel_id": "#general", 
    "topic": "Welcome to our main discussion!",
    "purpose": "General team discussions and updates"
  }
}

// Check cache status and manage
{
  "method": "cache",
  "params": {
    "operation": "info"
  }
}

// List members of #general channel
{
  "method": "channels",
  "params": {
    "operation": "members",
    "channel_id": "#general"
  }
}

// Check user presence for multiple users
{
  "method": "users",
  "params": {
    "operation": "bulk_presence",
    "user_ids": "@john, @jane, @admin"
  }
}

// Get thread replies with user details
{
  "method": "conversations",
  "params": {
    "operation": "replies",
    "channel_id": "#general",
    "message_ts": "1699123456.123456",
    "include_user_details": true
  }
}

// List files shared by specific user
{
  "method": "workspace",
  "params": {
    "operation": "files",
    "user_id": "@chris",
    "count": 20,
    "types": "images"
  }
}

// Check what API permissions are available
{
  "method": "workspace",
  "params": {
    "operation": "permissions"
  }
}

// Initialize and manage cache files
{
  "method": "cache",
  "params": {
    "operation": "initialize"
  }
}
```

## Security

- Message posting disabled by default for safety
- Token-based authentication for multiuser support
- No secrets logged or committed to repository
- Follows Slack API rate limits and best practices