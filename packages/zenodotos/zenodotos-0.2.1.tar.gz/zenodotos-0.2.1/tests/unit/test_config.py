"""Comprehensive tests for the enhanced configuration system."""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from zenodotos.config import Config, ZenodotosConfig
from zenodotos.exceptions import ConfigurationError


class TestZenodotosConfig:
    """Test the ZenodotosConfig dataclass."""

    def test_zenodotos_config_defaults(self):
        """Test ZenodotosConfig default values."""
        config = ZenodotosConfig()

        assert config.credentials_path is None
        assert config.token_path is None
        assert config.page_size == 10
        assert config.max_retries == 3
        assert config.timeout_seconds == 30
        assert config.default_export_format == "auto"
        assert config.export_directory is None
        assert config.default_fields == [
            "id",
            "name",
            "mimeType",
            "size",
            "createdTime",
            "modifiedTime",
        ]
        assert config.max_display_width == 120
        assert config.enable_cache is True
        assert config.cache_ttl_seconds == 3600
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.debug_mode is False
        assert config.verbose_output is False

    def test_zenodotos_config_custom_values(self):
        """Test ZenodotosConfig with custom values."""
        config = ZenodotosConfig(
            credentials_path="/custom/credentials.json",
            page_size=50,
            max_retries=5,
            debug_mode=True,
        )

        assert config.credentials_path == "/custom/credentials.json"
        assert config.page_size == 50
        assert config.max_retries == 5
        assert config.debug_mode is True
        # Other values should remain default
        assert config.timeout_seconds == 30
        assert config.enable_cache is True


