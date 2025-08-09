"""Global configuration for pyrion library."""

import multiprocessing as mp
import os
from typing import Optional


class PyrionConfig:
    """Global configuration for pyrion library.
    
    Manages parallelization settings and other global options.
    """
    
    def __init__(self):
        # Detect available cores at initialization
        self._available_cores = self._detect_available_cores()
        
        # Default to using all available cores, but with a reasonable upper limit
        # This follows the existing pattern but makes it configurable
        self._max_cores = min(self._available_cores, 8)
        
        # Minimum items threshold for multiprocessing (configurable)
        self._min_items_for_parallel = 100
        
        # Whether multiprocessing is available
        self._multiprocessing_available = self._test_multiprocessing()
    
    def _detect_available_cores(self) -> int:
        """Detect the number of available CPU cores."""
        try:
            # Try different methods to get CPU count
            # 1. multiprocessing.cpu_count() - logical cores
            logical_cores = mp.cpu_count()
            
            # 2. os.cpu_count() - may be different in some environments
            os_cores = os.cpu_count()
            
            # Use the minimum of both (more conservative)
            cores = min(logical_cores, os_cores) if os_cores is not None else logical_cores
            
            # Ensure we have at least 1 core
            return max(1, cores)
        except Exception:
            # Fallback to 1 core if detection fails
            return 1
    
    def _test_multiprocessing(self) -> bool:
        """Test if multiprocessing is available and safe to use."""
        try:
            # Test if we can create a pool (some environments disable this)
            with mp.Pool(1) as test_pool:
                pass
            return True
        except Exception:
            return False
    
    @property
    def available_cores(self) -> int:
        """Get the number of available CPU cores (read-only)."""
        return self._available_cores
    
    @property
    def max_cores(self) -> int:
        """Get the maximum number of cores to use for parallel processing."""
        return self._max_cores
    
    @max_cores.setter
    def max_cores(self, value: int) -> None:
        """Set the maximum number of cores to use for parallel processing.
        
        Args:
            value: Number of cores to use. Must be between 1 and available_cores.
                  If 0 is provided, parallel processing will be disabled.
        
        Raises:
            ValueError: If value is negative or greater than available cores.
        """
        if value < 0:
            raise ValueError("max_cores must be non-negative")
        
        if value > self._available_cores:
            raise ValueError(f"max_cores ({value}) cannot exceed available cores ({self._available_cores})")
        
        self._max_cores = value
    
    @property
    def min_items_for_parallel(self) -> int:
        """Get the minimum number of items required to use parallel processing."""
        return self._min_items_for_parallel
    
    @min_items_for_parallel.setter
    def min_items_for_parallel(self, value: int) -> None:
        """Set the minimum number of items required to use parallel processing.
        
        Args:
            value: Minimum number of items. Must be non-negative.
        """
        if value < 0:
            raise ValueError("min_items_for_parallel must be non-negative")
        self._min_items_for_parallel = value
    
    @property
    def multiprocessing_available(self) -> bool:
        """Check if multiprocessing is available (read-only)."""
        return self._multiprocessing_available
    
    def disable_parallel(self) -> None:
        """Disable all parallel processing by setting max_cores to 0."""
        self._max_cores = 0
    
    def enable_parallel(self, max_cores: Optional[int] = None) -> None:
        """Enable parallel processing.
        
        Args:
            max_cores: Maximum cores to use. If None, uses default (min(available, 8)).
        """
        if max_cores is None:
            self._max_cores = min(self._available_cores, 8)
        else:
            self.max_cores = max_cores  # Use setter for validation
    
    def get_optimal_processes(self, n_items: int, max_processes: Optional[int] = None) -> int:
        """Determine optimal number of processes based on data size and configuration.
        
        Args:
            n_items: Number of items to process
            max_processes: Override max processes for this call
        
        Returns:
            Optimal number of processes (0 means use sequential processing)
        """
        # If parallel processing is disabled globally
        if self._max_cores == 0:
            return 0
        
        # If multiprocessing is not available
        if not self._multiprocessing_available:
            return 0
        
        # If dataset is too small
        if n_items < self._min_items_for_parallel:
            return 0
        
        # Determine effective max processes
        effective_max = max_processes if max_processes is not None else self._max_cores
        effective_max = min(effective_max, self._max_cores)  # Respect global limit
        
        # Don't use more processes than items (at least 10 items per process)
        optimal = min(effective_max, n_items // 10)
        
        return max(0, optimal)
    
    def summary(self) -> dict:
        """Get a summary of current configuration."""
        return {
            "available_cores": self._available_cores,
            "max_cores": self._max_cores,
            "min_items_for_parallel": self._min_items_for_parallel,
            "multiprocessing_available": self._multiprocessing_available,
            "parallel_enabled": self._max_cores > 0
        }


# Global configuration instance
_config = PyrionConfig()


# Public API functions
def get_available_cores() -> int:
    """Get the number of available CPU cores."""
    return _config.available_cores


def get_max_cores() -> int:
    """Get the current maximum number of cores for parallel processing."""
    return _config.max_cores


def set_max_cores(cores: int) -> None:
    """Set the maximum number of cores to use for parallel processing.
    
    Args:
        cores: Number of cores to use (1 to available_cores, or 0 to disable)
    """
    _config.max_cores = cores


def get_min_items_for_parallel() -> int:
    """Get the minimum number of items required for parallel processing."""
    return _config.min_items_for_parallel


def set_min_items_for_parallel(items: int) -> None:
    """Set the minimum number of items required for parallel processing."""
    _config.min_items_for_parallel = items


def disable_parallel() -> None:
    """Disable all parallel processing."""
    _config.disable_parallel()


def enable_parallel(max_cores: Optional[int] = None) -> None:
    """Enable parallel processing with optional core limit."""
    _config.enable_parallel(max_cores)


def is_multiprocessing_available() -> bool:
    """Check if multiprocessing is available."""
    return _config.multiprocessing_available


def get_config_summary() -> dict:
    """Get a summary of current configuration."""
    return _config.summary()


# Internal function for use by parallel utilities
def _get_config() -> PyrionConfig:
    """Get the global configuration instance (internal use)."""
    return _config 