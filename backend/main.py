"""
FastAPI Backend for Todo Application with AI Chatbot
Provides CRUD endpoints for tasks and an advanced AI chat endpoint with tool calling.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from pydantic import BaseModel
from openai import OpenAI

# --- FIX: Changed 'db' to 'database' and removed 'backend.' prefix ---
from database import create_db_and_tables, get_session
from models import Task, Priority, Conversation, Message, MessageRole
from auth import get_current_user, router as auth_router
from tools import (
    mcp,
    add_task_legacy,
    delete_task_legacy,
    add_task,
    list_tasks,
    update_task,
    delete_task,
    complete_task,
    search_tasks
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Todo AI Assistant API", version="1.0.0")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Include auth router
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# =============================================================================
# CHATBOT CONFIGURATION
# =============================================================================

# System prompt with persona, current datetime, and user_id injection
def get_system_prompt(user_id: str) -> str:
    """Generate system prompt with current datetime context and user_id."""
    current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    return f"""You are a helpful Todo AI assistant with access to tools to manage tasks.

Current Date & Time: {current_datetime}
Current User ID: {user_id}

⚠️ CRITICAL ANTI-HALLUCINATION RULES ⚠️
1. You are NOT allowed to pretend to create, update, or delete tasks.
2. You MUST call the actual tool functions (add_task, list_tasks, etc.) to perform any task operation.
3. If you do NOT call the tool, the task is NOT created/updated/deleted in the database.
4. NEVER say "Task added" or "Task created" unless you have actually called the add_task tool.
5. You MUST pass the user_id '{user_id}' to EVERY tool call. Do not ask the user for it.

⚠️ CRITICAL TOOL USAGE RULES ⚠️
- If the user request requires a tool, you MUST output a tool call.
- DO NOT write a text response confirming the action before calling the tool.
- DO NOT say "I'll add the task" or "Let me create that for you" - JUST CALL THE TOOL.
- Call the tool FIRST, then respond with the result after the tool executes.

EXECUTION RULES:
- When the user wants to add/create a task → IMMEDIATELY call add_task tool (NO text response first)
- When the user wants to list/show tasks → IMMEDIATELY call list_tasks tool (NO text response first)
- When the user wants to complete a task → IMMEDIATELY call complete_task tool (NO text response first)
- When the user wants to delete a task → IMMEDIATELY call delete_task tool (NO text response first)
- When the user wants to update a task → IMMEDIATELY call update_task tool (NO text response first)
- When the user wants to search tasks → IMMEDIATELY call search_tasks tool (NO text response first)
- Do NOT ask for confirmation unless the request is genuinely ambiguous
- Do NOT simulate or pretend to perform actions

Your Capabilities:
- Answer general questions and have friendly conversations
- Create, update, complete, delete, and search tasks using your tools
- List tasks with various filters (all, completed, pending)
- Understand natural language requests about tasks

Guidelines:
- For general questions or greetings, respond conversationally without forcing task management
- For task-related requests, execute the appropriate tool immediately
- When users say "today" or "tomorrow", use the current date/time context above
- After completing task actions, provide clear confirmation with relevant details

Tone: Friendly, helpful, and action-oriented."""

# Manually define tool schemas for OpenAI
def get_mcp_tools_for_openai():
    """
    Manually define tool schemas in OpenAI format.
    This ensures tools are always available regardless of FastMCP introspection issues.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for a user with full field support.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED: The ID of the user creating the task. This is automatically provided by the system."
                        },
                        "title": {
                            "type": "string",
                            "description": "Title of the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the task"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority level (LOW, MEDIUM, HIGH)",
                            "enum": ["LOW", "MEDIUM", "HIGH"]
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category for the task"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Optional due date in ISO format (YYYY-MM-DD)"
                        },
                        "is_recurring": {
                            "type": "boolean",
                            "description": "Whether the task repeats"
                        }
                    },
                    "required": ["user_id", "title", "priority", "category"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve tasks for a user, optionally filtered by completion status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED: The ID of the user. This is automatically provided by the system."
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional filter - 'completed', 'pending', or omit for all tasks",
                            "enum": ["completed", "pending"]
                        }
                    },
                    "required": ["user_id"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as completed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED: The ID of the user. This is automatically provided by the system."
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to complete"
                        }
                    },
                    "required": ["user_id", "task_id"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task permanently.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED: The ID of the user. This is automatically provided by the system."
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["user_id", "task_id"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's title, description, priority, category, and/or due_date.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED: The ID of the user. This is automatically provided by the system."
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional new title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional new description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["LOW", "MEDIUM", "HIGH"],
                            "description": "The new priority level"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["Work", "Personal", "Health", "Finance", "Study"],
                            "description": "The new category"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "The new due date in ISO format (YYYY-MM-DD)"
                        }
                    },
                    "required": ["user_id", "task_id"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_tasks",
                "description": "Search for tasks by keyword in title or description (case-insensitive).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "REQUIRED: The ID of the user. This is automatically provided by the system."
                        },
                        "keyword": {
                            "type": "string",
                            "description": "Search term to look for in title or description"
                        }
                    },
                    "required": ["user_id", "keyword"],
                    "additionalProperties": False
                }
            }
        }
    ]

    return tools

# Get tools from MCP instance
TOOLS = get_mcp_tools_for_openai()

# Verification: Print loaded tools
print(f"✅ FINAL CHECK: Loaded {len(TOOLS)} tools manually.")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_conversation_history(session: Session, conversation_id: int, limit: int = 10) -> List[Dict[str, str]]:
    try:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = session.exec(statement).all()
        messages = list(reversed(messages))
        
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return []

def save_message(session: Session, conversation_id: int, user_id: str, role: MessageRole, content: str) -> Message:
    try:
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving message: {str(e)}")
        raise

def execute_tool(tool_name: str, tool_args: Dict[str, Any], user_id: str, session: Session) -> Dict[str, Any]:
    """Execute tools by calling the imported functions directly."""
    try:
        logger.info(f"🔧 DEBUG: execute_tool called - Tool: {tool_name}, User ID: {user_id}, Args: {tool_args}")

        # Add user_id to tool arguments (all tools require user_id)
        tool_args_with_user = {"user_id": user_id, **tool_args}
        logger.info(f"🔧 DEBUG: Final tool arguments with user_id: {tool_args_with_user}")

        # Map tool names to imported functions
        tool_map = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "update_task": update_task,
            "search_tasks": search_tasks
        }

        if tool_name in tool_map:
            tool_func = tool_map[tool_name]
            result = tool_func(**tool_args_with_user)
            logger.info(f"✅ DEBUG: Tool {tool_name} executed successfully: {result}")
            return result
        else:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def run_agent_loop(session: Session, conversation_id: int, user_id: str, user_message: str) -> str:
    logger.info(f"🤖 DEBUG: run_agent_loop started - User ID: {user_id}, Conversation ID: {conversation_id}")
    try:
        history = get_conversation_history(session, conversation_id)
        messages = [{"role": "system", "content": get_system_prompt(user_id)}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # DEBUG: Log tools being passed to OpenAI
            logger.info(f"🔧 DEBUG: Passing {len(TOOLS)} tools to OpenAI: {[t['function']['name'] for t in TOOLS]}")

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                timeout=20.0  # 20 second timeout to prevent hanging
            )

            assistant_msg = response.choices[0].message

            if assistant_msg.tool_calls:
                logger.info(f"🔨 DEBUG: AI requested {len(assistant_msg.tool_calls)} tool call(s)")
                # Add the assistant's request to call a tool to history
                messages.append(assistant_msg)

                # Execute tools
                for tool_call in assistant_msg.tool_calls:
                    logger.info(f"🔨 DEBUG: Executing tool: {tool_call.function.name}")
                    args = json.loads(tool_call.function.arguments)
                    result = execute_tool(tool_call.function.name, args, user_id, session)
                    logger.info(f"🔨 DEBUG: Tool result: {result}")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                continue # Loop back to let OpenAI generate the text response
            
            return assistant_msg.content or "Done."
            
        return "I'm sorry, I got stuck in a loop."

    except Exception as e:
        logger.error(f"Agent Loop Error: {e}")
        return "I encountered an error while processing your request."

# =============================================================================
# API MODELS
# =============================================================================

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[Priority] = Priority.MEDIUM
    category: Optional[str] = None
    due_date: Optional[datetime] = None
    is_recurring: Optional[bool] = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[Priority] = None

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- CHAT ENDPOINT ---
@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f"💬 DEBUG: Chat endpoint called - User ID: {user_id}, Message: {request.message[:50]}...")

    # 1. Get/Create Conversation
    conversation_id = request.conversation_id
    if conversation_id:
        conv = session.get(Conversation, conversation_id)
        if not conv or conv.user_id != user_id:
            raise HTTPException(404, "Conversation not found")
    else:
        conv = Conversation(user_id=user_id)
        session.add(conv)
        session.commit()
        session.refresh(conv)
        conversation_id = conv.id

    # 2. Save User Message
    save_message(session, conversation_id, user_id, MessageRole.USER, request.message)

    # 3. Run Agent
    response_text = run_agent_loop(session, conversation_id, user_id, request.message)

    # 4. Save Assistant Response
    save_message(session, conversation_id, user_id, MessageRole.ASSISTANT, response_text)

    return ChatResponse(response=response_text, conversation_id=conversation_id)

# --- CRUD ENDPOINTS (Simplified to use direct DB/Tools to avoid Orchestrator errors) ---

@app.get("/api/todos", response_model=List[Task])
def list_todos(user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    logger.info(f"📋 DEBUG: Dashboard fetching tasks for User ID: {user_id}")
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    logger.info(f"📋 DEBUG: Found {len(tasks)} tasks for User ID: {user_id}")
    return tasks

@app.post("/api/todos", response_model=Task)
def create_todo(task_data: TaskCreate, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    # Using legacy wrapper to keep it consistent with session-based approach
    logger.info(f"📥 Creating task with data: {task_data.dict()}")
    result = add_task_legacy(
        session,
        user_id,
        task_data.title,
        task_data.description,
        task_data.priority,
        task_data.category,
        task_data.due_date,
        task_data.is_recurring
    )
    if result["status"] == "success":
        # Tools return a dict, but API needs the Task object
        task = session.get(Task, result["task_id"])
        logger.info(f"✅ Task created: ID={task.id}, Priority={task.priority}")
        return task
    raise HTTPException(400, result["message"])

@app.put("/api/todos/{task_id}", response_model=Task)
def update_todo(task_id: int, task_data: TaskUpdate, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(404, "Task not found")
    
    task_dict = task_data.dict(exclude_unset=True)
    for key, value in task_dict.items():
        setattr(task, key, value)
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/api/todos/{task_id}", status_code=204)
def delete_todo(task_id: int, user_id: str = Depends(get_current_user), session: Session = Depends(get_session)):
    result = delete_task_legacy(session, user_id, task_id)
    if result["status"] == "error":
        raise HTTPException(404, result["message"])
    return None