"""
Adaptive Agent Swarm Manager with dynamic re-planning capabilities
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import re
from enum import Enum
import traceback

from ..agents.agent import MCPAgent
from ..providers.base import LLMProvider

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Task execution type"""
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"


@dataclass
class Task:
    """Represents a single task in the execution plan"""
    id: str
    description: str
    type: TaskType = TaskType.SEQUENTIAL
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    agent_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    triggers_replan: bool = False
    retry_count: int = 0
    max_retries: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Execution plan created by the manager"""
    tasks: List[Task]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    version: int = 1  # Track plan versions


class AdaptiveSwarmManager:
    """
    Orchestrates multiple agents with dynamic task decomposition and adaptive replanning
    """
    
    def __init__(
        self,
        provider: Union[str, LLMProvider] = "anthropic",
        model: Optional[str] = None,
        max_parallel_agents: int = 5,
        observee_url: Optional[str] = None,
        observee_api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        server_name: str = "observee",
        enable_filtering: bool = False,
        filter_type: str = "bm25",
        manager_system_prompt: Optional[str] = None,
        agent_system_prompt: Optional[str] = None,
        enable_adaptive_planning: bool = True,
        task_timeout: float = 300.0,  # 5 minutes default
        enable_retry: bool = True,
        max_retries: int = 1,
        strict_error_detection: bool = False,  # When True, detects errors in task results
        **provider_kwargs
    ):
        # Validate inputs
        if max_parallel_agents < 1:
            raise ValueError("max_parallel_agents must be at least 1")
        if task_timeout <= 0:
            raise ValueError("task_timeout must be positive")
            
        self.provider = provider
        self.model = model
        self.max_parallel_agents = max_parallel_agents
        self.observee_url = observee_url
        self.observee_api_key = observee_api_key
        self.client_id = client_id
        self.server_name = server_name
        self.enable_filtering = enable_filtering
        self.filter_type = filter_type
        self.enable_adaptive_planning = enable_adaptive_planning
        self.task_timeout = task_timeout
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        self.strict_error_detection = strict_error_detection
        self.provider_kwargs = provider_kwargs
        
        # System prompts
        self.manager_system_prompt = manager_system_prompt or self._get_default_manager_prompt()
        self.agent_system_prompt = agent_system_prompt or "You are a helpful AI assistant with access to various tools. Complete your assigned task thoroughly."
        
        # Runtime state with thread safety
        self.active_agents: Dict[str, MCPAgent] = {}
        self.execution_plan: Optional[ExecutionPlan] = None
        self.task_results: Dict[str, Task] = {}
        self.discovered_data: Dict[str, Any] = {}
        self.execution_lock = asyncio.Lock()
        self.agent_semaphore: Optional[asyncio.Semaphore] = None
        
        # Manager agent for task decomposition
        self.manager_agent: Optional[MCPAgent] = None
        
        # Track execution state
        self.is_executing = False
        self.cancelled = False
    
    def _extract_json_from_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response"""
        if not content:
            return None
            
        # Try direct JSON parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in the content
        import re
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _create_fallback_plan(self, query: str, error: str) -> ExecutionPlan:
        """Create a simple fallback plan when planning fails"""
        fallback_task = Task(
            id="task_0",
            description=query,
            type=TaskType.SEQUENTIAL,
            dependencies=[],
            triggers_replan=False
        )
        
        return ExecutionPlan(
            tasks=[fallback_task],
            metadata={
                "error": error,
                "original_query": query,
                "fallback": True
            },
            version=1
        )
    
    def _validate_task_dependencies(self, tasks: List[Task]) -> None:
        """Validate task dependencies"""
        task_ids = {task.id for task in tasks}
        
        # Remove invalid dependencies
        for task in tasks:
            valid_deps = []
            for dep_id in task.dependencies:
                if dep_id in task_ids:
                    valid_deps.append(dep_id)
                else:
                    logger.warning(f"Task {task.id} has invalid dependency: {dep_id}")
            task.dependencies = valid_deps
    
    def _get_default_manager_prompt(self) -> str:
        return """Analyze queries and create execution plans that adapt based on discovered data.

Output JSON:
{
    "tasks": [{
        "id": "task_X",
        "description": "what to do",
        "type": "parallel|sequential",
        "dependencies": ["task_ids"],
        "triggers_replan": true/false
    }],
    "reasoning": "strategy explanation"
}

Rules:
- Parallel tasks when independent
- triggers_replan=true for discovery tasks
- Split lists into individual parallel tasks (e.g., multiple phone calls)
- Self-contained tasks per agent"""
    
    async def __aenter__(self):
        """Initialize the manager agent"""
        try:
            # Get observee config using the same logic as main __init__.py
            from .. import _get_observee_config
            config = _get_observee_config(self.observee_url, self.observee_api_key, self.client_id)
            
            self.manager_agent = MCPAgent(
                provider=self.provider,
                model=self.model,
                server_name=self.server_name,
                server_url=config["url"],
                auth_token=config["auth_token"],
                enable_filtering=False,  # Manager doesn't need tool filtering
                system_prompt=self.manager_system_prompt,
                **self.provider_kwargs
            )
            await self.manager_agent.__aenter__()
            
            # Initialize semaphore for agent pool
            self.agent_semaphore = asyncio.Semaphore(self.max_parallel_agents)
            
            return self
        except Exception as e:
            logger.error(f"Failed to initialize manager: {e}")
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup manager and any active agents"""
        # Cancel any running execution
        self.cancelled = True
        
        # Close manager agent
        if self.manager_agent:
            try:
                await self.manager_agent.__aexit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                logger.error(f"Error closing manager agent: {e}")
        
        # Close any remaining active agents with timeout
        if self.active_agents:
            close_tasks = []
            for agent_id, agent in self.active_agents.items():
                async def close_agent(a_id, a):
                    try:
                        await asyncio.wait_for(
                            a.__aexit__(None, None, None),
                            timeout=10.0
                        )
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout closing agent {a_id}")
                    except Exception as e:
                        logger.error(f"Error closing agent {a_id}: {e}")
                
                close_tasks.append(close_agent(agent_id, agent))
            
            if close_tasks:
                await asyncio.gather(*close_tasks, return_exceptions=True)
        
        self.active_agents.clear()
        self.task_results.clear()
        self.discovered_data.clear()
    
    async def create_execution_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> ExecutionPlan:
        """Use the manager agent to create an execution plan"""
        if not self.manager_agent:
            raise RuntimeError("Manager agent not initialized")
            
        # Get count of available tools
        tools_count = len(self.manager_agent.tool_handler.all_tools) if self.manager_agent and hasattr(self.manager_agent, 'tool_handler') else 0
        
        # Build context section
        context_section = ""
        if context:
            # Truncate large contexts to avoid token limits
            context_str = json.dumps(context, indent=2)
            if len(context_str) > 2000:
                context_str = context_str[:2000] + "\n... (truncated)"
            context_section = f"\n\nContext from previous tasks:\n{context_str}\n"
        
        prompt = f"""Analyze this query and create an execution plan:

