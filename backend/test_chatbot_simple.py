"""
Standalone Test Script for Chatbot Backend
Tests the AI chatbot logic without complex imports.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
from sqlmodel import Session, select
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from local modules
from db import engine, create_db_and_tables
from models import User, Conversation, Message, MessageRole, Task
import tools

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_system_prompt() -> str:
    """Generate system prompt with current datetime context."""
    current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    return f"""You are an advanced Todo Assistant with access to powerful task management tools.

Current Date & Time: {current_datetime}

Your Capabilities:
- Create, update, complete, delete, and search tasks
- List tasks with various filters (all, completed, pending)
- Understand natural language requests about tasks

Guidelines:
- Always confirm actions before executing them (e.g., "I'll create a task for you...")
- Be concise but friendly in your responses
- When users say "today" or "tomorrow", use the current date/time context above
- If a user request is ambiguous, ask for clarification
- After completing actions, provide clear confirmation with relevant details
- Use tools proactively to help users manage their tasks efficiently

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
                    "description": {"type": "string", "description": "Optional details about the task"}
                },
                "required": ["title"]
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
                }
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: dict, user_id: str, session: Session) -> dict:
    """Execute a tool function."""
    print(f"  → Executing tool: {tool_name} with args: {tool_args}")

    if tool_name == "add_task_tool":
        return tools.add_task(
            session=session,
            user_id=user_id,
            title=tool_args.get("title"),
            description=tool_args.get("description", "")
        )
    elif tool_name == "list_tasks_tool":
        return tools.list_tasks(
            session=session,
            user_id=user_id,
            status=tool_args.get("status")
        )
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}


def run_agent_loop_simple(session: Session, user_id: str, user_message: str) -> str:
    """
    Simplified agent loop for testing.
    """
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": user_message}
    ]

    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"  Iteration {iteration}...")

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.7
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            # Add assistant's message
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

            # Execute tool calls
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

        # Final response
        return assistant_message.content or "No response generated."

    return "Max iterations reached."


def test_brain():
    """Test the chatbot brain."""
    print("=" * 60)
    print("TESTING CHATBOT BACKEND")
    print("=" * 60)
    print()

    # Ensure tables exist
    create_db_and_tables()

    with Session(engine) as session:
        print("[1/4] Setting up test user...")

        # Get or create test user
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
            print(f"  ✓ Created test user: {user.email}")
        else:
            print(f"  ✓ Found test user: {user.email}")

        print()
        print("[2/4] User message:")
        user_message = "Please add a task called 'Buy Milk' and then list my pending tasks."
        print(f'  "{user_message}"')
        print()

        print("[3/4] Processing with AI agent...")
        try:
            ai_response = run_agent_loop_simple(
                session=session,
                user_id=test_user_id,
                user_message=user_message
            )

            print()
            print("[4/4] AI Response:")
            print("─" * 60)
            print(ai_response)
            print("─" * 60)
            print()
            print("✓ TEST COMPLETED SUCCESSFULLY!")
            print("=" * 60)

        except Exception as e:
            print()
            print(f"✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_brain()
