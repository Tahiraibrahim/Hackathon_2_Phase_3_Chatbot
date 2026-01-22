#!/usr/bin/env python3
"""
Quick test script for the AI Chatbot Brain
Tests the chat endpoint with sample requests.
"""

import os
import sys
import httpx
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_TOKEN = os.getenv("TEST_AUTH_TOKEN", "")  # Set this to your test user's token

def test_chat(message: str, conversation_id: Optional[int] = None):
    """
    Send a message to the chat endpoint and print the response.

    Args:
        message: The message to send
        conversation_id: Optional conversation ID to continue existing conversation
    """
    url = f"{BASE_URL}/api/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }

    payload = {"message": message}
    if conversation_id:
        payload["conversation_id"] = conversation_id

    print(f"\n{'='*60}")
    print(f"📤 USER: {message}")
    print(f"{'='*60}")

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()

        data = response.json()
        ai_response = data.get("response", "")
        conversation_id = data.get("conversation_id", "")

        print(f"🤖 AI: {ai_response}")
        print(f"💬 Conversation ID: {conversation_id}")

        return conversation_id

    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def main():
    """Run a series of test conversations."""

    print("=" * 60)
    print("AI CHATBOT BRAIN - TEST SCRIPT")
    print("=" * 60)

    # Check if auth token is set
    if not AUTH_TOKEN:
        print("\n⚠️  WARNING: TEST_AUTH_TOKEN environment variable not set!")
        print("   Set it with: export TEST_AUTH_TOKEN='your-bearer-token'")
        print("   You can get a token by signing in through the auth endpoint.")
        sys.exit(1)

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: OPENAI_API_KEY environment variable not set!")
        print("   The backend needs this to work.")
        sys.exit(1)

    print(f"\n✅ Testing endpoint: {BASE_URL}/api/chat")
    print(f"✅ Auth token: {AUTH_TOKEN[:20]}...")

    # Test 1: Create a new conversation and add a task
    print("\n" + "="*60)
    print("TEST 1: Create a task")
    print("="*60)
    conv_id = test_chat("Add a task to buy groceries")

    if not conv_id:
        print("\n❌ Test 1 failed. Check if the backend is running.")
        return

    # Test 2: List tasks
    print("\n" + "="*60)
    print("TEST 2: List tasks")
    print("="*60)
    conv_id = test_chat("Show me all my tasks", conversation_id=conv_id)

    # Test 3: Add another task
    print("\n" + "="*60)
    print("TEST 3: Add multiple tasks")
    print("="*60)
    conv_id = test_chat("Add two tasks: call dentist and finish report", conversation_id=conv_id)

    # Test 4: Search tasks
    print("\n" + "="*60)
    print("TEST 4: Search tasks")
    print("="*60)
    conv_id = test_chat("Find tasks about grocery", conversation_id=conv_id)

    # Test 5: Complete a task (note: this requires knowing a task ID)
    print("\n" + "="*60)
    print("TEST 5: Complete a task")
    print("="*60)
    conv_id = test_chat("List my pending tasks and mark the first one as complete", conversation_id=conv_id)

    # Test 6: Natural language query
    print("\n" + "="*60)
    print("TEST 6: Natural language query")
    print("="*60)
    conv_id = test_chat("What do I need to do today?", conversation_id=conv_id)

    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print(f"Final Conversation ID: {conv_id}")
    print("\nCheck the logs above to verify the AI responses are appropriate.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.")
        sys.exit(0)
