import asyncio
import weakref
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

import psutil
from aiohttp._websocket.reader_c import deque

from pilottai.agent.agent import Agent
from pilottai.job.job import Job
from pilottai.enums.health_e import HealthStatus
from pilottai.config.model import ScalingMetrics, AgentHealth
from pilottai.core.base_config import FaultToleranceConfig, ScalingConfig
from pilottai.utils.logger import Logger


class FaultTolerance:
    def __init__(self, orchestrator, config: Optional[Dict] = None):
        self.orchestrator = weakref.proxy(orchestrator)
        self.config = FaultToleranceConfig(**(config or {}))
        self.health_status: Dict[str, AgentHealth] = {}
        self.recovery_history: Dict[str, List[Dict]] = {}
        self.running = False
        self.monitoring_job: Optional[asyncio.Task] = None
        self.logger = Logger("FaultTolerance")
        self._health_lock = asyncio.Lock()
        self._monitored_agents: Set[str] = set()
        self._setup_logging()

    async def start(self):
        if self.running:
            self.logger.warning("Fault tolerance monitoring is already running")
            return

        try:
            self.running = True
            self.monitoring_job = asyncio.create_task(self._monitoring_loop())
            self.logger.info("Fault tolerance monitoring started")
        except Exception as e:
            self.running = False
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            raise


    def _setup_logging(self):
        """Setup logging for fault tolerance"""
        self.logger.setLevel(self.logger.DEBUG if self.orchestrator.verbose else self.logger.INFO)
        if not self.logger.handlers:
            handler = self.logger.StreamHandler()
            handler.setFormatter(
                self.logger.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(handler)

    async def stop(self):
        if not self.running:
            return
        try:
            self.running = False
            if self.monitoring_job:
                self.monitoring_job.cancel()
                try:
                    await self.monitoring_job
                except asyncio.CancelledError:
                    pass
            self.logger.info("Fault tolerance monitoring stopped")
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {str(e)}")

    async def register_agent(self, agent_id: str):
        """Register a new agent for monitoring"""
        async with self._health_lock:
            if agent_id not in self._monitored_agents:
                self._monitored_agents.add(agent_id)
                self.health_status[agent_id] = AgentHealth(
                    status=HealthStatus.HEALTHY,
                    last_heartbeat=datetime.now(),
                    resource_usage=0.0,
                    error_count=0,
                    recovery_attempts=0,
                    stuck_jobs=[]
                )

    async def unregister_agent(self, agent_id: str):
        """Unregister an agent from monitoring"""
        async with self._health_lock:
            self._monitored_agents.discard(agent_id)
            self.health_status.pop(agent_id, None)

    async def _monitoring_loop(self):
        while self.running:
            try:
                async with self._health_lock:
                    await self._check_system_health()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(self.config.health_check_interval)

    async def _check_system_health(self):
        for agent_id in list(self._monitored_agents):
            try:
                agent = self.orchestrator.child_agents.get(agent_id)
                if not agent:
                    await self.unregister_agent(agent_id)
                    continue

                health_status = await self._check_agent_health(agent)
                if health_status.status != HealthStatus.HEALTHY:
                    await self._handle_unhealthy_agent(agent, health_status)

            except Exception as e:
                self.logger.error(f"Health check failed for agent {agent_id}: {str(e)}")

    async def _check_agent_health(self, agent) -> AgentHealth:
        try:
            # Check heartbeat
            heartbeat_ok = await self._check_heartbeat(agent)

            # Check resource usage
            metrics = await agent.get_metrics()
            resource_usage = max(
                metrics.get('cpu_usage', 0),
                metrics.get('memory_usage', 0)
            )

            # Check stuck job
            stuck_jobs = await self._check_stuck_jobs(agent)

            # Get error count
            error_count = metrics.get('error_count', 0)

            # Determine status
            status = self._determine_health_status(
                heartbeat_ok,
                resource_usage,
                len(stuck_jobs),
                error_count
            )

            return AgentHealth(
                status=status,
                last_heartbeat=datetime.now() if heartbeat_ok else self.health_status[agent.id].last_heartbeat,
                resource_usage=resource_usage,
                error_count=error_count,
                recovery_attempts=self.health_status[agent.id].recovery_attempts,
                stuck_jobs=stuck_jobs,
                last_error=metrics.get('last_error')
            )

        except Exception as e:
            self.logger.error(f"Health check error for {agent.id}: {str(e)}")
            return AgentHealth(
                status=HealthStatus.CRITICAL,
                last_heartbeat=self.health_status[agent.id].last_heartbeat,
                resource_usage=1.0,
                error_count=self.health_status[agent.id].error_count + 1,
                recovery_attempts=self.health_status[agent.id].recovery_attempts,
                stuck_jobs=[],
                last_error=str(e)
            )

    def _determine_health_status(
            self,
            heartbeat_ok: bool,
            resource_usage: float,
            stuck_jobs: int,
            error_count: int
    ) -> HealthStatus:
        if not heartbeat_ok:
            return HealthStatus.CRITICAL

        if resource_usage > self.config.resource_threshold:
            return HealthStatus.CRITICAL

        if stuck_jobs > 0:
            return HealthStatus.DEGRADED

        if error_count > self.config.error_threshold:
            return HealthStatus.UNHEALTHY

        return HealthStatus.HEALTHY

    async def _check_heartbeat(self, agent) -> bool:
        try:
            last_heartbeat = await agent.send_heartbeat()
            timeout = timedelta(seconds=self.config.heartbeat_timeout)
            return datetime.now() - last_heartbeat < timeout
        except:
            return False

    async def _check_stuck_jobs(self, agent) -> List[str]:
        stuck_jobs = []
        try:
            for job_id, job in agent.jobs.items():
                if self._is_job_stuck(job):
                    stuck_jobs.append(job_id)
        except Exception as e:
            self.logger.error(f"Error checking stuck job: {str(e)}")
        return stuck_jobs

    def _is_job_stuck(self, job: Dict) -> bool:
        if job.get('status') not in ['completed', 'failed']:
            created_time = datetime.fromisoformat(job['created_at'])
            return (datetime.now() - created_time).total_seconds() > self.config.job_timeout
        return False

    async def _handle_unhealthy_agent(self, agent, health_status: AgentHealth):
        try:
            if await self._should_attempt_recovery(agent.id):
                await self._recover_agent(agent, health_status)
            else:
                await self._replace_agent(agent, health_status)
        except Exception as e:
            self.logger.error(f"Failed to handle unhealthy agent {agent.id}: {str(e)}")

    async def _should_attempt_recovery(self, agent_id: str) -> bool:
        health = self.health_status[agent_id]
        if health.recovery_attempts >= self.config.max_recovery_attempts:
            return False

        if health.status == HealthStatus.CRITICAL:
            return False

        last_recovery = next(
            (r['timestamp'] for r in reversed(self.recovery_history.get(agent_id, []))),
            datetime.min
        )

        cooldown = timedelta(seconds=self.config.recovery_cooldown)
        return datetime.now() - last_recovery > cooldown

    async def _recover_agent(self, agent, health_status: AgentHealth):
        """Attempt to recover an agent"""
        try:
            self.logger.info(f"Attempting recovery of agent {agent.id}")

            # Record recovery attempt
            health_status.recovery_attempts += 1
            self.health_status[agent.id] = health_status

            self._record_recovery_attempt(agent.id, "started")

            # Stop agent
            await agent.stop()

            # Reset agent state
            await agent.reset()

            # Restart agent
            await agent.start()

            # Verify recovery
            new_health = await self._check_agent_health(agent)
            if new_health.status == HealthStatus.HEALTHY:
                self._record_recovery_attempt(agent.id, "success")
                self.logger.info(f"Successfully recovered agent {agent.id}")
            else:
                self._record_recovery_attempt(agent.id, "failed")
                raise Exception(f"Recovery verification failed: {new_health.status}")

        except Exception as e:
            self.logger.error(f"Recovery failed for {agent.id}: {str(e)}")
            if health_status.recovery_attempts >= self.config.max_recovery_attempts:
                await self._replace_agent(agent, health_status)

    def _record_recovery_attempt(self, agent_id: str, status: str):
        if agent_id not in self.recovery_history:
            self.recovery_history[agent_id] = []

        self.recovery_history[agent_id].append({
            'timestamp': datetime.now(),
            'status': status,
            'health_status': self.health_status[agent_id].model_dump()
        })

    async def _replace_agent(self, agent, health_status: AgentHealth):
        """Replace a failed agent"""
        try:
            self.logger.info(f"Replacing failed agent {agent.id}")

            # Create new agent
            new_agent = await self.orchestrator.create_agent(
                title=agent.config.title,
                agent_type=agent.config.agent_type
            )

            if not new_agent:
                raise Exception("Failed to create replacement agent")

            # Move recoverable job
            await self._transfer_jobs(agent, new_agent)

            # Remove old agent
            await self.unregister_agent(agent.id)
            await self.orchestrator.remove_child_agent(agent.id)

            # Register and add new agent
            await self.register_agent(new_agent.id)
            await self.orchestrator.add_child_agent(new_agent)

            self.logger.info(f"Successfully replaced agent {agent.id} with {new_agent.id}")

        except Exception as e:
            self.logger.error(f"Agent replacement failed: {str(e)}")
            raise

    async def _transfer_jobs(self, old_agent, new_agent):
        """Transfer recoverable job to new agent"""
        try:
            recoverable_jobs = [
                job for job in old_agent.jobs.values()
                if self._is_job_recoverable(job)
            ]

            for job in recoverable_jobs:
                try:
                    await new_agent.add_job(job)
                except Exception as e:
                    self.logger.error(f"Failed to transfer job {job['id']}: {str(e)}")

            self.logger.info(f"Transferred {len(recoverable_jobs)} job to new agent")

        except Exception as e:
            self.logger.error(f"Job transfer failed: {str(e)}")
            raise

    def _is_job_recoverable(self, job: Dict) -> bool:
        return (
                job['status'] in ['pending', 'in_progress'] and
                not job.get('non_recoverable', False)
        )

    def get_health_metrics(self) -> Dict:
        """Get current health metrics"""
        return {
            'agent_health': {
                agent_id: health.model_dump()
                for agent_id, health in self.health_status.items()
            },
            'recovery_history': self.recovery_history,
            'monitored_agents': len(self._monitored_agents)
        }

    async def _check_resource_usage(self, agent: Agent) -> bool:
        """Check if agent's resource usage is within limits"""
        try:
            # TODO get metrics for agent ops
            metrics = await agent.get_metrics()
            usage = metrics.get('resource_usage', 0)
            is_within_limits = usage < self.config.resource_threshold
            if not is_within_limits:
                self.logger.warning(f"Agent {agent.id} resource usage too high: {usage:.2f}")
            return is_within_limits
        except Exception as e:
            self.logger.error(f"Resource check failed for {agent.id}: {str(e)}")
            return False

    async def _check_job_progress(self, agent: Agent) -> bool:
        """Check if agent is making progress on job"""
        try:
            stuck_jobs = [job for job in agent.jobs.values()
                           if self._is_job_stuck(job)]
            progress_ok = len(stuck_jobs) == 0
            if not progress_ok:
                self.logger.warning(f"Agent {agent.id} has {len(stuck_jobs)} stuck job")
            return progress_ok
        except Exception as e:
            self.logger.error(f"Job progress check failed for {agent.id}: {str(e)}")
            return False

    def _get_recoverable_jobs(self, agent: Agent) -> List[Job]:
        """Get job that can be recovered"""
        return [
            job for job in agent.jobs.values()
            if job['status'] in ['queued', 'in_progress']
               and not job.get('non_recoverable', False)
        ]

class DynamicScaling:
    def __init__(self, orchestrator, config: Optional[Dict] = None):
        self.orchestrator = weakref.proxy(orchestrator)
        self.config = ScalingConfig(**(config or {}))
        self.logger = Logger("DynamicScaling")
        self.running = False
        self.scaling_job: Optional[asyncio.Task] = None
        self.metrics_history: deque = deque(maxlen=60)
        self.last_scale_time = datetime.now()
        self._scaling_lock = asyncio.Lock()
        self._setup_logging()

    def _setup_logging(self):
        self.logger.setLevel(self.logger.DEBUG if self.orchestrator.verbose else self.logger.INFO)
        if not self.logger.handlers:
            handler = self.logger.StreamHandler()
            handler.setFormatter(
                self.logger.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(handler)

    async def start(self):
        if self.running:
            return

        try:
            self.running = True
            #TODO create job
            self.scaling_job = asyncio.create_job(self._scaling_loop())
            self.logger.info("Dynamic scaling started")
        except Exception as e:
            self.running = False
            self.logger.error(f"Failed to start dynamic scaling: {str(e)}")
            raise

    async def stop(self):
        if not self.running:
            return

        try:
            self.running = False
            if self.scaling_job:
                self.scaling_job.cancel()
                try:
                    await self.scaling_job
                except asyncio.CancelledError:
                    pass
            self.logger.info("Dynamic scaling stopped")
        except Exception as e:
            self.logger.error(f"Error stopping dynamic scaling: {str(e)}")

    async def _scaling_loop(self):
        while self.running:
            try:
                async with self._scaling_lock:
                    await self._check_and_adjust_scale()
                await asyncio.sleep(self.config.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in scaling loop: {str(e)}")
                await asyncio.sleep(self.config.check_interval)

    async def _check_and_adjust_scale(self):
        try:
            current_metrics = await self._get_system_metrics()
            self._update_metrics_history(current_metrics)

            if not self._can_scale():
                return

            trend = self._analyze_load_trend()
            if trend > self.config.scale_up_threshold:
                await self._scale_up()
            elif trend < self.config.scale_down_threshold:
                await self._scale_down()

        except Exception as e:
            self.logger.error(f"Error adjusting scale: {str(e)}")

    async def _get_system_metrics(self) -> ScalingMetrics:
        try:
            agent_metrics = await asyncio.gather(*[
                agent.get_metrics()
                for agent in self.orchestrator.child_agents.values()
            ])

            num_agents = len(self.orchestrator.child_agents)
            if num_agents == 0:
                return ScalingMetrics(
                    timestamp=datetime.now(),
                    load=0.0,
                    num_agents=0,
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    queue_size=0
                )

            total_queue_size = sum(m.get('queue_size', 0) for m in agent_metrics)
            avg_queue_util = sum(m.get('queue_utilization', 0) for m in agent_metrics) / num_agents

            cpu_usage = psutil.cpu_percent() / 100
            memory_usage = psutil.virtual_memory().percent / 100

            load = min(1.0,
                      0.35 * avg_queue_util +
                      0.25 * cpu_usage +
                      0.25 * memory_usage +
                      0.15 * (total_queue_size / (num_agents * 100)))

            return ScalingMetrics(
                timestamp=datetime.now(),
                load=load,
                num_agents=num_agents,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                queue_size=total_queue_size
            )

        except Exception as e:
            self.logger.error(f"Error getting system metrics: {str(e)}")
            raise

    def _update_metrics_history(self, metrics: ScalingMetrics):
        cutoff = datetime.now() - timedelta(seconds=self.config.metrics_retention_period)
        self.metrics_history = deque(
            [m for m in self.metrics_history if m.timestamp > cutoff],
            maxlen=60
        )
        self.metrics_history.append(metrics)

    def _analyze_load_trend(self) -> float:
        if len(self.metrics_history) < 5:
            return 0.0

        recent_metrics = list(self.metrics_history)[-5:]
        weighted_sum = sum(
            m.load * (i + 1)
            for i, m in enumerate(recent_metrics)
        )
        weight_sum = sum(range(1, len(recent_metrics) + 1))
        return weighted_sum / weight_sum

    async def _scale_up(self):
        current_agents = len(self.orchestrator.child_agents)
        if current_agents >= self.config.max_agents:
            return

        try:
            agents_to_add = min(
                self.config.scale_up_increment,
                self.config.max_agents - current_agents
            )

            for _ in range(agents_to_add):
                new_agent = await self.orchestrator.create_agent()
                if new_agent:
                    await self.orchestrator.add_child_agent(new_agent)

            self.last_scale_time = datetime.now()
            self.logger.info(f"Scaled up by {agents_to_add} agents")

        except Exception as e:
            self.logger.error(f"Error scaling up: {str(e)}")
            raise

    async def _scale_down(self):
        current_agents = len(self.orchestrator.child_agents)
        if current_agents <= self.config.min_agents:
            return

        try:
            agents_to_remove = min(
                self.config.scale_down_increment,
                current_agents - self.config.min_agents
            )

            removed = 0
            for _ in range(agents_to_remove):
                idle_agent = await self._find_idle_agent()
                if idle_agent:
                    await self._safely_remove_agent(idle_agent)
                    removed += 1

            if removed > 0:
                self.last_scale_time = datetime.now()
                self.logger.info(f"Scaled down by {removed} agents")

        except Exception as e:
            self.logger.error(f"Error scaling down: {str(e)}")
            raise

    async def _safely_remove_agent(self, agent):
        try:
            await agent.wait_for_jobs()
            await agent.stop()
            await self.orchestrator.remove_child_agent(agent.id)
        except Exception as e:
            self.logger.error(f"Error removing agent {agent.id}: {str(e)}")
            raise

    def _can_scale(self) -> bool:
        if not self.running:
            return False
        return (datetime.now() - self.last_scale_time).seconds > self.config.cooldown_period

    async def _find_idle_agent(self):
        try:
            idle_agents = []
            for agent in self.orchestrator.child_agents.values():
                metrics = await agent.get_metrics()
                if (
                    agent.status == 'idle' and
                    metrics['queue_size'] == 0 and
                    metrics['active_jobs'] == 0
                ):
                    idle_agents.append((agent, metrics['success_rate']))

            if not idle_agents:
                return None

            return min(idle_agents, key=lambda x: x[1])[0]

        except Exception as e:
            self.logger.error(f"Error finding idle agent: {str(e)}")
            return None

    async def get_scaling_metrics(self) -> Dict:
        try:
            current_metrics = await self._get_system_metrics()
            trend = self._analyze_load_trend()

            return {
                'current_metrics': current_metrics.model_dump(),
                'load_trend': trend,
                'history': [m.model_dump() for m in self.metrics_history],
                'last_scale_time': self.last_scale_time.isoformat(),
                'can_scale_up': len(self.orchestrator.child_agents) < self.config.max_agents,
                'can_scale_down': len(self.orchestrator.child_agents) > self.config.min_agents
            }
        except Exception as e:
            self.logger.error(f"Error getting scaling metrics: {str(e)}")
            return {}
