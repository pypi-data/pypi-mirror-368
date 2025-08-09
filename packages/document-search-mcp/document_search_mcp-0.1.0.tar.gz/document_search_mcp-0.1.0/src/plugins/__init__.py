"""Plugin system for extensible document processing."""

from .base_plugin import (
    FilterProvider,
    MetadataEnhancer,
    PluginConfig,
    SearchEnhancer,
)

__all__ = [
    "MetadataEnhancer",
    "SearchEnhancer",
    "FilterProvider",
    "PluginConfig",
]