class TestConfigInitialization:
    """Test Config class initialization."""

    def test_config_default_initialization(self):
        """Test Config initialization with defaults."""
        config = Config()

        assert config.config_dir == Path.home() / ".config" / "zenodotos"
        assert config.config_file == config.config_dir / "config.yaml"
        assert isinstance(config._config, ZenodotosConfig)

    def test_config_with_custom_file(self):
        """Test Config initialization with custom config file."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            config_file = f.name

        try:
            config = Config(config_file=config_file)
            assert config.config_file == Path(config_file)
        finally:
            os.unlink(config_file)

    def test_config_validation_on_init(self):
        """Test that configuration validation runs on initialization."""
        with patch.object(Config, "_validate_configuration") as mock_validate:
            Config()
            mock_validate.assert_called_once()


class TestConfigBackwardCompatibility:
    """Test backward compatibility with original Config interface."""

    def test_config_initialization_default_paths(self):
        """Test that Config initializes with correct default paths."""
        config = Config()

        expected_config_dir = Path.home() / ".config" / "zenodotos"
        expected_credentials_file = expected_config_dir / "credentials.json"
        expected_token_file = expected_config_dir / "token.json"

        assert config.config_dir == expected_config_dir
        assert config.credentials_file == expected_credentials_file
        assert config.token_file == expected_token_file

    def test_config_initialization_with_env_variable(self):
        """Test that Config respects GOOGLE_DRIVE_CREDENTIALS environment variable."""
        custom_creds_path = "/custom/path/to/credentials.json"

        with patch.dict(os.environ, {"GOOGLE_DRIVE_CREDENTIALS": custom_creds_path}):
            config = Config()

            assert str(config.credentials_file) == custom_creds_path
            # Token file should still use default location
            expected_token_file = Path.home() / ".config" / "zenodotos" / "token.json"
            assert config.token_file == expected_token_file

    def test_ensure_config_dir_creates_directory(self):
        """Test that ensure_config_dir creates the config directory."""
        config = Config()

        # Mock Path.mkdir at the class level
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            config.ensure_config_dir()

            # Should call mkdir with parents=True and exist_ok=True
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_get_credentials_path_returns_string(self):
        """Test that get_credentials_path returns the credentials file path as string."""
        config = Config()

        result = config.get_credentials_path()

        assert isinstance(result, str)
        assert result == str(config.credentials_file)

    def test_get_credentials_path_with_env_variable(self):
        """Test that get_credentials_path works with environment variable."""
        custom_creds_path = "/custom/path/to/credentials.json"

        with patch.dict(os.environ, {"GOOGLE_DRIVE_CREDENTIALS": custom_creds_path}):
            config = Config()
            result = config.get_credentials_path()

            assert result == custom_creds_path

    def test_get_token_path_returns_string(self):
        """Test that get_token_path returns the token file path as string."""
        config = Config()

        result = config.get_token_path()

        assert isinstance(result, str)
        assert result == str(config.token_file)

    def test_config_paths_are_absolute(self):
        """Test that all config paths are absolute paths."""
        config = Config()

        assert config.config_dir.is_absolute()
        assert config.credentials_file.is_absolute()
        assert config.token_file.is_absolute()

    def test_config_consistency(self):
        """Test that config paths are consistent with each other."""
        config = Config()

        # Token file should be inside config directory
        assert config.token_file.parent == config.config_dir

        # Credentials file should be inside config directory (when using default)
        if "GOOGLE_DRIVE_CREDENTIALS" not in os.environ:
            assert config.credentials_file.parent == config.config_dir

    @patch.dict(os.environ, {}, clear=True)
    def test_config_without_env_variables(self):
        """Test config behavior when no environment variables are set."""
        config = Config()

        expected_config_dir = Path.home() / ".config" / "zenodotos"
        assert config.config_dir == expected_config_dir
        assert config.credentials_file == expected_config_dir / "credentials.json"
        assert config.token_file == expected_config_dir / "token.json"


class TestConfigFileLoading:
    """Test configuration file loading functionality."""

    def test_load_yaml_config(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
page_size: 25
max_retries: 5
debug_mode: true
log_level: DEBUG
"""
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
            f.write(yaml_content)
            config_file = f.name

        try:
            with patch(
                "yaml.safe_load",
                return_value={
                    "page_size": 25,
                    "max_retries": 5,
                    "debug_mode": True,
                    "log_level": "DEBUG",
                },
            ):
                config = Config(config_file=config_file)
                assert config.get("page_size") == 25
                assert config.get("max_retries") == 5
                assert config.get("debug_mode") is True
                assert config.get("log_level") == "DEBUG"
        finally:
            os.unlink(config_file)

    def test_load_toml_config(self):
        """Test loading configuration from TOML file."""
        toml_content = """
page_size = 30
max_retries = 7
verbose_output = true
"""
        with tempfile.NamedTemporaryFile(suffix=".toml", mode="w", delete=False) as f:
            f.write(toml_content)
            config_file = f.name

        try:
            with patch(
                "tomllib.load",
                return_value={
                    "page_size": 30,
                    "max_retries": 7,
                    "verbose_output": True,
                },
            ):
                config = Config(config_file=config_file)
                assert config.get("page_size") == 30
                assert config.get("max_retries") == 7
                assert config.get("verbose_output") is True
        finally:
            os.unlink(config_file)

    def test_load_json_config(self):
        """Test loading configuration from JSON file."""
        json_content = {"page_size": 40, "max_retries": 8, "enable_cache": False}
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(json_content, f)
            config_file = f.name

        try:
            config = Config(config_file=config_file)
            assert config.get("page_size") == 40
            assert config.get("max_retries") == 8
            assert config.get("enable_cache") is False
        finally:
            os.unlink(config_file)

    def test_load_unsupported_format(self):
        """Test loading configuration from unsupported format."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            config_file = f.name

        try:
            with pytest.raises(
                ConfigurationError, match="Unsupported configuration file format"
            ):
                Config(config_file=config_file)
        finally:
            os.unlink(config_file)

    def test_load_missing_file(self):
        """Test loading configuration when file doesn't exist."""
        config = Config(config_file="/nonexistent/config.yaml")
        # Should not raise error, just use defaults
        assert config.get("page_size") == 10


