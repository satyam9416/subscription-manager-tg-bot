# Telegram Group Manager API Documentation

This document provides detailed information about the API endpoints available in the Telegram Group Manager application.

## Table of Contents

1. [Product API](#product-api)
2. [Group API](#group-api)
3. [Subscription API](#subscription-api)
4. [Telegram API](#telegram-api)

---

## Product API

The Product API allows you to manage products in the system.

### Get All Products

Retrieves a list of all products.

- **URL**: `/products`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved products

**Response Format**:

```json
{
  "data": [
    {
      "id": 1,
      "name": "Product Name",
      "description": "Product Description",
      "price": 99.99,
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

### Get Product by ID

Retrieves a specific product by its ID.

- **URL**: `/products/<product_id>`
- **Method**: `GET`
- **URL Parameters**:
  - `product_id`: The ID of the product to retrieve
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved product
  - `404 Not Found`: Product not found

**Response Format**:

```json
{
  "id": 1,
  "name": "Product Name",
  "description": "Product Description",
  "price": 99.99,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Create Product

Creates a new product.

- **URL**: `/products`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:

```json
{
  "name": "New Product",
  "description": "Product Description",
  "price": 99.99
}
```

- **Response Codes**:
  - `201 Created`: Successfully created product
  - `400 Bad Request`: Validation error
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "id": 1,
  "name": "New Product",
  "description": "Product Description",
  "price": 99.99,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Update Product

Updates an existing product.

- **URL**: `/products/<product_id>`
- **Method**: `PUT`
- **URL Parameters**:
  - `product_id`: The ID of the product to update
- **Authentication**: Not required
- **Request Body**:

```json
{
  "name": "Updated Product Name",
  "description": "Updated Description",
  "price": 149.99
}
```

- **Response Codes**:
  - `200 OK`: Successfully updated product
  - `400 Bad Request`: Validation error
  - `404 Not Found`: Product not found
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "id": 1,
  "name": "Updated Product Name",
  "description": "Updated Description",
  "price": 149.99,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-02T12:00:00Z"
}
```

### Delete Product

Deletes a product.

- **URL**: `/products/<product_id>`
- **Method**: `DELETE`
- **URL Parameters**:
  - `product_id`: The ID of the product to delete
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully deleted product
  - `404 Not Found`: Product not found
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "message": "Product deleted successfully"
}
```

---

## Group API

The Group API allows you to manage Telegram groups and their mappings to products.

### Get All Groups

Retrieves a list of all Telegram groups.

- **URL**: `/groups`
- **Method**: `GET`
- **Query Parameters**:
  - `status` (optional): Filter by status. Allowed: `active`, `inactive`
  - `role` (optional): Filter by bot role. Allowed: `member`, `administrator`, `left`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved groups

**Response Format**:

```json
[
  {
    "id": 1,
    "telegram_group_id": "-1001234567890",
    "telegram_group_name": "Group Name",
    "bot_role": "member",
    "product_id": 1,
    "is_active": true,
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

### Get Unmapped Groups

Retrieves a list of Telegram groups that are not mapped to any product.

- **URL**: `/groups/unmapped`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved unmapped groups

**Response Format**:

```json
[
  {
    "id": 1,
    "telegram_group_id": "-1001234567890",
    "telegram_group_name": "Group Name",
    "product_id": null,
    "bot_role": "member",
    "is_active": true,
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

### Map Product to Group

Maps a product to a Telegram group.

- **URL**: `/products/<product_id>/map`
- **Method**: `POST`
- **URL Parameters**:
  - `product_id`: The ID of the product to map
- **Authentication**: Not required
- **Request Body**:

```json
{
  "telegram_group_id": "-1001234567890",
  "telegram_group_name": "Group Name"
}
```

- **Response Codes**:
  - `200 OK`: Successfully mapped product to group
  - `400 Bad Request`: Missing required fields or other error
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "id": 1,
  "telegram_group_id": "-1001234567890",
  "telegram_group_name": "Group Name",
  "bot_role": "member",
  "product_id": 1,
  "is_active": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Unmap Product from Group

Removes the mapping between a product and a Telegram group.

- **URL**: `/products/<product_id>/unmap`
- **Method**: `DELETE`
- **URL Parameters**:
  - `product_id`: The ID of the product to unmap
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully unmapped product
  - `404 Not Found`: No mapping found for this product
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "message": "Product unmapped successfully"
}
```

### Remove Bot and Delete Group

Removes the bot from a Telegram group and deletes the group record from the system.

- **URL**: `/groups/<telegram_group_id>`
- **Method**: `DELETE`
- **URL Parameters**:
  - `telegram_group_id`: Telegram's internal group ID (string)
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Bot removed and group deleted
  - `404 Not Found`: Group not found
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "message": "Bot removed and group deleted"
}
```

---

## Subscription API

The Subscription API allows you to manage user subscriptions to products.

### Get All Subscriptions

Retrieves a paginated list of all subscriptions with filtering options.

- **URL**: `/subscriptions`
- **Method**: `GET`
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `per_page`: Items per page (default: 10, max: 100)
  - `sort_by`: Field to sort by (default: "created_at")
  - `sort_order`: Sort direction, "asc" or "desc" (default: "desc")
  - `search`: Search term to filter results
  - `status`: Filter by subscription status
  - `product_id`: Filter by product ID
  - `user_id`: Filter by user ID
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved subscriptions

**Response Format**:

```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "product_id": 1,
      "status": "active",
      "subscription_expires_at": "2024-01-01T12:00:00Z",
      "invite_link_url": "https://t.me/joinchat/abcdefg",
      "invite_link_expires_at": "2023-02-01T12:00:00Z",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 10,
  "pages": 5
}
```

### Create Subscription

Creates a new subscription for a user to a product.

- **URL**: `/subscribe`
- **Method**: `POST`
- **Authentication**: Not required
- **Request Body**:

```json
{
  "email": "user@example.com",
  "product_id": 1,
  "expiration_datetime": "2024-01-01T12:00:00Z"
}
```

OR

```json
{
  "email": "user@example.com",
  "product_name": "Product Name",
  "expiration_datetime": "2024-01-01T12:00:00Z"
}
```

- **Response Codes**:
  - `201 Created`: Successfully created subscription
  - `400 Bad Request`: Validation error
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "message": "Subscription created successfully",
  "invite_link": "https://t.me/joinchat/abcdefg",
  "invite_expires_at": "2023-02-01T12:00:00Z",
  "subscription_expires_at": "2024-01-01T12:00:00Z"
}
```

### Cancel Subscription by Email and Product ID

Cancels a subscription based on user email and product ID.

- **URL**: `/subscriptions`
- **Method**: `DELETE`
- **Authentication**: Not required
- **Request Body**:

```json
{
  "email": "user@example.com",
  "product_id": 1
}
```

- **Response Codes**:
  - `200 OK`: Successfully cancelled subscription
  - `400 Bad Request`: Validation error
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "message": "Subscription cancelled successfully"
}
```

### Get All Users

Retrieves a list of all users.

- **URL**: `/users`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully retrieved users

**Response Format**:

```json
[
  {
    "id": 1,
    "email": "user@example.com"
  }
]
```

### Cancel Subscription by ID

Cancels a subscription by its ID.

- **URL**: `/subscriptions/<subscription_id>/cancel`
- **Method**: `POST`
- **URL Parameters**:
  - `subscription_id`: The ID of the subscription to cancel
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Successfully cancelled subscription
  - `400 Bad Request`: Error cancelling subscription
  - `500 Internal Server Error`: Server error

**Response Format**:

```json
{
  "message": "Subscription cancelled successfully"
}
```

---

## Telegram API

The Telegram API handles webhook interactions with the Telegram Bot API.

### Telegram Webhook

Endpoint for receiving updates from Telegram.

- **URL**: `/telegram/webhook/<token>`
- **Method**: `POST`
- **URL Parameters**:
  - `token`: The Telegram bot token for verification
- **Authentication**: Token-based (only for this endpoint)
- **Request Body**: Telegram Update object
- **Response Codes**:
  - `200 OK`: Update processed successfully
  - `401 Unauthorized`: Invalid token
  - `500 Internal Server Error`: Error processing update

**Response Format**:

```json
{
  "message": "Update processed successfully"
}
```

### Test Webhook

Tests the Telegram webhook configuration.

- **URL**: `/telegram/webhook/test`
- **Method**: `GET`
- **Authentication**: Not required
- **Response Codes**:
  - `200 OK`: Webhook info retrieved successfully
  - `500 Internal Server Error`: Error getting webhook info

**Response Format**:

```json
{
  "message": "Webhook info retrieved successfully",
  "webhook_url": "https://example.com/telegram/webhook/token",
  "has_custom_certificate": false,
  "pending_update_count": 0,
  "last_error_date": null,
  "last_error_message": null,
  "max_connections": 40
}
```

---

## Error Responses

All API endpoints may return the following error responses:

### Validation Error

```json
{
  "message": "Validation error",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

### General Error

```json
{
  "message": "Error message"
}
```

## Authentication

No authentication is required for any endpoints in this API, except for the Telegram webhook endpoint which uses token-based verification.

## Rate Limiting

API requests may be subject to rate limiting. When rate limits are exceeded, the API will return a `429 Too Many Requests` response.

---

## Schemas

### Product Schema

- `id`: Integer - Unique identifier
- `name`: String - Product name
- `description`: String - Product description
- `price`: Float - Product price
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last update timestamp

### Telegram Group Schema

- `id`: Integer - Unique identifier
- `telegram_group_id`: String - Telegram's internal group ID
- `telegram_group_name`: String - Group name
- `bot_role`: String - Bot role in the group (`member`, `administrator`, `left`)
- `product_id`: Integer - Associated product ID (nullable)
- `is_active`: Boolean - Whether the group is currently active in the system
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last update timestamp

### Subscription Schema

- `id`: Integer - Unique identifier
- `user_id`: Integer - User ID
- `product_id`: Integer - Product ID
- `status`: String - Subscription status (active, cancelled, expired)
- `subscription_expires_at`: DateTime - Expiration timestamp
- `invite_link_url`: String - Telegram group invite link
- `invite_link_expires_at`: DateTime - Invite link expiration timestamp
- `created_at`: DateTime - Creation timestamp
- `updated_at`: DateTime - Last update timestamp

### User Schema

- `id`: Integer - Unique identifier
- `email`: String - User email address
