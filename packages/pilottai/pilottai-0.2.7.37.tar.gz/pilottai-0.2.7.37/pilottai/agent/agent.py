from __future__ import annotations

import re
import uuid
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Union, Callable, Any

from pilottai.core.base_agent import BaseAgent
from pilottai.core.base_config import AgentConfig, LLMConfig
from pilottai.config.model import JobResult
from pilottai.job.job import Job
from pilottai.enums.agent_e import AgentStatus
from pilottai.memory.memory import Memory
from pilottai.engine.llm import LLMHandler
from pilottai.tools.tool import Tool
from pilottai.utils.excpetions.agent import AgentExecutionError
from pilottai.utils.job_utils import JobUtility
from pilottai.utils.common_utils import format_system_prompt, get_agent_rule, extract_json_from_response
from pilottai.utils.logger import Logger




class Agent(BaseAgent):
    """
    Extended agent implementation with customized functionality
    """
    def __init__(
        self,
        title: str,
        goal: str,
        description: str,
        jobs: Union[str, Job, List[str], List[Job]],
        tools: Optional[List[Tool]] = None,
        config: Optional[AgentConfig] = None,
        llm_config: Optional[LLMConfig] = None,
        output_format=None,
        output_sample=None,
        memory_enabled: bool = True,
        reasoning: bool = True,
        feedback: bool = False,
        funcs: List[Callable[..., Any]] = None,
        args: Optional[Dict] = None,
        depends_on: Optional[Union[List[Agent], Agent]] = None
    ):
        super().__init__(
            title=title,
            goal=goal,
            description=description,
            jobs=jobs,
            tools=tools,
            config=config,
            llm_config=llm_config,
            output_format=output_format,
            output_sample=output_sample,
            memory_enabled=memory_enabled,
            reasoning=reasoning,
            feedback=feedback,
            args=args,
            depends_on=depends_on
        )

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
        self.current_jon: Optional[Job] = None
        self._job_lock = asyncio.Lock()
        self.depends_on = depends_on

        # Components
        self.tools = tools
        self.memory = Memory() if memory_enabled else None
        self.llm = LLMHandler(llm_config) if llm_config else None

        # Output management
        self._output = None
        self.output_format = output_format
        self.output_sample = output_sample
        self.reasoning = reasoning

        self.system_prompt = format_system_prompt(title, goal, description)

        # HITL
        self.feedback = feedback

        # Setup logging
        self.logger = self._setup_logger()

    @property
    def output(self):
        if self._output is None:
            raise RuntimeError(f"Agent '{self.title}' has not been executed yet.")
        return self._output

    @output.setter
    def output(self, value):
        self._output = value

    def _verify_jobs(self, jobs):
        try:
            if isinstance(jobs, str):
                jobs_obj = JobUtility.to_job_list(jobs)
            elif all(isinstance(t, (str, Job)) for t in jobs):
                jobs_obj = JobUtility.to_job_list(jobs)
            else:
                jobs_obj = jobs
        except:
            raise ValueError(f"Cannot convert {type(jobs)} to Job. Must be a string, dictionary, or Job object.")
        return jobs_obj

    async def execute_jobs(self) -> List[JobResult]:
        """Execute all job assigned to this agent"""
        results = []
        for job in self.jobs:
            try:
                result = await self.execute_job(job, dependent_agent=self.depends_on, args=self.args)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to execute job {job.id if hasattr(job, 'id') else 'unknown'}: {str(e)}")
                results.append(JobResult(
                    success=False,
                    output=None,
                    error=str(e),
                    execution_time=0.0,
                    metadata={"agent_id": self.id}
                ))
        return results

    async def execute_job(self, job: Job, dependent_agent: Optional[Union[List[Agent], Agent]]=None, args: Optional[Dict]=None) -> Optional[JobResult]:
        """Execute a job with comprehensive planning and execution"""
        if not self.llm:
            raise ValueError("LLM configuration required for job execution")

        if dependent_agent:
            job = self._resolve_job_dependency(job, dependent_agent, args)

        start_time = datetime.now()

        try:
            async with self._job_lock:
                self.status = AgentStatus.BUSY
                self.current_job = job

                # Store job start in memory if enabled
                if self.memory:
                    await self.memory.store_job_start(
                        job_id=job.id,
                        description=job.description,
                        agent_id=self.id,
                        context=getattr(job, 'context', {})
                    )

                # Format job with context
                formatted_job = self._format_job(job)
                self.logger.info(f"Executing job: {formatted_job}")

                # Generate execution plan
                execution_plan = await self._create_plan(formatted_job)
                self.logger.info(f"Execution plan created with {len(execution_plan.get('steps', []))} steps")

                # Execute the plan
                result = await self._execute_plan(execution_plan)
                if result is None:
                    raise AgentExecutionError

                # Calculate execution time
                execution_time = (datetime.now() - start_time).total_seconds()

                # Store job result in memory if enabled
                job_result = JobResult(
                    success=True,
                    output=result,
                    execution_time=execution_time,
                    metadata={
                        "agent_id": self.id,
                        "title": self.title,
                        "plan": execution_plan
                    }
                )

                if self.memory:
                    await self.memory.store_job_result(
                        job_id=job.id,
                        result=result,
                        success=True,
                        execution_time=execution_time,
                        agent_id=self.id
                    )

                return job_result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Job execution failed: {str(e)}")

            # Store failed job in memory if enabled
            if self.memory:
                await self.memory.store_job_result(
                    job_id=job.id if job else "unknown",
                    result=str(e),
                    success=False,
                    execution_time=execution_time,
                    agent_id=self.id
                )

            return JobResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time,
                metadata={"agent_id": self.id}
            )

        finally:
            self.status = AgentStatus.IDLE
            self.current_job = None

    def _format_job(self, job: Job) -> str:
        """Format job with context and more robust error handling"""
        if not job:
            return "No job provided"

        job_text = job.description

        if hasattr(job, 'context') and job.context:
            try:
                # Try direct formatting
                job_text = job_text.format(**job.context)
            except KeyError as e:
                # Handle missing keys gracefully
                self.logger.warning(f"Missing context key: {e}")
                # Try to substitute only available keys
                for key, value in job.context.items():
                    placeholder = "{" + key + "}"
                    if placeholder in job_text:
                        job_text = job_text.replace(placeholder, str(value))
            except Exception as e:
                self.logger.error(f"Error formatting job: {str(e)}")

        return job_text

    async def _create_plan(self, job: str) -> Dict:
        """Create execution plan using LLM and templates from rules.yaml"""
        try:
            # Load the step_planning template from rules.yaml
            try:
                plan_template = get_agent_rule('step_planning', 'agent', '')
            except Exception as e:
                self.logger.warning(f"Failed to load template from rules.yaml: {str(e)}")
                plan_template = """
                Job: {job_description}
                Available Tools: {available_tools}

                Return as JSON:
                {{
                  "steps": [
                    {{
                      "action": "tool",
                      "tool_name": "name of tool if applicable",
                      "parameters": {{}},
                      "description": "what this step does"
                    }}
                  ]
                }}
                """

            # Format available tools for template
            available_tools = []
            if self.tools:
                for tool in self.tools:
                    available_tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters
                    })

            formatted_template = plan_template.format(
                job_description=job,
                completed_steps=[],  # Start with no completed steps
                last_result=None  # Start with no last result
            )

            if available_tools:
                available_tools_str = f"Tools: {json.dumps(available_tools, indent=2)}"
                formatted_template += available_tools_str

            formatted_template += get_agent_rule('expected_result', 'agent', '')

            # Create prompt for LLM
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": formatted_template
                }
            ]

            # Get plan from LLM
            response = await self.llm.generate_response(messages)
            response_content = response["content"]

            # Try to extract JSON from response
            plan = self._extract_json_from_response(response_content)

            # Ensure plan has the proper format
            if not plan:
                # If plan is empty or invalid, create a default plan
                self.logger.warning("Using fallback single-step direct execution")
                return {
                    "steps": [{
                        "action": "direct_execution",
                        "input": job,
                        "description": "Direct job execution"
                    }]
                }

            # If we got the plan as a string instead of a dictionary
            if isinstance(plan, str):
                # Try to parse string as JSON
                try:
                    plan = json.loads(plan)
                except json.JSONDecodeError:
                    # If it's not valid JSON, use it as direct execution input
                    return {
                        "steps": [{
                            "action": "direct_execution",
                            "input": plan,
                            "description": "Direct execution of LLM result"
                        }]
                    }

            # Handle case where plan might be valid but doesn't have steps
            if not isinstance(plan, dict) or "steps" not in plan:
                self.logger.warning("Plan does not contain 'steps', using fallback")
                return {
                    "steps": [{
                        "action": "direct_execution",
                        "input": job,
                        "description": "Direct job execution (fallback)"
                    }]
                }

            # Ensure plan["steps"] is a list
            if not isinstance(plan["steps"], list):
                # If steps is a string, make it a single direct_execution step
                if isinstance(plan["steps"], str):
                    return {
                        "steps": [{
                            "action": "direct_execution",
                            "input": plan["steps"],
                            "description": "Direct execution of step"
                        }]
                    }
                else:
                    return {
                        "steps": [{
                            "action": "direct_execution",
                            "input": job,
                            "description": "Direct job execution (fallback)"
                        }]
                    }

            return plan

        except AgentExecutionError as e:
            self.logger.error(f"Error creating execution plan: {str(e)}")
            # Fallback to simple execution
            return {
                "steps": [{
                    "action": "direct_execution",
                    "input": job,
                    "description": "Direct job execution (fallback)"
                }]
            }

    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from LLM response with better error handling"""
        try:
            # Try to find JSON in code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in response:
                # Try any code block
                json_str = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)

            # Try to find JSON with braces
            import re
            json_pattern = r"\{[\s\S]*\}"
            match = re.search(json_pattern, response)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)

            # Last resort, try the whole response
            return json.loads(response)
        except Exception as e:
            self.logger.warning(f"Failed to extract JSON from response: {str(e)}")
            return {}

    async def _execute_plan(self, plan: Dict) -> str:
        """Execute the planned steps with proper type checking and error handling"""
        results = []
        step_results = {}  # Store results by step for context

        # Ensure plan has a steps key that's a list
        if not isinstance(plan, dict) or "steps" not in plan:
            self.logger.warning("Invalid plan format, using direct execution")
            return await self._execute_step({
                "action": "direct_execution",
                "input": "Invalid plan format, executing job directly",
                "description": "Direct execution fallback"
            }, {})

        steps = plan.get("steps", [])

        # Handle string steps - common issue
        if isinstance(steps, str):
            self.logger.warning("Steps is a string, not a list")
            return await self._execute_step({
                "action": "direct_execution",
                "input": steps,
                "description": "Direct execution of steps string"
            }, {})

        # Limit to a reasonable number of steps to avoid excessive errors
        if len(steps) > 50:
            self.logger.warning(f"Too many steps ({len(steps)}), limiting to 50")
            steps = steps[:50]

        has_job = any("job" in step.get("action", "").lower() for step in steps)

        # If not, append the default block
        if not has_job:
            steps.append({
                "action": "job",
                "description": "description",
                "validation_criteria": ["criteria"]
            })

        # Execute each step with proper validation
        for i, step in enumerate(steps):
            try:
                # Ensure step is a dictionary with required fields
                if not isinstance(step, dict):
                    # Convert string steps to direct_execution
                    if isinstance(step, str):
                        step = {
                            "action": "direct_execution",
                            "input": step,
                            "description": f"Direct execution of step {i + 1}"
                        }
                    else:
                        self.logger.error(f"Invalid step format for step {i + 1}: {type(step)}")
                        results.append(f"Error in step {i + 1}: Invalid step format")
                        continue

                self.logger.info(f"Executing step {i + 1}: {step.get('description', 'No description')}")

                # Add context from previous steps
                step_context = {f"step_{j + 1}": result for j, result in enumerate(results)}

                # Execute step with context
                step_result = await self._execute_step(step, step_context)

                # Store result
                results.append(step_result)
                step_results[f"step_{i + 1}"] = step_result

                # Store step in memory if enabled
                if self.memory:
                    await self.memory.store_semantic(
                        text=f"Step {i + 1}: {step}\nResult: {step_result}",
                        metadata={"type": "execution_step", "step_number": i + 1}
                    )

            except Exception as e:
                error_msg = f"Error in step {i + 1}: {str(e)}"
                self.logger.error(error_msg)
                results.append(error_msg)
                step_results[f"step_{i + 1}"] = error_msg

        # Summarize results with context
        summary = await self._summarize_results(results, step_results)
        plan["job_complete"] = True
        return summary

    async def _execute_step(self, step: Dict, context: Dict) -> str:
        """Execute a single step with proper type checking"""
        try:
            action = step.get("action", "").lower()

            if action == "tool":
                # Execute a tool
                tool_name = step.get("tool_name")
                parameters = step.get("parameters", {})

                # Find the requested tool
                tool = None
                for t in self.tools:
                    if t.name == tool_name:
                        tool = t
                        break

                if not tool:
                    return f"Error: Tool '{tool_name}' not found"

                # Execute the tool with parameters
                try:
                    result = await tool.execute(**parameters)
                    return str(result)
                except Exception as e:
                    return f"Error executing tool '{tool_name}': {str(e)}"

            elif action == "job":
                # Use LLM for job execution
                return await self._execute_direct_step(step.get("description", ""), context)

            else:
                return await self._execute_direct_step(step.get("input", ""), context)

        except Exception as e:
            self.logger.error(f"Step execution error: {str(e)}")
            return f"Error executing step: {str(e)}"

    async def _execute_direct_step(self, input_text: str, context: Dict) -> str:
        """Execute direct step with LLM"""
        # Format context for LLM
        context_text = ""
        if context:
            context_text = "Previous step results:\n"
            for key, value in context.items():
                context_text += f"{key}: {value}\n"
            context_text += "\n"

        # Create messages for LLM
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },
            {
                "role": "user",
                "content": f"{context_text}Job: {input_text}"
            }
        ]

        response = await self.llm.generate_response(messages)
        return response["content"]

    async def _summarize_results(self, results: List[str], step_results: Dict[str, str]) -> None | dict | str:
        """Generate the final result based on job description and execution steps"""
        try:
            retry_count = self.config.retry_limit
            for _ in range(retry_count):
                # Compile execution results
                execution_context = "\n\n".join([f"Step {i + 1}: {result}" for i, result in enumerate(results)])

                # Get the original job description
                job_description = self.current_job.description if self.current_job else "Unknown job"

                # Try to load result_evaluation template from rules.yaml
                template = None
                try:
                    template = get_agent_rule('result_evaluation', 'agent')
                except Exception as e:
                    self.logger.warning(f"Failed to load result_evaluation template: {str(e)}")

                # Format the template with the job description and results
                prompt = template.format(
                    job_description=job_description,
                    result=execution_context
                )

                # Create messages for LLM
                messages = [
                    {
                        "role": "system",
                        "content": self._get_system_prompt(True)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                # Get final result from LLM
                response = await self.llm.generate_response(messages)

                # Return the final result
                result = extract_json_from_response(response["content"])
                if result.get("success"):
                    return result.get("job_result")
                return None

        except Exception as e:
            self.logger.error(f"Error generating final result: {str(e)}")
            # Fallback to returning the last result if available
            if results:
                return f"Final result: {results[-1]}"
            else:
                return "Failed to generate a result for the requested job."

    def _get_system_prompt(self, is_summary: bool = False) -> str:
        """Get system prompt with fallback error handling"""
        try:
            # Create a basic system prompt
            base_prompt = f"""You are an AI agent with:
            Title: {self.title}
            Goal: {self.goal}
            Description: {self.description or 'No specific description.'}

            Make decisions and take actions based on your title and goal.
            """

            # Try to load from rules.yaml if available
            try:
                base_template = get_agent_rule('system.base', 'agent', '')

                if base_template:
                    return base_template.format(
                        title=self.title,
                        goal=self.goal,
                        description=self.description
                    )
                if is_summary:
                    base_template += "\nYour job is to deliver the final result that fulfills the requested job, not to summarize the execution process."
            except Exception as e:
                self.logger.error(f"Error loading system prompt template: {str(e)}")

            # Return the basic prompt if we couldn't get the template
            return base_prompt

        except Exception as e:
            self.logger.error(f"Error creating system prompt: {str(e)}")
            # Super simple fallback
            return f"You are an agent with title: {self.title}. Complete the job to the best of your ability."

    def _parse_json_response(self, response: str) -> str:
        """Parse JSON response from LLM"""
        try:
            # First try to extract JSON from markdown code blocks
            # if "```json" in response:
            #     json_str = response.split("```json")[1].split("```")[0]
            # elif "```" in response:
            #     json_str = response.split("```")[1].split("```")[0]
            # else:
            json_str = response

            return json_str  # Using eval for more forgiving parsing

        except Exception as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            return ""

    async def evaluate_job_suitability(self, job: Dict) -> float:
        """Evaluate how suitable this agent is for a job"""
        try:
            # Base suitability score
            score = 0.7

            if "required_capabilities" in job:
                missing = set(job["required_capabilities"]) - set(self.config.required_capabilities)
                if missing:
                    return 0.0

            # Adjust based on job type match
            if "type" in job and hasattr(self, "specializations"):
                if job["type"] in self.specializations:
                    score += 0.2

            # Adjust based on current load
            if self.status == AgentStatus.BUSY:
                score -= 0.3

            return min(1.0, score)

        except Exception as e:
            self.logger.error(f"Error evaluating suitability: {str(e)}")
            return 0.0

    async def start(self):
        """Start the agent"""
        try:
            self.status = AgentStatus.IDLE

            # Store agent start in memory if enabled
            if self.memory:
                await self.memory.store_semantic(
                    text=f"Agent {self.title} started",
                    metadata={
                        "type": "status_change",
                        "status": "started",
                        "agent_id": self.id
                    },
                    tags={"status_change", "agent_start"}
                )

            self.logger.info(f"Agent {self.id} started")

        except Exception as e:
            self.logger.error(f"Failed to start agent: {str(e)}")
            self.status = AgentStatus.ERROR
            raise

    async def stop(self):
        """Stop the agent"""
        try:
            self.status = AgentStatus.STOPPED

            # Store agent stop in memory if enabled
            if self.memory:
                await self.memory.store_semantic(
                    text=f"Agent {self.title} stopped",
                    metadata={
                        "type": "status_change",
                        "status": "stopped",
                        "agent_id": self.id
                    },
                    tags={"status_change", "agent_stop"}
                )

            self.logger.info(f"Agent {self.id} stopped")

        except Exception as e:
            self.logger.error(f"Failed to stop agent: {str(e)}")
            raise

    def _setup_logger(self) -> Logger:
        """Setup agent logging"""
        logger = Logger(f"Agent_{self.title}_{self.id}")

        if not logger.handlers:
            handler = logger.StreamHandler()
            formatter = logger.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(logger.DEBUG if self.config.verbose else logger.INFO)
        return logger

    def _resolve_job_dependency(self, job, dependents=None, context: dict = None):
        if job is None or job.description is None:
            return job  # or raise an error if job must not be None

        # Default context to empty dict if None
        if context is None:
            context = {}

        # Step 1: Build agent name → output map
        if dependents and isinstance(dependents, Agent):
            agents = {dependents.title.lower().replace(" ", "_"): dependents}
        elif dependents and isinstance(dependents, list):
            agents = {
                agent.title.lower().replace(" ", "_"): agent for agent in dependents
            }
        elif dependents is None:
            agents = {}
        else:
            raise ValueError(f"Invalid type for dependents: {type(dependents)}")

        # Step 2: Replace agent outputs
        def replace_agent(match):
            holder = match.group(1)
            key = holder
            value = 'output'
            if "." in holder:
                key, value = holder.split(".")
            agent = agents.get(key)
            if agent and hasattr(agent, "output"):
                return str(agents[key].output.to_dict()[value])
            return match.group(0)  # leave untouched

        # Step 3: Replace context variables
        def replace_context(match):
            key = match.group(1)
            if key in context:
                return str(context[key])
            return match.group(0)  # leave untouched

        # First, replace agent outputs
        description = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)}", replace_agent, job.description)
        # Then, replace user args/placeholders
        description = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*)}", replace_context, description)

        job.description = description
        return job
