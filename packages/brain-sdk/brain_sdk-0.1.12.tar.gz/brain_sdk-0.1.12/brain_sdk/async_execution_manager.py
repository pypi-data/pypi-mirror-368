"""
Async Execution Manager for the Brain SDK.

This module provides the central orchestrator for managing hundreds of concurrent
async executions with intelligent polling, resource management, and comprehensive
monitoring capabilities.
"""

import asyncio
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin
import uuid

from .async_config import AsyncConfig
from .execution_state import ExecutionState, ExecutionStatus, ExecutionPriority
from .http_connection_manager import ConnectionManager
from .result_cache import ResultCache
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class PollingMetrics:
    """Metrics for polling performance monitoring."""
    
    total_polls: int = 0
    successful_polls: int = 0
    failed_polls: int = 0
    timeout_polls: int = 0
    batch_polls: int = 0
    average_poll_duration: float = 0.0
    last_poll_time: float = field(default_factory=time.time)
    
    @property
    def success_rate(self) -> float:
        """Calculate polling success rate as a percentage."""
        if self.total_polls == 0:
            return 0.0
        return (self.successful_polls / self.total_polls) * 100
    
    def record_poll(self, success: bool, duration: float, timeout: bool = False) -> None:
        """Record a polling operation."""
        self.total_polls += 1
        self.last_poll_time = time.time()
        
        if success:
            self.successful_polls += 1
        else:
            self.failed_polls += 1
            if timeout:
                self.timeout_polls += 1
        
        # Update average duration using exponential moving average
        alpha = 0.1  # Smoothing factor
        self.average_poll_duration = (alpha * duration + 
                                    (1 - alpha) * self.average_poll_duration)


@dataclass
class ExecutionManagerMetrics:
    """Comprehensive metrics for the execution manager."""
    
    # Execution counts
    total_executions: int = 0
    active_executions: int = 0
    completed_executions: int = 0
    failed_executions: int = 0
    cancelled_executions: int = 0
    timeout_executions: int = 0
    
    # Performance metrics
    average_execution_time: float = 0.0
    average_queue_time: float = 0.0
    peak_concurrent_executions: int = 0
    
    # Resource metrics
    memory_usage_mb: float = 0.0
    cleanup_operations: int = 0
    
    # Polling metrics
    polling_metrics: PollingMetrics = field(default_factory=PollingMetrics)
    
    # Timestamps
    created_at: float = field(default_factory=time.time)
    last_cleanup: float = field(default_factory=time.time)
    
    @property
    def uptime(self) -> float:
        """Get manager uptime in seconds."""
        return time.time() - self.created_at
    
    @property
    def success_rate(self) -> float:
        """Calculate execution success rate as a percentage."""
        total_completed = (self.completed_executions + self.failed_executions + 
                          self.cancelled_executions + self.timeout_executions)
        if total_completed == 0:
            return 0.0
        return (self.completed_executions / total_completed) * 100


