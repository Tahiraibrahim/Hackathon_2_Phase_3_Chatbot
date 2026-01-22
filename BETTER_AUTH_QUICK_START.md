# Better Auth Quick Start Guide

## What Changed?

✅ **Replaced**: Custom JWT auth system
✅ **With**: Better Auth library (production-grade)
✅ **Backend Role**: Token verification only (no longer issues tokens)
✅ **Frontend Role**: Handles signup/login via Better Auth

## Quick Commands

### Start Development

```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn backend.main:app --reload

# Terminal 2: Start Frontend
cd frontend
npm run dev
```

Visit: http://localhost:3000

### Database Setup

```bash
cd backend
python -c "from backend.db import create_db_and_tables; create_db_and_tables()"
```

## Key Files

### Frontend Auth
- `frontend/lib/auth.ts` - Better Auth configuration
- `frontend/app/login/page.tsx` - Login page (uses `authClient.signIn.email()`)
- `frontend/app/signup/page.tsx` - Signup page (uses `authClient.signUp.email()`)
- `frontend/lib/api.ts` - API client with token interceptor
- `frontend/context/AuthContext.tsx` - Auth state management

### Backend Auth
- `backend/auth.py` - Token verification (no signup/login endpoints)
- `backend/models.py` - Database models including Better Auth tables

## How It Works

### User Signs Up
```
User enters email/password → Better Auth creates user →
JWT token generated → Stored in localStorage → Redirected to dashboard
```

### User Makes API Request
```
Frontend intercepts request → Gets JWT from Better Auth →
Adds "Authorization: Bearer {token}" header → Backend verifies signature →
Returns response
```

### Backend Verifies Token
```
Receives: "Authorization: Bearer {token}"
→ Decodes JWT using BETTER_AUTH_SECRET
→ Checks expiration
→ Extracts user ID
→ Validates user in DB
→ Processes request
```

## Important Environment Variables

Both frontend and backend **must use the same `BETTER_AUTH_SECRET`**:

```
BETTER_AUTH_SECRET=hackathon_phase2_secure_secret_key_2025_tahira
```

If they don't match, token verification will fail!

## Testing Auth

### Test Signup
```bash
1. Go to http://localhost:3000/signup
2. Enter email, password (min 8 chars), confirm password
3. Should redirect to dashboard
```

### Test API with Token
```bash
# Get token from browser console:
token = localStorage.getItem('authToken')

# Test API:
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer $token"
```

### Test Invalid Token
```bash
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer invalid"

# Should return: {"detail": "Invalid token: ..."}
```

## Common Issues

### "Invalid authentication credentials"
- [ ] Check `BETTER_AUTH_SECRET` matches between frontend and backend
- [ ] Verify token is in localStorage: `localStorage.getItem('authToken')`
- [ ] Check Authorization header is sent: Network tab in DevTools

### Signup/Login doesn't work
- [ ] Frontend must be running (serves Better Auth API)
- [ ] Check browser console for errors
- [ ] Verify database is accessible

### 401 Errors on API Calls
- [ ] Token might be expired (15 minute default)
- [ ] Try logging out and back in
- [ ] Check token exists in localStorage
- [ ] Verify Authorization header is present (Network tab)

### "User not found"
- [ ] Happens when token is valid but user doesn't exist in DB
- [ ] Usually means database wasn't created properly
- [ ] Run: `python -c "from backend.db import create_db_and_tables; create_db_and_tables()"`

## Token Inspection

```javascript
// In browser console:
const token = localStorage.getItem('authToken');
const payload = JSON.parse(atob(token.split('.')[1]));
console.log(payload);

// Look for:
// - "sub": user ID
// - "exp": expiration timestamp
// - "iat": issued at timestamp
```

## Making API Calls

### From Frontend (Already Configured)
```typescript
import { taskApi } from '@/lib/api';

// Token automatically attached by interceptor
const tasks = await taskApi.getTasks();
```

### Manual cURL
```bash
TOKEN=$(curl -s http://localhost:3000 | grep -o 'authToken":"[^"]*' | cut -d'"' -f3)
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer $TOKEN"
```

## Deploying

### Environment Variables Required

**Frontend**:
```
BETTER_AUTH_SECRET=<same as backend>
DATABASE_URL=<postgres url>
NEXT_PUBLIC_API_URL=<backend api url>
NEXT_PUBLIC_APP_URL=<frontend url>
```

**Backend**:
```
DATABASE_URL=<same postgres url as frontend>
BETTER_AUTH_SECRET=<same as frontend>
BETTER_AUTH_URL=<frontend url>
```

⚠️ **Critical**: Both `BETTER_AUTH_SECRET` must be **identical** or token verification will fail

## Next Steps

1. ✅ Signup/login working?
2. ✅ Can create tasks?
3. ✅ Profile shows correct info?
4. ✅ Logout works?

If all yes → You're good to go! 🚀

## Advanced

### Add OAuth (Google, GitHub, etc.)
See Better Auth docs: https://www.better-auth.com/docs/integrations

### Custom Token Claims
Modify Better Auth config in `frontend/lib/auth.ts` to include custom claims in JWT

### Session Management
Better Auth stores sessions in DB. Sessions are automatically managed.

## Support

**Check docs**:
- `BETTER_AUTH_MIGRATION_SUMMARY.md` - Full implementation details
- `BETTER_AUTH_TESTING.md` - Comprehensive testing guide
- Better Auth docs: https://www.better-auth.com

**Debug**:
```bash
# Backend logs
cd backend && python -m uvicorn backend.main:app --reload

# Check token
# Browser: localStorage.getItem('authToken')

# Network check
# DevTools Network tab → Look for Authorization header
```
