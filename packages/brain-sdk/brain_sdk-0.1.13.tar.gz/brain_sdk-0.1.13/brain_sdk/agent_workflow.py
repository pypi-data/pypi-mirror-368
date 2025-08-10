import asyncio
import inspect
import json
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Optional

from brain_sdk.agent_utils import AgentUtils
from brain_sdk.execution_context import ExecutionContext
from brain_sdk.logger import log_track, log_fire, log_debug, log_warn, log_error

# Import aiohttp for fire-and-forget HTTP calls
try:
    import aiohttp
except ImportError:
    aiohttp = None


class AgentWorkflow:
    """
    Handles workflow tracking functionality for Agent instances.

    This class manages execution tracking, notifications, and workflow management
    for agent reasoner calls and cross-agent communications.
    """

    def __init__(self, agent_instance):
        """
        Initialize the workflow handler with a reference to the agent instance.

        Args:
            agent_instance: The Agent instance this workflow handler belongs to
        """
        self.agent = agent_instance

    def generate_execution_id(self) -> str:
        """Generate a unique execution ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"exec_{timestamp}_{unique_id}"

    def replace_function_references(
        self, original_func: Callable, tracked_func: Callable, func_name: str
    ) -> None:
        """
        Comprehensively replace all references to original function with tracked version.

        This ensures that direct calls like `await analyze_sentiment()` use the tracked
        version instead of bypassing workflow tracking.
        """
        try:
            # 1. Replace in agent instance
            setattr(self.agent, func_name, tracked_func)

            # 2. Replace in caller's module globals
            try:
                frame = sys._getframe(2)  # Get caller's frame (skip decorator frame)
                if func_name in frame.f_globals:
                    frame.f_globals[func_name] = tracked_func
                    if self.agent.dev_mode:
                        print(f"🔍 SETUP: Replaced {func_name} in caller's globals")
            except Exception as e:
                if self.agent.dev_mode:
                    print(f"🔍 SETUP: Could not replace in caller's globals: {e}")

            # 3. Replace in original function's module
            try:
                if hasattr(original_func, "__module__"):
                    module = sys.modules.get(original_func.__module__)
                    if module and hasattr(module, func_name):
                        setattr(module, func_name, tracked_func)
                        if self.agent.dev_mode:
                            print(
                                f"🔍 SETUP: Replaced {func_name} in module {original_func.__module__}"
                            )
            except Exception as e:
                if self.agent.dev_mode:
                    print(f"🔍 SETUP: Could not replace in module: {e}")

            # 4. Store reference to original function for debugging
            try:
                setattr(tracked_func, "__wrapped__", original_func)
            except (AttributeError, TypeError):
                # Some function types don't allow setting __wrapped__
                pass

            if self.agent.dev_mode:
                print(f"🔍 SETUP: Function replacement complete for {func_name}")

        except Exception as e:
            if self.agent.dev_mode:
                print(f"⚠️ Function replacement failed for {func_name}: {e}")

    async def execute_with_tracking(
        self, original_func: Callable, args: tuple, kwargs: dict
    ) -> Any:
        """
        Unified execution pipeline for both direct calls and app.call().

        This method provides consistent workflow tracking for all reasoner calls,
        whether they are direct function calls or cross-agent calls via app.call().
        """
        log_track(f"{original_func.__name__} called with args={args}, kwargs={kwargs}")

        # Check if we're in a tracked execution context (prefer enhanced decorator context)
        from brain_sdk.execution_context import get_current_context
        current_context = get_current_context() or self.agent._current_execution_context

        if current_context:
            log_track(f"Found execution context for {original_func.__name__}, creating child context")

            # Create child context for tracking
            child_context = current_context.create_child_context()
            # 🔥 FIX: Update the child context's reasoner name with the actual function name
            child_context.reasoner_name = original_func.__name__
            child_execution_id = child_context.execution_id  # Use the execution_id from the child context

            if self.agent.dev_mode:
                print(f"🔍 TRACK: Created child context for {original_func.__name__}")
                print(f"  Parent Execution ID: {current_context.execution_id}")
                print(f"  Child Execution ID: {child_execution_id}")
                print(f"  Workflow ID: {child_context.workflow_id}")
                print(f"  Parent Workflow ID: {child_context.parent_workflow_id}")
                print(f"  Reasoner Name: {child_context.reasoner_name}")

            # Inject execution context if function accepts it
            sig = inspect.signature(original_func)
            if "execution_context" in sig.parameters:
                kwargs["execution_context"] = child_context
                if self.agent.dev_mode:
                    print(
                        f"🔍 TRACK: Injected execution context into {original_func.__name__}"
                    )

            # Set child context as current during execution
            previous_context = self.agent._current_execution_context
            self.agent._current_execution_context = child_context

            if self.agent.dev_mode:
                print(
                    f"🔍 TRACK: Sending start notification for {original_func.__name__}"
                )

            # 🔧 FIX: Capture original input data before function execution
            # Combine args and kwargs to get complete input data
            original_input_data = {}
            
            # Add positional arguments with parameter names if available
            try:
                sig = inspect.signature(original_func)
                param_names = [name for name, param in sig.parameters.items() 
                             if name not in ["self", "execution_context"]]
                
                # Map positional args to parameter names
                for i, arg in enumerate(args):
                    if i < len(param_names):
                        original_input_data[param_names[i]] = arg
                
                # Add keyword arguments (these override positional if same name)
                original_input_data.update(kwargs)
                
            except Exception:
                # Fallback: use generic names for args and include kwargs
                for i, arg in enumerate(args):
                    original_input_data[f"arg_{i}"] = arg
                original_input_data.update(kwargs)

            # Fire-and-forget start notification
            asyncio.create_task(
                self.notify_call_start(
                    child_execution_id,
                    child_context,
                    original_func.__name__,
                    original_input_data,  # 🔧 FIX: Send complete input data
                    parent_execution_id=current_context.execution_id,
                )
            )

            start_time = time.time()
            try:
                if self.agent.dev_mode:
                    print(f"🔍 TRACK: Executing {original_func.__name__}")

                # Execute the original function
                if asyncio.iscoroutinefunction(original_func):
                    result = await original_func(*args, **kwargs)
                else:
                    result = original_func(*args, **kwargs)

                if self.agent.dev_mode:
                    print(
                        f"🔍 TRACK: {original_func.__name__} completed successfully, sending completion notification"
                    )

                # Fire-and-forget completion notification
                end_time = time.time()
                asyncio.create_task(
                    self.notify_call_complete(
                        child_execution_id,
                        child_context.workflow_id,
                        result,
                        int((end_time - start_time) * 1000),
                        child_context,  # 🔥 FIX: Pass child_context to get parent_workflow_id
                        input_data=original_input_data,  # 🔧 FIX: Pass original complete input data
                        parent_execution_id=current_context.execution_id,
                    )
                )

                return result

            except Exception as e:
                if self.agent.dev_mode:
                    print(
                        f"🔍 TRACK: {original_func.__name__} failed with error: {e}, sending error notification"
                    )

                # Fire-and-forget error notification
                end_time = time.time()
                asyncio.create_task(
                    self.notify_call_error(
                        child_execution_id,
                        child_context.workflow_id,
                        str(e),
                        int((end_time - start_time) * 1000),
                        child_context,  # 🔥 FIX: Pass child_context to get parent_workflow_id
                        input_data=original_input_data,  # 🔧 FIX: Pass original complete input data
                        parent_execution_id=current_context.execution_id,
                    )
                )
                raise
            finally:
                # Always restore previous context
                self.agent._current_execution_context = previous_context
                if self.agent.dev_mode:
                    print(
                        f"🔍 TRACK: Restored previous context for {original_func.__name__}"
                    )
        else:
            if self.agent.dev_mode:
                print(
                    f"🔍 TRACK: No execution context found for {original_func.__name__}, creating root context"
                )

            # Create a new root execution context for tracking
            root_context = ExecutionContext.create_new(
                agent_node_id=self.agent.node_id,
                workflow_name=f"{self.agent.node_id}_{original_func.__name__}",
            )
            root_execution_id = root_context.execution_id  # Use the execution_id from the root context

            if self.agent.dev_mode:
                print(
                    f"🔍 TRACK: Created root context - workflow_id={root_context.workflow_id}, execution_id={root_execution_id}"
                )

            # Inject execution context if function accepts it
            sig = inspect.signature(original_func)
            if "execution_context" in sig.parameters:
                kwargs["execution_context"] = root_context
                if self.agent.dev_mode:
                    print(
                        f"🔍 TRACK: Injected execution context into {original_func.__name__}"
                    )

            # Set root context as current during execution
            previous_context = self.agent._current_execution_context
            self.agent._current_execution_context = root_context

            if self.agent.dev_mode:
                print(
                    f"🔍 TRACK: Sending start notification for {original_func.__name__}"
                )

            # Fire-and-forget start notification
            asyncio.create_task(
                self.notify_call_start(
                    root_execution_id,
                    root_context,
                    original_func.__name__,
                    kwargs,
                    parent_execution_id=None,  # This is a root context
                )
            )

            start_time = time.time()
            try:
                if self.agent.dev_mode:
                    print(f"🔍 TRACK: Executing {original_func.__name__}")

                # Execute the original function
                if asyncio.iscoroutinefunction(original_func):
                    result = await original_func(*args, **kwargs)
                else:
                    result = original_func(*args, **kwargs)

                if self.agent.dev_mode:
                    print(
                        f"🔍 TRACK: {original_func.__name__} completed successfully, sending completion notification"
                    )

                # Fire-and-forget completion notification
                end_time = time.time()
                asyncio.create_task(
                    self.notify_call_complete(
                        root_execution_id,
                        root_context.workflow_id,
                        result,
                        int((end_time - start_time) * 1000),
                        root_context,  # 🔥 FIX: Pass root_context (parent_workflow_id will be None for root)
                        input_data=kwargs,  # 🔧 FIX: Pass actual input data
                    )
                )

                return result

            except Exception as e:
                if self.agent.dev_mode:
                    print(
                        f"🔍 TRACK: {original_func.__name__} failed with error: {e}, sending error notification"
                    )

                # Fire-and-forget error notification
                end_time = time.time()
                asyncio.create_task(
                    self.notify_call_error(
                        root_execution_id,
                        root_context.workflow_id,
                        str(e),
                        int((end_time - start_time) * 1000),
                        root_context,  # 🔥 FIX: Pass root_context (parent_workflow_id will be None for root)
                        input_data=kwargs,  # 🔧 FIX: Pass actual input data
                    )
                )
                raise
            finally:
                # Always restore previous context (which was None)
                self.agent._current_execution_context = previous_context
                if self.agent.dev_mode:
                    print(
                        f"🔍 TRACK: Restored previous context for {original_func.__name__}"
                    )

    async def notify_call_start(
        self,
        execution_id: str,
        context: ExecutionContext,
        reasoner_name: str,
        input_data: dict,
        parent_execution_id: Optional[str] = None,
    ):
        """Fire-and-forget notification when internal call starts"""
        try:
            payload = {
                "execution_id": execution_id,
                "workflow_id": context.workflow_id,
                "parent_workflow_id": context.parent_workflow_id,
                "parent_execution_id": parent_execution_id,
                "agent_node_id": self.agent.node_id,
                "reasoner_id": reasoner_name,
                "status": "running",
                "input_data": AgentUtils.serialize_result(input_data),
                "started_at": time.time(),
                "type": reasoner_name,
            }

            # Validation logging for parent-child relationships
            if self.agent.dev_mode:
                log_debug(f"🔍 VALIDATION: Workflow tracking for {reasoner_name}")
                log_debug(f"  Execution ID: {execution_id}")
                log_debug(f"  Workflow ID: {context.workflow_id}")
                log_debug(f"  Parent Workflow ID: {context.parent_workflow_id}")
                log_debug(f"  Parent Execution ID: {parent_execution_id}")
                log_debug(f"  Context Depth: {getattr(context, 'depth', 'unknown')}")
                
                # Validate parent-child relationship
                if parent_execution_id and context.parent_workflow_id:
                    log_debug(f"✅ VALIDATION: Child call detected - proper hierarchy")
                    log_debug(f"  → Child execution {execution_id} has parent execution {parent_execution_id}")
                    log_debug(f"  → Child workflow {context.workflow_id} has parent workflow {context.parent_workflow_id}")
                elif parent_execution_id is None and context.parent_workflow_id is None:
                    log_debug(f"✅ VALIDATION: Root call detected - no parent")
                else:
                    log_warn(f"⚠️ VALIDATION: Potential hierarchy issue detected")
                    log_warn(f"  → parent_execution_id: {parent_execution_id}")
                    log_warn(f"  → parent_workflow_id: {context.parent_workflow_id}")

            # Fire-and-forget HTTP call
            await self.fire_and_forget_update(payload)

        except Exception as e:
            if self.agent.dev_mode:
                log_error(f"⚠️ Failed to notify call start: {e}")

    async def notify_call_complete(
        self, execution_id: str, workflow_id: str, result: Any, duration_ms: int, context: ExecutionContext, input_data: Optional[dict] = None, parent_execution_id: Optional[str] = None
    ):
        """Fire-and-forget notification when internal call completes"""
        try:
            # 🔥 FIX: Serialize Pydantic models and other complex objects
            serialized_result = AgentUtils.serialize_result(result)

            # 🔥 FIX: Use parent_workflow_id directly from the child context
            # This ensures consistency with notify_call_start() which also uses context.parent_workflow_id
            parent_workflow_id = context.parent_workflow_id

            # 🔥 FIX: Use context.reasoner_name (now properly updated) instead of fallback
            reasoner_name = context.reasoner_name if hasattr(context, 'reasoner_name') and context.reasoner_name != "child_call" else "unknown"

            # 🔧 FIX: Use actual input data instead of empty dict
            serialized_input = AgentUtils.serialize_result(input_data) if input_data is not None else {}

            payload = {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "parent_execution_id": parent_execution_id,
                "parent_workflow_id": parent_workflow_id,  # 🔥 FIX: Now correctly includes parent_workflow_id
                "agent_node_id": self.agent.node_id,
                "reasoner_id": reasoner_name,  # 🔥 FIX: Use properly updated reasoner name
                "status": "completed",
                "input_data": serialized_input,  # 🔧 FIX: Send actual input data
                "result": serialized_result,  # ✅ JSON-serializable
                "duration_ms": duration_ms,
                "completed_at": time.time(),
                "type": reasoner_name,  # 🔥 FIX: Use properly updated reasoner name
            }

            # Validation logging for completion tracking
            if self.agent.dev_mode:
                log_debug(f"🔍 COMPLETION: Workflow completion for {reasoner_name}")
                log_debug(f"  Execution ID: {execution_id}")
                log_debug(f"  Workflow ID: {workflow_id}")
                log_debug(f"  Parent Workflow ID: {parent_workflow_id}")
                log_debug(f"  Parent Execution ID: {parent_execution_id}")
                log_debug(f"  Reasoner Name: {reasoner_name} (was: {context.reasoner_name})")
                if parent_execution_id and parent_workflow_id:
                    log_debug(f"✅ COMPLETION: Child workflow completion - proper hierarchy maintained")
                elif parent_execution_id is None and parent_workflow_id is None:
                    log_debug(f"✅ COMPLETION: Root workflow completion - no parent")
                else:
                    log_warn(f"⚠️ COMPLETION: Potential hierarchy issue in completion")

            # Fire-and-forget HTTP call
            await self.fire_and_forget_update(payload)

        except Exception as e:
            if self.agent.dev_mode:
                log_error(f"🔥 FIRE: Error in completion notification: {e}")
            # Continue execution - don't break workflow

    async def notify_call_error(
        self, execution_id: str, workflow_id: str, error: str, duration_ms: int, context: ExecutionContext, input_data: Optional[dict] = None, parent_execution_id: Optional[str] = None
    ):
        """Fire-and-forget notification when internal call fails"""
        try:
            # 🔥 FIX: Use parent_workflow_id directly from the context (consistent with completion fix)
            parent_workflow_id = context.parent_workflow_id

            # 🔥 FIX: Use context.reasoner_name (now properly updated) instead of fallback
            reasoner_name = context.reasoner_name if hasattr(context, 'reasoner_name') and context.reasoner_name != "child_call" else "unknown"

            # 🔧 FIX: Use actual input data instead of empty dict
            serialized_input = AgentUtils.serialize_result(input_data) if input_data is not None else {}

            payload = {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "parent_execution_id": parent_execution_id,
                "parent_workflow_id": parent_workflow_id,  # 🔥 FIX: Now correctly includes parent_workflow_id
                "agent_node_id": self.agent.node_id,
                "reasoner_id": reasoner_name,  # 🔥 FIX: Use properly updated reasoner name
                "status": "failed",
                "input_data": serialized_input,  # 🔧 FIX: Send actual input data
                "result": {},  # Provide empty dict as default for result
                "error": error,
                "duration_ms": duration_ms,
                "completed_at": time.time(),
                "type": reasoner_name,  # 🔥 FIX: Use properly updated reasoner name
            }

            # Validation logging for error tracking
            if self.agent.dev_mode:
                log_debug(f"🔍 ERROR: Workflow error for {reasoner_name}")
                log_debug(f"  Execution ID: {execution_id}")
                log_debug(f"  Workflow ID: {workflow_id}")
                log_debug(f"  Parent Workflow ID: {parent_workflow_id}")
                log_debug(f"  Parent Execution ID: {parent_execution_id}")
                log_debug(f"  Reasoner Name: {reasoner_name} (was: {context.reasoner_name})")
                log_error(f"  Error: {error}")

            # Fire-and-forget HTTP call
            await self.fire_and_forget_update(payload)

        except Exception as e:
            if self.agent.dev_mode:
                log_error(f"⚠️ Failed to notify call error: {e}")

    async def fire_and_forget_update(self, payload: dict):
        """Send update to Brain server without waiting for response"""
        try:
            log_fire(
                f"Sending workflow update - {payload.get('status')} for {payload.get('reasoner_id')}",
                payload
            )
            log_fire(f"URL: {self.agent.brain_server}/api/v1/workflow/update")
            
            # 🔧 DEBUG: Log input data specifically to diagnose empty input issue
            input_data = payload.get('input_data')
            if input_data is not None:
                log_fire(f"🔍 INPUT_DEBUG: Sending input_data: {input_data} (type: {type(input_data)})")
            else:
                log_fire("🔍 INPUT_DEBUG: Sending None input_data")

            if aiohttp:
                # Use aiohttp for non-blocking HTTP calls
                timeout = aiohttp.ClientTimeout(total=1.0)  # 1 second timeout
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.agent.brain_server}/api/v1/workflow/update",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    ) as response:
                        log_fire(f"Response status: {response.status}")
                        # Don't wait for response, just fire and forget
                        pass
            else:
                # Fallback to httpx if aiohttp not available
                import httpx

                async with httpx.AsyncClient(timeout=1.0) as client:
                    response = await client.post(
                        f"{self.agent.brain_server}/api/v1/workflow/update",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    log_fire(f"Response status: {response.status_code}")
        except Exception as e:
            log_fire(f"Error sending workflow update: {e}")
            # Continue silently for fire-and-forget
            pass
