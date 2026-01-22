# Agent Behavior Specification

## Overview
This document describes how the Todo AI Assistant agent analyzes user requests and decides which MCP tools to invoke. The agent uses OpenAI's GPT-4-mini model with function calling capabilities to provide intelligent task management assistance.

## Implementation Architecture

### MCP SDK Integration
- **SDK**: Official FastMCP (Model Context Protocol SDK)
- **Tool Definition**: Tools are defined using `@mcp.tool()` decorators in `backend/tools.py`
- **Schema Generation**: FastMCP automatically generates OpenAI-compatible function schemas
- **Tool Execution**: Tools are executed via `execute_tool()` function in `backend/main.py`

### System Prompt
The agent operates with a system prompt that defines its:
- **Persona**: Advanced AI assistant with dual role (conversational AI + task management expert)
- **Context Awareness**: Current date/time for temporal references (dynamically generated)
- **Capabilities**: Full CRUD operations on tasks plus search functionality via 6 MCP tools
- **Guidelines**: Warm and welcoming for greetings, conversational for general questions, tool-focused for task operations

### Agent Loop
The agent operates in an iterative loop (max 5 iterations) implemented in `run_agent_loop()`:
1. **Receive** user message and conversation history from database
2. **Build Context** - Combine system prompt, history, and current message
3. **Analyze** intent using GPT-4-mini with tool definitions
4. **Decide** which tool(s) to call (if any) via OpenAI function calling
5. **Execute** tools via `execute_tool()` which calls FastMCP registered functions
6. **Append Results** - Add tool results to message history
7. **Loop** back to step 3 if tools were called (allows multi-tool orchestration)
8. **Formulate** natural language response when no more tools needed
9. **Return** response to user and save to database

### Tool Schema Extraction
The `get_mcp_tools_for_openai()` function in `main.py`:
- Accesses FastMCP's internal `_tools` registry
- Inspects function signatures using Python's `inspect` module
- Extracts parameter types and requirements
- Generates OpenAI-compatible function schemas
- Returns list of tool definitions for GPT-4-mini

## Decision-Making Logic

### Intent Recognition

The agent analyzes user messages to identify task management intents:

#### Create Intent
**Triggers**: "add", "create", "new task", "remember to", "I need to"

**Example Inputs**:
- "Add a task to buy milk"
- "Create a new todo for the meeting with high priority"
- "Remember to call John tomorrow"

**Agent Decision**: Call `add_task`
- Extracts title from user message
- Includes description if details are provided
- Extracts priority if mentioned (HIGH, MEDIUM, LOW)
- Extracts category and due_date if specified
- Confirms action with user

#### List/View Intent
**Triggers**: "show", "list", "what are", "view", "see my tasks"

**Example Inputs**:
- "Show me all my tasks"
- "What tasks do I have pending?"
- "List completed tasks"

**Agent Decision**: Call `list_tasks`
- Determines filter based on context:
  - "completed" → `status="completed"`
  - "pending"/"active"/"todo" → `status="pending"`
  - No modifier → `status=None` (all tasks)

#### Complete Intent
**Triggers**: "done", "complete", "finish", "mark as done"

**Example Inputs**:
- "Mark task 5 as done"
- "I completed the shopping task"
- "Finish task number 3"

**Agent Decision**: Call `complete_task`
- Extracts task_id from message
- If ID not provided, may call `list_tasks` first to help user identify task
- Confirms completion

#### Delete Intent
**Triggers**: "delete", "remove", "get rid of", "cancel"

**Example Inputs**:
- "Delete task 7"
- "Remove the shopping task"
- "Cancel my meeting reminder"

**Agent Decision**: Call `delete_task`
- Extracts task_id from message
- May search first if task referenced by name
- Confirms deletion

#### Update Intent
**Triggers**: "change", "update", "edit", "modify", "rename"

**Example Inputs**:
- "Change task 4's title to 'Buy groceries'"
- "Update the description of task 2"
- "Edit my workout task"

**Agent Decision**: Call `update_task`
- Identifies task_id
- Determines what field(s) to update (title, description)
- Provides new values
- Confirms update

#### Search Intent
**Triggers**: "find", "search", "look for", "tasks about", "containing"

