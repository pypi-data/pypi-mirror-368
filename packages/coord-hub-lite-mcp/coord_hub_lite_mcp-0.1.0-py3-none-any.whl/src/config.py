"""Configuration management for Coord-Hub-Lite server."""
from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server configuration
    host: str = Field(default="127.0.0.1", description="Server host address")
    port: int = Field(default=8000, description="Server port", ge=1, le=65535)
    workers: int = Field(default=1, description="Number of worker processes", ge=1)
    
    # Database configuration
    database_url: str = Field(
        default="sqlite+aiosqlite:///coord_hub_lite.db",
        description="Database connection URL"
    )
    
    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Environment configuration
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        description="Deployment environment"
    )
    
    # Debug mode
    debug: bool = Field(default=True, description="Enable debug mode")
    
    # Prometheus metrics
    prometheus_port: int = Field(
        default=9000,
        description="Port for Prometheus metrics endpoint",
        ge=1,
        le=65535
    )
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @field_validator("port", "prometheus_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range."""
        if not 1 <= v <= 65535:
            raise ValueError(f"Port must be between 1 and 65535, got {v}")
        return v
    
    @field_validator("workers")
    @classmethod
    def validate_workers(cls, v: int) -> int:
        """Validate worker count is positive."""
        if v < 1:
            raise ValueError(f"Workers must be at least 1, got {v}")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}, got {v}")
        return v
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is valid."""
        valid_envs = ["development", "staging", "production", "test"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}, got {v}")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings: Application settings
        
    Note:
        This function is cached to ensure settings are only loaded once.
        Call get_settings.cache_clear() to reload settings.
    """
    return Settings()