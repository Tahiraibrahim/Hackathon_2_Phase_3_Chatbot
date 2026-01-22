# Better Auth Integration Testing Guide

This document outlines the testing procedure for the Better Auth migration from custom JWT authentication.

## Architecture Overview

### Frontend (Next.js)
- **Auth Library**: Better Auth with JWT plugin
- **Token Storage**: localStorage and cookies (Better Auth sessions)
- **Auth Flow**:
  1. User signs up/in via Better Auth (`authClient.signUp.email` or `authClient.signIn.email`)
  2. Better Auth creates session and JWT token
  3. Frontend retrieves JWT token via `getJWTToken()`
  4. Token is attached to all API requests via axios interceptor

### Backend (FastAPI)
- **Auth Method**: JWT token verification (only)
- **Token Source**: Better Auth (frontend)
- **Verification**:
  1. Backend receives JWT in Authorization header
  2. Decodes and verifies signature using `BETTER_AUTH_SECRET`
  3. Extracts user ID from token payload
  4. Fetches user from database for validation

## Setup Steps

### 1. Install Dependencies

**Backend**:
```bash
cd backend
pip install -e .
# or
pip install httpx>=0.24.0  # For JWKS fetching (if needed in future)
```

**Frontend**:
```bash
cd frontend
npm install
# better-auth should already be installed
```

### 2. Environment Configuration

**Backend** (`.env`):
```
DATABASE_URL=postgresql://neondb_owner:npg_Y6VMRp0SjbiB@...
BETTER_AUTH_SECRET=hackathon_phase2_secure_secret_key_2025_tahira
BETTER_AUTH_URL=http://localhost:3000
```

**Frontend** (`.env.local`):
```
BETTER_AUTH_SECRET=hackathon_phase2_secure_secret_key_2025_tahira
DATABASE_URL=postgresql://neondb_owner:npg_Y6VMRp0SjbiB@...
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Database Migration

Before running the application, create the new tables:

```bash
cd backend
python -c "from backend.db import create_db_and_tables; create_db_and_tables()"
```

This will create:
- `accounts` - OAuth/linked accounts
- `sessions` - User sessions
- `verifications` - Email verification tokens
- Updated `users` table with `name` field

## Testing Procedures

### Test 1: User Signup

**Steps**:
1. Navigate to `http://localhost:3000/signup`
2. Enter:
   - Full Name: `Test User`
   - Email: `test@example.com`
   - Password: `TestPassword123!`
   - Confirm Password: `TestPassword123!`
3. Click "Sign up"

**Expected Behavior**:
- [ ] Form validates (password min 8 chars, passwords match)
- [ ] Better Auth creates user in database
- [ ] User is automatically logged in
- [ ] Redirected to `/dashboard`
- [ ] Toast notification: "Account created! Welcome to TaskFlow, Test User!"

**Database Checks**:
```sql
-- Check user was created
SELECT * FROM users WHERE email = 'test@example.com';

-- Check session was created
SELECT * FROM sessions WHERE user_id = 1;
```

### Test 2: User Login

**Steps**:
1. Navigate to `http://localhost:3000/login`
2. Enter:
   - Email: `test@example.com`
   - Password: `TestPassword123!`
3. Click "Sign in"

**Expected Behavior**:
- [ ] Form validates input
- [ ] Better Auth authenticates user
- [ ] JWT token is retrieved
- [ ] Redirected to `/dashboard`
- [ ] Toast notification: "Welcome back! You have successfully logged in."

**Token Verification**:
```javascript
// In browser console:
localStorage.getItem('authToken')  // Should show JWT token
```

### Test 3: JWT Token Verification

**Backend Token Verification Test**:

```bash
# 1. Get a valid token from a logged-in user
# Copy from: localStorage.getItem('authToken')

# 2. Test the token against backend
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json"
```

**Expected Response**:
```json
[]  // Empty array if no tasks yet, or array of tasks
```

**Token Expiry Test**:
```bash
# Wait for token to expire (default 15 minutes in Better Auth)
# Or manually craft an expired token
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer <EXPIRED_TOKEN>" \
  -H "Content-Type: application/json"
```

**Expected Response**:
```json
{
  "detail": "Token has expired"
}
```

### Test 4: Dashboard Access

**Steps**:
1. After login, verify you're on `/dashboard`
2. Check that tasks load correctly
3. Navigate to different dashboard sections:
   - Analytics (`/dashboard/analytics`)
   - Profile (`/dashboard/profile`)
   - Settings (`/dashboard/settings`)
   - Search (`/dashboard/search`)

