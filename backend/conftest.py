"""
ResQAI – pytest configuration
Blocks the broken langsmith.pytest_plugin entry point from loading.
"""
import sys
from unittest.mock import MagicMock

# Prevent langsmith pytest plugin from crashing the test runner
# (installed version 0.1.147 has broken entry point on some systems)
sys.modules.setdefault("langsmith.pytest_plugin", MagicMock())
