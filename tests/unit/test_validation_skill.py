"""
Unit Tests for validation_skill.py

Following TDD approach:
1. Write tests first (RED phase) ✓
2. Run tests - they should FAIL
3. Implement validation_skill.py (GREEN phase)
4. Run tests - they should PASS
5. Verify 90%+ coverage

Test Coverage:
- validate_task_title: All business rules and edge cases
- validate_task_category: All business rules and edge cases
"""

import pytest
from backend.skills.validation_skill import validate_task_title, validate_task_category


class TestValidateTaskTitle:
    """Test suite for validate_task_title function"""

    # =========================================================================
    # VALID CASES (should return True, None)
    # =========================================================================

    def test_valid_title_returns_true(self):
        """Valid title should return (True, None)"""
        # Arrange
        title = "Buy groceries"

        # Act
        is_valid, error_msg = validate_task_title(title)

        # Assert
        assert is_valid is True
        assert error_msg is None

    def test_valid_title_with_spaces_returns_true(self):
        """Valid title with spaces should return (True, None)"""
        is_valid, error_msg = validate_task_title("Complete project report")
        assert is_valid is True
        assert error_msg is None

    def test_valid_title_with_special_chars_returns_true(self):
        """Valid title with special characters should return (True, None)"""
        is_valid, error_msg = validate_task_title("Review PR #123 - Bug fix!")
        assert is_valid is True
        assert error_msg is None

    def test_valid_title_single_char_returns_true(self):
        """Single character title should be valid"""
        is_valid, error_msg = validate_task_title("A")
        assert is_valid is True
        assert error_msg is None

    def test_valid_title_exactly_500_chars_returns_true(self):
        """Title with exactly 500 characters should be valid"""
        title = "a" * 500
        is_valid, error_msg = validate_task_title(title)
        assert is_valid is True
        assert error_msg is None

    def test_valid_title_with_leading_trailing_spaces_returns_true(self):
        """Title with leading/trailing spaces (but has content) should be valid"""
        is_valid, error_msg = validate_task_title("  Buy groceries  ")
        assert is_valid is True
        assert error_msg is None

    def test_valid_title_with_numbers_returns_true(self):
        """Title with numbers should be valid"""
        is_valid, error_msg = validate_task_title("Complete 5 tasks by 3pm")
        assert is_valid is True
        assert error_msg is None

    def test_valid_title_with_unicode_returns_true(self):
        """Title with unicode characters should be valid"""
        is_valid, error_msg = validate_task_title("کام مکمل کریں")  # Urdu
        assert is_valid is True
        assert error_msg is None

    # =========================================================================
    # INVALID CASES - None/Empty
    # =========================================================================

    def test_none_title_returns_false_with_error(self):
        """None title should return (False, error message)"""
        is_valid, error_msg = validate_task_title(None)
        assert is_valid is False
        assert error_msg == "Title is required and cannot be empty"

    def test_empty_string_title_returns_false_with_error(self):
        """Empty string title should return (False, error message)"""
        is_valid, error_msg = validate_task_title("")
        assert is_valid is False
        assert error_msg == "Title is required and cannot be empty"

    def test_whitespace_only_title_returns_false_with_error(self):
        """Whitespace-only title should return (False, error message)"""
        is_valid, error_msg = validate_task_title("   ")
        assert is_valid is False
        assert error_msg == "Title is required and cannot be empty"

    def test_tab_only_title_returns_false_with_error(self):
        """Tab-only title should return (False, error message)"""
        is_valid, error_msg = validate_task_title("\t\t")
        assert is_valid is False
        assert error_msg == "Title is required and cannot be empty"

    def test_newline_only_title_returns_false_with_error(self):
        """Newline-only title should return (False, error message)"""
        is_valid, error_msg = validate_task_title("\n\n")
        assert is_valid is False
        assert error_msg == "Title is required and cannot be empty"

    def test_mixed_whitespace_only_title_returns_false_with_error(self):
        """Mixed whitespace-only title should return (False, error message)"""
        is_valid, error_msg = validate_task_title("  \t\n  ")
        assert is_valid is False
        assert error_msg == "Title is required and cannot be empty"

    # =========================================================================
    # INVALID CASES - Too Long
    # =========================================================================

    def test_title_exceeding_500_chars_returns_false_with_error(self):
        """Title exceeding 500 characters should return (False, error message)"""
        title = "a" * 501
        is_valid, error_msg = validate_task_title(title)
        assert is_valid is False
        assert error_msg == "Title cannot exceed 500 characters"

    def test_title_much_longer_than_500_chars_returns_false_with_error(self):
        """Title much longer than 500 characters should return (False, error message)"""
        title = "a" * 1000
        is_valid, error_msg = validate_task_title(title)
        assert is_valid is False
        assert error_msg == "Title cannot exceed 500 characters"

    # =========================================================================
    # EDGE CASES
    # =========================================================================

    def test_title_with_only_numbers_is_valid(self):
        """Title with only numbers should be valid"""
        is_valid, error_msg = validate_task_title("12345")
        assert is_valid is True
        assert error_msg is None

    def test_title_with_emojis_is_valid(self):
        """Title with emojis should be valid"""
        is_valid, error_msg = validate_task_title("Buy groceries 🛒")
        assert is_valid is True
        assert error_msg is None


