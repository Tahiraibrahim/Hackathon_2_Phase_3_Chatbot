from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr
from typing import Annotated, Optional
from datetime import datetime, timezone, timedelta
from urllib.parse import unquote
import secrets
import bcrypt
import uuid

from db import get_session
from models import User, Session as SessionModel, Account

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

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user: UserResponse
    session: SessionResponse
    token: str  # Session token for client-side storage

# --- Helper Functions ---
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)

def create_user_session(
    session: Session,
    user_id: str,
    request: Request
) -> SessionModel:
    """Create a new session for a user."""
    token = create_session_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)  # 7-day session

    # Extract client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    session_record = SessionModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    session.add(session_record)
    session.commit()
    session.refresh(session_record)

    return session_record

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


@router.post("/sign-up/email", response_model=AuthResponse)
def sign_up_email(
    request_data: SignUpRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Sign up a new user with email and password.

    This endpoint:
    1. Checks if the email already exists
    2. Creates a new User record
    3. Creates an Account record with hashed password
    4. Creates a session for the user
    5. Returns user, session, and token
    """
    print("\n" + "="*80)
    print("AUTH DEBUG - /sign-up/email endpoint")
    print("="*80)
    print(f"Email: {request_data.email}")
    print(f"Name: {request_data.name}")

    try:
        # 1. Check if user already exists
        statement = select(User).where(User.email == request_data.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            print(f"❌ User already exists with email: {request_data.email}")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # 2. Create new User
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            email=request_data.email,
            name=request_data.name,
            email_verified=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        session.add(new_user)

        # 3. Create Account with hashed password
        hashed_password = hash_password(request_data.password)
        account = Account(
            id=str(uuid.uuid4()),
            user_id=user_id,
            account_id=request_data.email,  # Use email as account_id for email provider
            provider_id="credential",  # Better Auth uses "credential" for email/password
            password=hashed_password,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        session.add(account)

        # Commit user and account
        session.commit()
        session.refresh(new_user)

        print(f"✅ User created: {user_id}")
        print(f"   Email: {new_user.email}")

        # 4. Create session
        session_record = create_user_session(session, user_id, request)

        print(f"✅ Session created: {session_record.id}")
        print(f"   Token: {session_record.token[:20]}...")
        print("="*80 + "\n")

        # 5. Return response
        return AuthResponse(
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                name=new_user.name,
                emailVerified=new_user.email_verified,
                image=new_user.image,
                createdAt=new_user.created_at,
                updatedAt=new_user.updated_at
            ),
            session=SessionResponse(
                id=session_record.id,
                userId=session_record.user_id,
                token=session_record.token,
                expiresAt=session_record.expires_at,
                ipAddress=session_record.ip_address,
                userAgent=session_record.user_agent,
                createdAt=session_record.created_at,
                updatedAt=session_record.updated_at
            ),
            token=session_record.token
        )

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        print(f"❌ Sign-up error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("="*80 + "\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign-up failed: {str(e)}"
        )


@router.post("/sign-in/email", response_model=AuthResponse)
def sign_in_email(
    request_data: SignInRequest,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Sign in an existing user with email and password.

    This endpoint:
    1. Finds the user by email
    2. Verifies the password from the Account table
    3. Creates a new session
    4. Returns user, session, and token
    """
    print("\n" + "="*80)
    print("AUTH DEBUG - /sign-in/email endpoint")
    print("="*80)
    print(f"Email: {request_data.email}")

    try:
        # 1. Find user by email
        statement = select(User).where(User.email == request_data.email)
        user = session.exec(statement).first()

        if not user:
            print(f"❌ User not found: {request_data.email}")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        print(f"✓ User found: {user.id}")

        # 2. Find account and verify password
        account_statement = select(Account).where(
            Account.user_id == user.id,
            Account.provider_id == "credential"
        )
        account = session.exec(account_statement).first()

        if not account or not account.password:
            print(f"❌ No credential account found for user: {user.id}")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(request_data.password, account.password):
            print(f"❌ Invalid password for user: {user.id}")
            print("="*80 + "\n")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        print(f"✓ Password verified for user: {user.id}")

        # 3. Create new session
        session_record = create_user_session(session, user.id, request)

        print(f"✅ Sign-in successful for user: {user.id}")
        print(f"   Session: {session_record.id}")
        print(f"   Token: {session_record.token[:20]}...")
        print("="*80 + "\n")

        # 4. Return response
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                emailVerified=user.email_verified,
                image=user.image,
                createdAt=user.created_at,
                updatedAt=user.updated_at
            ),
            session=SessionResponse(
                id=session_record.id,
                userId=session_record.user_id,
                token=session_record.token,
                expiresAt=session_record.expires_at,
                ipAddress=session_record.ip_address,
                userAgent=session_record.user_agent,
                createdAt=session_record.created_at,
                updatedAt=session_record.updated_at
            ),
            token=session_record.token
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Sign-in error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print("="*80 + "\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign-in failed: {str(e)}"
        )