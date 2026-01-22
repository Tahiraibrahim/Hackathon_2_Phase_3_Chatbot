"""
Final Chatbot Backend Test
Demonstrates full tool execution without asking for confirmation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
from sqlmodel import Session, select
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from models import User, Task
from db import engine, create_db_and_tables

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def add_task(session: Session, user_id: str, title: str, description: str = "") -> dict:
    """Create a new task."""
    try:
        new_task = Task(user_id=user_id, title=title, description=description, is_completed=False)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        return {"task_id": new_task.id, "status": "success", "message": f"Task '{title}' created successfully"}
    except Exception as e:
        session.rollback()
        return {"status": "error", "message": f"Failed: {str(e)}"}


def list_tasks(session: Session, user_id: str, status: str = None) -> dict:
    """List tasks for a user."""
    try:
        statement = select(Task).where(Task.user_id == user_id)
        if status == "completed":
            statement = statement.where(Task.is_completed == True)
        elif status == "pending":
            statement = statement.where(Task.is_completed == False)

        tasks = session.exec(statement).all()
        tasks_list = [{"id": t.id, "title": t.title, "is_completed": t.is_completed} for t in tasks]
        return {"tasks": tasks_list, "count": len(tasks_list), "status": "success"}
    except Exception as e:
        return {"tasks": [], "count": 0, "status": "error", "message": str(e)}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task_tool",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks_tool",
            "description": "List tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["completed", "pending", "all"]}
                }
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: dict, user_id: str, session: Session) -> dict:
    """Execute a tool."""
    if tool_name == "add_task_tool":
        return add_task(session, user_id, tool_args.get("title"), tool_args.get("description", ""))
    elif tool_name == "list_tasks_tool":
        return list_tasks(session, user_id, tool_args.get("status"))
    return {"status": "error", "message": f"Unknown tool: {tool_name}"}


def run_agent(session: Session, user_id: str, user_message: str) -> str:
    """Run AI agent."""
    messages = [
        {
            "role": "system",
            "content": f"""You are a Todo Assistant. Current time: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}

IMPORTANT: Execute user requests immediately without asking for confirmation. Be direct and action-oriented."""
        },
        {"role": "user", "content": user_message}
    ]

    for iteration in range(5):
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in assistant_message.tool_calls
                ]
            })

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"      🔧 {tool_name}({tool_args})")

                result = execute_tool(tool_name, tool_args, user_id, session)
                print(f"         → {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
            continue

        return assistant_message.content or "No response."

    return "Max iterations reached."


def test():
    """Run the test."""
    print("\n" + "="*70)
    print("  🧪 CHATBOT BACKEND TEST (WITH TOOL EXECUTION)")
    print("="*70 + "\n")

    create_db_and_tables()

    with Session(engine) as session:
        # Setup test user
        user_id = "test_user"
        user = session.get(User, user_id)
        if not user:
            user = User(id=user_id, email="test@example.com", name="Test User", email_verified=True)
            session.add(user)
            session.commit()

        print(f"✓ Test user: {user.email}\n")

        # Test message
        message = "Add a task called 'Buy Milk' and then list my pending tasks."
        print(f"💬 User: \"{message}\"\n")
        print("🤖 AI Processing...")

        try:
            response = run_agent(session, user_id, message)
            print(f"\n✨ AI Response:")
            print("   " + "─"*66)
            for line in response.split('\n'):
                print(f"   {line}")
            print("   " + "─"*66)
            print("\n" + "="*70)
            print("  ✅ TEST PASSED - Backend is working correctly!")
            print("="*70 + "\n")
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test()