Query: {query}

Maximum parallel agents available: {self.max_parallel_agents}
Total tools available: {tools_count}
{context_section}
You have access to all MCP tools. Consider which tasks might discover data that requires creating additional parallel tasks.

Remember to output a valid JSON execution plan."""
        
        try:
            # Get plan from manager with timeout
            response = await asyncio.wait_for(
                self.manager_agent.chat(prompt),
                timeout=60.0  # 1 minute timeout for planning
            )
            
            # Extract JSON from response
            content = response.get("content", "")
            
            # Try multiple extraction methods
            plan_data = self._extract_json_from_response(content)
            
            if not plan_data:
                raise ValueError("No valid JSON found in response")
            
            # Validate and create Task objects
            tasks = []
            task_ids = set()
            
            for i, task_data in enumerate(plan_data.get("tasks", [])):
                # Validate task data
                task_id = task_data.get("id", f"task_{i}")
                if task_id in task_ids:
                    task_id = f"{task_id}_{i}"  # Make unique
                task_ids.add(task_id)
                
                # Parse task type
                task_type_str = task_data.get("type", "sequential").lower()
                task_type = TaskType.PARALLEL if task_type_str == "parallel" else TaskType.SEQUENTIAL
                
                # Validate dependencies
                dependencies = task_data.get("dependencies", [])
                if not isinstance(dependencies, list):
                    dependencies = []
                
                task = Task(
                    id=task_id,
                    description=task_data.get("description", ""),
                    type=task_type,
                    dependencies=[d for d in dependencies if isinstance(d, str)],
                    triggers_replan=bool(task_data.get("triggers_replan", False)),
                    max_retries=self.max_retries if self.enable_retry else 0,
                    metadata=task_data.get("metadata", {})
                )
                tasks.append(task)
            
            # Validate task dependencies
            self._validate_task_dependencies(tasks)
            
            # Create execution plan
            version = 1
            if self.execution_plan:
                version = self.execution_plan.version + 1
                
            plan = ExecutionPlan(
                tasks=tasks,
                metadata={
                    "reasoning": plan_data.get("reasoning", ""),
                    "potential_replanning": plan_data.get("potential_replanning", ""),
                    "original_query": query,
                    "context": context
                },
                version=version
            )
            
            return plan
            
        except asyncio.TimeoutError:
            logger.error("Timeout creating execution plan")
            return self._create_fallback_plan(query, "Planning timeout")
        except Exception as e:
            logger.error(f"Failed to create execution plan: {e}")
            logger.debug(f"Full error: {traceback.format_exc()}")
            return self._create_fallback_plan(query, str(e))
    
    async def replan_if_needed(self, completed_task: Task) -> Optional[ExecutionPlan]:
        """Check if replanning is needed based on completed task results"""
        if not self.enable_adaptive_planning or not completed_task.triggers_replan:
            return None
        
        # Extract meaningful data from task results
        result_content = ""
        if completed_task.result:
            result_content = completed_task.result.get("content", "")
        
        # Check if the result contains data that suggests parallelization opportunity
        # This is a simple heuristic - could be made more sophisticated
        contains_list = any(keyword in result_content.lower() for keyword in [
            "list", "multiple", "several", "found", "items", "entries", "rows", "partners"
        ])
        
        if not contains_list:
            return None
        
        # Build context for replanning
        context = {
            "completed_tasks": {
                task_id: {
                    "description": t.description,
                    "result_preview": t.result.get("content", "")[:500] if t.result else ""
                }
                for task_id, t in self.task_results.items()
                if t.status == TaskStatus.COMPLETED
            },
            "discovered_data": self.discovered_data,
            "remaining_tasks": [
                {"id": t.id, "description": t.description}
                for t in self.execution_plan.tasks
                if t.status == TaskStatus.PENDING
            ]
        }
        
        # Ask manager to create an updated plan
        replan_prompt = f"""Based on newly discovered information, update the execution plan to optimize parallel processing.

