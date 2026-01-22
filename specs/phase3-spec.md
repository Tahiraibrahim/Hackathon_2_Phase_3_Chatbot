# Phase III: Todo AI Chatbot Specification

## Objective
Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture.

## Technology Stack
- **Frontend:** OpenAI ChatKit
- **Backend:** Python FastAPI
- **AI Framework:** OpenAI Agents SDK
- **MCP Server:** Official MCP SDK
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** Better Auth (via Bearer Tokens)

## Database Models

1. **Task** (Existing)
   - Fields: user_id, id, title, description, completed, created_at, updated_at
2. **Conversation** (New)
   - Fields: user_id, id, created_at, updated_at
   - Description: Stores Chat session metadata.
3. **Message** (New)
   - Fields: user_id, id, conversation_id, role (user/assistant), content, created_at
   - Description: Stores Chat history.

## Architecture & Flow (Stateless)
1. **Receive Message:** POST /api/chat (Input: conversation_id, message).
2. **Fetch History:** Retrieve past messages from Database.
3. **Run Agent:** OpenAI Agents SDK processes the message.
4. **Tool Use:** Agent calls MCP Tools (add_task, list_tasks, etc.) if needed.
5. **Persist:** Store User message and Assistant response in Database.
6. **Response:** Return response to client.

## MCP Tools Specification (The "Brain" Actions)
The MCP server must expose these tools:
1. **add_task** (user_id, title, description) -> Returns task_id, status
2. **list_tasks** (user_id, status) -> Returns List[Task]
3. **complete_task** (user_id, task_id) -> Returns status
4. **delete_task** (user_id, task_id) -> Returns status
5. **update_task** (user_id, task_id, title, description) -> Returns status

## Agent Behavior
- **Tone:** Friendly and helpful.
- **Logic:**
  - "Add grocery" -> call `add_task`
  - "What to do?" -> call `list_tasks`
  - "Done with task 3" -> call `complete_task`

## Deliverables
- Working chatbot endpoint with MCP Tools.
- Database migration scripts for Conversation/Message tables.
