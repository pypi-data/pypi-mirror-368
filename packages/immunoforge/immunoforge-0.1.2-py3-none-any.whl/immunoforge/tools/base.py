"""
Base class for all prediction tools
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import logging
from pathlib import Path
import json
import hashlib
import pickle

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Abstract base class for all epitope prediction tools"""

    def __init__(
            self,
            name: str = None,
            cache_dir: Optional[Union[str, Path]] = None,
            enable_cache: bool = True,
            **kwargs
    ):
        """
        Initialize base tool

        Parameters
        ----------
        name : str
            Tool name
        cache_dir : str or Path, optional
            Directory for caching results
        enable_cache : bool
            Whether to enable result caching
        **kwargs
            Tool-specific parameters
        """
        self.name = name or self.__class__.__name__
        self.enable_cache = enable_cache
        self.cache_dir = None

        if enable_cache and cache_dir:
            self.cache_dir = Path(cache_dir) / self.name
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.config = kwargs
        self._validate_config()

        logger.debug(f"Initialized {self.name} with config: {self.config}")

    def _validate_config(self):
        """Validate tool configuration"""
        # Override in subclasses for specific validation
        pass

    @abstractmethod
    def predict(self, sequences: Any, **kwargs) -> pd.DataFrame:
        """
        Run predictions on sequences

        Parameters
        ----------
        sequences : Any
            Input sequences (format depends on tool)
        **kwargs
            Additional prediction parameters

        Returns
        -------
        pd.DataFrame
            Prediction results
        """
        pass

    def _get_cache_key(self, data: Any, **kwargs) -> str:
        """Generate cache key for given input"""
        # Create a string representation of all inputs
        cache_data = {
            'data': str(data),
            'config': self.config,
            'kwargs': kwargs
        }

        # Generate hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Load results from cache"""
        if not self.enable_cache or not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    logger.debug(f"Loading {self.name} results from cache")
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load from cache: {e}")

        return None

    def _save_to_cache(self, cache_key: str, results: pd.DataFrame):
        """Save results to cache"""
        if not self.enable_cache or not self.cache_dir:
            return

        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(results, f)
                logger.debug(f"Saved {self.name} results to cache")
        except Exception as e:
            logger.warning(f"Failed to save to cache: {e}")

    def predict_with_cache(self, sequences: Any, **kwargs) -> pd.DataFrame:
        """Predict with caching support"""
        # Generate cache key
        cache_key = self._get_cache_key(sequences, **kwargs)

        # Try to load from cache
        results = self._load_from_cache(cache_key)
        if results is not None:
            return results

        # Run prediction
        results = self.predict(sequences, **kwargs)

        # Save to cache
        self._save_to_cache(cache_key, results)

        return results

    def validate_input(self, sequences: Any) -> bool:
        """
        Validate input sequences

        Parameters
        ----------
        sequences : Any
            Input sequences

        Returns
        -------
        bool
            Whether input is valid
        """
        # Override in subclasses for specific validation
        return True

    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            'name': self.name,
            'class': self.__class__.__name__,
            'config': self.config,
            'cache_enabled': self.enable_cache,
            'cache_dir': str(self.cache_dir) if self.cache_dir else None
        }