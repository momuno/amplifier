---
name: API Reference Template
description: API documentation structure for REST/GraphQL APIs
suggested_sources:
  - src/api/**/*.py
  - docs/api-spec.yaml
  - src/routes/**/*.py
---

# {{project_name}} API Reference

{{api_overview}}

## Base URL

[Provide the base URL for API endpoints, including any versioning]

```
Production: https://api.example.com/v1
Staging: https://api-staging.example.com/v1
```

## Authentication

[Explain authentication mechanism - API keys, OAuth, JWT, etc.]

### Authentication Method

[Detailed explanation of how to authenticate]

### Example Authentication

[Show working examples of authenticated requests]

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.example.com/v1/endpoint
```

## Rate Limiting

[Explain any rate limiting policies, quotas, or throttling]

## Endpoints

[List all available endpoints organized by resource or functionality]

### Resource Name

#### GET /resource

[Description of what this endpoint does]

**Parameters:**
- `param1` (string, required): Description
- `param2` (integer, optional): Description

**Example Request:**
```bash
curl https://api.example.com/v1/resource?param1=value
```

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

**Status Codes:**
- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found

#### POST /resource

[Description of what this endpoint does]

**Request Body:**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Example Request:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"field1":"value1"}' \
  https://api.example.com/v1/resource
```

**Example Response:**
```json
{
  "status": "success",
  "id": "123",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /resource/{id}

[Update resource description]

#### DELETE /resource/{id}

[Delete resource description]

## Request/Response Format

[Explain the general structure of requests and responses]

### Request Headers

[Common headers required or recommended]

### Response Structure

[Standard response format used across all endpoints]

```json
{
  "status": "success|error",
  "data": {},
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Error Codes

[Comprehensive list of error codes and their meanings]

| Code | HTTP Status | Description | Resolution |
|------|-------------|-------------|------------|
| `INVALID_INPUT` | 400 | Invalid request parameters | Check parameter format |
| `UNAUTHORIZED` | 401 | Authentication failed | Verify API credentials |
| `FORBIDDEN` | 403 | Insufficient permissions | Check account permissions |
| `NOT_FOUND` | 404 | Resource not found | Verify resource ID |
| `RATE_LIMITED` | 429 | Too many requests | Wait and retry |
| `SERVER_ERROR` | 500 | Internal server error | Contact support |

## Webhooks

[If applicable: Explain webhook system for event notifications]

### Available Events

[List webhook events]

### Webhook Payload

[Show webhook payload structure]

## SDKs and Libraries

[If available: List official and community SDKs]

- **Python**: `pip install project-sdk`
- **JavaScript**: `npm install project-sdk`
- **Go**: `go get github.com/project/sdk`

## Examples

[Provide common use case examples]

### Example 1: [Use Case Name]

[Step-by-step example of common workflow]

### Example 2: [Use Case Name]

[Another practical example]

## Changelog

[Link to API changelog or version history]

## Support

[How to get help with API integration]