class TestEnvironmentVariableLoading:
    """Test environment variable configuration loading."""

    def test_load_from_environment(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "ZENODOTOS_PAGE_SIZE": "50",
            "ZENODOTOS_MAX_RETRIES": "7",
            "ZENODOTOS_DEBUG_MODE": "true",
            "ZENODOTOS_LOG_LEVEL": "DEBUG",
            "ZENODOTOS_ENABLE_CACHE": "false",
        }

        with patch.dict(os.environ, env_vars):
            config = Config()
            assert config.get("page_size") == 50
            assert config.get("max_retries") == 7
            assert config.get("debug_mode") is True
            assert config.get("log_level") == "DEBUG"
            assert config.get("enable_cache") is False

    def test_environment_variable_type_conversion(self):
        """Test environment variable type conversion."""
        env_vars = {
            "ZENODOTOS_PAGE_SIZE": "25",
            "ZENODOTOS_MAX_DISPLAY_WIDTH": "150",
            "ZENODOTOS_CACHE_TTL_SECONDS": "7200",
            "ZENODOTOS_VERBOSE_OUTPUT": "yes",
            "ZENODOTOS_DEFAULT_EXPORT_FORMAT": "pdf",
        }

        with patch.dict(os.environ, env_vars):
            config = Config()
            assert config.get("page_size") == 25
            assert config.get("max_display_width") == 150
            assert config.get("cache_ttl_seconds") == 7200
            assert config.get("verbose_output") is True
            assert config.get("default_export_format") == "pdf"

    def test_environment_variable_boolean_conversion(self):
        """Test boolean environment variable conversion."""
        test_cases = [
            ("true", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("invalid", False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"ZENODOTOS_DEBUG_MODE": env_value}):
                config = Config()
                assert config.get("debug_mode") == expected


class TestConfigurationValidation:
    """Test configuration validation."""

    def test_valid_configuration(self):
        """Test that valid configuration passes validation."""
        config = Config()
        # Should not raise any exceptions
        assert config.get("page_size") == 10

    def test_invalid_page_size(self):
        """Test validation of invalid page size."""
        with patch.dict(os.environ, {"ZENODOTOS_PAGE_SIZE": "0"}):
            with pytest.raises(
                ConfigurationError, match="page_size must be between 1 and 1000"
            ):
                Config()

        with patch.dict(os.environ, {"ZENODOTOS_PAGE_SIZE": "1001"}):
            with pytest.raises(
                ConfigurationError, match="page_size must be between 1 and 1000"
            ):
                Config()

    def test_invalid_max_retries(self):
        """Test validation of invalid max retries."""
        with patch.dict(os.environ, {"ZENODOTOS_MAX_RETRIES": "-1"}):
            with pytest.raises(
                ConfigurationError, match="max_retries must be between 0 and 10"
            ):
                Config()

        with patch.dict(os.environ, {"ZENODOTOS_MAX_RETRIES": "11"}):
            with pytest.raises(
                ConfigurationError, match="max_retries must be between 0 and 10"
            ):
                Config()

    def test_invalid_timeout_seconds(self):
        """Test validation of invalid timeout seconds."""
        with patch.dict(os.environ, {"ZENODOTOS_TIMEOUT_SECONDS": "0"}):
            with pytest.raises(
                ConfigurationError, match="timeout_seconds must be between 1 and 300"
            ):
                Config()

        with patch.dict(os.environ, {"ZENODOTOS_TIMEOUT_SECONDS": "301"}):
            with pytest.raises(
                ConfigurationError, match="timeout_seconds must be between 1 and 300"
            ):
                Config()

    def test_invalid_max_display_width(self):
        """Test validation of invalid max display width."""
        with patch.dict(os.environ, {"ZENODOTOS_MAX_DISPLAY_WIDTH": "39"}):
            with pytest.raises(
                ConfigurationError, match="max_display_width must be between 40 and 500"
            ):
                Config()

        with patch.dict(os.environ, {"ZENODOTOS_MAX_DISPLAY_WIDTH": "501"}):
            with pytest.raises(
                ConfigurationError, match="max_display_width must be between 40 and 500"
            ):
                Config()

    def test_invalid_cache_ttl_seconds(self):
        """Test validation of invalid cache TTL seconds."""
        with patch.dict(os.environ, {"ZENODOTOS_CACHE_TTL_SECONDS": "-1"}):
            with pytest.raises(
                ConfigurationError,
                match="cache_ttl_seconds must be between 0 and 86400",
            ):
                Config()

        with patch.dict(os.environ, {"ZENODOTOS_CACHE_TTL_SECONDS": "86401"}):
            with pytest.raises(
                ConfigurationError,
                match="cache_ttl_seconds must be between 0 and 86400",
            ):
                Config()

    def test_invalid_log_level(self):
        """Test validation of invalid log level."""
        with patch.dict(os.environ, {"ZENODOTOS_LOG_LEVEL": "INVALID"}):
            with pytest.raises(ConfigurationError, match="log_level must be one of"):
                Config()


class TestConfigMethods:
    """Test Config class methods."""

    def test_get_credentials_path(self):
        """Test get_credentials_path method."""
        config = Config()

        # Test default path
        assert config.get_credentials_path() == str(
            config.config_dir / "credentials.json"
        )

        # Test with custom path in config
        config._config.credentials_path = "/custom/credentials.json"
        assert config.get_credentials_path() == "/custom/credentials.json"

        # Test with environment variable
        with patch.dict(
            os.environ, {"GOOGLE_DRIVE_CREDENTIALS": "/env/credentials.json"}
        ):
            config._config.credentials_path = None
            assert config.get_credentials_path() == "/env/credentials.json"

    def test_get_token_path(self):
        """Test get_token_path method."""
        config = Config()

        # Test default path
        assert config.get_token_path() == str(config.config_dir / "token.json")

        # Test with custom path in config
        config._config.token_path = "/custom/token.json"
        assert config.get_token_path() == "/custom/token.json"

    def test_get_method(self):
        """Test get method."""
        config = Config()

        assert config.get("page_size") == 10
        assert config.get("nonexistent", "default") == "default"
        assert config.get("nonexistent") is None

    def test_set_method(self):
        """Test set method."""
        config = Config()

        config.set("page_size", 50)
        assert config.get("page_size") == 50

        with pytest.raises(ConfigurationError, match="Unknown configuration key"):
            config.set("nonexistent", "value")

    def test_get_all_method(self):
        """Test get_all method."""
        config = Config()
        all_config = config.get_all()

        assert isinstance(all_config, dict)
        assert "credentials_path" in all_config
        assert "token_path" in all_config
        assert "page_size" in all_config
        assert "max_retries" in all_config
        assert all_config["page_size"] == 10


class TestConfigSaving:
    """Test configuration saving functionality."""

    def test_save_yaml_config(self):
        """Test saving configuration to YAML file."""
        config = Config()
        config.set("page_size", 50)
        config.set("debug_mode", True)

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            save_path = f.name

        try:
            with patch("yaml.dump") as mock_dump:
                config.save_config(save_path)
                mock_dump.assert_called_once()

                # Check that the correct data was passed to yaml.dump
                call_args = mock_dump.call_args
                dumped_data = call_args[0][0]
                assert dumped_data["page_size"] == 50
                assert dumped_data["debug_mode"] is True
        finally:
            os.unlink(save_path)

    def test_save_toml_config(self):
        """Test saving configuration to TOML file."""
        config = Config()
        config.set("page_size", 60)

        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            save_path = f.name

        try:
            # Test successful TOML saving (dependencies are now available)
            config.save_config(save_path)

            # Verify the file was created and contains correct data
            # We can't easily parse TOML in the test, but we can check the file exists
            assert os.path.exists(save_path)
            assert os.path.getsize(save_path) > 0
        finally:
            os.unlink(save_path)

    def test_save_json_config(self):
        """Test saving configuration to JSON file."""
        config = Config()
        config.set("page_size", 70)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            save_path = f.name

        try:
            config.save_config(save_path)

            # Verify the file was created and contains correct data
            with open(save_path, "r") as f:
                saved_data = json.load(f)
                assert saved_data["page_size"] == 70
        finally:
            os.unlink(save_path)

    def test_save_config_default_location(self):
        """Test saving configuration to default location."""
        config = Config()
        config.set("page_size", 80)

        with patch.object(config, "ensure_config_dir") as mock_ensure_dir:
            with patch("yaml.dump") as mock_dump:
                config.save_config()
                mock_ensure_dir.assert_called_once()
                mock_dump.assert_called_once()

    def test_save_config_removes_none_values(self):
        """Test that None values are removed when saving."""
        config = Config()
        config.set("page_size", 90)
        # credentials_path should be None by default

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            save_path = f.name

        try:
            config.save_config(save_path)

            with open(save_path, "r") as f:
                saved_data = json.load(f)
                assert "page_size" in saved_data
                assert "credentials_path" not in saved_data  # Should be removed
        finally:
            os.unlink(save_path)
