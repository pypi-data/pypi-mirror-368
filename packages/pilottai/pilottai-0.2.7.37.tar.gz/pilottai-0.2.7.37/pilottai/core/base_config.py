import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from cryptography.fernet import Fernet
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from pilottai.enums.type_e import AgentType
from pilottai.enums.process_e import ProcessType


class ServeConfig:
    """Configuration for Serve orchestrator"""
    process_type: ProcessType = ProcessType.SEQUENTIAL
    memory_enabled: bool = True
    verbose: bool = True
    max_concurrent_jobs: int = 5
    job_timeout: int = 300
    max_queue_size: int = 1000


class SecureConfig:
    """Handles secure storage and retrieval of sensitive config values"""

    def __init__(self, key_path: Optional[Path] = None):
        self._key_path = key_path
        if key_path and key_path.exists():
            self.key = key_path.read_bytes()
        else:
            self.key = Fernet.generate_key()
            if key_path:
                key_path.parent.mkdir(parents=True, exist_ok=True)
                key_path.write_bytes(self.key)
        self.cipher = Fernet(self.key)

    def encrypt(self, value: str) -> bytes:
        if not value:
            raise ValueError("Cannot encrypt empty value")
        return self.cipher.encrypt(value.encode())

    def decrypt(self, value: bytes) -> str:
        if not value:
            raise ValueError("Cannot decrypt empty value")
        return self.cipher.decrypt(value).decode()

    def cleanup(self):
        try:
            if self._key_path and self._key_path.exists():
                self._key_path.unlink()
        except Exception:
            pass

class LLMConfig(BaseModel):
    """Enhanced configuration for LLM integration"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True
    )

    model_name: str = "gpt-4o"
    provider: str = "openai"
    api_key: SecretStr
    temperature: float = Field(ge=0.0, le=1.0, default=0.0)
    max_tokens: int = Field(gt=0, default=2000)
    max_rpm: int = Field(gt=0, default=0)
    retry_delay: float = Field(gt=0, default=1.0)
    function_calling_model: Optional[str] = None
    system_template: Optional[str] = None
    prompt_template: Optional[str] = None
    retry_attempts: int = Field(ge=0, default=3)
    timeout: float = Field(gt=0, default=30.0)
    _secure_config: Optional[SecureConfig] = None

    def __init__(self, **data):
        super().__init__(**data)
        self._secure_config = SecureConfig()

    @field_validator('api_key')
    def encrypt_api_key(cls, v):
        if isinstance(v, str):
            return SecretStr(v)
        return v

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "provider": self.provider,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "function_calling_model": self.function_calling_model
        }


class LogConfig(BaseModel):
    """Enhanced logging configuration"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    verbose: bool = True
    log_to_file: bool = False
    log_dir: Path = Field(default=Path("logs"))
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    backup_count: int = Field(ge=0, default=5)
    log_rotation: str = Field(default="midnight")

    @field_validator('log_dir')
    def create_log_dir(cls, v):
        v = Path(v)
        try:
            v.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Failed to create log directory: {str(e)}")
        return v