Original query: {self.execution_plan.metadata.get('original_query', '')}

Newly discovered information from {completed_task.id}:
{result_content[:1000]}

Current context: {json.dumps(context, indent=2)}

Create an updated plan that:
1. Incorporates the discovered data
2. Maximizes parallel execution where possible
3. Only includes tasks that haven't been completed yet
4. If you discovered multiple items (like phone numbers, contacts, etc.), create INDIVIDUAL PARALLEL TASKS for each item
5. For example: if you found 3 phone numbers, create 3 separate parallel tasks to call each number

IMPORTANT: Look at the discovered data carefully. If it contains a list of items that need processing (like multiple phone numbers to call), you MUST create separate tasks for each item.

Output a new JSON execution plan."""
        
        try:
            # Pass the replan prompt directly to the manager
            new_plan = await self.create_execution_plan(
                replan_prompt,
                context
            )
            
            # Merge new tasks into existing plan
            existing_task_ids = {t.id for t in self.execution_plan.tasks}
            for task in new_plan.tasks:
                if task.id not in existing_task_ids:
                    self.execution_plan.tasks.append(task)
            
            self.execution_plan.version += 1
            return new_plan
            
        except Exception as e:
            logger.error(f"Failed to replan: {e}")
            return None
    
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task with an agent"""
        agent_id = str(uuid.uuid4())
        
        try:
            # Get observee config using the same logic as main __init__.py
            from .. import _get_observee_config
            config = _get_observee_config(self.observee_url, self.observee_api_key, self.client_id)
            
            # Create agent for this task
            agent = MCPAgent(
                provider=self.provider,
                model=self.model,
                server_name=self.server_name,
                server_url=config["url"],
                auth_token=config["auth_token"],
                enable_filtering=self.enable_filtering,
                filter_type=self.filter_type,
                system_prompt=self.agent_system_prompt,
                **self.provider_kwargs
            )
            
            await agent.__aenter__()
            self.active_agents[agent_id] = agent
            
            # Update task status
            task.agent_id = agent_id
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            # Build context-aware prompt
            prompt = f"""Execute this task: {task.description}

Context from previous tasks:
{json.dumps(context, indent=2)}

Complete the task and provide detailed results."""
            
            # Execute task
            result = await agent.chat_with_tools(prompt)
            
            # Check if the result indicates an error (if strict error detection is enabled)
            if self.strict_error_detection:
                result_content = result.get("content", "")
                is_error = any(indicator in result_content.lower() for indicator in [
                    "error", "failed", "issue", "problem", "unable to", "could not"
                ])
                
                # Update task with results
                if is_error and "successfully" not in result_content.lower():
                    task.status = TaskStatus.FAILED
                    task.error = "Task completed but reported errors"
                else:
                    task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            # Store in results
            self.task_results[task.id] = task
            
            return {
                "task_id": task.id,
                "status": "failed" if task.status == TaskStatus.FAILED else "success",
                "result": result,
                "duration": (task.completed_at - task.started_at).total_seconds(),
                "error": task.error
            }
            
        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            return {
                "task_id": task.id,
                "status": "failed",
                "error": str(e)
            }
            
        finally:
            # Cleanup agent
            if agent_id in self.active_agents:
                agent = self.active_agents.pop(agent_id)
                await agent.__aexit__(None, None, None)
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (dependencies satisfied)"""
        if not self.execution_plan:
            return []
        
        ready_tasks = []
        for task in self.execution_plan.tasks:
            if task.status == TaskStatus.PENDING:
                # Check dependency status
                has_failed_dep = False
                all_deps_done = True
                
                for dep_id in task.dependencies:
                    dep_task = self.get_task_by_id(dep_id)
                    if dep_task:
                        if dep_task.status == TaskStatus.FAILED:
                            has_failed_dep = True
                            break
                        elif dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                            all_deps_done = False
                
                # Skip tasks with failed dependencies
                if has_failed_dep:
                    task.status = TaskStatus.CANCELLED
                    task.error = "Skipped due to failed dependency"
                    self.task_results[task.id] = task
                    logger.warning(f"Task {task.id} cancelled due to failed dependencies")
                elif all_deps_done:
                    ready_tasks.append(task)
        
        return ready_tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID"""
        if not self.execution_plan:
            return None
        
        for task in self.execution_plan.tasks:
            if task.id == task_id:
                return task
        return None
    
    def build_task_context(self, task: Task) -> Dict[str, Any]:
        """Build context for a task from its dependencies"""
        context = {
            "task_id": task.id,
            "dependencies": {}
        }
        
        for dep_id in task.dependencies:
            dep_task = self.task_results.get(dep_id)
            if dep_task and dep_task.status == TaskStatus.COMPLETED:
                # Extract meaningful content
                result_content = ""
                if dep_task.result:
                    result_content = dep_task.result.get("content", "")
                    # Truncate if too long
                    if len(result_content) > 1000:
                        result_content = result_content[:1000] + "... (truncated)"
                
                context["dependencies"][dep_id] = {
                    "description": dep_task.description,
                    "result": result_content,
                    "completed_at": dep_task.completed_at.isoformat() if dep_task.completed_at else None
                }
        
        # Add discovered data if relevant
        if self.discovered_data:
            context["discovered_data"] = self.discovered_data
        
        return context
    
    async def execute_stream(self, query: str):
        """
        Stream execution updates with adaptive replanning
        """
        start_time = datetime.now()
        
        # Stream: Starting
        yield {
            "type": "start",
            "query": query,
            "timestamp": start_time.isoformat(),
            "adaptive_planning": self.enable_adaptive_planning
        }
        
        # Stream: Planning phase
        yield {
            "type": "planning",
            "message": "Creating initial execution plan..."
        }
        
        self.execution_plan = await self.create_execution_plan(query)
        
        yield {
            "type": "plan_created",
            "total_tasks": len(self.execution_plan.tasks),
            "reasoning": self.execution_plan.metadata.get("reasoning", ""),
            "version": self.execution_plan.version
        }
        
        # Stream task details
        for task in self.execution_plan.tasks:
            yield {
                "type": "task_planned",
                "task_id": task.id,
                "description": task.description,
                "dependencies": task.dependencies,
                "can_run_parallel": task.type == "parallel",
                "triggers_replan": task.triggers_replan
            }
        
        # Execute tasks with streaming updates
        while True:
            # Count completed/failed/cancelled tasks
            finished_tasks = sum(1 for t in self.execution_plan.tasks 
                               if t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED])
            
            # Check if all tasks are done
            if finished_tasks >= len(self.execution_plan.tasks):
                break
            ready_tasks = self.get_ready_tasks()
            
            if ready_tasks:
                current_parallel = len([t for t in self.execution_plan.tasks if t.status == TaskStatus.RUNNING])
                available_slots = self.max_parallel_agents - current_parallel
                tasks_to_run = ready_tasks[:available_slots]
                
                # Start tasks
                if len(tasks_to_run) > 1:
                    yield {
                        "type": "parallel_batch_start",
                        "count": len(tasks_to_run),
                        "task_ids": [t.id for t in tasks_to_run]
                    }
                
                for task in tasks_to_run:
                    yield {
                        "type": "task_started",
                        "task_id": task.id,
                        "description": task.description,
                        "running_in_parallel": len(tasks_to_run) > 1
                    }
                
                # Execute in parallel
                execution_tasks = []
                for task in tasks_to_run:
                    context = self.build_task_context(task)
                    execution_tasks.append(self.execute_task(task, context))
                
                results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                
                # Process results and check for replanning
                for i, result in enumerate(results):
                    task = tasks_to_run[i]
                    if isinstance(result, Exception) or (isinstance(result, dict) and result.get("status") == "failed"):
                        yield {
                            "type": "task_failed",
                            "task_id": task.id,
                            "error": str(result) if isinstance(result, Exception) else result.get("error", "Unknown error")
                        }
                    else:
                        yield {
                            "type": "task_completed" if task.status == TaskStatus.COMPLETED else "task_failed",
                            "task_id": task.id,
                            "result": task.result.get("content", "") if task.result else "",
                            "status": task.status.value
                        }
                        
                        # Check if replanning is needed
                        if task.triggers_replan and self.enable_adaptive_planning:
                            yield {
                                "type": "replanning_check",
                                "task_id": task.id,
                                "message": "Checking if plan update needed based on discovered data..."
                            }
                            
                            new_plan = await self.replan_if_needed(task)
                            if new_plan:
                                # Update total expected tasks
                                total_expected_tasks = len(self.execution_plan.tasks)
                                
                                yield {
                                    "type": "plan_updated",
                                    "version": self.execution_plan.version,
                                    "new_tasks": len(new_plan.tasks),
                                    "total_tasks": total_expected_tasks,
                                    "reason": "Discovered data requiring parallel processing"
                                }
                                
                                # Stream new tasks
                                for new_task in new_plan.tasks:
                                    if not any(t.id == new_task.id for t in self.execution_plan.tasks[:-len(new_plan.tasks)]):
                                        yield {
                                            "type": "task_planned",
                                            "task_id": new_task.id,
                                            "description": new_task.description,
                                            "dependencies": new_task.dependencies,
                                            "can_run_parallel": new_task.type == "parallel",
                                            "triggers_replan": new_task.triggers_replan,
                                            "added_dynamically": True
                                        }
                    
                    # Count is now tracked in the while loop condition
            else:
                await asyncio.sleep(0.1)
        
        # Stream: Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        all_results = []
        for task in self.execution_plan.tasks:
            if task.result:
                all_results.append({
                    "task_id": task.id,
                    "description": task.description,
                    "status": task.status.value,
                    "result": task.result.get("content", "")
                })
        
        yield {
            "type": "complete",
            "summary": self._create_summary(all_results),
            "duration": duration,
            "tasks_completed": len([t for t in self.execution_plan.tasks if t.status == TaskStatus.COMPLETED]),
            "tasks_failed": len([t for t in self.execution_plan.tasks if t.status == TaskStatus.FAILED]),
            "tasks_cancelled": len([t for t in self.execution_plan.tasks if t.status == TaskStatus.CANCELLED]),
            "plan_versions": self.execution_plan.version,
            "final_task_count": len(self.execution_plan.tasks)
        }
    
    def _create_summary(self, results: List[Dict[str, Any]]) -> str:
        """Create a summary of all task results"""
        if not results:
            return "No tasks were completed."
        
        summary_parts = []
        for result in results:
            if result["status"] == "completed":
                summary_parts.append(f"- {result['description']}: Completed successfully")
            else:
                summary_parts.append(f"- {result['description']}: Failed")
        
        return "\n".join(summary_parts)