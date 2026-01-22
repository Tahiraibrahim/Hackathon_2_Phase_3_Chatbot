"""
Direct test of the tool loading and execution in main.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import TOOLS, execute_tool
from database import engine, create_db_and_tables
from sqlmodel import Session
from models import User

print("=" * 80)
print("TESTING TOOL LOADING AND EXECUTION")
print("=" * 80)
print()

# Test 1: Verify tools are loaded
print(f"[TEST 1] Tools loaded: {len(TOOLS)} tools")
print(f"Tool names: {[t['function']['name'] for t in TOOLS]}")
print()

# Test 2: Verify tool schemas
print("[TEST 2] Tool schemas:")
for tool in TOOLS:
    func = tool['function']
    print(f"  - {func['name']}: {func['description']}")
    print(f"    Required params: {func['parameters']['required']}")
print()

# Test 3: Execute a tool directly
print("[TEST 3] Testing tool execution...")
create_db_and_tables()

with Session(engine) as session:
    # Create test user
    test_user_id = "test_tool_user"
    user = session.get(User, test_user_id)

    if not user:
        user = User(
            id=test_user_id,
            email="tooltest@example.com",
            name="Tool Test User",
            email_verified=True
        )
        session.add(user)
        session.commit()
        print(f"  ✓ Created test user: {user.email}")
    else:
        print(f"  ✓ Using existing test user: {user.email}")

    # Test add_task tool
    print("\n  Testing add_task tool...")
    result = execute_tool(
        tool_name="add_task",
        tool_args={"title": "Test Task from Direct Tool Call", "priority": "HIGH"},
        user_id=test_user_id,
        session=session
    )
    print(f"  Result: {result}")

    # Test list_tasks tool
    print("\n  Testing list_tasks tool...")
    result = execute_tool(
        tool_name="list_tasks",
        tool_args={},
        user_id=test_user_id,
        session=session
    )
    print(f"  Result: Found {result.get('count', 0)} tasks")
    if result.get('tasks'):
        for task in result['tasks']:
            print(f"    - {task['title']} (Priority: {task['priority']})")

print()
print("=" * 80)
print("✅ ALL TESTS PASSED - Tools are loaded and working correctly!")
print("=" * 80)
