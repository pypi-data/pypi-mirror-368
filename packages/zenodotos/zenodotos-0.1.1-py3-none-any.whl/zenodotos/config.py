"""Enhanced configuration management for Zenodotos."""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from .exceptions import ConfigurationError


@dataclass
class ZenodotosConfig:
    """Configuration settings for Zenodotos library and CLI."""

    # Authentication settings
    credentials_path: Optional[str] = None
    token_path: Optional[str] = None

    # API settings
    page_size: int = 10
    max_retries: int = 3
    timeout_seconds: int = 30

    # Export settings
    default_export_format: str = "auto"
    export_directory: Optional[str] = None

    # Display settings
    default_fields: list = field(
        default_factory=lambda: [
            "id",
            "name",
            "mimeType",
            "size",
            "createdTime",
            "modifiedTime",
        ]
    )
    max_display_width: int = 120

    # Cache settings
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour

    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Development settings
    debug_mode: bool = False
    verbose_output: bool = False


class Config:
    """Enhanced configuration management for Zenodotos."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration with optional config file path.

        Args:
            config_file: Optional path to configuration file (YAML/TOML/JSON)
        """
        self.config_dir = Path.home() / ".config" / "zenodotos"
        self.config_file = (
            Path(config_file) if config_file else self.config_dir / "config.yaml"
        )

        # Initialize with defaults
        self._config = ZenodotosConfig()

        # Load configuration from various sources (in order of precedence)
        self._load_configuration()

        # Validate configuration
        self._validate_configuration()

        # Backward compatibility attributes
        self.credentials_file = Path(self.get_credentials_path())
        self.token_file = Path(self.get_token_path())

    def _load_configuration(self):
        """Load configuration from multiple sources in order of precedence:
        1. Environment variables (highest priority)
        2. Configuration file
        3. Default values (lowest priority)
        """
        # Load from configuration file first
        self._load_from_file()

        # Override with environment variables
        self._load_from_environment()

    def _load_from_file(self):
        """Load configuration from file (YAML/TOML/JSON)."""
        if not self.config_file.exists():
            return

        try:
            file_ext = self.config_file.suffix.lower()

            if file_ext == ".yaml" or file_ext == ".yml":
                self._load_yaml_config()
            elif file_ext == ".toml":
                self._load_toml_config()
            elif file_ext == ".json":
                self._load_json_config()
            else:
                raise ConfigurationError(
                    f"Unsupported configuration file format: {file_ext}"
                )

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file: {e}")

    def _load_yaml_config(self):
        """Load configuration from YAML file."""
        try:
            import yaml

            with open(self.config_file, "r") as f:
                config_data = yaml.safe_load(f) or {}
                self._update_config_from_dict(config_data)
        except ImportError:
            raise ConfigurationError("PyYAML is required for YAML configuration files")

    def _load_toml_config(self):
        """Load configuration from TOML file."""
        import tomllib

        with open(self.config_file, "rb") as f:
            config_data = tomllib.load(f)
            self._update_config_from_dict(config_data)

    def _load_json_config(self):
        """Load configuration from JSON file."""
        with open(self.config_file, "r") as f:
            config_data = json.load(f)
            self._update_config_from_dict(config_data)

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        env_mappings = {
            "ZENODOTOS_CREDENTIALS_PATH": "credentials_path",
            "ZENODOTOS_TOKEN_PATH": "token_path",
            "ZENODOTOS_PAGE_SIZE": "page_size",
            "ZENODOTOS_MAX_RETRIES": "max_retries",
            "ZENODOTOS_TIMEOUT_SECONDS": "timeout_seconds",
            "ZENODOTOS_DEFAULT_EXPORT_FORMAT": "default_export_format",
            "ZENODOTOS_EXPORT_DIRECTORY": "export_directory",
            "ZENODOTOS_MAX_DISPLAY_WIDTH": "max_display_width",
            "ZENODOTOS_ENABLE_CACHE": "enable_cache",
            "ZENODOTOS_CACHE_TTL_SECONDS": "cache_ttl_seconds",
            "ZENODOTOS_LOG_LEVEL": "log_level",
            "ZENODOTOS_LOG_FILE": "log_file",
            "ZENODOTOS_DEBUG_MODE": "debug_mode",
            "ZENODOTOS_VERBOSE_OUTPUT": "verbose_output",
        }

        for env_var, config_attr in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert value to appropriate type
                converted_value = self._convert_env_value(value, config_attr)
                setattr(self._config, config_attr, converted_value)

    def _convert_env_value(self, value: str, config_attr: str) -> Any:
        """Convert environment variable string to appropriate type."""
        if config_attr in [
            "page_size",
            "max_retries",
            "timeout_seconds",
            "max_display_width",
            "cache_ttl_seconds",
        ]:
            return int(value)
        elif config_attr in ["enable_cache", "debug_mode", "verbose_output"]:
            return value.lower() in ["true", "1", "yes", "on"]
        else:
            return value

    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in config_data.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def _validate_configuration(self):
        """Validate configuration values."""
        if self._config.page_size < 1 or self._config.page_size > 1000:
            raise ConfigurationError("page_size must be between 1 and 1000")

        if self._config.max_retries < 0 or self._config.max_retries > 10:
            raise ConfigurationError("max_retries must be between 0 and 10")

        if self._config.timeout_seconds < 1 or self._config.timeout_seconds > 300:
            raise ConfigurationError("timeout_seconds must be between 1 and 300")

        if self._config.max_display_width < 40 or self._config.max_display_width > 500:
            raise ConfigurationError("max_display_width must be between 40 and 500")

        if self._config.cache_ttl_seconds < 0 or self._config.cache_ttl_seconds > 86400:
            raise ConfigurationError("cache_ttl_seconds must be between 0 and 86400")

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self._config.log_level.upper() not in valid_log_levels:
            raise ConfigurationError(
                f"log_level must be one of: {', '.join(valid_log_levels)}"
            )

    def ensure_config_dir(self):
        """Ensure the configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_credentials_path(self) -> str:
        """Get the path to the credentials file."""
        if self._config.credentials_path:
            return self._config.credentials_path

        # Fall back to environment variable
        env_path = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
        if env_path:
            return env_path

        # Default path
        return str(self.config_dir / "credentials.json")

    def get_token_path(self) -> str:
        """Get the path to the token file."""
        if self._config.token_path:
            return self._config.token_path
        return str(self.config_dir / "token.json")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return getattr(self._config, key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        if hasattr(self._config, key):
            setattr(self._config, key, value)
        else:
            raise ConfigurationError(f"Unknown configuration key: {key}")

    def save_config(self, file_path: Optional[str] = None):
        """Save current configuration to file.

        Args:
            file_path: Optional path to save configuration. If not provided,
                      saves to the default config file location.
        """
        save_path = Path(file_path) if file_path else self.config_file
        self.ensure_config_dir()

        # Convert config to dictionary
        config_dict = {
            "credentials_path": self._config.credentials_path,
            "token_path": self._config.token_path,
            "page_size": self._config.page_size,
            "max_retries": self._config.max_retries,
            "timeout_seconds": self._config.timeout_seconds,
            "default_export_format": self._config.default_export_format,
            "export_directory": self._config.export_directory,
            "default_fields": self._config.default_fields,
            "max_display_width": self._config.max_display_width,
            "enable_cache": self._config.enable_cache,
            "cache_ttl_seconds": self._config.cache_ttl_seconds,
            "log_level": self._config.log_level,
            "log_file": self._config.log_file,
            "debug_mode": self._config.debug_mode,
            "verbose_output": self._config.verbose_output,
        }

        # Remove None values
        config_dict = {k: v for k, v in config_dict.items() if v is not None}

        try:
            file_ext = save_path.suffix.lower()

            if file_ext == ".yaml" or file_ext == ".yml":
                self._save_yaml_config(config_dict, save_path)
            elif file_ext == ".toml":
                self._save_toml_config(config_dict, save_path)
            elif file_ext == ".json":
                self._save_json_config(config_dict, save_path)
            else:
                # Default to YAML
                self._save_yaml_config(config_dict, save_path.with_suffix(".yaml"))

        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration file: {e}")

    def _save_yaml_config(self, config_dict: Dict[str, Any], file_path: Path):
        """Save configuration to YAML file."""
        try:
            import yaml

            with open(file_path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        except ImportError:
            raise ConfigurationError("PyYAML is required for YAML configuration files")

    def _save_toml_config(self, config_dict: Dict[str, Any], file_path: Path):
        """Save configuration to TOML file."""
        import tomli_w

        with open(file_path, "wb") as f:
            tomli_w.dump(config_dict, f)

    def _save_json_config(self, config_dict: Dict[str, Any], file_path: Path):
        """Save configuration to JSON file."""
        with open(file_path, "w") as f:
            json.dump(config_dict, f, indent=2)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values as a dictionary."""
        return {
            "credentials_path": self.get_credentials_path(),
            "token_path": self.get_token_path(),
            "page_size": self.get("page_size"),
            "max_retries": self.get("max_retries"),
            "timeout_seconds": self.get("timeout_seconds"),
            "default_export_format": self.get("default_export_format"),
            "export_directory": self.get("export_directory"),
            "default_fields": self.get("default_fields"),
            "max_display_width": self.get("max_display_width"),
            "enable_cache": self.get("enable_cache"),
            "cache_ttl_seconds": self.get("cache_ttl_seconds"),
            "log_level": self.get("log_level"),
            "log_file": self.get("log_file"),
            "debug_mode": self.get("debug_mode"),
            "verbose_output": self.get("verbose_output"),
        }
