from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Annotated, Optional
from datetime import datetime, timezone, timedelta
from urllib.parse import unquote

from db import get_session
from models import User, Session as SessionModel

# Expiry buffer to handle timezone/clock skew issues
EXPIRY_BUFFER_MINUTES = 5

router = APIRouter()

# Security Config
security = HTTPBearer()

# --- Models ---
class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    emailVerified: bool
    image: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

class SessionResponse(BaseModel):
    id: str
    userId: str
    token: str
    expiresAt: datetime
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

class GetSessionResponse(BaseModel):
    user: UserResponse
    session: SessionResponse

# --- Dependency ---
def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Session = Depends(get_session)
) -> str:
    """
    Verify Better Auth session token by checking the database.

    Logic:
    1. Extract Bearer token from Authorization header
    2. Query session table for matching token
    3. Validate session exists and hasn't expired (with 5-minute buffer)
    4. Return string user_id from Better Auth

    Returns:
        str: String user ID from Better Auth
    """
    token = credentials.credentials
    # Decode token to handle %3D issues from frontend cookies
    token = unquote(token)

    # Strip signature (everything after the first dot) if present
    # Frontend may send signed tokens (token.signature), but DB stores only raw token
    if "." in token:
        token = token.split(".")[0]

    print("\n" + "="*80)
    print("AUTH DEBUG - get_current_user()")
    print("="*80)
    print(f"Token received: {token[:20]}...{token[-10:] if len(token) > 30 else token}")

    try:
        # 1. Query session table for this token
        statement = select(SessionModel).where(SessionModel.token == token)
        result = session.exec(statement).first()

        # 2. Check if session exists
        if not result:
            print("❌ Token NOT found in database")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(f"✓ Token found in DB: Yes")
        print(f"  Session ID: {result.id}")
        print(f"  User ID (from DB): {result.user_id}")

        # 3. Check if session has expired (with buffer for timezone/clock skew)
        current_time = datetime.now(timezone.utc)

        # Make expires_at timezone-aware if it's naive
        expires_at = result.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Add buffer to allow for clock skew
        buffered_current_time = current_time - timedelta(minutes=EXPIRY_BUFFER_MINUTES)

        print(f"  Token Expiry Time: {expires_at.isoformat()}")
        print(f"  Current Server Time (UTC): {current_time.isoformat()}")
        print(f"  Buffered Check Time (UTC-{EXPIRY_BUFFER_MINUTES}m): {buffered_current_time.isoformat()}")

        if expires_at < buffered_current_time:
            time_diff = (current_time - expires_at).total_seconds() / 60
            print(f"❌ Session EXPIRED: Token expired {time_diff:.1f} minutes ago")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        time_remaining = (expires_at - current_time).total_seconds() / 60
        print(f"✓ Session valid: {time_remaining:.1f} minutes remaining")

        # 4. Verify user still exists
        user = session.get(User, result.user_id)
        if not user:
            print(f"❌ User NOT found: user_id={result.user_id}")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(f"✓ User found: {user.email}")
        print(f"✅ Authentication successful for user: {user.id}")
        print("="*80 + "\n")

        # 5. Return string user_id from Better Auth
        return user.id

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any other errors
        print(f"❌ Unexpected error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("="*80 + "\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Routes ---
@router.get("/get-session", response_model=GetSessionResponse)
def get_session(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Session = Depends(get_session)
):
    """
    Get current session and user information.

    This endpoint validates the Bearer token and returns the user and session details
    in the format that Better Auth expects for session persistence.

    Returns:
        GetSessionResponse: User and session information
    """
    token = credentials.credentials
    # Decode token to handle %3D issues from frontend cookies
    token = unquote(token)

    # Strip signature (everything after the first dot) if present
    # Frontend may send signed tokens (token.signature), but DB stores only raw token
    if "." in token:
        token = token.split(".")[0]

    print("\n" + "="*80)
    print("AUTH DEBUG - /get-session endpoint")
    print("="*80)
    print(f"Token received: {token[:20]}...{token[-10:] if len(token) > 30 else token}")

    try:
        # Query session table for this token
        statement = select(SessionModel).where(SessionModel.token == token)
        session_record = session.exec(statement).first()

        # Check if session exists
        if not session_record:
            print("❌ Token NOT found in database")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(f"✓ Token found in DB: Yes")
        print(f"  Session ID: {session_record.id}")
        print(f"  User ID (from DB): {session_record.user_id}")

        # Check if session has expired (with buffer for timezone/clock skew)
        current_time = datetime.now(timezone.utc)

        # Make expires_at timezone-aware if it's naive
        expires_at = session_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # Add buffer to allow for clock skew
        buffered_current_time = current_time - timedelta(minutes=EXPIRY_BUFFER_MINUTES)

        print(f"  Token Expiry Time: {expires_at.isoformat()}")
        print(f"  Current Server Time (UTC): {current_time.isoformat()}")
        print(f"  Buffered Check Time (UTC-{EXPIRY_BUFFER_MINUTES}m): {buffered_current_time.isoformat()}")

        if expires_at < buffered_current_time:
            time_diff = (current_time - expires_at).total_seconds() / 60
            print(f"❌ Session EXPIRED: Token expired {time_diff:.1f} minutes ago")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        time_remaining = (expires_at - current_time).total_seconds() / 60
        print(f"✓ Session valid: {time_remaining:.1f} minutes remaining")

        # Get user information
        user = session.get(User, session_record.user_id)
        if not user:
            print(f"❌ User NOT found: user_id={session_record.user_id}")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(f"✓ User found: {user.email}")
        print(f"✅ Session retrieval successful for user: {user.id}")
        print("="*80 + "\n")

        # Build response in Better Auth format
        return GetSessionResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                emailVerified=user.email_verified,
                image=user.image,
                createdAt=user.created_at,
                updatedAt=user.updated_at,
            ),
            session=SessionResponse(
                id=session_record.id,
                userId=session_record.user_id,
                token=session_record.token,
                expiresAt=session_record.expires_at,
                ipAddress=session_record.ip_address,
                userAgent=session_record.user_agent,
                createdAt=session_record.created_at,
                updatedAt=session_record.updated_at,
            ),
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any other errors
        print(f"❌ Unexpected error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("="*80 + "\n")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )