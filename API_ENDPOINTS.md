# Better Auth API Endpoints

## Base URL

```
http://localhost:3001/api/auth
```
(or http://localhost:3000 if port 3001 is not in use)

---

## Authentication Endpoints

### 1. Sign Up (Create Account)

**Endpoint:** `POST /api/auth/sign-up/email`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "John Doe"
}
```

**Success Response (200):**
```json
{
  "token": "aAbBcCdDeEfFgGhHiIjJkKlMnNoOpPqQrRsStTuUvVwXyZ0123456789",
  "user": {
    "id": "DLyTsDDqpM5Z82Mbmu2pFpYizhzVCJws",
    "name": "John Doe",
    "email": "user@example.com",
    "emailVerified": false,
    "image": null,
    "createdAt": "2026-01-02T12:32:43.054Z",
    "updatedAt": "2026-01-02T12:32:43.054Z"
  }
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "message": "User with this email already exists"
}
```

**curl Example:**
```bash
curl -X POST http://localhost:3001/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123",
    "name": "John Doe"
  }'
```

**JavaScript/TypeScript Example:**
```typescript
import { authClient } from "@/lib/auth";

const response = await authClient.signUp.email({
  email: "john@example.com",
  password: "SecurePassword123",
  name: "John Doe"
});

if (response.data) {
  console.log("Signup successful:", response.data.user);
} else {
  console.error("Signup failed:", response.error);
}
```

---

### 2. Sign In (Login)

**Endpoint:** `POST /api/auth/sign-in/email`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "rememberMe": true
}
```

**Success Response (200):**
```json
{
  "redirect": false,
  "token": "bBcCdDeEfFgGhHiIjJkKlMnNoOpPqQrRsStTuUvVwXyZ0123456789aA",
  "user": {
    "id": "DLyTsDDqpM5Z82Mbmu2pFpYizhzVCJws",
    "name": "John Doe",
    "email": "user@example.com",
    "emailVerified": false,
    "image": null,
    "createdAt": "2026-01-02T12:32:43.054Z",
    "updatedAt": "2026-01-02T12:32:43.054Z"
  }
}
```

**Error Response (401):**
```json
{
  "status": "error",
  "message": "Invalid email or password"
}
```

**curl Example:**
```bash
curl -X POST http://localhost:3001/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123",
    "rememberMe": true
  }'
```

**JavaScript/TypeScript Example:**
```typescript
import { authClient } from "@/lib/auth";

const response = await authClient.signIn.email({
  email: "john@example.com",
  password: "SecurePassword123",
  rememberMe: true
});

if (response.data) {
  console.log("Login successful:", response.data.user);
} else {
  console.error("Login failed:", response.error);
}
```

---

### 3. Get Session

**Endpoint:** `GET /api/auth/get-session`

**Request Headers:**
```
Content-Type: application/json
Cookie: better-auth.session_token=...
```

**Response (200 - Authenticated):**
```json
{
  "session": {
    "id": "session_id_here",
    "expiresAt": 1700000000,
    "token": "session_token_here",
    "createdAt": "2026-01-02T12:32:43.054Z",
    "updatedAt": "2026-01-02T12:32:43.054Z"
  },
  "user": {
    "id": "DLyTsDDqpM5Z82Mbmu2pFpYizhzVCJws",
    "name": "John Doe",
    "email": "user@example.com",
    "emailVerified": false,
    "image": null,
    "createdAt": "2026-01-02T12:32:43.054Z",
    "updatedAt": "2026-01-02T12:32:43.054Z"
  }
}
```

**Response (200 - Not Authenticated):**
```json
null
```

**curl Example:**
```bash
# Without session cookie
curl -X GET http://localhost:3001/api/auth/get-session

# With session cookie
curl -X GET http://localhost:3001/api/auth/get-session \
  -H "Cookie: better-auth.session_token=your_token_here"
```

**JavaScript/TypeScript Example:**
```typescript
import { authClient } from "@/lib/auth";

const session = await authClient.getSession();

if (session) {
  console.log("User is logged in:", session.user);
} else {
  console.log("User is not logged in");
}
```

---

### 4. Sign Out (Logout)

**Endpoint:** `POST /api/auth/sign-out`

**Request Headers:**
```
Content-Type: application/json
Cookie: better-auth.session_token=...
```

**Request Body:**
```json
{}
```

**Success Response (200):**
```json
{
  "status": "success"
}
```

**curl Example:**
```bash
curl -X POST http://localhost:3001/api/auth/sign-out \
  -H "Content-Type: application/json" \
  -H "Cookie: better-auth.session_token=your_token_here" \
  -d '{}'
```

**JavaScript/TypeScript Example:**
```typescript
import { authClient } from "@/lib/auth";

await authClient.signOut();
console.log("User logged out");
```

---

## Request Validation

### Password Requirements
- **Minimum length:** 8 characters
- **Allowed characters:** Any (no special restrictions)
- **Example valid passwords:**
  - `SecurePassword123`
  - `MyPassword@2026`
  - `P@ssw0rd!`

