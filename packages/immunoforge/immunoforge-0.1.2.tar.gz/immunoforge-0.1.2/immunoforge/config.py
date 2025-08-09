"""
Default configuration for ImmunoForge tools
"""

import os
from pathlib import Path
from typing import Dict, Optional

class DefaultConfig:
    """Default configuration for tool executables and settings"""
    
    # Default executable paths
    TOOL_EXECUTABLES = {
        'netchop': '/tamir2/nicolaslynn/tools/netchop-3.1/netchop',
        'netmhcpan': '/tamir2/nicolaslynn/tools/netMHCpan-4.1/netMHCpan',
        'blastp': 'blastp',  # Assumes blastp is in PATH
        'mhcflurry': None,   # Python package, no executable needed
        'iedb': None,        # API-based, no executable needed
    }
    
    # Default database paths
    DATABASE_PATHS = {
        'uniprot_blast_db': '/tamir2/nicolaslynn/data/UniProt/raw_downloads',
        'mhcflurry_models': '/tamir2/nicolaslynn/data/mhcflurry/4/2.2.0/models_class1_presentation/models/',
    }
    
    # Default temporary directories
    TEMP_DIRS = {
        'netchop': '/tmp/netchop',
        'netmhcpan': '/tmp/netmhcpan',
        'uniprot_blast': '/tmp/uniprot_blast',
    }
    
    @classmethod
    def get_executable_path(cls, tool_name: str) -> Optional[str]:
        """
        Get the default executable path for a tool
        
        Parameters
        ----------
        tool_name : str
            Name of the tool
            
        Returns
        -------
        str or None
            Path to executable or None if not configured
        """
        return cls.TOOL_EXECUTABLES.get(tool_name)
    
    @classmethod
    def get_database_path(cls, db_name: str) -> Optional[str]:
        """
        Get the default database path
        
        Parameters
        ----------
        db_name : str
            Name of the database
            
        Returns
        -------
        str or None
            Path to database or None if not configured
        """
        return cls.DATABASE_PATHS.get(db_name)
    
    @classmethod
    def get_temp_dir(cls, tool_name: str) -> str:
        """
        Get the default temporary directory for a tool
        
        Parameters
        ----------
        tool_name : str
            Name of the tool
            
        Returns
        -------
        str
            Path to temporary directory
        """
        return cls.TEMP_DIRS.get(tool_name, f'/tmp/{tool_name}')
    
    @classmethod
    def update_executable_path(cls, tool_name: str, path: str) -> None:
        """
        Update the default executable path for a tool
        
        Parameters
        ----------
        tool_name : str
            Name of the tool
        path : str
            New path to executable
        """
        cls.TOOL_EXECUTABLES[tool_name] = path
    
    @classmethod
    def load_from_env(cls) -> None:
        """
        Load configuration from environment variables
        Environment variables should be named: IMMUNOFORGE_<TOOL>_EXECUTABLE
        """
        for tool_name in cls.TOOL_EXECUTABLES.keys():
            env_var = f'IMMUNOFORGE_{tool_name.upper()}_EXECUTABLE'
            env_path = os.getenv(env_var)
            if env_path:
                cls.TOOL_EXECUTABLES[tool_name] = env_path
        
        # Load database paths
        for db_name in cls.DATABASE_PATHS.keys():
            env_var = f'IMMUNOFORGE_{db_name.upper()}_PATH'
            env_path = os.getenv(env_var)
            if env_path:
                cls.DATABASE_PATHS[db_name] = env_path
    
    @classmethod
    def validate_executables(cls) -> Dict[str, bool]:
        """
        Validate that all configured executables exist
        
        Returns
        -------
        dict
            Dictionary mapping tool names to existence status
        """
        status = {}
        for tool_name, path in cls.TOOL_EXECUTABLES.items():
            if path is None:
                status[tool_name] = True  # No executable needed
            else:
                status[tool_name] = Path(path).exists()
        return status
    
    @classmethod
    def get_config_summary(cls) -> str:
        """
        Get a summary of current configuration
        
        Returns
        -------
        str
            Configuration summary
        """
        summary = "ImmunoForge Configuration Summary\n"
        summary += "=" * 35 + "\n\n"
        
        summary += "Tool Executables:\n"
        summary += "-" * 17 + "\n"
        for tool, path in cls.TOOL_EXECUTABLES.items():
            if path:
                exists = "✓" if Path(path).exists() else "✗"
                summary += f"{tool:12} : {path} {exists}\n"
            else:
                summary += f"{tool:12} : Not required\n"
        
        summary += "\nDatabase Paths:\n"
        summary += "-" * 15 + "\n"
        for db, path in cls.DATABASE_PATHS.items():
            if path:
                exists = "✓" if Path(path).exists() else "✗"
                summary += f"{db:20} : {path} {exists}\n"
            else:
                summary += f"{db:20} : Not configured\n"
        
        summary += "\nTemporary Directories:\n"
        summary += "-" * 22 + "\n"
        for tool, path in cls.TEMP_DIRS.items():
            summary += f"{tool:12} : {path}\n"
        
        return summary


# Load configuration from environment on import
DefaultConfig.load_from_env()


# Convenience functions for backward compatibility
def get_executable_path(tool_name: str) -> Optional[str]:
    """Get default executable path for a tool"""
    return DefaultConfig.get_executable_path(tool_name)


def get_database_path(db_name: str) -> Optional[str]:
    """Get default database path"""
    return DefaultConfig.get_database_path(db_name)


def get_temp_dir(tool_name: str) -> str:
    """Get default temp directory for a tool"""
    return DefaultConfig.get_temp_dir(tool_name)