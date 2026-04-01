# RealtyAI API Documentation

Base URL: `http://localhost:8000/api`

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Authentication

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "is_admin": false
  }
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Reset Password Request
```http
POST /auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

### Reset Password Confirm
```http
POST /auth/password-reset-confirm
Content-Type: application/json

{
  "token": "reset_token",
  "new_password": "newsecurepassword"
}
```

## OAuth

### Google OAuth Callback
```http
POST /oauth/google/callback
Content-Type: application/json

{
  "token": "google_access_token"
}
```

### Apple OAuth Callback
```http
POST /oauth/apple/callback
Content-Type: application/json

{
  "token": "apple_id_token"
}
```

## Users

### Get Current User
```http
GET /users/me
Authorization: Bearer <token>
```

### Update Profile
```http
PUT /users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name",
  "phone": "+1234567890"
}
```

### Change Password
```http
PUT /users/me/password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

### Delete Account
```http
DELETE /users/me
Authorization: Bearer <token>
```

## Listings

### Create Listing
```http
POST /listings
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Beautiful House",
  "property_type": "house",
  "transaction_type": "sale",
  "address": "123 Main St",
  "city": "Springfield",
  "state": "IL",
  "postal_code": "62701",
  "price": 450000,
  "bedrooms": 3,
  "bathrooms": 2,
  "square_feet": 2000,
  "description": "Beautiful home in great location",
  "amenities": ["Pool", "Garage", "Garden"]
}
```

### Get All Listings
```http
GET /listings?skip=0&limit=20
Authorization: Bearer <token>
```

### Get Listing by ID
```http
GET /listings/{listing_id}
Authorization: Bearer <token>
```

### Update Listing
```http
PUT /listings/{listing_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "price": 475000,
  "title": "Updated Title"
}
```

### Delete Listing
```http
DELETE /listings/{listing_id}
Authorization: Bearer <token>
```

## Images

### Upload Image
```http
POST /images/upload?listing_id={listing_id}
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image_file>
```

### Get Listing Images
```http
GET /images/listing/{listing_id}
Authorization: Bearer <token>
```

### Delete Image
```http
DELETE /images/{image_id}
Authorization: Bearer <token>
```

## Descriptions

### Generate AI Description
```http
POST /descriptions/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "listing_id": "uuid",
  "tone": "professional",
  "focus": "general"
}
```

Response:
```json
{
  "listing_id": "uuid",
  "description": "Generated description text...",
  "tone": "professional",
  "focus": "general"
}
```

### Get Available Filters
```http
GET /descriptions/filters
Authorization: Bearer <token>
```

Response:
```json
{
  "tones": ["professional", "friendly", "luxury", "modern"],
  "focuses": ["general", "investment", "family", "luxury", "location", "amenities"]
}
```

## Maps

### Get Points of Interest
```http
GET /maps/poi?address=123%20Main%20St
Authorization: Bearer <token>
```

Response:
```json
{
  "address": "123 Main St",
  "formatted_address": "123 Main St, City, State",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "poi": [
    {
      "name": "Central Park",
      "type": "park",
      "vicinity": "New York, NY",
      "rating": 4.8
    }
  ],
  "description_text": "Nearby amenities include: ..."
}
```

### Save POI to Listing
```http
POST /maps/listing/{listing_id}/poi
Authorization: Bearer <token>
Content-Type: application/json

{
  "address": "123 Main St, City, State"
}
```

## Admin (Requires Admin Role)

### Get API Keys Config
```http
GET /admin/config/api-keys
Authorization: Bearer <admin_token>
```

### Update API Key
```http
PUT /admin/config/api-keys
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "key_name": "qwen",
  "key_value": "new_api_key"
}
```

### Get AI Filters
```http
GET /admin/filters
Authorization: Bearer <admin_token>
```

### Create AI Filter
```http
POST /admin/filters
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "New Filter",
  "slug": "new-filter",
  "description": "Filter description",
  "tone": "professional",
  "focus": "general",
  "is_active": true,
  "display_order": 0
}
```

### Update AI Filter
```http
PUT /admin/filters/{filter_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Updated Name",
  "is_active": false
}
```

### Delete AI Filter
```http
DELETE /admin/filters/{filter_id}
Authorization: Bearer <admin_token>
```

### Get Feature Tiers
```http
GET /admin/features/tiers
Authorization: Bearer <admin_token>
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `400`: Bad Request - Invalid input
- `401`: Unauthorized - Missing or invalid token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource doesn't exist
- `500`: Internal Server Error
