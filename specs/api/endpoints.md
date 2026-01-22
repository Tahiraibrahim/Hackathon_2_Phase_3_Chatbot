# API Endpoints Specification

**Created**: 2025-12-18
**Status**: Draft
**Phase**: Hackathon Phase 2 - Task Management System

## Overview

This specification defines the REST API endpoints for the Task Management System backend. All endpoints are secured with JWT Bearer Token authentication and follow RESTful conventions.

## Base URL

```
/api
```

All routes MUST be prefixed with `/api` as per project constitution (Section 4: Coding Standards).

---

## Authentication

### Security Model

**Type**: JWT Bearer Token Authentication

**Header Format**:
```http
Authorization: Bearer <JWT_TOKEN>
```

**Security Requirements (ALL ENDPOINTS)**:
- ✅ **MANDATORY**: Every endpoint requires a valid JWT Bearer Token in the Authorization header
- ✅ **Token Validation**: Backend must verify token signature, expiration, and claims
- ✅ **Shared Secret**: Frontend (Better Auth) and Backend (FastAPI) share JWT secret for verification
- ✅ **User Context**: Decoded JWT must contain `user_id` claim for authorization
- ✅ **401 Unauthorized**: Return if token is missing, invalid, or expired
- ✅ **403 Forbidden**: Return if user attempts to access another user's resources

**JWT Claims (Expected)**:
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "exp": 1735689600,
  "iat": 1735603200
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Human-readable error message"
}
```

**Standard HTTP Status Codes**:
- `200 OK` - Successful GET/PUT operations
- `201 Created` - Successful POST operations
- `204 No Content` - Successful DELETE operations
- `400 Bad Request` - Invalid request body or parameters
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - Valid token but insufficient permissions
- `404 Not Found` - Resource does not exist
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server errors

---

## Endpoints

### 1. List All Tasks

**Endpoint**: `GET /api/todos`

**Description**: Retrieves all tasks belonging to the authenticated user.

**Authentication**: Required (JWT Bearer Token)

**Request**:
```http
GET /api/todos HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write API specs and database schema",
    "is_completed": false,
    "user_id": 123
  },
  {
    "id": 2,
    "title": "Review pull requests",
    "description": null,
    "is_completed": true,
    "user_id": 123
  }
]
```

**Response** (401 Unauthorized):
```json
{
  "detail": "Invalid or expired token"
}
```

**Business Logic**:
- Filter tasks by `user_id` extracted from JWT token
- Return only tasks owned by authenticated user
- Return empty array `[]` if user has no tasks
- Order by `id` descending (newest first)

**Query Optimization**:
- Use indexed query on `tasks.user_id`
- No N+1 queries

---

### 2. Create New Task

**Endpoint**: `POST /api/todos`

**Description**: Creates a new task for the authenticated user.

**Authentication**: Required (JWT Bearer Token)

**Request**:
```http
POST /api/todos HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "New task title",
  "description": "Optional task description"
}
```

**Request Body Schema**:
```json
{
  "title": "string (required, max 500 chars)",
  "description": "string | null (optional, no max length)"
}
```

**Response** (201 Created):
```json
{
  "id": 3,
  "title": "New task title",
  "description": "Optional task description",
  "is_completed": false,
  "user_id": 123
}
```

**Response** (400 Bad Request):
```json
{
  "detail": "Title is required and cannot be empty"
}
```

**Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Business Logic**:
- Extract `user_id` from JWT token
- Set `user_id` automatically (user cannot specify this)
- Default `is_completed` to `false`
- Validate `title` is not empty
- `description` is optional (can be `null`)
- Return newly created task with assigned `id`

**Validation Rules**:
- `title`: Required, non-empty, max 500 characters
- `description`: Optional, no max length
- `is_completed`: Not accepted in request body (always defaults to false)
- `user_id`: Not accepted in request body (extracted from JWT)

---

### 3. Update Task

**Endpoint**: `PUT /api/todos/{id}`

**Description**: Updates a task's title, description, or completion status. User can only update their own tasks.

**Authentication**: Required (JWT Bearer Token)

**Path Parameters**:
- `id` (integer): Task ID to update

**Request**:
```http
PUT /api/todos/3 HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Updated task title",
  "description": "Updated description",
  "is_completed": true
}
```

**Request Body Schema** (All fields optional):
```json
{
  "title": "string (optional, max 500 chars)",
  "description": "string | null (optional)",
  "is_completed": "boolean (optional)"
}
```

**Response** (200 OK):
```json
{
  "id": 3,
  "title": "Updated task title",
  "description": "Updated description",
  "is_completed": true,
  "user_id": 123
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Task not found"
}
```

**Response** (403 Forbidden):
```json
{
  "detail": "You do not have permission to update this task"
}
```

**Business Logic**:
1. Extract `user_id` from JWT token
2. Fetch task by `id`
3. Verify task exists (404 if not)
4. Verify `task.user_id == authenticated_user_id` (403 if mismatch)
5. Update only provided fields (partial update)
6. Validate updated fields
7. Save and return updated task

**Validation Rules**:
- `title`: If provided, must be non-empty and max 500 chars
- `description`: Can be set to `null` to clear
- `is_completed`: If provided, must be boolean
- `user_id`: Cannot be changed (ignored if sent)

**Authorization**:
- User can only update tasks where `task.user_id == authenticated_user_id`
- Return 403 Forbidden if attempting to update another user's task

---

### 4. Delete Task

**Endpoint**: `DELETE /api/todos/{id}`

**Description**: Permanently deletes a task. User can only delete their own tasks.

**Authentication**: Required (JWT Bearer Token)

**Path Parameters**:
- `id` (integer): Task ID to delete

**Request**:
```http
DELETE /api/todos/3 HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** (204 No Content):
```
(Empty response body)
```

