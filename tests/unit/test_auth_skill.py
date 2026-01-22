"""
Unit Tests for auth_skill.py

Following TDD approach:
1. Write tests first (RED phase) ✓
2. Run tests - they should FAIL
3. Implement auth_skill.py (GREEN phase)
4. Run tests - they should PASS
5. Verify 90%+ coverage

Test Coverage:
- hash_password: Generate bcrypt hashes
- verify_password: Verify plaintext against hash
- create_jwt_token: Create JWT with user_id and expiry
- decode_jwt_token: Decode JWT and extract user_id
"""

import pytest
import time
from backend.skills.auth_skill import (
    hash_password,
    verify_password,
    create_jwt_token,
    decode_jwt_token,
)


# =============================================================================
# TEST: hash_password
# =============================================================================

class TestHashPassword:
    """Test suite for hash_password function"""

    def test_hash_password_returns_string(self):
        """Should return a string hash"""
        hashed = hash_password("mypassword")

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_returns_bcrypt_hash(self):
        """Should return a bcrypt hash (starts with $2b$)"""
        hashed = hash_password("mypassword")

        # Bcrypt hashes start with $2b$ (or $2a$, $2y$)
        assert hashed.startswith("$2")

    def test_hash_password_different_for_same_input(self):
        """Should generate different hashes for same password (salt)"""
        password = "mypassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Due to salt, hashes should be different
        assert hash1 != hash2

    def test_hash_password_with_empty_string(self):
        """Should handle empty string password"""
        hashed = hash_password("")

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_with_long_password(self):
        """Should handle long passwords"""
        long_password = "a" * 1000
        hashed = hash_password(long_password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_with_special_characters(self):
        """Should handle special characters"""
        password = "p@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert hashed.startswith("$2")

    def test_hash_password_with_unicode(self):
        """Should handle unicode characters"""
        password = "پاسورڈ"  # Urdu
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_with_spaces(self):
        """Should handle passwords with spaces"""
        password = "my password with spaces"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0


# =============================================================================
# TEST: verify_password
# =============================================================================

class TestVerifyPassword:
    """Test suite for verify_password function"""

    def test_verify_password_returns_true_for_correct_password(self):
        """Should return True when password matches hash"""
        password = "mypassword"
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_returns_false_for_incorrect_password(self):
        """Should return False when password doesn't match hash"""
        password = "mypassword"
        hashed = hash_password(password)

        result = verify_password("wrongpassword", hashed)

        assert result is False

    def test_verify_password_case_sensitive(self):
        """Should be case-sensitive"""
        password = "MyPassword"
        hashed = hash_password(password)

        result = verify_password("mypassword", hashed)

        assert result is False

    def test_verify_password_with_empty_string(self):
        """Should verify empty string password"""
        password = ""
        hashed = hash_password(password)

        result = verify_password("", hashed)

        assert result is True

    def test_verify_password_with_special_characters(self):
        """Should verify passwords with special characters"""
        password = "p@ssw0rd!#$%"
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_with_unicode(self):
        """Should verify unicode passwords"""
        password = "پاسورڈ"  # Urdu
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_with_spaces(self):
        """Should verify passwords with spaces"""
        password = "my password with spaces"
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_returns_false_for_invalid_hash(self):
        """Should return False for invalid hash format"""
        result = verify_password("password", "not_a_valid_hash")

        assert result is False


# =============================================================================
# TEST: create_jwt_token
# =============================================================================

class TestCreateJwtToken:
    """Test suite for create_jwt_token function"""

    def test_create_jwt_token_returns_string(self):
        """Should return a string token"""
        token = create_jwt_token(
            user_id=1,
            secret_key="test_secret",
            expiry_minutes=60
        )

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_jwt_token_contains_three_parts(self):
        """Should return JWT with three parts (header.payload.signature)"""
        token = create_jwt_token(
            user_id=1,
            secret_key="test_secret",
            expiry_minutes=60
        )

        parts = token.split(".")
        assert len(parts) == 3

    def test_create_jwt_token_with_different_user_ids(self):
        """Should create different tokens for different user IDs"""
        token1 = create_jwt_token(user_id=1, secret_key="secret")
        token2 = create_jwt_token(user_id=2, secret_key="secret")

        assert token1 != token2

    def test_create_jwt_token_with_different_secrets(self):
        """Should create different tokens for different secrets"""
        token1 = create_jwt_token(user_id=1, secret_key="secret1")
        token2 = create_jwt_token(user_id=1, secret_key="secret2")

        assert token1 != token2

    def test_create_jwt_token_default_expiry(self):
        """Should use default expiry if not specified"""
        token = create_jwt_token(user_id=1, secret_key="secret")

        # Should not raise error and token should be valid
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_jwt_token_custom_expiry(self):
        """Should accept custom expiry minutes"""
        token = create_jwt_token(
            user_id=1,
            secret_key="secret",
            expiry_minutes=120
        )

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_jwt_token_with_large_user_id(self):
        """Should handle large user IDs"""
        token = create_jwt_token(
            user_id=999999999,
            secret_key="secret"
        )

        assert isinstance(token, str)
        assert len(token) > 0


# =============================================================================
# TEST: decode_jwt_token
# =============================================================================

class TestDecodeJwtToken:
    """Test suite for decode_jwt_token function"""

    def test_decode_jwt_token_returns_user_id(self):
        """Should decode token and return user_id"""
        user_id = 42
        token = create_jwt_token(user_id=user_id, secret_key="secret")

        decoded_user_id = decode_jwt_token(token=token, secret_key="secret")

        assert decoded_user_id == user_id

    def test_decode_jwt_token_with_different_user_ids(self):
        """Should correctly decode different user IDs"""
        for user_id in [1, 100, 999, 123456]:
            token = create_jwt_token(user_id=user_id, secret_key="secret")
            decoded = decode_jwt_token(token=token, secret_key="secret")
            assert decoded == user_id

    def test_decode_jwt_token_returns_none_for_invalid_token(self):
        """Should return None for invalid token format"""
        decoded = decode_jwt_token(
            token="invalid.token.format",
            secret_key="secret"
        )

        assert decoded is None

    def test_decode_jwt_token_returns_none_for_wrong_secret(self):
        """Should return None when decoded with wrong secret"""
        token = create_jwt_token(user_id=1, secret_key="correct_secret")

        decoded = decode_jwt_token(token=token, secret_key="wrong_secret")

        assert decoded is None

    def test_decode_jwt_token_returns_none_for_expired_token(self):
        """Should return None for expired token"""
        # Create token that expires in 1 second
        token = create_jwt_token(
            user_id=1,
            secret_key="secret",
            expiry_minutes=0.0001  # Very short expiry (~0.006 seconds)
        )

        # Wait for token to expire
        time.sleep(0.01)

        decoded = decode_jwt_token(token=token, secret_key="secret")

        assert decoded is None

    def test_decode_jwt_token_returns_none_for_malformed_token(self):
        """Should return None for malformed token"""
        decoded = decode_jwt_token(
            token="not_a_jwt_token",
            secret_key="secret"
        )

        assert decoded is None

    def test_decode_jwt_token_returns_none_for_empty_token(self):
        """Should return None for empty token"""
        decoded = decode_jwt_token(token="", secret_key="secret")

        assert decoded is None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestAuthSkillIntegration:
    """Integration tests for auth_skill functions together"""

    def test_hash_and_verify_workflow(self):
        """Should support hash → verify workflow"""
        password = "mypassword"

        # Hash password
        hashed = hash_password(password)

        # Verify correct password
        assert verify_password(password, hashed) is True

        # Verify incorrect password
        assert verify_password("wrongpassword", hashed) is False

    def test_create_and_decode_token_workflow(self):
        """Should support create → decode token workflow"""
        user_id = 123
        secret_key = "test_secret_key"

        # Create token
        token = create_jwt_token(user_id=user_id, secret_key=secret_key)

        # Decode token
        decoded_user_id = decode_jwt_token(token=token, secret_key=secret_key)

        assert decoded_user_id == user_id

    def test_multiple_users_workflow(self):
        """Should handle multiple users correctly"""
        secret_key = "shared_secret"

        # User 1
        user1_id = 1
        user1_password = "password1"
        user1_hash = hash_password(user1_password)
        user1_token = create_jwt_token(user1_id, secret_key)

        # User 2
        user2_id = 2
        user2_password = "password2"
        user2_hash = hash_password(user2_password)
        user2_token = create_jwt_token(user2_id, secret_key)

        # Verify User 1
        assert verify_password(user1_password, user1_hash) is True
        assert verify_password(user2_password, user1_hash) is False
        assert decode_jwt_token(user1_token, secret_key) == user1_id

        # Verify User 2
        assert verify_password(user2_password, user2_hash) is True
        assert verify_password(user1_password, user2_hash) is False
        assert decode_jwt_token(user2_token, secret_key) == user2_id

    def test_password_hash_and_token_are_independent(self):
        """Should show that password hashing and JWT tokens are independent"""
        user_id = 1
        password = "mypassword"
        secret_key = "jwt_secret"

        # Hash password (uses bcrypt)
        hashed_password = hash_password(password)

        # Create JWT token (uses JWT)
        jwt_token = create_jwt_token(user_id, secret_key)

        # These are completely different
        assert hashed_password != jwt_token
        assert not hashed_password.startswith("eyJ")  # JWT tokens start with eyJ
        assert hashed_password.startswith("$2")  # Bcrypt hashes start with $2

        # Password verification doesn't depend on JWT
        assert verify_password(password, hashed_password) is True

        # JWT decoding doesn't depend on password
        assert decode_jwt_token(jwt_token, secret_key) == user_id