class AsyncExecutionManager:
    """
    Central orchestrator for managing hundreds of concurrent async executions.
    
    This class provides:
    - Concurrent execution tracking with ExecutionState objects
    - Intelligent polling with adaptive intervals based on execution age
    - Resource management with cleanup of completed executions
    - Background polling task coordination using asyncio
    - Thread-safe operations for concurrent access
    - Comprehensive metrics and monitoring
    - Integration with ConnectionManager and ResultCache
    """
    
    def __init__(
        self,
        base_url: str,
        config: Optional[AsyncConfig] = None,
        connection_manager: Optional[ConnectionManager] = None,
        result_cache: Optional[ResultCache] = None
    ):
        """
        Initialize the async execution manager.
        
        Args:
            base_url: Base URL for the brain server
            config: AsyncConfig instance for configuration parameters
            connection_manager: Optional ConnectionManager instance
            result_cache: Optional ResultCache instance
        """
        self.base_url = base_url.rstrip('/')
        self.config = config or AsyncConfig()
        
        # Validate configuration
        self.config.validate()
        
        # Initialize components
        self.connection_manager = connection_manager or ConnectionManager(self.config)
        self.result_cache = result_cache or ResultCache(self.config)
        
        # Execution tracking
        self._executions: Dict[str, ExecutionState] = {}
        self._execution_lock = asyncio.Lock()
        
        # Polling coordination
        self._polling_task: Optional[asyncio.Task] = None
        self._polling_semaphore = asyncio.Semaphore(self.config.max_active_polls)
        self._shutdown_event = asyncio.Event()
        
        # Metrics and monitoring
        self.metrics = ExecutionManagerMetrics()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        
        # Circuit breaker state
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure = 0.0
        self._circuit_breaker_open = False
        
        logger.debug(f"AsyncExecutionManager initialized with base_url={base_url}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    async def start(self) -> None:
        """
        Start the execution manager and all background tasks.
        
        Raises:
            RuntimeError: If manager is already started
        """
        if self._polling_task is not None:
            raise RuntimeError("AsyncExecutionManager is already started")
        
        # Start components
        await self.connection_manager.start()
        await self.result_cache.start()
        
        # Start background tasks
        self._polling_task = asyncio.create_task(self._polling_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        if self.config.enable_performance_logging:
            self._metrics_task = asyncio.create_task(self._metrics_loop())
        
        logger.info(f"AsyncExecutionManager started with max_concurrent={self.config.max_concurrent_executions}")
    
    async def stop(self) -> None:
        """
        Stop the execution manager and cleanup all resources.
        """
        logger.info("Stopping AsyncExecutionManager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel background tasks
        tasks_to_cancel = [
            self._polling_task,
            self._cleanup_task,
            self._metrics_task
        ]
        
        for task in tasks_to_cancel:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Cancel all active executions
        async with self._execution_lock:
            for execution in self._executions.values():
                if execution.is_active:
                    execution.cancel("Manager shutdown")
        
        # Stop components
        await self.connection_manager.close()
        await self.result_cache.stop()
        
        logger.info("AsyncExecutionManager stopped")
    
    async def submit_execution(
        self,
        target: str,
        input_data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        priority: ExecutionPriority = ExecutionPriority.NORMAL
    ) -> str:
        """
        Submit an async execution and return execution_id.
        
        Args:
            target: Target endpoint for execution
            input_data: Input data for the execution
            headers: Optional HTTP headers
            timeout: Optional execution timeout (uses config default if None)
            priority: Execution priority for queue management
            
        Returns:
            str: Execution ID for tracking the execution
            
        Raises:
            RuntimeError: If manager is not started or at capacity
            aiohttp.ClientError: For HTTP-related errors
        """
        if self._polling_task is None:
            raise RuntimeError("AsyncExecutionManager is not started")
        
        # Check capacity
        async with self._execution_lock:
            if len(self._executions) >= self.config.max_concurrent_executions:
                raise RuntimeError(f"Maximum concurrent executions reached: {self.config.max_concurrent_executions}")
        
        # Check circuit breaker
        if self._is_circuit_breaker_open():
            raise RuntimeError("Circuit breaker is open - too many recent failures")
        
        # Prepare request
        url = urljoin(self.base_url, f"/api/v1/execute/async/{target}")
        request_headers = {
            'Content-Type': 'application/json',
            **(headers or {})
        }
        
        # Set timeout
        execution_timeout = timeout or self.config.default_execution_timeout
        
        try:
            # Submit execution
            start_time = time.time()
            async with self.connection_manager.get_session() as session:
                response = await session.post(
                    url,
                    json=input_data,
                    headers=request_headers,
                    timeout=self.config.polling_timeout
                )
                response.raise_for_status()
                result = await response.json()
            
            execution_id = result.get('execution_id')
            if not execution_id:
                raise ValueError("Server did not return execution_id")
            
            # Create execution state
            execution_state = ExecutionState(
                execution_id=execution_id,
                target=target,
                input_data=input_data,
                priority=priority,
                timeout=execution_timeout
            )
            
            # Store execution
            async with self._execution_lock:
                self._executions[execution_id] = execution_state
                self.metrics.total_executions += 1
                self.metrics.active_executions += 1
                
                # Update peak concurrent executions
                if self.metrics.active_executions > self.metrics.peak_concurrent_executions:
                    self.metrics.peak_concurrent_executions = self.metrics.active_executions
            
            # Reset circuit breaker on success
            self._circuit_breaker_failures = 0
            
            duration = time.time() - start_time
            logger.debug(f"Submitted execution {execution_id[:8]}... for target {target} in {duration:.3f}s")
            
            return execution_id
            
        except Exception as e:
            self._record_circuit_breaker_failure()
            logger.error(f"Failed to submit execution for target {target}: {e}")
            raise
    
    async def wait_for_result(
        self,
        execution_id: str,
        timeout: Optional[float] = None
    ) -> Any:
        """
        Wait for execution result with intelligent polling.
        
        Args:
            execution_id: Execution ID to wait for
            timeout: Optional timeout override
            
        Returns:
            Any: Execution result
            
        Raises:
            KeyError: If execution_id is not found
            TimeoutError: If execution times out
            RuntimeError: If execution fails or is cancelled
        """
        # Check cache first
        cached_result = self.result_cache.get_execution_result(execution_id)
        if cached_result is not None:
            logger.debug(f"Retrieved cached result for execution {execution_id[:8]}...")
            return cached_result
        
        # Get execution state
        async with self._execution_lock:
            execution = self._executions.get(execution_id)
            if execution is None:
                raise KeyError(f"Execution {execution_id} not found")
        
        # Set timeout
        wait_timeout = timeout or execution.timeout or self.config.default_execution_timeout
        start_time = time.time()
        
        # Wait for completion
        while time.time() - start_time < wait_timeout:
            async with self._execution_lock:
                execution = self._executions.get(execution_id)
                if execution is None:
                    raise KeyError(f"Execution {execution_id} was removed")
                
                if execution.is_terminal:
                    if execution.is_successful:
                        # Cache successful result
                        if execution.result is not None:
                            self.result_cache.set_execution_result(execution_id, execution.result)
                        return execution.result
                    elif execution.status == ExecutionStatus.FAILED:
                        raise RuntimeError(f"Execution failed: {execution.error_message}")
                    elif execution.status == ExecutionStatus.CANCELLED:
                        raise RuntimeError(f"Execution was cancelled: {execution._cancellation_reason}")
                    elif execution.status == ExecutionStatus.TIMEOUT:
                        raise TimeoutError(f"Execution timed out after {execution.timeout} seconds")
            
            # Wait before next check
            await asyncio.sleep(0.1)
        
        # Timeout reached
        async with self._execution_lock:
            execution = self._executions.get(execution_id)
            if execution and execution.is_active:
                execution.timeout_execution()
                self.metrics.timeout_executions += 1
        
        raise TimeoutError(f"Wait timeout reached after {wait_timeout} seconds")
    
    async def cancel_execution(self, execution_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel an active execution.
        
        Args:
            execution_id: Execution ID to cancel
            reason: Optional cancellation reason
            
        Returns:
            bool: True if execution was cancelled, False if not found or already terminal
        """
        async with self._execution_lock:
            execution = self._executions.get(execution_id)
            if execution is None or execution.is_terminal:
                return False
            
            execution.cancel(reason)
            self.metrics.cancelled_executions += 1
            self.metrics.active_executions -= 1
            
            logger.debug(f"Cancelled execution {execution_id[:8]}... - {reason or 'No reason provided'}")
            return True
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of an execution.
        
        Args:
            execution_id: Execution ID to check
            
        Returns:
            Optional[Dict]: Execution status dictionary or None if not found
        """
        async with self._execution_lock:
            execution = self._executions.get(execution_id)
            if execution is None:
                return None
            
            return execution.to_dict()
    
    async def list_executions(
        self,
        status_filter: Optional[ExecutionStatus] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List executions with optional filtering.
        
        Args:
            status_filter: Optional status to filter by
            limit: Optional limit on number of results
            
        Returns:
            List[Dict]: List of execution status dictionaries
        """
        async with self._execution_lock:
            executions = list(self._executions.values())
            
            # Apply status filter
            if status_filter:
                executions = [e for e in executions if e.status == status_filter]
            
            # Sort by creation time (newest first)
            executions.sort(key=lambda e: e.created_at, reverse=True)
            
            # Apply limit
            if limit:
                executions = executions[:limit]
            
            return [execution.to_dict() for execution in executions]
    
    async def cleanup_completed_executions(self) -> int:
        """
        Clean up completed executions to manage memory.
        
        Returns:
            int: Number of executions cleaned up
        """
        cleanup_count = 0
        current_time = time.time()
        
        async with self._execution_lock:
            # Get completed executions sorted by completion time
            completed_executions = [
                (exec_id, execution) for exec_id, execution in self._executions.items()
                if execution.is_terminal
            ]
            
            # Keep only the most recent completed executions
            if len(completed_executions) > self.config.max_completed_executions:
                # Sort by end time (oldest first)
                completed_executions.sort(key=lambda x: x[1].metrics.end_time or 0)
                
                # Remove oldest executions
                to_remove = len(completed_executions) - self.config.max_completed_executions
                for i in range(to_remove):
                    exec_id, execution = completed_executions[i]
                    
                    # Cache successful results before removal
                    if execution.is_successful and execution.result is not None:
                        self.result_cache.set_execution_result(exec_id, execution.result)
                    
                    del self._executions[exec_id]
                    cleanup_count += 1
        
        if cleanup_count > 0:
            self.metrics.cleanup_operations += 1
            self.metrics.last_cleanup = current_time
            logger.debug(f"Cleaned up {cleanup_count} completed executions")
        
        return cleanup_count
    
    async def start_polling_task(self) -> None:
        """
        Start the background polling task.
        
        Note: This is automatically called by start() and should not be called manually.
        """
        if self._polling_task is None or self._polling_task.done():
            self._polling_task = asyncio.create_task(self._polling_loop())
            logger.debug("Background polling task started")
    
    async def stop_polling_task(self) -> None:
        """
        Stop the background polling task.
        
        Note: This is automatically called by stop() and should not be called manually.
        """
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None
            logger.debug("Background polling task stopped")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive execution manager metrics.
        
        Returns:
            Dict[str, Any]: Metrics dictionary
        """
        # Update current metrics
        async def _update_metrics():
            async with self._execution_lock:
                active_count = sum(1 for e in self._executions.values() if e.is_active)
                self.metrics.active_executions = active_count
        
        # Run the update if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_update_metrics())
        except RuntimeError:
            pass  # Not in async context
        
        return {
            'total_executions': self.metrics.total_executions,
            'active_executions': self.metrics.active_executions,
            'completed_executions': self.metrics.completed_executions,
            'failed_executions': self.metrics.failed_executions,
            'cancelled_executions': self.metrics.cancelled_executions,
            'timeout_executions': self.metrics.timeout_executions,
            'success_rate': self.metrics.success_rate,
            'average_execution_time': self.metrics.average_execution_time,
            'average_queue_time': self.metrics.average_queue_time,
            'peak_concurrent_executions': self.metrics.peak_concurrent_executions,
            'memory_usage_mb': self.metrics.memory_usage_mb,
            'cleanup_operations': self.metrics.cleanup_operations,
            'uptime': self.metrics.uptime,
            'polling_metrics': {
                'total_polls': self.metrics.polling_metrics.total_polls,
                'successful_polls': self.metrics.polling_metrics.successful_polls,
                'failed_polls': self.metrics.polling_metrics.failed_polls,
                'success_rate': self.metrics.polling_metrics.success_rate,
                'average_poll_duration': self.metrics.polling_metrics.average_poll_duration,
                'batch_polls': self.metrics.polling_metrics.batch_polls,
            },
            'circuit_breaker': {
                'failures': self._circuit_breaker_failures,
                'is_open': self._circuit_breaker_open,
                'last_failure': self._circuit_breaker_last_failure,
            },
            'connection_manager': self.connection_manager.get_metrics().__dict__,
            'result_cache': self.result_cache.get_stats(),
        }
    
    async def _polling_loop(self) -> None:
        """Background task for intelligent polling of active executions."""
        logger.debug("Starting polling loop")
        
        while not self._shutdown_event.is_set():
            try:
                await self._poll_active_executions()
                await asyncio.sleep(self.config.batch_poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Polling loop error: {e}")
                await asyncio.sleep(1.0)  # Brief pause on error
        
        logger.debug("Polling loop stopped")
    
    async def _poll_active_executions(self) -> None:
        """Poll all active executions that are ready for polling."""
        # Get executions ready for polling
        executions_to_poll = []
        current_time = time.time()
        
        async with self._execution_lock:
            for execution in self._executions.values():
                if execution.should_poll:
                    # Check for timeout
                    if execution.is_overdue:
                        execution.timeout_execution()
                        self.metrics.timeout_executions += 1
                        self.metrics.active_executions -= 1
                        continue
                    
                    executions_to_poll.append(execution)
        
        if not executions_to_poll:
            return
        
        # Use batch polling if enabled and beneficial
        if (self.config.enable_batch_polling and 
            len(executions_to_poll) >= 3):  # Batch threshold
            await self._batch_poll_executions(executions_to_poll)
        else:
            await self._individual_poll_executions(executions_to_poll)
    
    async def _batch_poll_executions(self, executions: List[ExecutionState]) -> None:
        """Poll multiple executions in batches for efficiency."""
        # Split into batches
        batch_size = min(self.config.batch_size, len(executions))
        
        for i in range(0, len(executions), batch_size):
            batch = executions[i:i + batch_size]
            
            # Create batch requests
            requests = []
            for execution in batch:
                url = urljoin(self.base_url, f"/api/v1/executions/{execution.execution_id}/status")
                requests.append({
                    'method': 'GET',
                    'url': url,
                    'timeout': self.config.polling_timeout
                })
            
            # Execute batch
            start_time = time.time()
            try:
                responses = await self.connection_manager.batch_request(requests)
                duration = time.time() - start_time
                
                # Process responses
                for execution, response in zip(batch, responses):
                    await self._process_poll_response(execution, response, duration / len(batch))
                
                self.metrics.polling_metrics.batch_polls += 1
                
            except Exception as e:
                logger.error(f"Batch polling failed: {e}")
                # Fall back to individual polling
                await self._individual_poll_executions(batch)
    
    async def _individual_poll_executions(self, executions: List[ExecutionState]) -> None:
        """Poll executions individually with concurrency control."""
        # Use semaphore to limit concurrent polls
        async def poll_single(execution: ExecutionState):
            async with self._polling_semaphore:
                await self._poll_single_execution(execution)
        
        # Create tasks for concurrent polling
        tasks = [poll_single(execution) for execution in executions]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _poll_single_execution(self, execution: ExecutionState) -> None:
        """Poll a single execution for status updates."""
        url = urljoin(self.base_url, f"/api/v1/executions/{execution.execution_id}/status")
        
        start_time = time.time()
        try:
            response = await self.connection_manager.request(
                'GET',
                url,
                timeout=self.config.polling_timeout
            )
            duration = time.time() - start_time
            
            await self._process_poll_response(execution, response, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            await self._process_poll_response(execution, e, duration)
    
    async def _process_poll_response(
        self,
        execution: ExecutionState,
        response: Any,
        duration: float
    ) -> None:
        """Process the response from a polling operation."""
        success = False
        timeout_occurred = False
        
        try:
            if isinstance(response, Exception):
                # Handle error response
                if isinstance(response, asyncio.TimeoutError):
                    timeout_occurred = True
                
                execution.record_poll_attempt(False, duration)
                
                # Update poll interval based on failure
                new_interval = min(
                    execution.current_poll_interval * 1.5,
                    self.config.max_poll_interval
                )
                execution.update_poll_interval(new_interval)
                
                logger.debug(f"Poll failed for execution {execution.execution_id[:8]}...: {response}")
                
            else:
                # Handle successful response
                response.raise_for_status()
                status_data = await response.json()
                
                # Update execution state
                await self._update_execution_from_status(execution, status_data)
                
                execution.record_poll_attempt(True, duration)
                success = True
                
                # Update poll interval based on execution age
                new_interval = self.config.get_poll_interval_for_age(execution.age)
                execution.update_poll_interval(new_interval)
        
        except Exception as e:
            execution.record_poll_attempt(False, duration)
            logger.error(f"Error processing poll response for {execution.execution_id[:8]}...: {e}")
        
        finally:
            # Record metrics
            self.metrics.polling_metrics.record_poll(success, duration, timeout_occurred)
    
    async def _update_execution_from_status(
        self,
        execution: ExecutionState,
        status_data: Dict[str, Any]
    ) -> None:
        """Update execution state from status response."""
        status_str = status_data.get('status', '').lower()
        
        # Map status string to enum
        status_mapping = {
            'queued': ExecutionStatus.QUEUED,
            'running': ExecutionStatus.RUNNING,
            'completed': ExecutionStatus.COMPLETED,
            'failed': ExecutionStatus.FAILED,
            'cancelled': ExecutionStatus.CANCELLED,
            'timeout': ExecutionStatus.TIMEOUT
        }
        
        new_status = status_mapping.get(status_str)
        if new_status is None:
            logger.warn(f"Unknown status '{status_str}' for execution {execution.execution_id[:8]}...")
            return
        
        old_status = execution.status
        
        # Update status
        if new_status != old_status:
            if new_status == ExecutionStatus.COMPLETED:
                result = status_data.get('result')
                execution.set_result(result)
                
                async with self._execution_lock:
                    self.metrics.completed_executions += 1
                    self.metrics.active_executions -= 1
                
            elif new_status == ExecutionStatus.FAILED:
                error_msg = status_data.get('error', 'Execution failed')
                error_details = status_data.get('error_details')
                execution.set_error(error_msg, error_details)
                
                async with self._execution_lock:
                    self.metrics.failed_executions += 1
                    self.metrics.active_executions -= 1
                
            else:
                execution.update_status(new_status)
            
            logger.debug(f"Execution {execution.execution_id[:8]}... status: {old_status.value} -> {new_status.value}")
    
    async def _cleanup_loop(self) -> None:
        """Background task for periodic cleanup of completed executions."""
        logger.debug("Starting cleanup loop")
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self.cleanup_completed_executions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
        
        logger.debug("Cleanup loop stopped")
    
    async def _metrics_loop(self) -> None:
        """Background task for periodic metrics logging."""
        logger.debug("Starting metrics loop")
        
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(60.0)  # Log metrics every minute
                
                metrics = self.get_metrics()
                logger.debug(
                    f"Execution metrics: "
                    f"active={metrics['active_executions']}, "
                    f"total={metrics['total_executions']}, "
                    f"success_rate={metrics['success_rate']:.1f}%, "
                    f"poll_success_rate={metrics['polling_metrics']['success_rate']:.1f}%"
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics loop error: {e}")
        
        logger.debug("Metrics loop stopped")
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        if not self._circuit_breaker_open:
            return False
        
        # Check if recovery timeout has passed
        if (time.time() - self._circuit_breaker_last_failure > 
            self.config.circuit_breaker_recovery_timeout):
            self._circuit_breaker_open = False
            self._circuit_breaker_failures = 0
            logger.info("Circuit breaker closed - attempting recovery")
            return False
        
        return True
    
    def _record_circuit_breaker_failure(self) -> None:
        """Record a failure for circuit breaker logic."""
        self._circuit_breaker_failures += 1
        self._circuit_breaker_last_failure = time.time()
        
        if (self._circuit_breaker_failures >= 
            self.config.circuit_breaker_failure_threshold):
            self._circuit_breaker_open = True
            logger.warn(f"Circuit breaker opened after {self._circuit_breaker_failures} failures")
    
    def __repr__(self) -> str:
        """String representation of the execution manager."""
        return (
            f"AsyncExecutionManager("
            f"base_url='{self.base_url}', "
            f"active_executions={self.metrics.active_executions}, "
            f"total_executions={self.metrics.total_executions}, "
            f"success_rate={self.metrics.success_rate:.1f}%"
            f")"
        )