**Example Inputs**:
- "Find all tasks about the project"
- "Search for grocery-related tasks"
- "Show me tasks containing 'meeting'"

**Agent Decision**: Call `search_tasks`
- Extracts search keyword(s)
- Returns matching tasks
- Summarizes results

### Multi-Tool Scenarios

The agent can chain multiple tool calls in a single conversation turn:

#### Example 1: List then Complete
**User**: "Show me my pending tasks and mark the first one as done"

**Agent Flow**:
1. Calls `list_tasks(user_id="user123", status="pending")`
2. Receives task list
3. Identifies first task ID
4. Calls `complete_task(user_id="user123", task_id=X)`
5. Confirms both actions

#### Example 2: Search then Update
**User**: "Find the meeting task and change its description to include the Zoom link"

**Agent Flow**:
1. Calls `search_tasks(user_id="user123", keyword="meeting")`
2. Receives matching tasks
3. Identifies most relevant task
4. Calls `update_task(user_id="user123", task_id=X, description="...")`
5. Confirms update

## Conversational Patterns

### Confirmation Before Action
The agent confirms destructive or significant actions:

**User**: "Delete all my completed tasks"

**Agent Response**: "I found 15 completed tasks. Are you sure you want to delete all of them? This action cannot be undone."

### Clarification Requests
When intent is ambiguous, the agent asks for clarification:

**User**: "Update task 5"

**Agent Response**: "I can update task 5 for you. What would you like to change - the title, description, or both?"

### Proactive Suggestions
The agent offers helpful suggestions:

**User**: "Show my tasks"

**Agent Response** (if many overdue tasks): "You have 12 pending tasks, including 5 that are overdue. Would you like me to show only the overdue ones first?"

## Natural Language Understanding

### Temporal References
The agent uses current date/time context to interpret:
- "today" → Current date
- "tomorrow" → Current date + 1 day
- "next week" → Current date + 7 days
- "by Friday" → Next occurrence of Friday

### Implicit References
The agent handles implicit task references:
- "the grocery task" → Searches for task with "grocery" in title
- "task 5" → Direct ID reference
- "my last task" → Most recently created task
- "the first pending one" → First task from pending list

### Contextual Awareness
The agent maintains conversation context:

**Turn 1**:
- User: "Show me my tasks"
- Agent: Lists 5 tasks

**Turn 2**:
- User: "Delete the second one"
- Agent: Remembers the list from Turn 1, deletes task ID from position 2

## Error Handling

### Tool Execution Failures
If a tool returns an error, the agent:
1. Interprets the error message
2. Explains the issue to the user in natural language
3. Suggests corrective actions

**Example**:
- Tool Error: "Task with ID 99 not found"
- Agent Response: "I couldn't find task #99. Would you like me to show you your current tasks so you can choose the right one?"

### Invalid Requests
For requests outside its capabilities, the agent:
1. Acknowledges the limitation
2. Suggests alternative approaches

**Example**:
- User: "Set a reminder to notify me in 2 hours"
- Agent: "I can create a task for you, but I don't have the ability to send timed notifications. Would you like me to create a task with a due date instead?"

## Response Style

### Tone
- Professional but friendly
- Concise and action-oriented
- Supportive and helpful

### Structure
1. **Acknowledgment**: Confirm understanding of request
2. **Action**: Describe what will be done
3. **Result**: Summarize outcome with relevant details
4. **Follow-up**: Offer next steps if appropriate

**Example**:
- User: "Add a task to prepare the presentation"
- Agent: "I'll create a task for you. ✓ Task 'Prepare the presentation' has been added to your list. Would you like to set a due date or priority?"

## Tool Selection Priority

When multiple tools could apply, the agent prioritizes by:
1. **Specificity**: More specific actions (complete, delete) over general ones (list, search)
2. **Efficiency**: Fewest tool calls needed to accomplish the goal
3. **User Experience**: Actions that provide immediate value

## Testing & Validation

The agent behavior is validated through:
- Unit tests for intent recognition
- Integration tests for tool execution
- End-to-end conversation tests
- User acceptance testing

## Version History

- **v2.0.0** (2024-01): Migrated to Official FastMCP SDK with `@mcp.tool()` decorators and enhanced dual-role persona
- **v1.0.0** (2024-01): Initial agent behavior specification with GPT-4-mini integration