**Expected Behavior**:
- [ ] All pages load successfully
- [ ] User information displays correctly in profile
- [ ] Tasks are fetched and displayed
- [ ] User cannot access dashboard without valid token (test by clearing token from localStorage)

### Test 5: Profile Page Verification

**Steps**:
1. After login, navigate to `/dashboard/profile`
2. Verify user information displays:
   - Username/Avatar
   - Email address
   - Account type (Pro Account)
   - Member since date

**Expected Behavior**:
- [ ] Profile page shows correct user information
- [ ] Avatar shows first letter of username
- [ ] Email matches the logged-in user's email

### Test 6: Task Operations with Better Auth

**Create Task**:
```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing task creation with Better Auth",
    "priority": "High",
    "category": "Testing"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "title": "Test Task",
  "description": "Testing task creation with Better Auth",
  "is_completed": false,
  "priority": "High",
  "category": "Testing",
  "due_date": null,
  "is_recurring": false,
  "user_id": 1
}
```

**Get Tasks**:
```bash
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json"
```

**Expected Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Test Task",
    "description": "Testing task creation with Better Auth",
    "is_completed": false,
    "priority": "High",
    "category": "Testing",
    "due_date": null,
    "is_recurring": false,
    "user_id": 1
  }
]
```

### Test 7: Unauthorized Access (No Token)

**Steps**:
```bash
curl -X GET http://localhost:8000/api/todos \
  -H "Content-Type: application/json"
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

**Frontend Behavior**:
- [ ] 401 response redirects to `/login`
- [ ] localStorage authToken is cleared
- [ ] User sees login page

### Test 8: Invalid Token

**Steps**:
```bash
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer invalid.token.here" \
  -H "Content-Type: application/json"
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Invalid token: <error details>"
}
```

### Test 9: Logout Flow

**Steps**:
1. Navigate to `/dashboard`
2. Click logout button in sidebar or navbar
3. Observe redirect

**Expected Behavior**:
- [ ] `authToken` is removed from localStorage
- [ ] `userName` is removed from localStorage
- [ ] User is redirected to `/login`
- [ ] Attempting to access protected routes (dashboard) redirects to login

## Edge Cases to Test

### Case 1: Multiple Tabs/Windows
1. Open app in two browser tabs
2. Login in first tab
3. Switch to second tab - verify authenticated state

**Expected**: Second tab should recognize login from first tab

### Case 2: Token Refresh
1. Login and get JWT token
2. Token expires after 15 minutes
3. Make another API request

**Expected**: Request fails with 401, user is logged out

### Case 3: Database Connection Loss
1. Stop the PostgreSQL database
2. Try to login
3. Try to access protected routes

**Expected**: Clear error messages, graceful degradation

### Case 4: Frontend-Backend Version Mismatch
- Verify both use same `BETTER_AUTH_SECRET`
- Verify token algorithm matches (HS256)

## Rollback Instructions

If issues occur, rollback to custom JWT:

1. **Backend**: Restore `auth.py` endpoints for `/signup` and `/login`
2. **Frontend**: Restore login/signup pages to use direct API calls
3. **Database**: Keep the new tables or drop them (no dependent data)

## Debugging Tips

### Check Better Auth Session
```javascript
// In browser console
const { authClient } = await import('@/lib/auth');
const { data: session } = await authClient.getSession();
console.log(session);
```

### Verify JWT Token
```javascript
// In browser console
const token = localStorage.getItem('authToken');
const parts = token.split('.');
const payload = JSON.parse(atob(parts[1]));
console.log(payload);
```

### Check Backend Logs
```bash
cd backend
python -m uvicorn backend.main:app --reload
# Watch for JWT verification errors in logs
```

## Success Checklist

- [ ] User can signup with email and password
- [ ] User can login with credentials
- [ ] JWT token is generated and stored
- [ ] Token is attached to all API requests
- [ ] Backend verifies token signature correctly
- [ ] Tasks can be created, read, updated, deleted
- [ ] Profile page shows correct user information
- [ ] Dashboard and protected routes work
- [ ] Logout clears token and redirects
- [ ] Invalid tokens return 401 errors
- [ ] Expired tokens are handled gracefully
- [ ] CORS works between frontend and backend

## Support

For issues:
1. Check `.env` files match between frontend and backend
2. Verify `BETTER_AUTH_SECRET` is identical
3. Clear browser cache and localStorage
4. Restart both frontend and backend services
5. Check network tab in browser DevTools for auth header
6. Review backend server logs for token verification errors
