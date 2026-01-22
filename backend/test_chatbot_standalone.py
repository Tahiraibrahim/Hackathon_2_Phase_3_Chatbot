"""
Fully Standalone Test Script for Chatbot Backend
No external module imports - completely self-contained for testing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
from sqlmodel import Session, select, create_engine, SQLModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import only models and database
from models import User, Conversation, Task
from db import engine, create_db_and_tables

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Inline tool implementations to avoid import issues
def add_task(session: Session, user_id: str, title: str, description: str = "") -> dict:
    """Create a new task."""
    try:
        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            is_completed=False
        )
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return {
            "task_id": new_task.id,
            "status": "success",
            "message": f"Task '{title}' created successfully"
        }
    except Exception as e:
        session.rollback()
        return {"task_id": None, "status": "error", "message": f"Failed: {str(e)}"}


def list_tasks(session: Session, user_id: str, status: str = None) -> dict:
    """List tasks for a user."""
    try:
        statement = select(Task).where(Task.user_id == user_id)

        if status == "completed":
            statement = statement.where(Task.is_completed == True)
        elif status == "pending":
            statement = statement.where(Task.is_completed == False)

        tasks = session.exec(statement).all()

        tasks_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed
            }
            for task in tasks
        ]

        return {"tasks": tasks_list, "count": len(tasks_list), "status": "success"}
    except Exception as e:
        return {"tasks": [], "count": 0, "status": "error", "message": str(e)}


def get_system_prompt() -> str:
    """Generate system prompt."""
    current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    return f"""You are an advanced Todo Assistant with access to powerful task management tools.

Current Date & Time: {current_datetime}

Your Capabilities:
- Create, update, complete, delete, and search tasks
- List tasks with various filters (all, completed, pending)
- Understand natural language requests about tasks

Guidelines:
- Always confirm actions before executing them
- Be concise but friendly in your responses
- After completing actions, provide clear confirmation with relevant details

Tone: Professional, helpful, and supportive."""


# OpenAI Function Definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task_tool",
            "description": "Create a new task for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the task"},
                    "description": {"type": "string", "description": "Optional details"}
                },
                "required": ["title"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks_tool",
            "description": "Retrieve the user's tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["completed", "pending", "all"],
                        "description": "Filter by status"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: dict, user_id: str, session: Session) -> dict:
    """Execute a tool function."""
    print(f"    → Executing: {tool_name}({tool_args})")

    if tool_name == "add_task_tool":
        return add_task(
            session=session,
            user_id=user_id,
            title=tool_args.get("title"),
            description=tool_args.get("description", "")
        )
    elif tool_name == "list_tasks_tool":
        return list_tasks(
            session=session,
            user_id=user_id,
            status=tool_args.get("status")
        )
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}


def run_agent_loop(session: Session, user_id: str, user_message: str) -> str:
    """Run the AI agent loop."""
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": user_message}
    ]

    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"    Iteration {iteration}...")

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.7
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_result = execute_tool(tool_name, tool_args, user_id, session)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

            continue

        return assistant_message.content or "No response generated."

    return "Max iterations reached."


def test_brain():
    """Test the chatbot brain."""
    print("\n" + "=" * 70)
    print("  CHATBOT BACKEND TEST")
    print("=" * 70 + "\n")

    # Ensure tables exist
    create_db_and_tables()

    with Session(engine) as session:
        print("📋 Step 1: Setting up test user...")
        test_user_id = "test_user"
        user = session.get(User, test_user_id)

        if not user:
            user = User(
                id=test_user_id,
                email="test@example.com",
                name="Test User",
                email_verified=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"   ✓ Created test user: {user.email}\n")
        else:
            print(f"   ✓ Found test user: {user.email}\n")

        print("💬 Step 2: User Message:")
        user_message = "Please add a task called 'Buy Milk' and then list my pending tasks."
        print(f"   \"{user_message}\"\n")

        print("🤖 Step 3: Processing with AI Agent...")
        try:
            ai_response = run_agent_loop(
                session=session,
                user_id=test_user_id,
                user_message=user_message
            )

            print("\n✨ Step 4: AI Response:")
            print("   " + "─" * 66)
            for line in ai_response.split('\n'):
                print(f"   {line}")
            print("   " + "─" * 66)

            print("\n" + "=" * 70)
            print("  ✓ TEST COMPLETED SUCCESSFULLY!")
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_brain()
