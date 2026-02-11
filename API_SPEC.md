# Reverb Backend API Documentation

## Overview
Reverb is a content aggregation service that collects engineering blog posts from various tech companies (Uber, Airbnb, Stripe, Lyft). This API provides access to the aggregated posts and the list of supported companies.

**Base URL**: `http://localhost:8000` (Local Development)

## Endpoints

### 1. Posts

**Endpoint**: `GET /posts`

Fetches a paginated list of aggregated blog posts. Supports filtering by source company.

**Authentication**: Optional. If `x-user-id` header is provided, `is_liked` field will be populated personalized to that user.

**Query Parameters**:
- `limit` (int, default: 20): Number of posts to return.
- `offset` (int, default: 0): Number of posts to skip.
- `source_id` (string, optional): Filter by company ID (e.g., `uber`, `airbnb`).
- `sort_by` (string, default: `published_date`): Field to sort by. Supported: `published_date`.
- `sort_by` (string, default: `published_date`): Field to sort by. Supported: `published_date`.
- `sort_order` (string, default: `desc`): Sort order. Supported: `asc`, `desc`.
- `liked_only` (boolean, optional): If true, returns only posts liked by the user. Requires Auth.
- `bookmarked_only` (boolean, optional): If true, returns only posts bookmarked by the user. Requires Auth.

**Response**: `200 OK`
Returns a JSON array of [Post Objects](#post-object).

**Example Request**:
```http
GET /posts?limit=2&sort_order=desc
```

**Example Response**:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Newest Post",
    "published_date": "2023-11-01T10:00:00Z",
    "source_id": "uber",
    "authors": ["Engineer A"],
    "site_name": "Uber Engineering",
    "url": "https://example.com/newest"
  },
  {
    "id": "123e4567-e89b-12d3-a456-426614174001",
    "title": "Older Post",
    "published_date": "2023-10-31T10:00:00Z",
    "source_id": "airbnb",
    "authors": ["Engineer B"],
    "site_name": "Airbnb Tech Blog",
    "url": "https://example.com/older"
  }
]
```

**Endpoint**: `GET /posts/{post_id}`

Fetches a single post by its UUID.

**Path Parameters**:
- `post_id` (string): The UUID of the post.

**Response**: `200 OK`
Returns a single [Post Object](#post-object).

---

### 2. Companies

**Endpoint**: `GET /companies`

Fetches the list of supported tech companies/sources configured in the system.

**Response**: `200 OK`
Returns a JSON array of [Company Objects](#company-object).

**Example Request**:
```http
GET /companies
```

---

### 3. Authentication

**Endpoint**: `POST /auth/login`

Login or Signup a user by phone number.

**Request Body**:
```json
{
  "phone_number": "+15550199"
}
```

**Response**: `200 OK`
Returns a [User Object](#user-object).

**Example Request**:
```http
POST /auth/login
Content-Type: application/json

{
    "phone_number": "+15550123"
}
```

**Example Response**:
```json
{
  "phone_number": "+15550123",
  "id": "85dca3a1-f0ae-456b-a290-c260ec8979cb",
  "created_at": "2023-11-01T12:00:00Z"
}
```

---

### 4. Personalization

**Endpoint**: `POST /personalization/likes`

Like a post. Requires `x-user-id` header.

**Headers**:
- `x-user-id`: UUID of the user.

**Request Body**:
```json
{
  "post_id": "uuid-string"
}
```

**Response**: `200 OK`
```json
{
  "status": "success",
  "message": "Post liked"
}
```

**Endpoint**: `DELETE /personalization/likes/{post_id}`

Unlike a post. Requires `x-user-id` header.

**Response**: `200 OK`
```json
{
  "status": "success",
  "message": "Post unliked"
}
```

**Endpoint**: `GET /personalization/likes`

Get list of posts liked by the user. Requires `x-user-id` header.

**Response**: `200 OK`
Returns a JSON array of [Post Objects](#post-object).

---

### 5. Bookmarks

**Endpoint**: `POST /personalization/bookmarks`

Bookmark a post. Requires `x-user-id` header.

**Request Body**:
```json
{
  "post_id": "uuid-string"
}
```

**Response**: `200 OK`
```json
{
  "status": "success",
  "message": "Post bookmarked"
}
```

**Endpoint**: `DELETE /personalization/bookmarks/{post_id}`

Unbookmark a post. Requires `x-user-id` header.

**Response**: `200 OK`
```json
{
  "status": "success",
  "message": "Post unbookmarked"
}
```

**Endpoint**: `GET /personalization/bookmarks`

Get list of posts bookmarked by the user. Requires `x-user-id` header.

**Response**: `200 OK`
Returns a JSON array of [Post Objects](#post-object).

---

## Data Schemas

### Post Object
Represents a single blog post.

```json
{
  "id": "uuid-string",
  "title": "Post Title",
  "url": "https://example.com/blog-post",
  "description": "Brief summary or excerpt...",
  "authors": ["Author Name"],
  "published_date": "2023-10-27T10:00:00Z",
  "site_name": "Airbnb Tech Blog",
  "source_id": "airbnb",
  "image_url": "https://example.com/image.jpg",
  "created_at": "2023-10-28T12:00:00Z"
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string (UUID) | Unique identifier for the post. |
| `title` | string | Title of the blog post. |
| `url` | string (URL) | Original link to the post. |
| `description` | string (optional) | Short description or excerpt. |
| `authors` | array[string] | List of author names. |
| `published_date` | string (ISO 8601) | Original publication date. |
| `site_name` | string | Name of the source site (e.g., "Uber Engineering"). |
| `source_id` | string | ID of the source company (e.g., `uber`, `airbnb`). |
| `image_url` | string (URL, optional) | URL of the post's featured image. |
| `created_at` | string (ISO 8601) | When the post was crawled/saved. |
| `is_liked` | boolean | True if the current user has liked this post. |
| `is_bookmarked` | boolean | True if the current user has bookmarked this post. |

### Company Object
Represents a source company.

```json
{
  "id": "uber",
  "name": "Uber Engineering",
  "url": "https://www.uber.com/en-US/blog/engineering/"
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string | Unique machine-readable ID (used for `source_id` filter). |
| `name` | string | Display name of the company. |
| `url` | string (URL) | URL of the company's main blog page. |

### User Object
Represents a registered user.

```json
{
  "id": "uuid-string",
  "phone_number": "+1555...",
  "created_at": "2023-11-01T10:00:00Z"
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string (UUID) | Unique user ID. |
| `phone_number` | string | User's phone number (unique). |
| `created_at` | string (ISO 8601) | Account creation timestamp. |
