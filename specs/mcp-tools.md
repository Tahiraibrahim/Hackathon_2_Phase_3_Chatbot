# MCP Tools Specification

## Overview
This document specifies the 6 MCP (Model Context Protocol) tools available in the Todo AI Chatbot application. These tools are implemented using the **Official FastMCP SDK** with `@mcp.tool()` decorators and enable the AI agent to perform comprehensive task management operations on behalf of users.

## Implementation Details
- **SDK**: FastMCP (Official Model Context Protocol SDK)
- **Location**: `backend/tools.py`
- **Decorator**: `@mcp.tool()` for each tool function
- **Authentication**: All tools require `user_id` parameter for user isolation
- **Database**: SQLModel with PostgreSQL backend

## Tool Definitions

### 1. add_task

**Purpose**: Create a new task for a user with full field support.

**Decorator**: `@mcp.tool()`

**Parameters**:
- `user_id` (string, required): The ID of the user creating the task
- `title` (string, required): Title of the task
- `description` (string, optional): Additional details about the task
- `priority` (string, optional): Priority level - "LOW", "MEDIUM", or "HIGH" (default: "MEDIUM")
- `category` (string, optional): Optional category for the task
- `due_date` (string, optional): Optional due date in ISO format (e.g., "2024-01-20T00:00:00")
- `is_recurring` (boolean, optional): Whether the task repeats (default: false)

**Returns**:
```json
{
  "task_id": 123,
  "status": "success",
  "message": "Task 'Buy groceries' created successfully with priority MEDIUM"
}
```

**Error Response**:
```json
{
  "task_id": null,
  "status": "error",
  "message": "Failed to create task: [error details]"
}
```

**Example Usage**:
- User: "Add a task to buy milk with high priority"
- Agent calls: `add_task(user_id="user123", title="Buy milk", priority="HIGH")`

---

### 2. list_tasks

**Purpose**: Retrieve tasks for a user, optionally filtered by completion status.

**Decorator**: `@mcp.tool()`

**Parameters**:
- `user_id` (string, required): The ID of the user
- `status` (string, optional): Filter by completion status
  - `"completed"`: Show only completed tasks
  - `"pending"`: Show only pending/incomplete tasks
  - `None` or omitted: Show all tasks

