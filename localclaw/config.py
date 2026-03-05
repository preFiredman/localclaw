"""Configuration management"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager"""
    
    DEFAULT_CONFIG_PATH = Path("config.yaml")
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            return self._default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "model": {
                "name": "qwen2.5:7b",
                "base_url": "http://localhost:11434/v1",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            "memory": {
                "db_path": "./memory_db",
                "collection_name": "localclaw_memory"
            },
            "workspace": {
                "path": "./workspace",
                "restrict_to_workspace": True
            },
            "system_prompt": "You are LocalClaw, a helpful local AI assistant."
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    @property
    def model_name(self) -> str:
        return self.get("model.name", "qwen2.5:7b")
    
    @property
    def model_base_url(self) -> str:
        return self.get("model.base_url", "http://localhost:11434/v1")
    
    @property
    def model_temperature(self) -> float:
        return self.get("model.temperature", 0.7)
    
    @property
    def model_max_tokens(self) -> int:
        return self.get("model.max_tokens", 4096)
    
    @property
    def memory_db_path(self) -> str:
        return self.get("memory.db_path", "./memory_db")
    
    @property
    def workspace_path(self) -> str:
        return self.get("workspace.path", "./workspace")
    
    @property
    def restrict_to_workspace(self) -> bool:
        return self.get("workspace.restrict_to_workspace", True)
    
    @property
    def system_prompt(self) -> str:
        return self.get("system_prompt", "You are LocalClaw, a helpful assistant.")