**Response** (404 Not Found):
```json
{
  "detail": "Task not found"
}
```

**Response** (403 Forbidden):
```json
{
  "detail": "You do not have permission to delete this task"
}
```

**Business Logic**:
1. Extract `user_id` from JWT token
2. Fetch task by `id`
3. Verify task exists (404 if not)
4. Verify `task.user_id == authenticated_user_id` (403 if mismatch)
5. Delete task from database
6. Return 204 No Content

**Authorization**:
- User can only delete tasks where `task.user_id == authenticated_user_id`
- Return 403 Forbidden if attempting to delete another user's task

**Idempotency**:
- Second DELETE to same ID returns 404 (not idempotent by REST standards)
- Alternative: Return 204 even if already deleted (more lenient)
- **Decision**: Return 404 for consistency (task truly doesn't exist)

---

## API Summary Table

| Method | Endpoint           | Description                     | Auth Required | Success Code |
|--------|--------------------|---------------------------------|---------------|--------------|
| GET    | `/api/todos`       | List all user's tasks           | Yes           | 200          |
| POST   | `/api/todos`       | Create new task                 | Yes           | 201          |
| PUT    | `/api/todos/{id}`  | Update task (partial or full)   | Yes           | 200          |
| DELETE | `/api/todos/{id}`  | Delete task                     | Yes           | 204          |

---

## Implementation Requirements

### FastAPI Setup

**Dependencies**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
```

**Authentication Dependency**:
```python
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Validates JWT token and returns user_id.
    Raises 401 if invalid.
    """
    token = credentials.credentials
    # Verify token signature and decode
    # Return user_id from JWT claims
    # Raise HTTPException(status_code=401) if invalid
```

**Route Protection**:
```python
@app.get("/api/todos")
async def list_todos(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # user_id is guaranteed to be valid here
    tasks = db.exec(select(Task).where(Task.user_id == user_id)).all()
    return tasks
```

---

## Request/Response Examples

### Creating a Task (Full Flow)

**Request**:
```http
POST /api/todos HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsImV4cCI6MTczNTY4OTYwMH0.signature
Content-Type: application/json

{
  "title": "Implement API endpoints",
  "description": "Build FastAPI routes for CRUD operations"
}
```

**Response**:
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 15,
  "title": "Implement API endpoints",
  "description": "Build FastAPI routes for CRUD operations",
  "is_completed": false,
  "user_id": 123
}
```

### Updating Task Status

**Request** (Mark as completed):
```http
PUT /api/todos/15 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "is_completed": true
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 15,
  "title": "Implement API endpoints",
  "description": "Build FastAPI routes for CRUD operations",
  "is_completed": true,
  "user_id": 123
}
```

---

## Security Checklist

- [ ] All endpoints require JWT Bearer Token in Authorization header
- [ ] Token signature verified using shared secret
- [ ] Token expiration checked on every request
- [ ] `user_id` extracted from verified JWT claims
- [ ] Tasks filtered by `user_id` on all list/read operations
- [ ] Ownership verified before update/delete operations
- [ ] 401 returned for missing/invalid tokens
- [ ] 403 returned for unauthorized resource access
- [ ] No user can access another user's tasks
- [ ] SQL injection prevented via SQLModel ORM
- [ ] No sensitive data in error messages
- [ ] CORS configured appropriately for frontend

---

## Testing Scenarios

### Positive Cases
1. ✅ Create task with valid token → 201 Created
2. ✅ List tasks with valid token → 200 OK with user's tasks
3. ✅ Update own task with valid token → 200 OK
4. ✅ Delete own task with valid token → 204 No Content
5. ✅ Create task with only title (no description) → 201 Created

### Negative Cases
1. ❌ Any endpoint without Authorization header → 401 Unauthorized
2. ❌ Any endpoint with invalid token → 401 Unauthorized
3. ❌ Any endpoint with expired token → 401 Unauthorized
4. ❌ Update another user's task → 403 Forbidden
5. ❌ Delete another user's task → 403 Forbidden
6. ❌ Create task with empty title → 400 Bad Request
7. ❌ Update/Delete non-existent task → 404 Not Found
8. ❌ Create task with title > 500 chars → 422 Unprocessable Entity

---

## Performance Considerations

1. **Database Queries**:
   - Use indexes on `user_id` for fast filtering
   - Avoid N+1 queries with relationship loading
   - Use connection pooling for concurrent requests

2. **Token Verification**:
   - Cache public keys if using asymmetric JWT
   - Verify signatures efficiently
   - Consider token caching with short TTL

3. **Response Times**:
   - Target < 100ms for CRUD operations
   - Use async/await for database operations
   - Enable database query logging in development

---

## Acceptance Criteria

- [ ] All 4 endpoints defined: GET, POST, PUT, DELETE
- [ ] All routes prefixed with `/api`
- [ ] JWT Bearer Token authentication required on ALL endpoints
- [ ] Token verification logic specified
- [ ] `user_id` extraction from JWT claims documented
- [ ] Authorization checks for update/delete operations
- [ ] Proper HTTP status codes for all scenarios
- [ ] Error response format standardized
- [ ] Request/response schemas documented
- [ ] Validation rules specified for all inputs
- [ ] Security requirements explicitly stated
- [ ] No endpoint allows cross-user data access

---

## References

- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- JWT Authentication: https://jwt.io/introduction
- REST API Best Practices: https://restfulapi.net/
- HTTPBearer: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- Constitution: `/constitution.md` (Section 4: Coding Standards)
- Database Schema: `/specs/database/schema.md`
