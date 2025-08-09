"""
Configuration loading and management utilities for LLMBuilder.

This module provides the ConfigManager class for loading, validating,
and managing configuration settings from various sources.
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from ..utils import ConfigurationError
from .defaults import Config, DefaultConfigs


class ConfigManager:
    """
    Manages configuration loading, validation, and merging.
    
    Supports loading from JSON, YAML files, dictionaries, and preset configurations.
    """
    
    def __init__(self):
        self._config_cache: Dict[str, Config] = {}
    
    def load_config(
        self, 
        path: Optional[Union[str, Path]] = None,
        preset: Optional[str] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        validate: bool = True
    ) -> Config:
        """
        Load configuration from various sources.
        
        Args:
            path: Path to configuration file (JSON or YAML)
            preset: Name of preset configuration
            config_dict: Configuration dictionary
            validate: Whether to validate the configuration
            
        Returns:
            Config: Loaded and validated configuration
            
        Raises:
            ConfigurationError: If configuration is invalid or cannot be loaded
        """
        try:
            # Determine source and load base config
            if preset:
                config = self._load_preset(preset)
            elif path:
                config = self._load_from_file(path)
            elif config_dict:
                config = self._load_from_dict(config_dict)
            else:
                # Default configuration
                config = Config()
            
            # Validate if requested
            if validate:
                config.validate()
            
            return config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}") from e
    
    def _load_preset(self, preset: str) -> Config:
        """Load a preset configuration."""
        cache_key = f"preset_{preset}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            config = DefaultConfigs.get_preset(preset)
            self._config_cache[cache_key] = config
            return config
        except ValueError as e:
            raise ConfigurationError(f"Invalid preset '{preset}': {str(e)}") from e
    
    def _load_from_file(self, path: Union[str, Path]) -> Config:
        """Load configuration from a file."""
        path = Path(path)
        
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")
        
        cache_key = f"file_{path.absolute()}"
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.json']:
                    data = json.load(f)
                elif path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration file format: {path.suffix}. "
                        "Supported formats: .json, .yaml, .yml"
                    )
            
            config = Config.from_dict(data)
            self._config_cache[cache_key] = config
            return config
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {path}: {str(e)}") from e
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in {path}: {str(e)}") from e
        except Exception as e:
            raise ConfigurationError(f"Error loading {path}: {str(e)}") from e
    
    def _load_from_dict(self, config_dict: Dict[str, Any]) -> Config:
        """Load configuration from a dictionary."""
        try:
            return Config.from_dict(config_dict)
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration dictionary: {str(e)}") from e
    
    def merge_configs(self, base: Config, override: Config) -> Config:
        """
        Merge two configurations, with override taking precedence.
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Config: Merged configuration
        """
        try:
            base_dict = base.to_dict()
            override_dict = override.to_dict()
            
            merged_dict = self._deep_merge(base_dict, override_dict)
            return Config.from_dict(merged_dict)
            
        except Exception as e:
            raise ConfigurationError(f"Failed to merge configurations: {str(e)}") from e
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self, config: Config, path: Union[str, Path], format: str = "json") -> None:
        """
        Save configuration to a file.
        
        Args:
            config: Configuration to save
            path: Output file path
            format: Output format ("json" or "yaml")
            
        Raises:
            ConfigurationError: If saving fails
        """
        path = Path(path)
        
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            config_dict = config.to_dict()
            
            with open(path, 'w', encoding='utf-8') as f:
                if format.lower() == "json":
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                elif format.lower() in ["yaml", "yml"]:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ConfigurationError(f"Unsupported format: {format}")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration to {path}: {str(e)}") from e
    
    def validate_config(self, config: Config) -> bool:
        """
        Validate a configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            return config.validate()
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {str(e)}") from e
    
    def get_config_template(self, preset: str = "gpu_medium") -> Dict[str, Any]:
        """
        Get a configuration template as a dictionary.
        
        Args:
            preset: Preset configuration to use as template
            
        Returns:
            Dict[str, Any]: Configuration template
        """
        config = self._load_preset(preset)
        return config.to_dict()
    
    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._config_cache.clear()


# Global config manager instance
_config_manager = ConfigManager()


def load_config(
    path: Optional[Union[str, Path]] = None,
    preset: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    validate: bool = True
) -> Config:
    """
    Load configuration using the global config manager.
    
    Args:
        path: Path to configuration file
        preset: Name of preset configuration
        config_dict: Configuration dictionary
        validate: Whether to validate the configuration
        
    Returns:
        Config: Loaded configuration
    """
    return _config_manager.load_config(path, preset, config_dict, validate)


def get_default_config(preset: str = "gpu_medium") -> Config:
    """
    Get a default configuration by preset name.
    
    Args:
        preset: Preset name
        
    Returns:
        Config: Default configuration
    """
    return _config_manager.load_config(preset=preset)


def save_config(config: Config, path: Union[str, Path], format: str = "json") -> None:
    """
    Save configuration to a file.
    
    Args:
        config: Configuration to save
        path: Output file path
        format: Output format
    """
    _config_manager.save_config(config, path, format)


def merge_configs(base: Config, override: Config) -> Config:
    """
    Merge two configurations.
    
    Args:
        base: Base configuration
        override: Override configuration
        
    Returns:
        Config: Merged configuration
    """
    return _config_manager.merge_configs(base, override)


def validate_config(config: Config) -> bool:
    """
    Validate a configuration.
    
    Args:
        config: Configuration to validate
        
    Returns:
        bool: True if valid
    """
    return _config_manager.validate_config(config)


def get_config_template(preset: str = "gpu_medium") -> Dict[str, Any]:
    """
    Get a configuration template.
    
    Args:
        preset: Preset to use as template
        
    Returns:
        Dict[str, Any]: Configuration template
    """
    return _config_manager.get_config_template(preset)