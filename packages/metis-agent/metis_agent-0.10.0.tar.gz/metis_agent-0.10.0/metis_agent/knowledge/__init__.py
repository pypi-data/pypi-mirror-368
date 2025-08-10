"""
Metis Agent Knowledge Base System

This module provides a comprehensive knowledge base system that extends beyond
conversational memory to include domain-specific knowledge, user-configurable
categories, and modular architecture for different knowledge types.

Knowledge Base Package

Provides modular, configurable knowledge base functionality for the Metis Agent.
"""

from .knowledge_entry import KnowledgeEntry, KnowledgeQueryResult
from .knowledge_config import KnowledgeConfig
from .knowledge_base import KnowledgeBase
from .knowledge_adapter import KnowledgeAdapter

__all__ = [
    "KnowledgeEntry",
    "KnowledgeQueryResult", 
    "KnowledgeConfig",
    "KnowledgeBase",
    "KnowledgeAdapter"
]

__version__ = "1.0.0"