class AgentConfig(BaseModel):
    """Enhanced configuration for agent initialization"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True
    )

    # Optional fields with defaults
    agent_type: AgentType = AgentType.WORKER
    knowledge_sources: List[str] = Field(default_factory=list)
    max_iterations: int = 20
    max_rpm: Optional[int] = None
    max_execution_time: Optional[int] = None
    retry_limit: int = 2
    code_execution_mode: str = "safe"
    verbose: bool = True
    can_delegate: bool = False
    use_cache: bool = True
    can_execute_code: bool = False
    max_child_agents: int = 10
    max_queue_size: int = 100
    max_job_complexity: int = 5
    delegation_threshold: float = 0.7
    max_concurrent_jobs: int = 5
    job_timeout: int = 300

    # Optional resource limits with defaults
    resource_limits: Dict[str, float] = Field(
        default_factory=lambda: {
            "cpu_percent": 80.0,
            "memory_percent": 80.0,
            "disk_percent": 80.0
        }
    )

    # Optional websocket settings
    websocket_enabled: bool = True
    websocket_host: str = "localhost"
    websocket_port: int = 8765

    @field_validator('resource_limits')
    def validate_resource_limits(cls, v):
        for key, value in v.items():
            if value <= 0 or value > 100:
                raise ValueError(f"Resource limit {key} must be between 0 and 100")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary with type handling"""
        return {
            "title": str(self.title),
            "agent_type": str(self.agent_type),
            "goal": str(self.goal),
            "description": str(self.description),
            "backstory": str(self.backstory) if self.backstory else None,
            "knowledge_sources": list(self.knowledge_sources),
            "tools": list(self.tools),
            "required_capabilities": list(self.required_capabilities),
            "max_iterations": int(self.max_iterations),
            "max_rpm": int(self.max_rpm) if self.max_rpm else None,
            "max_execution_time": int(self.max_execution_time) if self.max_execution_time else None,
            "retry_limit": int(self.retry_limit),
            "code_execution_mode": str(self.code_execution_mode),
            "memory_enabled": bool(self.memory_enabled),
            "verbose": bool(self.verbose),
            "can_delegate": bool(self.can_delegate),
            "use_cache": bool(self.use_cache),
            "can_execute_code": bool(self.can_execute_code),
            "max_child_agents": int(self.max_child_agents),
            "max_queue_size": int(self.max_queue_size),
            "max_job_complexity": int(self.max_job_complexity),
            "delegation_threshold": float(self.delegation_threshold),
            "max_concurrent_jobs": int(self.max_concurrent_jobs),
            "job_timeout": int(self.job_timeout),
            "resource_limits": dict(self.resource_limits),
            "websocket_enabled": bool(self.websocket_enabled),
            "websocket_host": str(self.websocket_host),
            "websocket_port": int(self.websocket_port)
        }

    @classmethod
    def from_file(cls, path: Path) -> 'AgentConfig':
        """Load configuration from file with proper error handling"""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to load config: {str(e)}")

    @property
    def has_sensitive_data(self) -> bool:
        """Check if config contains sensitive data"""
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'auth']
        dict_data = self.to_dict()
        return any(
            pattern in str(value).lower() or pattern in str(key).lower()
            for pattern in sensitive_patterns
            for key, value in dict_data.items()
        )

    def save_to_file(self, path: Path):
        """Save configuration to file with backup"""
        path = Path(path)
        backup_path = None

        try:
            # Create backup if file exists
            if path.exists():
                backup_path = path.with_suffix('.bak')
                shutil.copy2(path, backup_path)

            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            # Save new config
            with open(path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)

            # Remove backup if everything succeeded
            if backup_path and backup_path.exists():
                backup_path.unlink()

        except Exception as e:
            # Restore backup if save failed
            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, path)
            raise ValueError(f"Failed to save config: {str(e)}")


class RouterConfig(BaseModel):
    load_check_interval: int = Field(ge=1, default=5)
    max_queue_size: int = Field(gt=0, default=100)
    routing_timeout: int = Field(gt=0, default=30)
    max_retry_attempts: int = Field(ge=0, default=3)
    load_threshold: float = Field(ge=0.0, le=1.0, default=0.8)


class LoadBalancerConfig(BaseModel):
    check_interval: int = Field(ge=1, default=30)
    overload_threshold: float = Field(ge=0.0, le=1.0, default=0.8)
    underload_threshold: float = Field(ge=0.0, le=1.0, default=0.2)
    max_jobs_per_agent: int = Field(ge=1, default=10)
    balance_batch_size: int = Field(ge=1, default=3)
    min_load_difference: float = Field(ge=0.0, le=1.0, default=0.3)
    metrics_retention_period: int = Field(ge=0, default=3600)
    job_move_timeout: int = Field(ge=1, default=30)


class ScalingConfig(BaseModel):
    scale_up_threshold: float = Field(ge=0.0, le=1.0, default=0.8)
    scale_down_threshold: float = Field(ge=0.0, le=1.0, default=0.3)
    min_agents: int = Field(ge=1, default=2)
    max_agents: int = Field(ge=1, default=10)
    cooldown_period: int = Field(ge=0, default=300)
    check_interval: int = Field(ge=1, default=60)
    scale_up_increment: int = Field(ge=1, default=1)
    scale_down_increment: int = Field(ge=1, default=1)
    metrics_retention_period: int = Field(ge=0, default=3600)


class FaultToleranceConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    health_check_interval: int = Field(ge=1, default=30)
    max_recovery_attempts: int = Field(ge=1, default=3)
    recovery_cooldown: int = Field(ge=0, default=300)
    heartbeat_timeout: int = Field(ge=1, default=60)
    resource_threshold: float = Field(ge=0.0, le=1.0, default=0.9)
    job_timeout: int = Field(ge=0, default=1800)
    error_threshold: int = Field(ge=0, default=5)
    metrics_retention: int = Field(ge=0, default=3600)
