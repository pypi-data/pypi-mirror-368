"""
Nexagen - Next-Generation Multi-Agent System Builder

A framework for building sophisticated multi-agent systems with MCP protocol integration.
"""

__version__ = "1.0.0"
__author__ = "Chongqing Taoxiang Network Technology Co., Ltd."
__email__ = "wei@taoxiang.org"
__license__ = "MIT"
__url__ = "https://github.com/taoxiang-org/nexagen"

from .core import create_project, build_project, run_project
from .cli import cli

__all__ = [
    "create_project",
    "build_project",
    "run_project",
    "cli"
]