"""
Auth Orchestrator
=================

Coordinates auth_skill and db_crud_skill to manage authentication operations.

CONSTRAINTS (from Constitution & ADR-001):
- ❌ NO FastAPI imports
- ❌ NO HTTP request/response handling
- ✅ ONLY: Skills (auth_skill, db_crud_skill), domain models
- ✅ Returns dictionaries with success/error/data pattern
- ✅ Must be testable WITHOUT FastAPI

Business Operations:
- signup_user: Hash password → Save user to database
- login_user: Verify password → Create JWT token

Security:
- Passwords are hashed with bcrypt before storage
- Never store plaintext passwords
- JWT tokens for authentication
"""

from typing import Dict, Any, Optional
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from skills.auth_skill import hash_password, verify_password, create_jwt_token
from models import User


class AuthOrchestrator:
    """
    Orchestrates authentication operations by coordinating auth and database skills.

    This orchestrator implements the business flow:
    1. Hash/verify passwords (auth_skill)
    2. Store/retrieve users (db operations)
    3. Generate JWT tokens (auth_skill)
    4. Return structured responses
    """

    def signup_user(
        self,
        session: Session,
        email: str,
        full_name: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Flow:
        1. Hash the password using bcrypt
        2. Create user in database
        3. Handle duplicate email errors

        Args:
            session: SQLModel database session
            email: User's email (must be unique)
            full_name: User's full name
            password: Plaintext password (will be hashed)

        Returns:
            Dict with keys:
            - success: bool (True if created, False on error)
            - user: User object if success, None otherwise
            - error: str error message if failed, None otherwise

        Examples:
            >>> orchestrator = AuthOrchestrator()
            >>> result = orchestrator.signup_user(
            ...     session, "user@example.com", "John Doe", "SecurePass123"
            ... )
            >>> result["success"]
            True
            >>> result["user"].email
            'user@example.com'
            >>> result["user"].password.startswith("$2")  # bcrypt hash
            True

            >>> result = orchestrator.signup_user(
            ...     session, "user@example.com", "Jane Doe", "pass"
            ... )
            >>> result["success"]
            False
            >>> "already exists" in result["error"].lower()
            True
        """
        # Step 1: Hash password
        hashed_password = hash_password(password)

        # Step 2: Create user object
        user = User(
            email=email,
            full_name=full_name,
            password=hashed_password,
        )

        # Step 3: Save to database (handle duplicate email)
        try:
            session.add(user)
            session.commit()
            session.refresh(user)

            return {
                "success": True,
                "user": user,
                "error": None,
            }

        except IntegrityError:
            # Duplicate email (unique constraint violation)
            session.rollback()
            return {
                "success": False,
                "user": None,
                "error": f"User with email '{email}' already exists",
            }

    def login_user(
        self,
        session: Session,
        email: str,
        password: str,
        secret_key: str,
        token_expiry_minutes: int = 60,
    ) -> Dict[str, Any]:
        """
        Authenticate a user and generate JWT token.

        Flow:
        1. Retrieve user by email
        2. Verify password matches stored hash
        3. Create JWT token with user_id

        Args:
            session: SQLModel database session
            email: User's email
            password: Plaintext password to verify
            secret_key: Secret key for JWT signing
            token_expiry_minutes: Token expiry in minutes (default: 60)

        Returns:
            Dict with keys:
            - success: bool (True if authenticated, False otherwise)
            - token: JWT token string if success, None otherwise
            - user_id: User ID if success, None otherwise
            - error: str error message if failed, None otherwise

        Examples:
            >>> orchestrator = AuthOrchestrator()
            >>> # First signup
            >>> orchestrator.signup_user(session, "user@example.com", "User", "MyPass")

            >>> # Then login
            >>> result = orchestrator.login_user(
            ...     session, "user@example.com", "MyPass", "secret_key"
            ... )
            >>> result["success"]
            True
            >>> len(result["token"]) > 50
            True
            >>> result["user_id"]
            1

            >>> # Wrong password
            >>> result = orchestrator.login_user(
            ...     session, "user@example.com", "WrongPass", "secret_key"
            ... )
            >>> result["success"]
            False
            >>> result["error"]
            'Invalid credentials'
        """
        # Step 1: Retrieve user by email
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        # Step 2: Verify user exists
        if user is None:
            return {
                "success": False,
                "token": None,
                "user_id": None,
                "error": "Invalid credentials",
            }

        # Step 3: Verify password
        password_valid = verify_password(password, user.password)
        if not password_valid:
            return {
                "success": False,
                "token": None,
                "user_id": None,
                "error": "Invalid credentials",
            }

        # Step 4: Create JWT token
        token = create_jwt_token(
            user_id=user.id,
            secret_key=secret_key,
            expiry_minutes=token_expiry_minutes,
        )

        return {
            "success": True,
            "token": token,
            "user_id": user.id,
            "error": None,
        }
