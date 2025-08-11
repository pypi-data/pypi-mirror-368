"""Configuration and directory management for LitAI."""

import json
from pathlib import Path
from typing import Any

from structlog import get_logger

logger = get_logger()


class Config:
    """Manages LitAI configuration and directory structure."""

    def __init__(self, base_dir: Path | None = None):
        """Initialize config with base directory.

        Args:
            base_dir: Base directory for LitAI data. Defaults to ~/.litai
        """
        if base_dir is None:
            base_dir = Path.home() / ".litai"
        self.base_dir = Path(base_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        directories = [
            self.base_dir,
            self.pdfs_dir,
            self.db_dir,
        ]

        for dir_path in directories:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info("Created directory", path=str(dir_path))

    @property
    def pdfs_dir(self) -> Path:
        """Directory for storing downloaded PDFs."""
        return self.base_dir / "pdfs"

    @property
    def db_dir(self) -> Path:
        """Directory for database files."""
        return self.base_dir / "db"

    @property
    def db_path(self) -> Path:
        """Path to the SQLite database file."""
        return self.db_dir / "litai.db"

    def pdf_path(self, paper_id: str) -> Path:
        """Get the path for a specific paper's PDF.

        Args:
            paper_id: Unique identifier for the paper

        Returns:
            Path where the PDF should be stored
        """
        return self.pdfs_dir / f"{paper_id}.pdf"

    @property
    def config_path(self) -> Path:
        """Path to the configuration file."""
        return self.base_dir / "config.json"

    @property
    def user_prompt_path(self) -> Path:
        """Path to user prompt file."""
        return self.base_dir / "user_prompt.txt"

    def load_config(self) -> dict[str, Any]:
        """Load configuration from file.

        Returns:
            Configuration dict or empty dict if file doesn't exist
        """
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                config = json.load(f)
                logger.info("Loaded configuration", path=str(self.config_path))
                return dict(config)
        except (OSError, json.JSONDecodeError) as e:
            logger.error(
                "Failed to load config", path=str(self.config_path), error=str(e),
            )
            return {}

    def save_config(self, config: dict[str, Any]) -> None:
        """Save configuration to file.

        Args:
            config: Configuration dictionary to save
        """
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info("Saved configuration", path=str(self.config_path))
        except OSError as e:
            logger.error(
                "Failed to save config", path=str(self.config_path), error=str(e),
            )
            raise

    def update_config(self, key_path: str, value: Any) -> None:
        """Update a specific configuration value.

        Args:
            key_path: Dot-separated path to config key (e.g., "llm.provider")
            value: Value to set
        """
        config = self.load_config()

        # Navigate through the key path, creating dicts as needed
        keys = key_path.split(".")
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the final value
        current[keys[-1]] = value

        self.save_config(config)

    def get_vi_mode(self) -> bool:
        """Get vi mode setting from configuration.

        Returns:
            True if vi mode is enabled, False otherwise (default)
        """
        config = self.load_config()
        editor_config = config.get("editor", {})
        return bool(editor_config.get("vi_mode", False))

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation.
        
        Args:
            key: Config key in dot notation (e.g., 'synthesis.tool_approval')
            default: Default value if key not found
        
        Returns:
            Config value or default
        """
        config = self.load_config()
        parts = key.split('.')
        value: Any = config
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set a config value using dot notation.
        
        Args:
            key: Config key in dot notation (e.g., 'synthesis.tool_approval')
            value: Value to set
        """
        config = self.load_config()
        parts = key.split('.')
        
        # Navigate to the parent dict
        current = config
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        self.save_config(config)
        logger.info(f"Config updated: {key} = {value}")

    def get_list_columns(self) -> list[str]:
        """Get configured columns for /list command.

        Returns default columns if not configured.
        """
        config = self.load_config()
        columns_str = config.get("display", {}).get("list_columns", "")

        if not columns_str:
            # Default columns
            return [
                "no",
                "title",
                "authors",
                "year",
                "citations",
                "ai_notes",
                "notes",
                "tags",
                "venue",
            ]

        return [col.strip().lower() for col in columns_str.split(",")]