**Returns**:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "is_completed": false,
      "priority": "MEDIUM",
      "category": "Personal",
      "due_date": "2024-01-20T00:00:00",
      "is_recurring": false
    }
  ],
  "count": 1,
  "status": "success"
}
```

**Error Response**:
```json
{
  "tasks": [],
  "count": 0,
  "status": "error",
  "message": "Failed to retrieve tasks: [error details]"
}
```

**Example Usage**:
- User: "Show me my pending tasks"
- Agent calls: `list_tasks(user_id="user123", status="pending")`

---

### 3. complete_task

**Purpose**: Mark a specific task as completed.

**Decorator**: `@mcp.tool()`

**Parameters**:
- `user_id` (string, required): The ID of the user
- `task_id` (integer, required): The unique identifier of the task to complete

**Returns**:
```json
{
  "status": "success",
  "message": "Task 'Buy groceries' marked as completed"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Task with ID 123 not found or does not belong to user"
}
```

**Example Usage**:
- User: "Mark task 5 as done"
- Agent calls: `complete_task(user_id="user123", task_id=5)`

---

### 4. delete_task

**Purpose**: Permanently delete a task from the database.

**Decorator**: `@mcp.tool()`

**Parameters**:
- `user_id` (string, required): The ID of the user
- `task_id` (integer, required): The unique identifier of the task to delete

**Returns**:
```json
{
  "status": "success",
  "message": "Task 'Old reminder' deleted successfully"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Task with ID 123 not found or does not belong to user"
}
```

**Example Usage**:
- User: "Delete task number 3"
- Agent calls: `delete_task(user_id="user123", task_id=3)`

---

### 5. update_task

**Purpose**: Update the title and/or description of an existing task.

**Decorator**: `@mcp.tool()`

**Parameters**:
- `user_id` (string, required): The ID of the user
- `task_id` (integer, required): The unique identifier of the task to update
- `title` (string, optional): New title for the task
- `description` (string, optional): New description for the task

**Returns**:
```json
{
  "status": "success",
  "message": "Task updated successfully (title, description changed)"
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Task with ID 123 not found or does not belong to user"
}
```

**Example Usage**:
- User: "Change task 7's title to 'Complete project report'"
- Agent calls: `update_task(user_id="user123", task_id=7, title="Complete project report")`

---

### 6. search_tasks

**Purpose**: Search for tasks by keyword in title or description (case-insensitive).

**Decorator**: `@mcp.tool()`

**Parameters**:
- `user_id` (string, required): The ID of the user
- `keyword` (string, required): The search term to find in task titles or descriptions

**Returns**:
```json
{
  "tasks": [
    {
      "id": 2,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "is_completed": false,
      "priority": "MEDIUM",
      "category": "Personal",
      "due_date": null,
      "is_recurring": false
    }
  ],
  "count": 1,
  "keyword": "groceries",
  "status": "success"
}
```

**Error Response**:
```json
{
  "tasks": [],
  "count": 0,
  "keyword": "test",
  "status": "error",
  "message": "Failed to search tasks: [error details]"
}
```

**Example Usage**:
- User: "Find all tasks related to shopping"
- Agent calls: `search_tasks(user_id="user123", keyword="shopping")`

---

## Security & Authorization

All MCP tools implement security through:
1. **User Isolation**: Every tool requires `user_id` parameter and only accesses data belonging to that user
2. **Authentication**: Tools are called by the AI agent after user authentication via JWT tokens
3. **Input Validation**: All inputs are validated before database operations
4. **SQL Injection Protection**: SQLModel ORM provides parameterized queries
5. **Session Management**: Database sessions are properly managed with try-catch-finally blocks

## Error Handling

All tools follow a consistent error handling pattern:
- Return structured JSON with `status` field indicating "success" or "error"
- Include descriptive `message` field for debugging and user feedback
- Database operations are wrapped in try-catch blocks
- Failed transactions are properly rolled back
- Sessions are closed in finally blocks to prevent connection leaks

## Database Schema

Tasks are stored with the following structure:
```typescript
interface Task {
  id: number;                    // Auto-incremented primary key
  user_id: string;               // Foreign key to user (Better Auth)
  title: string;                 // Task title (required, max 500 chars)
  description: string | null;    // Optional details
  is_completed: boolean;         // Completion status (default: false)
  priority: "LOW" | "MEDIUM" | "HIGH";  // Priority enum (default: MEDIUM)
  category: string | null;       // Optional categorization (max 100 chars)
  due_date: Date | null;         // Optional deadline
  is_recurring: boolean;         // Recurring task flag (default: false)
}
```

## Integration with AI Agent

These tools are exposed to the OpenAI GPT-4 model via FastMCP and function calling:

1. **Tool Registration**: Tools are registered using `@mcp.tool()` decorators in `backend/tools.py`
2. **Schema Generation**: FastMCP automatically generates OpenAI-compatible function schemas from tool signatures
3. **Agent Flow**:
   - User sends natural language message to `/api/chat` endpoint
   - Agent analyzes intent using GPT-4-mini with access to tool definitions
   - Agent decides which tool(s) to call based on user intent
   - Backend executes tool via `execute_tool()` function in `main.py`
   - Tool result is returned to agent
   - Agent formulates natural language response to user
4. **Multi-Tool Orchestration**: Agent can chain multiple tool calls in a single conversation turn
5. **Context Awareness**: Conversation history is maintained for contextual understanding

## Implementation Notes

- **FastMCP Server**: Initialized as `mcp = FastMCP("todo-server")` in `tools.py`
- **Tool Registry**: Tools are stored in `mcp._tools` dictionary
- **Session Management**: Each tool creates its own database session using `get_session()` generator
- **Type Conversion**: String parameters (priority, due_date) are converted to appropriate types (Enum, datetime)
- **Legacy Wrappers**: `add_task_legacy()` and `delete_task_legacy()` functions exist for backward compatibility with direct API endpoints

## Version History

- **v2.0.0** (2024-01): Migrated to Official FastMCP SDK with `@mcp.tool()` decorators
- **v1.0.0** (2024-01): Initial specification with 6 core MCP tools