### Email Requirements
- **Format:** Standard email format (e.g., `user@example.com`)
- **Uniqueness:** Must not already exist in database
- **Case insensitive:** `john@example.com` and `John@example.com` are treated as same

### Name Requirements
- **For signup:** Required, any non-empty string
- **Example:** `John Doe`, `Mary Smith`, `李明`

---

## HTTP Status Codes

| Status | Meaning | Example Scenario |
|--------|---------|------------------|
| 200 | Success | Login/signup successful |
| 400 | Bad Request | Missing required field, validation error |
| 401 | Unauthorized | Invalid password, no session |
| 409 | Conflict | Email already exists |
| 500 | Server Error | Database connection error |

---

## Session Management

### How Sessions Work

1. **User creates account or logs in**
   - Server returns `token` in response
   - Browser automatically stores in HTTP-only cookie `better-auth.session_token`

2. **Cookie sent with requests**
   - All subsequent requests include the session cookie
   - No need to manually add Authorization header

3. **Session validation**
   - Each request validates session token against database
   - Expired sessions return `null`

### Cookie Details

```
Name: better-auth.session_token
Value: <token>
Domain: localhost
Path: /
HttpOnly: true
Secure: false (development)
SameSite: Lax
Max-Age: <expires in>
```

---

## Error Handling

### Signup Errors

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| User with this email already exists | 409 | Email already registered | Use different email |
| Password must be at least 8 characters | 400 | Password too short | Use longer password |
| Email is required | 400 | Missing email field | Add email field |
| Name is required | 400 | Missing name field | Add name field |

### Login Errors

| Error | Status | Cause | Solution |
|-------|--------|-------|----------|
| Invalid email or password | 401 | Wrong credentials | Check email and password |
| User not found | 401 | Email doesn't exist | Create account first |
| Session expired | 401 | Token too old | Login again |

---

## Testing with Different Tools

### curl
```bash
# Signup
curl -X POST http://localhost:3001/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123","name":"Test"}'

# Login
curl -X POST http://localhost:3001/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPassword123"}'

# Get Session
curl http://localhost:3001/api/auth/get-session
```

### Postman

1. Create new POST request
2. URL: `http://localhost:3001/api/auth/sign-up/email`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "email": "test@example.com",
  "password": "TestPassword123",
  "name": "Test User"
}
```
5. Send

### JavaScript Fetch API

```javascript
const response = await fetch('http://localhost:3001/api/auth/sign-up/email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'TestPassword123',
    name: 'Test User'
  }),
  credentials: 'include' // Include cookies
});

const data = await response.json();
console.log(data);
```

---

## Integration with Frontend

All endpoints are automatically called through the `authClient`:

```typescript
import { authClient } from "@/lib/auth";

// Signup
await authClient.signUp.email({ email, password, name });

// Login
await authClient.signIn.email({ email, password });

// Get session
const session = await authClient.getSession();

// Logout
await authClient.signOut();
```

No need to construct URLs manually - the client handles all endpoint management.

---

## Database Records Created

When a user signs up, the following database records are created:

### user table
```sql
INSERT INTO "user" (id, name, email, emailVerified, createdAt, updatedAt)
VALUES (
  'unique_id_generated_by_better_auth',
  'John Doe',
  'john@example.com',
  false,
  NOW(),
  NOW()
);
```

### account table
```sql
INSERT INTO "account" (id, userId, providerId, accountId, password, createdAt, updatedAt)
VALUES (
  'account_id',
  'user_id',
  'credential',
  'email@example.com',
  'hashed_password_by_bcrypt',
  NOW(),
  NOW()
);
```

### session table
```sql
INSERT INTO "session" (id, userId, token, expiresAt, createdAt, updatedAt)
VALUES (
  'session_id',
  'user_id',
  'session_token',
  future_timestamp,
  NOW(),
  NOW()
);
```

---

## Troubleshooting

### Issue: 404 Not Found

**Solution:**
- Check port is 3001 (not 3000)
- Verify dev server is running: `npm run dev`
- Check endpoint path exactly matches

### Issue: 500 Internal Server Error

**Solution:**
- Check `.env.local` has DATABASE_URL
- Verify database connection works
- Check dev server console for error logs
- Restart dev server

### Issue: Session not persisting

**Solution:**
- Verify browser allows cookies
- Check `credentials: 'include'` in fetch options
- Ensure cookie domain matches

### Issue: "User already exists"

**Solution:**
- Use different email
- Or delete user from database and try again

---

## Production Considerations

Before deploying to production:

1. Update `BETTER_AUTH_URL` to production domain
2. Use HTTPS endpoints (not HTTP)
3. Set strong `BETTER_AUTH_SECRET`
4. Enable cookie security flags (Secure, HttpOnly, SameSite)
5. Configure CORS if frontend is on different domain
6. Add rate limiting to prevent brute force
7. Set up database backups
8. Monitor auth endpoint logs

---

## References

- Better Auth Docs: https://better-auth.com/docs
- Endpoint Documentation: This file
- Quick Start: BETTER_AUTH_QUICKSTART.md
- Implementation Details: BETTER_AUTH_IMPLEMENTATION.md
