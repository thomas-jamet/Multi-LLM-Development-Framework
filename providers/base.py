#!/usr/bin/env python3
"""
LLM Provider Base Class

Abstract interface for LLM-specific workspace configurations.
Providers implement templates for config files, MCP settings, and directory structures.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class LLMProvider(ABC):
    """Abstract base class for LLM workspace providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'gemini', 'claude')."""
        pass

    @property
    @abstractmethod
    def config_filename(self) -> str:
        """Main configuration file name (e.g., 'GEMINI.md', 'CLAUDE.md')."""
        pass

    @property
    @abstractmethod
    def config_dirname(self) -> str:
        """Configuration directory name (e.g., '.gemini', '.claude')."""
        pass

    @abstractmethod
    def get_config_template(self, tier: str, project_name: str) -> str:
        """
        Generate the main configuration file content.

        Args:
            tier: Workspace tier ("1", "2", or "3")
            project_name: Name of the workspace project

        Returns:
            Configuration file content as string
        """
        pass

    @abstractmethod
    def get_readme_template(self, tier: str, project_name: str) -> str:
        """
        Generate README.md content.

        Args:
            tier: Workspace tier
            project_name: Name of the workspace project

        Returns:
            README content as string
        """
        pass

    @abstractmethod
    def get_mcp_config(self) -> Dict:
        """
        Get MCP (Model Context Protocol) server configuration.

        Returns:
            MCP configuration as dictionary
        """
        pass

    @abstractmethod
    def get_settings(self, tier: str) -> Dict:
        """
        Get provider-specific settings.

        Args:
            tier: Workspace tier

        Returns:
            Settings dictionary
        """
        pass

    def get_additional_files(self, tier: str, project_name: str) -> Dict[str, str]:
        """
        Get any additional provider-specific files.

        Args:
            tier: Workspace tier
            project_name: Name of the workspace project

        Returns:
            Dictionary mapping file paths to content
        """
        return {}

    def get_additional_directories(self, tier: str) -> List[str]:
        """
        Get any additional provider-specific directories.

        Args:
            tier: Workspace tier

        Returns:
            List of directory paths
        """
        return []
