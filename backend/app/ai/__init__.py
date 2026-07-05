"""
ResQAI – Multi-LLM AI Package
Primary: Mistral Large Latest
Fallback: Google Gemini 1.5 Pro
Observability: LangSmith
"""
from .ai_manager import AIManager, get_ai_manager

__all__ = ["AIManager", "get_ai_manager"]
