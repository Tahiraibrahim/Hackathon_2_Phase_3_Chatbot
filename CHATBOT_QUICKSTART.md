# AI Chatbot Quick Start Guide

## Setup

### 1. Install Dependencies
```bash
cd backend
pip install -e .
```

This will install all required packages including the newly added `openai`.

### 2. Set Environment Variables
Create a `.env` file in the `backend/` directory:

```bash
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-...your-key-here...

# Database URL
DATABASE_URL=postgresql://user:pass@host/dbname

# Other existing variables...
```

### 3. Start the Backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### Endpoint
```
POST /api/chat
```

### Authentication
Requires Bearer token in Authorization header:
```
Authorization: Bearer YOUR_AUTH_TOKEN
```

### Request Format
```json
{
  "message": "Your message here",
  "conversation_id": 123  // Optional: omit to start new conversation
}
```

### Response Format
```json
{
  "response": "AI's response here",
  "conversation_id": 123
}
```

## Example Requests

### Start New Conversation (Create Task)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

### Continue Conversation (List Tasks)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Show me all my tasks",
    "conversation_id": 1
  }'
```

## Natural Language Examples

The AI understands natural language! Try these:

**Creating Tasks:**
- "Add buy milk to my tasks"
- "Remind me to call dentist tomorrow"
- "Create a task for finishing the project report"

**Listing Tasks:**
- "What do I need to do?"
- "Show my pending tasks"
- "List all completed tasks"

**Completing Tasks:**
- "Mark task 5 as done"
- "I finished task 3"
- "Complete the grocery shopping task"

**Searching Tasks:**
- "Find tasks about meeting"
- "Search for dentist in my tasks"
- "Show tasks with project in the name"

**Updating Tasks:**
- "Update task 5 title to 'Buy organic milk'"
- "Change the description of task 3"

**Deleting Tasks:**
- "Delete task 7"
- "Remove the dentist task"

## Testing

### Manual Testing
Use the provided test script:

```bash
# Set your auth token
export TEST_AUTH_TOKEN="your-bearer-token"
export OPENAI_API_KEY="sk-your-key"

# Run tests
python3 test_chatbot.py
```

### Interactive Testing
Use the Swagger UI:
```
http://localhost:8000/docs
```

Navigate to the "Chat" section and try the `/api/chat` endpoint interactively.

## How It Works

1. **User sends message** → Backend receives request
2. **Fetch conversation history** → Last 10 messages loaded
3. **AI processes with context** → OpenAI analyzes message + history
4. **AI decides on tools** → May call add_task, list_tasks, etc.
5. **Tools execute** → Backend runs the operations
6. **AI gets results** → Tool outputs sent back to AI
7. **AI responds** → Friendly message with results
8. **Save to database** → Both user message and AI response saved
9. **Return response** → User gets AI's answer

## Troubleshooting

### "AI processing error"
- Check if `OPENAI_API_KEY` is set correctly
- Verify your OpenAI API key is valid and has credits
- Check backend logs for detailed error messages

### "Conversation not found"
- The conversation_id might be invalid
- Try omitting conversation_id to start a new conversation
- Verify the conversation belongs to the authenticated user

### "Message cannot be empty"
- Ensure your message field is not empty or whitespace-only

### Tool Execution Fails
- Check database connection
- Verify task_id exists when completing/updating/deleting
- Check backend logs for detailed error messages

## Features

✅ **Multi-Turn Conversations** - Maintains context across messages
✅ **6 Advanced Tools** - Add, list, complete, delete, update, search tasks
✅ **Natural Language** - Understands conversational requests
✅ **Parallel Tool Calls** - Can execute multiple tools at once
✅ **Conversation History** - Remembers last 10 messages
✅ **Date/Time Awareness** - AI knows the current date and time
✅ **Error Handling** - Graceful error messages
✅ **Logging** - Comprehensive logs for debugging

## Architecture Highlights

- **Model:** GPT-4o-mini (fast, cost-effective, great function calling)
- **Max Iterations:** 10 (prevents infinite loops)
- **History Limit:** 10 messages (balances context vs. token usage)
- **Temperature:** 0.7 (balanced creativity and consistency)

## Frontend Integration

For frontend developers, here's what you need:

```typescript
// Example fetch request
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify({
    message: userInput,
    conversation_id: currentConversationId // or null for new conversation
  })
});

const data = await response.json();
console.log(data.response); // AI's response
console.log(data.conversation_id); // Save this for next message
```

## Cost Considerations

**GPT-4o-mini Pricing (as of 2024):**
- Input: ~$0.15 per 1M tokens
- Output: ~$0.60 per 1M tokens

**Typical conversation:**
- System prompt: ~150 tokens
- User message: ~20-50 tokens
- Tool definitions: ~500 tokens
- AI response: ~50-100 tokens
- **Total per turn:** ~700-800 tokens
- **Cost per turn:** ~$0.0005-0.001 (less than 1 cent)

**Tips to reduce costs:**
- Use shorter system prompts
- Reduce history limit if needed
- Consider caching for repeated queries
- Monitor usage with OpenAI dashboard

## Security

✅ **Authentication Required** - Bearer token validation
✅ **User Isolation** - Users can only access their own tasks/conversations
✅ **Input Validation** - Empty messages rejected
✅ **SQL Injection Protection** - SQLModel/SQLAlchemy handles escaping
✅ **Rate Limiting** - Consider adding for production
✅ **API Key Security** - Never expose OPENAI_API_KEY to frontend

## Next Steps

1. **Install dependencies:** `pip install -e .` in backend directory
2. **Set environment variables:** Create `.env` with OPENAI_API_KEY
3. **Start backend:** `uvicorn main:app --reload`
4. **Test with curl or test script:** Verify it works
5. **Integrate with frontend:** Use the `/api/chat` endpoint
6. **Deploy:** Consider rate limiting and monitoring for production

## Support

For issues or questions:
1. Check the logs: Backend outputs detailed logs
2. Review the comprehensive docs: `CHATBOT_BRAIN_IMPLEMENTATION.md`
3. Test with the script: `python3 test_chatbot.py`
4. Check OpenAI dashboard: Verify API usage and credits

---

**Status:** ✅ Ready for Production
**Last Updated:** 2026-01-15
