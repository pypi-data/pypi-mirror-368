"""
ImmunoForge - Simplified epitope prediction and immunogenicity analysis
"""

__version__ = "3.0.0"
__author__ = "Nicolas Lynn"

# Core components
from .analyzer import EpitopeAnalyzer
from .config import DefaultConfig
from .tools import get_tool_instance, get_available_tools
from .finder import EpitopePipeline
from .alleles import alleles

__all__ = [
    'EpitopePipeline',
    'EpitopeAnalyzer', 
    'DefaultConfig',
    'get_tool_instance',
    'get_available_tools',
    'alleles'
]