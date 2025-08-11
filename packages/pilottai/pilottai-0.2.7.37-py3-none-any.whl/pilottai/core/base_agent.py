from __future__ import annotations

from typing import Dict, List, Optional, Union
import asyncio
import uuid
from abc import ABC, abstractmethod

from pilottai.core.base_config import AgentConfig, LLMConfig
from pilottai.config.model import JobResult
from pilottai.job.job import Job
from pilottai.enums.agent_e import AgentStatus
from pilottai.memory.memory import Memory
from pilottai.engine.llm import LLMHandler
from pilottai.tools.tool import Tool
from pilottai.utils.common_utils import format_system_prompt
from pilottai.utils.logger import Logger


class BaseAgent(ABC):
    """
    Base agent class for PilottAI framework.
    Handles job execution, tool management, and LLM interactions.
    """

    def __init__(
            self,
            title: str,
            goal: str,
            description: str,
            jobs: Union[Job, str, List[str], List[Job]],
            tools: Optional[List[Tool]] = None,
            config: Optional[AgentConfig] = None,
            llm_config: Optional[LLMConfig] = None,
            output_format = None,
            output_sample = None,
            memory_enabled: bool = True,
            reasoning: bool = False,
            feedback: bool = False,
            args: Optional[Dict] = None,
            depends_on: Optional[Union[List[BaseAgent], BaseAgent]]=None
    ):
        # Basic Configuration
        # Required fields
        self.id = str(uuid.uuid4())
        self.title = title
        self.goal = goal
        self.description = description
        self.jobs = self._verify_jobs(jobs)
        self.args = args

        # Core configuration
        self.config = config if config else AgentConfig()
        self.id = str(uuid.uuid4())

        # State management
        self.status = AgentStatus.IDLE
        self.current_job: Optional[Job] = None
        self._job_lock = asyncio.Lock()
        self.depends_on = depends_on

        # Components
        self.tools = tools
        self.memory = Memory() if memory_enabled else None
        self.llm = LLMHandler(llm_config) if llm_config else None

        # Output management
        self.output_format = output_format
        self.output_sample = output_sample
        self.reasoning = reasoning

        self.system_prompt = format_system_prompt(title, goal, description)

        # HITL
        self.feedback = feedback

        # Setup logging
        self.logger = self._setup_logger()

    @abstractmethod
    def _verify_jobs(self, jobs):
        pass

    @abstractmethod
    async def execute_jobs(self) -> List[JobResult]:
        """Execute all job assigned to this agent"""
        pass

    @abstractmethod
    async def execute_job(self, job: Job, dependent_agent: Optional[Union[List[BaseAgent], BaseAgent]], args: Optional[Dict]=None) -> Optional[JobResult]:
        """Execute a job with comprehensive planning and execution"""
        pass

    @abstractmethod
    def _format_job(self, job: Job) -> str:
        """Format job with context and more robust error handling"""
        pass

    @abstractmethod
    async def _create_plan(self, job: str) -> Dict:
        """Create execution plan using LLM and templates from rules.yaml"""
        pass

    @abstractmethod
    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from LLM response with better error handling"""
        pass

    @abstractmethod
    async def _execute_plan(self, plan: Dict) -> str:
        """Execute the planned steps with proper type checking and error handling"""
        pass

    @abstractmethod
    async def _execute_step(self, step: Dict, context: Dict) -> str:
        """Execute a single step with proper type checking"""
        pass

    @abstractmethod
    async def _execute_direct_step(self, input_text: str, context: Dict) -> str:
        """Execute direct step with LLM"""
        pass

    @abstractmethod
    async def _summarize_results(self, results: List[str], step_results: Dict[str, str]) -> str:
        """Summarize execution results with contextual understanding"""
        pass

    @abstractmethod
    def _get_system_prompt(self, is_summary: bool) -> str:
        """Get system prompt with fallback error handling"""
        pass

    @abstractmethod
    def _parse_json_response(self, response: str) -> str:
        """Parse JSON response from LLM"""
        pass

    @abstractmethod
    async def evaluate_job_suitability(self, job: Dict) -> float:
        """Evaluate how suitable this agent is for a job"""
        pass

    @abstractmethod
    async def start(self):
        """Start the agent"""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the agent"""
        pass

    @abstractmethod
    def _setup_logger(self) -> Logger:
        """Setup agent logging"""
        pass
