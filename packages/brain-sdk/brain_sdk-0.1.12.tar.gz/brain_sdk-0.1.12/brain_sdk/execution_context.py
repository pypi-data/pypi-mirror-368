"""
Execution context management for automatic workflow tracking.
Provides thread-safe context management for reasoner execution tracking.
"""

import contextvars
import time
import uuid
from typing import Optional, Any
from dataclasses import dataclass


@dataclass
class ExecutionContext:
    """Represents the execution context for a reasoner call."""
    workflow_id: str
    execution_id: str
    agent_instance: Any  # Agent instance
    reasoner_name: str
    parent_execution_id: Optional[str] = None
    depth: int = 0
    started_at: Optional[float] = None
    parent_workflow_id: Optional[str] = None
    # DID-related fields
    session_id: Optional[str] = None
    caller_did: Optional[str] = None
    target_did: Optional[str] = None
    agent_node_did: Optional[str] = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = time.time()
    
    @classmethod
    def from_request(cls, request, agent_node_id: str) -> 'ExecutionContext':
        """Create ExecutionContext from FastAPI request headers."""
        headers = request.headers
        
        # 🔥 FIX: Case-insensitive header lookup (FastAPI converts headers to lowercase)
        workflow_id = headers.get("x-workflow-id") or headers.get("X-Workflow-ID") or generate_workflow_id()
        execution_id = headers.get("x-execution-id") or headers.get("X-Execution-ID") or generate_execution_id()
        parent_execution_id = headers.get("x-parent-execution-id") or headers.get("X-Parent-Execution-ID")
        parent_workflow_id = headers.get("x-parent-workflow-id") or headers.get("X-Parent-Workflow-ID")
        
        # Extract DID headers (case-insensitive)
        session_id = headers.get("x-session-id") or headers.get("X-Session-ID")
        caller_did = headers.get("x-caller-did") or headers.get("X-Caller-DID")
        target_did = headers.get("x-target-did") or headers.get("X-Target-DID")
        agent_node_did = headers.get("x-agent-node-did") or headers.get("X-Agent-Node-DID")
        
        # Get agent instance from registry
        from .agent_registry import get_current_agent_instance
        agent_instance = get_current_agent_instance()
        
        return cls(
            workflow_id=workflow_id,
            execution_id=execution_id,
            agent_instance=agent_instance,
            reasoner_name="unknown",  # Will be set by the reasoner
            parent_execution_id=parent_execution_id,
            parent_workflow_id=parent_workflow_id,
            depth=0,
            session_id=session_id,
            caller_did=caller_did,
            target_did=target_did,
            agent_node_did=agent_node_did
        )
    
    @classmethod
    def create_new(cls, agent_node_id: str, workflow_name: str) -> 'ExecutionContext':
        """Create a new root ExecutionContext."""
        from .agent_registry import get_current_agent_instance
        agent_instance = get_current_agent_instance()
        
        return cls(
            workflow_id=generate_workflow_id(),
            execution_id=generate_execution_id(),
            agent_instance=agent_instance,
            reasoner_name=workflow_name,
            depth=0
        )
    
    def create_child_context(self) -> 'ExecutionContext':
        """Create a child execution context for nested calls."""
        return ExecutionContext(
            workflow_id=self.workflow_id,  # Same workflow
            execution_id=generate_execution_id(),  # New execution
            agent_instance=self.agent_instance,
            reasoner_name="child_call",  # Will be updated by the actual reasoner
            parent_execution_id=self.execution_id,  # Parent's execution ID
            parent_workflow_id=self.workflow_id,  # Parent's workflow ID becomes parent_workflow_id
            depth=self.depth + 1
        )
    
    def to_headers(self) -> dict:
        """Convert context to HTTP headers for cross-agent calls."""
        headers = {
            "X-Workflow-ID": self.workflow_id,
            "X-Execution-ID": self.execution_id,
        }
        
        if self.parent_execution_id:
            headers["X-Parent-Execution-ID"] = self.parent_execution_id
        if self.parent_workflow_id:
            headers["X-Parent-Workflow-ID"] = self.parent_workflow_id
        
        # Add DID headers if available
        if self.session_id:
            headers["X-Session-ID"] = self.session_id
        if self.caller_did:
            headers["X-Caller-DID"] = self.caller_did
        if self.target_did:
            headers["X-Target-DID"] = self.target_did
        if self.agent_node_did:
            headers["X-Agent-Node-DID"] = self.agent_node_did
            
        return headers


class ExecutionContextManager:
    """Manages execution context using contextvars for async safety."""
    
    def __init__(self):
        self._context_var: contextvars.ContextVar[Optional[ExecutionContext]] = \
            contextvars.ContextVar('workflow_context', default=None)
    
    def get_current_context(self) -> Optional[ExecutionContext]:
        """Get the current execution context."""
        return self._context_var.get()
    
    def set_context(self, context: ExecutionContext) -> contextvars.Token:
        """Set the execution context and return a token for cleanup."""
        return self._context_var.set(context)
    
    def reset_context(self, token: contextvars.Token):
        """Reset the context using the provided token."""
        self._context_var.reset(token)


# Global context manager instance
_context_manager = ExecutionContextManager()


def get_current_context() -> Optional[ExecutionContext]:
    """Get the current execution context."""
    return _context_manager.get_current_context()


def set_execution_context(context: ExecutionContext) -> contextvars.Token:
    """Set the execution context."""
    return _context_manager.set_context(context)


def reset_execution_context(token: contextvars.Token):
    """Reset the execution context."""
    _context_manager.reset_context(token)


def generate_execution_id() -> str:
    """Generate a unique execution ID."""
    timestamp = int(time.time() * 1000)
    return f"exec_{timestamp}_{uuid.uuid4().hex[:8]}"


def generate_workflow_id() -> str:
    """Generate a unique workflow ID."""
    timestamp = int(time.time() * 1000)
    return f"wf_{timestamp}_{uuid.uuid4().hex[:8]}"