class TestValidateTaskCategory:
    """Test suite for validate_task_category function"""

    # =========================================================================
    # VALID CASES (should return True, None)
    # =========================================================================

    def test_none_category_returns_true(self):
        """None category (optional field) should return (True, None)"""
        is_valid, error_msg = validate_task_category(None)
        assert is_valid is True
        assert error_msg is None

    def test_valid_category_returns_true(self):
        """Valid category should return (True, None)"""
        is_valid, error_msg = validate_task_category("Work")
        assert is_valid is True
        assert error_msg is None

    def test_valid_category_with_spaces_returns_true(self):
        """Valid category with spaces should return (True, None)"""
        is_valid, error_msg = validate_task_category("Home Improvement")
        assert is_valid is True
        assert error_msg is None

    def test_empty_string_category_returns_true(self):
        """Empty string category should be treated as valid (optional field)"""
        is_valid, error_msg = validate_task_category("")
        assert is_valid is True
        assert error_msg is None

    def test_single_char_category_returns_true(self):
        """Single character category should be valid"""
        is_valid, error_msg = validate_task_category("A")
        assert is_valid is True
        assert error_msg is None

    def test_category_exactly_100_chars_returns_true(self):
        """Category with exactly 100 characters should be valid"""
        category = "a" * 100
        is_valid, error_msg = validate_task_category(category)
        assert is_valid is True
        assert error_msg is None

    def test_category_with_special_chars_returns_true(self):
        """Category with special characters should be valid"""
        is_valid, error_msg = validate_task_category("Work/Projects")
        assert is_valid is True
        assert error_msg is None

    def test_category_with_numbers_returns_true(self):
        """Category with numbers should be valid"""
        is_valid, error_msg = validate_task_category("Q4 2024")
        assert is_valid is True
        assert error_msg is None

    def test_category_with_unicode_returns_true(self):
        """Category with unicode characters should be valid"""
        is_valid, error_msg = validate_task_category("کام")  # Urdu
        assert is_valid is True
        assert error_msg is None

    # =========================================================================
    # INVALID CASES - Too Long
    # =========================================================================

    def test_category_exceeding_100_chars_returns_false_with_error(self):
        """Category exceeding 100 characters should return (False, error message)"""
        category = "a" * 101
        is_valid, error_msg = validate_task_category(category)
        assert is_valid is False
        assert error_msg == "Category cannot exceed 100 characters"

    def test_category_much_longer_than_100_chars_returns_false_with_error(self):
        """Category much longer than 100 characters should return (False, error message)"""
        category = "a" * 500
        is_valid, error_msg = validate_task_category(category)
        assert is_valid is False
        assert error_msg == "Category cannot exceed 100 characters"

    # =========================================================================
    # EDGE CASES
    # =========================================================================

    def test_category_with_only_numbers_is_valid(self):
        """Category with only numbers should be valid"""
        is_valid, error_msg = validate_task_category("2024")
        assert is_valid is True
        assert error_msg is None

    def test_category_with_emojis_is_valid(self):
        """Category with emojis should be valid"""
        is_valid, error_msg = validate_task_category("Work 💼")
        assert is_valid is True
        assert error_msg is None

    def test_whitespace_only_category_is_valid(self):
        """Whitespace-only category is valid (optional field)"""
        is_valid, error_msg = validate_task_category("   ")
        assert is_valid is True
        assert error_msg is None


# =============================================================================
# INTEGRATION TESTS (if needed in future)
# =============================================================================

class TestValidationSkillIntegration:
    """Integration tests for validation_skill functions together"""

    def test_both_validations_pass_for_valid_inputs(self):
        """Both title and category validation should pass for valid inputs"""
        title_valid, title_error = validate_task_title("Buy groceries")
        category_valid, category_error = validate_task_category("Shopping")

        assert title_valid is True
        assert title_error is None
        assert category_valid is True
        assert category_error is None

    def test_title_fails_and_category_passes_for_empty_title(self):
        """Title validation should fail while category passes"""
        title_valid, title_error = validate_task_title("")
        category_valid, category_error = validate_task_category("Shopping")

        assert title_valid is False
        assert title_error is not None
        assert category_valid is True
        assert category_error is None

    def test_title_passes_and_category_fails_for_long_category(self):
        """Title validation should pass while category fails"""
        title_valid, title_error = validate_task_title("Buy groceries")
        category_valid, category_error = validate_task_category("a" * 101)

        assert title_valid is True
        assert title_error is None
        assert category_valid is False
        assert category_error is not None
