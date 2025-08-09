"""
Tool management and registration system
"""

from typing import Dict, Type, Any, List
from .base import BaseTool
from .netchop import NetChopTool
from .mhcflurry import MHCFlurryTool
from .netmhcpan import NetMHCpanTool
from .iedb import IEDBTool
from .deepimmuno import DeepImmunoCNNTool

# Global tool registry
_TOOL_REGISTRY: Dict[str, Type[BaseTool]] = {
    'netchop': NetChopTool,
    'mhcflurry': MHCFlurryTool,
    'netmhcpan': NetMHCpanTool,
    'iedb': IEDBTool,
    'deepimmuno': DeepImmunoCNNTool,
}


def register_tool(name: str, tool_class: Type[BaseTool]) -> None:
    """
    Register a new tool

    Parameters
    ----------
    name : str
        Tool identifier
    tool_class : Type[BaseTool]
        Tool class (must inherit from BaseTool)
    """
    if not issubclass(tool_class, BaseTool):
        raise ValueError(f"Tool class must inherit from BaseTool")

    _TOOL_REGISTRY[name] = tool_class


def get_tool_instance(name: str, **kwargs) -> BaseTool:
    """
    Get an instance of a registered tool

    Parameters
    ----------
    name : str
        Tool identifier
    **kwargs
        Tool-specific configuration

    Returns
    -------
    BaseTool
        Initialized tool instance
    """
    if name not in _TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {name}. Available tools: {list(_TOOL_REGISTRY.keys())}")

    tool_class = _TOOL_REGISTRY[name]
    return tool_class(**kwargs)


def get_available_tools() -> List[str]:
    """Get list of available tool names"""
    return list(_TOOL_REGISTRY.keys())


__all__ = [
    'BaseTool',
    'register_tool',
    'get_tool_instance',
    'get_available_tools',
    'DeepImmunoCNNTool'
]