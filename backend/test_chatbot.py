"""
Test Script for Chatbot Backend
Tests the AI chatbot logic without requiring the frontend.
"""

import sys
import os

# Add both backend directory and parent directory to Python path to fix imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)
sys.path.insert(0, parent_dir)

from sqlmodel import Session
from db import engine
from models import User, Conversation
from main import run_agent_loop


def test_brain():
    """
    Test the chatbot brain by simulating a user interaction.

    Steps:
    1. Create a database session
    2. Get or create a test user
    3. Get or create a test conversation
    4. Simulate a user message
    5. Call run_agent_loop to process the message
    6. Print the AI's response
    """
    print("=== Testing Chatbot Backend ===\n")

    # Step 1: Create database session
    with Session(engine) as session:
        print("✓ Database session created")

        # Step 2: Get or create test user
        test_user_id = "test_user"
        test_user_email = "test@example.com"

        user = session.get(User, test_user_id)

        if not user:
            print(f"Creating test user: {test_user_id}")
            user = User(
                id=test_user_id,
                email=test_user_email,
                name="Test User",
                email_verified=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"✓ Test user created: {user.email}")
        else:
            print(f"✓ Test user found: {user.email}")

        # Step 3: Get or create test conversation
        conversation_id = 1
        conversation = session.get(Conversation, conversation_id)

        if not conversation:
            print(f"Creating test conversation: {conversation_id}")
            conversation = Conversation(
                id=conversation_id,
                user_id=test_user_id
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            print(f"✓ Test conversation created: {conversation.id}")
        else:
            print(f"✓ Test conversation found: {conversation.id}")

        # Step 4: Simulate user message
        user_message = "Please add a task called 'Buy Milk' and then list my pending tasks."
        print(f"\n--- User Message ---")
        print(f"{user_message}")

        # Step 5: Call the agent loop
        print(f"\n--- Processing with AI Agent ---")
        try:
            ai_response = run_agent_loop(
                session=session,
                conversation_id=conversation_id,
                user_id=test_user_id,
                user_message=user_message
            )

            # Step 6: Print AI's response
            print(f"\n--- AI Response ---")
            print(ai_response)
            print(f"\n✓ Test completed successfully!")

        except Exception as e:
            print(f"\n✗ Error during agent loop: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    test_brain()
