# Authentication System Specification

## Overview

This document specifies the authentication system implemented for the Todo application. The system provides secure user registration, login, and token-based session management using FastAPI's native security features.

## Technology Stack

### Backend Authentication Framework
- **FastAPI Custom Authentication** with `OAuth2PasswordBearer`
- **JWT (JSON Web Tokens)** for stateless authentication
- **Bcrypt** password hashing via passlib

### Core Libraries
- `pyjwt` - JWT token creation, encoding, and verification
- `passlib[bcrypt]` - Secure password hashing with bcrypt algorithm
- `python-multipart` - Form data parsing for OAuth2 password flow

## Architecture

### Authentication Flow

#### 1. User Registration (Signup)
```
Client → POST /api/auth/signup
       → {email, password, full_name}
       → Server validates & hashes password
       → Creates User record in database
       → Returns JWT token
```

#### 2. User Login
```
Client → POST /api/auth/login
       → {email, password}
       → Server verifies credentials
       → Returns JWT token
```

#### 3. Protected Endpoint Access
```
Client → GET/POST/PUT/DELETE /api/todos/*
       → Authorization: Bearer <token>
       → Server validates JWT
       → Extracts user_id from token payload
       → Processes request with user context
```

## Implementation Details

### Token Management

**Token Structure:**
```json
{
  "sub": "<user_id>",
  "exp": "<expiration_timestamp>"
}
```

**Configuration:**
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Secret Key:** Environment variable `JWT_SECRET` (defaults to "mysecretkey" for development)
- **Expiration:** 60 minutes from token creation
- **Token Location:** `Authorization` header with `Bearer` scheme

### Password Security

**Hashing Configuration:**
- **Scheme:** bcrypt
- **Context:** CryptContext from passlib
- **Deprecated schemes:** Auto-detected and rejected

**Security Features:**
- Passwords are never stored in plaintext
- One-way hashing prevents password recovery
- Salting prevents rainbow table attacks

### Database Schema

**User Model Fields:**
```python
- id: int (Primary Key, Auto-increment)
- email: str (Unique, Indexed)
- full_name: str
- password: str (Bcrypt hashed)
- created_at: datetime (Auto-generated)
```

## API Endpoints

### POST /api/auth/signup

**Purpose:** Register a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `400 Bad Request` - Email already registered

### POST /api/auth/login

**Purpose:** Authenticate existing user

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

## Authentication Middleware

### Dependency: `get_current_user`

**Purpose:** Validates JWT tokens and extracts user identity for protected endpoints

**Implementation Location:** `backend/auth.py:49`

**Process:**
1. Extracts token from `Authorization: Bearer <token>` header via OAuth2PasswordBearer
2. Decodes JWT using secret key and HS256 algorithm
3. Retrieves user_id from token payload (`sub` claim)
4. Validates user exists in database
5. Returns user_id for use in endpoint handlers

**Error Handling:**
- Missing/malformed token → `401 Unauthorized`
- Invalid signature → `401 Unauthorized`
- Expired token → `401 Unauthorized`
- User not found → `401 Unauthorized`

**Usage in Endpoints:**
```python
@app.get("/api/todos")
def list_todos(
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # user_id is guaranteed to be valid
    ...
```

## Frontend Integration

### Token Storage
The frontend stores the JWT token received from signup/login endpoints in browser storage (localStorage or sessionStorage).

### Request Headers
All authenticated API requests must include:
```
Authorization: Bearer <jwt_token>
```

### Token Lifecycle
1. **Acquisition:** Obtained from `/api/auth/signup` or `/api/auth/login`
2. **Storage:** Stored in browser storage
3. **Usage:** Attached to all protected API requests
4. **Expiration:** Valid for 60 minutes; frontend should handle 401 errors by redirecting to login
5. **Removal:** Cleared on logout or when expired

## Security Considerations

### Current Implementation
- ✅ Passwords hashed with bcrypt (industry standard)
- ✅ JWT tokens signed with HMAC-SHA256
- ✅ Token expiration enforced (60 minutes)
- ✅ Email uniqueness constraint prevents duplicate accounts
- ✅ Credentials validated before token issuance

### Production Recommendations
- 🔒 Use strong, randomly generated `JWT_SECRET` (32+ characters)
- 🔒 Store `JWT_SECRET` in environment variables, never in code
- 🔒 Enable HTTPS/TLS for all authentication endpoints
- 🔒 Implement rate limiting on login/signup endpoints
- 🔒 Add CORS restrictions to allowed origins
- 🔒 Consider refresh token mechanism for extended sessions
- 🔒 Implement account lockout after failed login attempts
- 🔒 Add email verification for new signups

## Configuration

### Environment Variables

```bash
# Required for production
JWT_SECRET=<strong_random_secret_key>

# Database configuration (inherited from db.py)
DATABASE_URL=<connection_string>
```

### CORS Settings
Current configuration in `backend/main.py:16`:
```python
allow_origins=["http://localhost:3000"]  # Frontend development URL
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**Production:** Restrict to actual frontend domain(s)

## Testing Considerations

### Unit Tests
- Password hashing and verification functions
- JWT token creation and validation
- get_current_user dependency with various token states

### Integration Tests
- Signup flow with duplicate email handling
- Login flow with invalid credentials
- Protected endpoints with valid/invalid/expired tokens
- Token expiration behavior

### Security Tests
- SQL injection attempts in email/password fields
- JWT tampering detection
- Expired token rejection
- Malformed token handling

## Future Enhancements

### Planned Features
- [ ] Email verification on signup
- [ ] Password reset flow via email
- [ ] Refresh token mechanism
- [ ] Remember me functionality
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 social login (Google, GitHub)
- [ ] Session management dashboard
- [ ] Account deletion functionality

### Performance Optimizations
- [ ] Redis caching for token blacklisting
- [ ] Rate limiting per user/IP
- [ ] Database query optimization for user lookups

## References

### Implementation Files
- `backend/auth.py` - Authentication logic, JWT handling, password hashing
- `backend/main.py` - Router registration, CORS configuration
- `backend/models.py` - User database model
- `backend/db.py` - Database session management

### External Documentation
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 with Password Flow](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Passlib Bcrypt](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html)
