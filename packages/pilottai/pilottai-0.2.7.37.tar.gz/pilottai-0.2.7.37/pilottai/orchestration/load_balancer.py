import asyncio
import weakref
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set, Any

import psutil

from pilottai.agent.agent import Agent
from pilottai.enums.agent_e import AgentStatus

from pilottai.config.model import LoadMetrics
from pilottai.core.base_config import LoadBalancerConfig
from pilottai.utils.logger import Logger


class LoadBalancer:
    def __init__(self, orchestrator, config: Optional[Dict] = None):
        self.orchestrator = weakref.proxy(orchestrator)
        self.config = LoadBalancerConfig(**(config or {}))
        self.logger = Logger("LoadBalancer")
        self.running = False
        self.balancing_job: Optional[asyncio.Task] = None
        self._balance_lock = asyncio.Lock()
        self._metrics_history: Dict[str, List[LoadMetrics]] = {}
        self._monitored_agents: Set[str] = set()
        self._last_balance_time = datetime.now()
        self._safe_mode = True
        self._setup_logging()

    async def start(self):
        if self.running:
            return
        try:
            self.running = True
            self.balancing_job = asyncio.create_task(self._balancing_loop())
            self.logger.info("Load balancer started")
        except Exception as e:
            self.running = False
            self.logger.error(f"Failed to start load balancer: {str(e)}")
            raise

    async def stop(self):
        if not self.running:
            return
        try:
            self.running = False
            if self.balancing_job:
                self.balancing_job.cancel()
                try:
                    await self.balancing_job
                except asyncio.CancelledError:
                    pass
            self.logger.info("Load balancer stopped")
        except Exception as e:
            self.logger.error(f"Error stopping load balancer: {str(e)}")

    async def _balancing_loop(self):
        while self.running:
            try:
                async with self._balance_lock:
                    await self._balance_system_load()
                await asyncio.sleep(self.config.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in balancing loop: {str(e)}")
                await asyncio.sleep(self.config.check_interval)

    async def _balance_system_load(self):
        try:
            current_metrics = await self._collect_system_metrics()
            self._update_metrics_history(current_metrics)
            overloaded, underloaded = await self._analyze_agent_loads(current_metrics)
            if not overloaded or not underloaded:
                return
            await self._redistribute_jobs(overloaded, underloaded, current_metrics)
        except Exception as e:
            self.logger.error(f"Load balancing error: {str(e)}")

    async def _collect_system_metrics(self) -> Dict[str, LoadMetrics]:
        metrics = {}
        for agent in await self._get_available_agents():
            try:
                # TODO get metrics for agent ops
                agent_metrics = await agent.get_metrics()
                system_cpu = psutil.cpu_percent(interval=1) / 100.0
                system_memory = psutil.virtual_memory().percent / 100.0

                metrics[agent.id] = LoadMetrics(
                    cpu_usage=max(system_cpu, agent_metrics.get('cpu_usage', 0.0)),
                    memory_usage=max(system_memory, agent_metrics.get('memory_usage', 0.0)),
                    queue_size=agent_metrics.get('queue_size', 0),
                    active_jobs=agent_metrics.get('active_jobs', 0),
                    total_jobs=agent_metrics.get('total_jobs', 0),
                    error_rate=1 - agent_metrics.get('success_rate', 0.0)
                )

                if metrics[agent.id].cpu_usage > self.config.overload_threshold or \
                   metrics[agent.id].memory_usage > self.config.overload_threshold:
                    await self._handle_overload(agent.id)

            except Exception as e:
                self.logger.error(f"Error collecting metrics for agent {agent.id}: {str(e)}")
        return metrics

    async def _handle_overload(self, agent_id: str):
        try:
            agent = self.orchestrator.child_agents[agent_id]
            await agent.pause_job_acceptance()
            self.logger.warning(f"Agent {agent_id} paused due to resource overload")
        except Exception as e:
            self.logger.error(f"Error handling overload for agent {agent_id}: {str(e)}")

    def _update_metrics_history(self, metrics: Dict[str, LoadMetrics]):
        current_time = datetime.now()
        retention_time = current_time - timedelta(seconds=self.config.metrics_retention_period)

        for agent_id, metric in metrics.items():
            if agent_id not in self._metrics_history:
                self._metrics_history[agent_id] = []

            self._metrics_history[agent_id].append(metric)
            self._metrics_history[agent_id] = [
                m for m in self._metrics_history[agent_id]
                if m.timestamp > retention_time
            ]

    async def _analyze_agent_loads(
            self,
            current_metrics: Dict[str, LoadMetrics]
    ) -> Tuple[List[str], List[str]]:
        overloaded = []
        underloaded = []

        for agent_id, metrics in current_metrics.items():
            load_trend = self._calculate_load_trend(agent_id)
            current_load = self._calculate_composite_load(metrics)

            if current_load > self.config.overload_threshold and load_trend > 0:
                overloaded.append(agent_id)
            elif current_load < self.config.underload_threshold and load_trend < 0:
                underloaded.append(agent_id)

        return overloaded, underloaded

    def _calculate_load_trend(self, agent_id: str) -> float:
        if agent_id not in self._metrics_history:
            return 0.0

        history = self._metrics_history[agent_id][-5:]
        if len(history) < 2:
            return 0.0

        loads = [self._calculate_composite_load(m) for m in history]
        return (loads[-1] - loads[0]) / len(loads)

    def _calculate_composite_load(self, metrics: LoadMetrics) -> float:
        return (
            0.3 * metrics.cpu_usage +
            0.3 * metrics.memory_usage +
            0.2 * (metrics.queue_size / self.config.max_jobs_per_agent) +
            0.2 * metrics.error_rate
        )

    async def _redistribute_jobs(
            self,
            overloaded: List[str],
            underloaded: List[str],
            current_metrics: Dict[str, LoadMetrics]
    ):
        for over_agent_id in overloaded:
            try:
                moveable_jobs = await self._get_moveable_jobs(over_agent_id)
                moves_made = 0

                moveable_jobs.sort(key=lambda x: x.get('priority', 0), reverse=True)

                for job in moveable_jobs:
                    if moves_made >= self.config.balance_batch_size:
                        break

                    best_agent_id = await self._find_best_agent(
                        job,
                        underloaded,
                        current_metrics
                    )

                    if best_agent_id:
                        try:
                            async with asyncio.timeout(self.config.job_move_timeout):
                                await self._move_job(job, over_agent_id, best_agent_id)
                                moves_made += 1
                        except asyncio.TimeoutError:
                            self.logger.error(f"Job move timed out for job {job['id']}")
                        except Exception as e:
                            self.logger.error(f"Failed to move job {job['id']}: {str(e)}")

                if moves_made > 0:
                    self._last_balance_time = datetime.now()
                    self.logger.info(f"Moved {moves_made} job from agent {over_agent_id}")

            except Exception as e:
                self.logger.error(f"Error redistributing job for agent {over_agent_id}: {str(e)}")

    async def _move_job(self, job: Dict, from_agent_id: str, to_agent_id: str):
        lock_acquired = False
        try:
            from_agent = self.orchestrator.child_agents[from_agent_id]
            to_agent = self.orchestrator.child_agents[to_agent_id]

            job['locked'] = True
            lock_acquired = True

            if self._safe_mode:
                # Save job state before moving
                job_backup = job.copy()

            await from_agent.remove_job(job['id'])
            await to_agent.add_job(job)

            job['moved_at'] = datetime.now().isoformat()
            job['moved_from'] = from_agent_id
            job['moved_to'] = to_agent_id

            self.logger.info(f"Moved job {job['id']} from {from_agent_id} to {to_agent_id}")

        except Exception as e:
            self.logger.error(f"Job movement failed: {str(e)}")
            if lock_acquired and self._safe_mode:
                try:
                    await from_agent.add_job(job_backup)
                except Exception as restore_error:
                    self.logger.error(f"Failed to restore job {job['id']}: {str(restore_error)}")
            raise
        finally:
            job['locked'] = False

    async def _get_moveable_jobs(self, agent_id: str) -> List[Dict]:
        try:
            agent = self.orchestrator.child_agents[agent_id]
            return [job for job in agent.jobs.values() if self._is_job_moveable(job)]
        except Exception as e:
            self.logger.error(f"Error getting moveable job: {str(e)}")
            return []

    def _is_job_moveable(self, job: Dict) -> bool:
        return (
            job.get('status') == 'pending' and
            not job.get('locked', False) and
            not job.get('unmoveable', False)
        )

    async def _find_best_agent(
            self,
            job: Dict,
            candidates: List[str],
            current_metrics: Dict[str, LoadMetrics]
    ) -> Optional[str]:
        best_agent_id = None
        best_score = float('-inf')

        for agent_id in candidates:
            try:
                agent = self.orchestrator.child_agents[agent_id]
                if not await self._can_accept_job(agent, current_metrics[agent_id]):
                    continue

                score = await self._calculate_agent_suitability(agent, job, current_metrics[agent_id])

                if score > best_score:
                    best_score = score
                    best_agent_id = agent_id

            except Exception as e:
                self.logger.error(f"Error calculating suitability for agent {agent_id}: {str(e)}")

        return best_agent_id

    async def _can_accept_job(
            self,
            agent: Any,
            metrics: LoadMetrics
    ) -> bool:
        """Check if agent can accept new job"""
        return (
            agent.status != 'stopped' and
            metrics.queue_size < self.config.max_jobs_per_agent and
            self._calculate_composite_load(metrics) < self.config.overload_threshold
        )

    async def _calculate_agent_suitability(
            self,
            agent: Any,
            job: Dict,
            metrics: LoadMetrics
    ) -> float:
        """Calculate comprehensive agent suitability score"""
        try:
            # Base capability score
            base_score = await agent.evaluate_job_suitability(job)

            # Load penalty
            load_score = 1 - self._calculate_composite_load(metrics)

            # Performance score
            perf_score = 1 - metrics.error_rate

            # Resource availability
            resource_score = 1 - max(metrics.cpu_usage, metrics.memory_usage)

            # Calculate weighted score
            return (
                    base_score * 0.4 +
                    load_score * 0.3 +
                    perf_score * 0.2 +
                    resource_score * 0.1
            )

        except Exception as e:
            self.logger.error(f"Error calculating agent suitability: {str(e)}")
            return float('-inf')

    async def get_metrics(self) -> Dict[str, Any]:
        return {
            "active_agents": len(await self._get_available_agents()),
            "overloaded_agents": len([
                agent_id for agent_id, metrics in (await self._collect_system_metrics()).items()
                if self._calculate_composite_load(metrics) > self.config.overload_threshold
            ]),
            "underloaded_agents": len([
                agent_id for agent_id, metrics in (await self._collect_system_metrics()).items()
                if self._calculate_composite_load(metrics) < self.config.underload_threshold
            ]),
            "last_balance_time": self._last_balance_time.isoformat(),
            "metrics_history": {
                agent_id: [m.model_dump() for m in history]
                for agent_id, history in self._metrics_history.items()
            }
        }

    def _setup_logging(self):
        self.logger.setLevel(self.logger.DEBUG if self.orchestrator.verbose else self.logger.INFO)
        if not self.logger.handlers:
            handler = self.logger.StreamHandler()
            handler.setFormatter(
                self.logger.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(handler)

    async def _get_available_agents(self) -> List[Agent]:
        return [
            agent for agent in self.orchestrator.child_agents.values()
            if agent.status != AgentStatus.STOPPED
        ]


    async def _calculate_agent_load(self, agent: Agent) -> float:
        """Calculate comprehensive load for an agent"""
        try:
            #TODO get metrics for agent ops
            metrics = await agent.get_metrics()
            # Calculate different types of load
            job_load = metrics['total_jobs'] / self.config.max_jobs_per_agent
            queue_load = metrics['queue_utilization']
            error_rate = 1 - metrics['success_rate']  # Convert success rate to error rate

            # Weighted average with error rate penalty
            base_load = (
                    0.4 * job_load +
                    0.4 * queue_load +
                    0.2 * error_rate
            )
            return min(1.0, base_load)  # Cap at 1.0

        except Exception as e:
            self.logger.error(f"Error calculating agent load: {str(e)}")
            return 0.0
