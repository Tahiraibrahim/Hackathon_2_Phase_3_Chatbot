from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class User(SQLModel, table=True):
    __tablename__ = "user"  # Match Better Auth table name

    id: str = Field(primary_key=True)  # Better Auth uses text ID
    email: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None)
    email_verified: bool = Field(default=False, sa_column_kwargs={"name": "emailVerified"})
    image: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"name": "createdAt"})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"name": "updatedAt"})

    tasks: List["Task"] = Relationship(back_populates="owner")
    accounts: List["Account"] = Relationship(back_populates="user")
    sessions: List["Session"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="owner")
    messages: List["Message"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    description: Optional[str] = None
    is_completed: bool = Field(default=False, alias="is_completed")
    priority: Priority = Field(default=Priority.MEDIUM)
    category: Optional[str] = Field(default=None, max_length=100)
    due_date: Optional[datetime] = Field(default=None, alias="due_date")
    is_recurring: bool = Field(default=False, alias="is_recurring")
    user_id: str = Field(foreign_key="user.id", index=True, alias="user_id")

    owner: User = Relationship(back_populates="tasks")

class Account(SQLModel, table=True):
    """
    Better Auth Account model
    Stores OAuth and other linked accounts for a user
    """
    __tablename__ = "account"  # Match Better Auth table name

    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, sa_column_kwargs={"name": "userId"})
    account_id: str = Field(sa_column_kwargs={"name": "accountId"})
    provider_id: str = Field(sa_column_kwargs={"name": "providerId"})
    access_token: Optional[str] = Field(default=None, sa_column_kwargs={"name": "accessToken"})
    refresh_token: Optional[str] = Field(default=None, sa_column_kwargs={"name": "refreshToken"})
    id_token: Optional[str] = Field(default=None, sa_column_kwargs={"name": "idToken"})
    access_token_expires_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"name": "accessTokenExpiresAt"})
    refresh_token_expires_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"name": "refreshTokenExpiresAt"})
    scope: Optional[str] = None
    password: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"name": "createdAt"})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"name": "updatedAt"})

    user: User = Relationship(back_populates="accounts")

class Session(SQLModel, table=True):
    """
    Better Auth Session model
    Stores user sessions for tracking active logins
    """
    __tablename__ = "session"  # Match Better Auth table name

    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, sa_column_kwargs={"name": "userId"})
    token: str = Field(unique=True, index=True)
    expires_at: datetime = Field(index=True, sa_column_kwargs={"name": "expiresAt"})
    ip_address: Optional[str] = Field(default=None, sa_column_kwargs={"name": "ipAddress"})
    user_agent: Optional[str] = Field(default=None, sa_column_kwargs={"name": "userAgent"})
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"name": "createdAt"})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"name": "updatedAt"})

    user: User = Relationship(back_populates="sessions")

class Verification(SQLModel, table=True):
    """
    Better Auth Verification model
    Stores email verification tokens and one-time tokens
    """
    __tablename__ = "verification"  # Match Better Auth table name

    id: str = Field(primary_key=True)
    identifier: str = Field(index=True)  # email address or phone number
    value: str = Field()  # verification code/token
    expires_at: datetime = Field(index=True, sa_column_kwargs={"name": "expiresAt"})
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"name": "createdAt"})
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"name": "updatedAt"})

class Conversation(SQLModel, table=True):
    """
    Conversation model for AI Chatbot
    Stores chat session metadata
    """
    __tablename__ = "conversation"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True, alias="user_id")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="created_at")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updated_at")

    owner: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    """
    Message model for AI Chatbot
    Stores chat history with role and content
    """
    __tablename__ = "message"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True, alias="conversation_id")
    user_id: str = Field(foreign_key="user.id", index=True, alias="user_id")
    role: MessageRole = Field()
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="created_at")

    conversation: Conversation = Relationship(back_populates="messages")
    user: User = Relationship(back_populates="messages")