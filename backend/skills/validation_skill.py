"""
Validation Skill
================

Pure business logic for input validation, framework-agnostic, independently testable.

CONSTRAINTS (from Constitution & ADR-001):
- ❌ NO FastAPI imports
- ❌ NO HTTP request/response handling
- ❌ NO HTML/template rendering
- ✅ ONLY: Python standard library
- ✅ Functions accept primitive types
- ✅ Functions return primitive types (bool, str, None)
- ✅ Must be testable WITHOUT FastAPI

This Skill contains validation logic extracted from backend/main.py:
- create_todo (lines 98-106): Title and category validation
- update_todo (lines 137-142, 154-155): Title and category validation

Business Rules:
- Task Title: Required, max 500 characters, cannot be empty/whitespace
- Task Category: Optional, max 100 characters if provided
"""

from typing import Optional, Tuple


def validate_task_title(title: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate task title according to business rules.

    Business Rules:
    1. Title is required (cannot be None or empty string)
    2. Title cannot be only whitespace
    3. Title max length: 500 characters

    Args:
        title: The task title to validate

    Returns:
        Tuple of (is_valid, error_message):
        - is_valid: True if valid, False otherwise
        - error_message: None if valid, error description if invalid

    Examples:
        >>> validate_task_title("Buy groceries")
        (True, None)

        >>> validate_task_title("")
        (False, "Title is required and cannot be empty")

        >>> validate_task_title("   ")
        (False, "Title is required and cannot be empty")

        >>> validate_task_title("a" * 501)
        (False, "Title cannot exceed 500 characters")

        >>> validate_task_title(None)
        (False, "Title is required and cannot be empty")

    Extracted from:
        - backend/main.py:98-103 (create_todo)
        - backend/main.py:137-142 (update_todo)
    """
    # Rule 1: Required - cannot be None or empty string
    if title is None or title == "":
        return (False, "Title is required and cannot be empty")

    # Rule 2: Cannot be only whitespace
    if not title.strip():
        return (False, "Title is required and cannot be empty")

    # Rule 3: Max length 500 characters
    if len(title) > 500:
        return (False, "Title cannot exceed 500 characters")

    # All rules passed
    return (True, None)


def validate_task_category(category: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate task category according to business rules.

    Business Rules:
    1. Category is optional (can be None or empty string)
    2. If provided and not empty, max length: 100 characters

    Args:
        category: The task category to validate (optional)

    Returns:
        Tuple of (is_valid, error_message):
        - is_valid: True if valid, False otherwise
        - error_message: None if valid, error description if invalid

    Examples:
        >>> validate_task_category(None)
        (True, None)

        >>> validate_task_category("")
        (True, None)

        >>> validate_task_category("Work")
        (True, None)

        >>> validate_task_category("a" * 101)
        (False, "Category cannot exceed 100 characters")

    Extracted from:
        - backend/main.py:104-106 (create_todo)
        - backend/main.py:154-155 (update_todo)
    """
    # Rule 1: Category is optional - None and empty string are valid
    if category is None or category == "":
        return (True, None)

    # Rule 2: Max length 100 characters (if provided and not empty)
    if len(category) > 100:
        return (False, "Category cannot exceed 100 characters")

    # All rules passed
    return (True, None)
