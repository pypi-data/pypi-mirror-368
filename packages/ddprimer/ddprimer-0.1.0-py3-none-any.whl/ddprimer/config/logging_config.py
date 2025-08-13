#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging configuration module for ddPrimer pipeline.

Contains functionality for:
1. Module-specific debug level control based on filenames
2. Debug filtering and formatting with colors  
3. Singleton pattern for consistent logging configuration
4. Automatic log file management and rotation

This module provides comprehensive logging configuration for the ddPrimer
pipeline, enabling granular debug control per module and enhanced
debugging capabilities with colored output.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ModuleDebugConfig:
    """
    Configuration for module-specific debug settings.
    
    This class manages debug level configuration for individual modules,
    providing filename-based debug control for intuitive usage and
    comprehensive module coverage.
    
    Attributes:
        MODULE_DEBUG_LEVELS: Dictionary mapping module names to log levels
        FILENAME_TO_MODULE: Dictionary mapping filenames to full module paths
        
    Example:
        >>> config = ModuleDebugConfig()
        >>> config.MODULE_DEBUG_LEVELS['ddprimer.pipeline']
        20
    """
    
    # All modules default to INFO level
    MODULE_DEBUG_LEVELS = {
        'ddprimer.main': logging.INFO,
        'ddprimer.core.snp_processor': logging.INFO,
        'ddprimer.core.annotation_processor': logging.INFO,
        'ddprimer.core.blast_processor': logging.INFO,
        'ddprimer.core.thermo_processor': logging.INFO,
        'ddprimer.core.primer3_processor': logging.INFO,
        'ddprimer.core.primer_processor': logging.INFO,
        'ddprimer.core.sequence_processor': logging.INFO,
        'ddprimer.utils.blast_db_manager': logging.INFO,
        'ddprimer.utils.file_io': logging.INFO,
        'ddprimer.utils.file_preparator': logging.INFO,
        'ddprimer.utils.direct_mode': logging.INFO,
        'ddprimer.config.config': logging.INFO,
        'ddprimer.config.config_display': logging.INFO,
        'ddprimer.config.template_generator': logging.INFO,
    }
    
    # Filename to module mapping for intuitive usage
    FILENAME_TO_MODULE = {
        # Main pipeline
        'main': 'ddprimer.main',

        # Core processing files
        'snp_processor': 'ddprimer.core.snp_processor',
        'annotation_processor': 'ddprimer.core.annotation_processor',
        'blast_processor': 'ddprimer.core.blast_processor',
        'thermo_processor': 'ddprimer.core.thermo_processor',
        'primer3_processor': 'ddprimer.core.primer3_processor',
        'primer_processor': 'ddprimer.core.primer_processor',
        'sequence_processor': 'ddprimer.core.sequence_processor',
        
        # Utility files
        'blast_db_manager': 'ddprimer.utils.manager',
        'file_io': 'ddprimer.utils.file_io',
        'file_preparator': 'ddprimer.utils.file_preparator',
        'direct_mode': 'ddprimer.utils.direct_mode',
        
        # Config files  
        'config': 'ddprimer.config.config',
        'config_display': 'ddprimer.config.config_display',
        'template_generator': 'ddprimer.config.template_generator',
    }


class SimpleDebugFormatter(logging.Formatter):
    """
    Simple formatter with colors for debug output.
    
    Provides color-coded log output for improved readability during
    debugging, with support for different log levels and optional
    color disabling for environments that don't support ANSI colors.
    
    Attributes:
        use_colors: Whether to use ANSI color codes in output
        COLORS: Dictionary mapping log levels to ANSI color codes
        
    Example:
        >>> formatter = SimpleDebugFormatter(use_colors=True)
        >>> handler.setFormatter(formatter)
    """
    
    def __init__(self, fmt=None, datefmt=None, use_colors=False):
        """
        Initialize formatter with optional color support.
        
        Args:
            fmt: Log message format string
            datefmt: Date format string
            use_colors: Whether to enable ANSI color codes
        """
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors
        
        # ANSI color codes
        self.COLORS = {
            'DEBUG': '\033[37m',      # White
            'INFO': '\033[1;37m',     # Bold White
            'WARNING': '\033[33m',    # Yellow
            'ERROR': '\033[31m',      # Red
            'CRITICAL': '\033[35m',   # Magenta
        }
        self.RESET = '\033[0m'
    
    def format(self, record):
        """
        Format the log record with colors.
        
        Args:
            record: LogRecord instance to format
            
        Returns:
            str: Formatted log message with optional colors
        """
        formatted_message = super().format(record)
        
        # Add colors if enabled
        if self.use_colors and record.levelname in self.COLORS:
            color_code = self.COLORS[record.levelname]
            formatted_message = f"{color_code}{formatted_message}{self.RESET}"
        
        return formatted_message


class DebugFilter(logging.Filter):
    """
    Filter that controls module-specific debug output.
    
    Provides granular control over debug output by filtering log records
    based on module-specific log levels, allowing users to enable debug
    mode for specific modules while keeping others at INFO level.
    
    Attributes:
        module_levels: Dictionary mapping module names to minimum log levels
        
    Example:
        >>> filter_obj = DebugFilter({'ddprimer.pipeline': logging.DEBUG})
        >>> handler.addFilter(filter_obj)
    """
    
    def __init__(self, module_levels: Dict[str, int]):
        """
        Initialize filter with module-specific log levels.
        
        Args:
            module_levels: Dictionary mapping module names to minimum log levels
        """
        super().__init__()
        self.module_levels = module_levels
    
    def filter(self, record):
        """
        Filter records based on module-specific levels.
        
        Args:
            record: LogRecord instance to filter
            
        Returns:
            bool: True if record should be logged, False otherwise
        """
        module_name = record.name
        
        # Try exact match first
        if module_name in self.module_levels:
            return record.levelno >= self.module_levels[module_name]
        
        # Try parent module matches - check from most specific to least specific
        module_parts = module_name.split('.')
        for i in range(len(module_parts), 0, -1):
            parent_module = '.'.join(module_parts[:i])
            if parent_module in self.module_levels:
                return record.levelno >= self.module_levels[parent_module]
        
        # For modules not in our config, use INFO level
        # This ensures that logger.info() calls from any module are shown
        return record.levelno >= logging.INFO

class DebugLogLimiter:
    """Global counter to limit debug logging across all modules"""
    _counters = {}
    
    @classmethod
    def should_log(cls, category: str, interval: int = 100, max_initial: int = 5) -> bool:
        """
        Determine if we should log for this category
        
        Args:
            category: Logging category (e.g., 'fragment_creation', 'primer_processing')
            interval: Log every Nth occurrence (default: 100)
            max_initial: Log first N occurrences (default: 5)
        
        Returns:
            True if should log, False otherwise
        """
        if category not in cls._counters:
            cls._counters[category] = 0
        
        cls._counters[category] += 1
        count = cls._counters[category]
        
        # Log first few occurrences OR every interval
        return count <= max_initial or count % interval == 0
    
    @classmethod
    def reset_counter(cls, category: str):
        """Reset counter for a specific category"""
        cls._counters[category] = 0
    
    @classmethod
    def reset_all(cls):
        """Reset all counters"""
        cls._counters.clear()

def setup_logging(debug: Union[bool, List[str], str] = False) -> str:
    """
    Configure logging with filename-based debug control and automatic log rotation.
    
    Sets up comprehensive logging configuration with support for module-specific
    debug levels, colored console output, and automatic log file management.
    Automatically rotates logs daily and keeps only the last 10 log files.
    Each run is clearly marked with timestamps for easy identification.
    
    Args:
        debug: Debug configuration options:
               - False: No debug logging
               - True: Universal debug for all modules
               - str: Single filename for debug (e.g., 'pipeline', 'SNP_processor')
               - List[str]: List of filenames for debug
        
    Returns:
        str: Path to the created log file
        
    Raises:
        LoggingConfigError: If logging setup fails
        
    Example:
        >>> log_file = setup_logging(debug=['pipeline', 'blast_processor'])
        >>> print(f"Logs saved to: {log_file}")
    """
    logger.debug(f"Setting up logging with debug={debug}")
    
    try:
        # Normalize debug input
        debug_enabled, debug_modules = _normalize_debug_input(debug)
        logger.debug(f"Normalized debug: enabled={debug_enabled}, modules={debug_modules}")
        
        # Start with default module configuration
        module_config = ModuleDebugConfig.MODULE_DEBUG_LEVELS.copy()
        
        # Apply module-specific debug configuration
        if debug_modules:
            # Keep INFO level for all modules by default
            # Only enable DEBUG for specified modules
            for module_name in debug_modules:
                full_module_name = _resolve_module_name(module_name)
                if full_module_name and full_module_name in module_config:
                    module_config[full_module_name] = logging.DEBUG
                    logger.debug(f"Enabled DEBUG for {full_module_name}")
        elif debug_enabled:
            # Universal debug - enable DEBUG for all modules
            for module in module_config:
                module_config[module] = logging.DEBUG
            logger.debug("Enabled DEBUG for all modules")
        
        # Set up log directory
        log_dir = os.path.join(os.path.expanduser("~"), ".ddPrimer", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create timestamped filename for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"ddPrimer_{timestamp}.log")
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # File handler - always saves all levels
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Console handler logic
        if debug_enabled:
            # In debug mode, use DEBUG level and apply the filter
            console_handler.setLevel(logging.DEBUG)
            console_formatter = SimpleDebugFormatter(
                fmt='%(levelname)-8s [%(name)s] %(message)s',
                use_colors=True
            )
            # Add module-specific filter
            debug_filter = DebugFilter(module_config)
            console_handler.addFilter(debug_filter)
        else:
            # In normal mode, use INFO level and simple formatter
            # This ensures all logger.info() calls are displayed
            console_handler.setLevel(logging.INFO)
            console_formatter = SimpleDebugFormatter(
                fmt='%(message)s',
                use_colors=False
            )
            # Don't apply the DebugFilter in normal mode
        
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to root logger
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Configure main logger
        main_logger = logging.getLogger("ddPrimer")
        
        if debug_enabled:
            main_logger.debug("Debug logging enabled")
            main_logger.debug(f"Log file: {log_file}")
            if debug_modules:
                resolved_modules = []
                unresolved_modules = []
                for module_name in debug_modules:
                    full_module_name = _resolve_module_name(module_name)
                    if full_module_name:
                        resolved_modules.append(f"{module_name} → {full_module_name}")
                    else:
                        unresolved_modules.append(module_name)
                
                if resolved_modules:
                    main_logger.debug(f"Debug enabled for modules: {', '.join(resolved_modules)}")
                if unresolved_modules:
                    main_logger.warning(f"Unknown module names: {', '.join(unresolved_modules)}")
            else:
                main_logger.debug("Debug enabled for all modules")
        
        # Clean up old log files
        _cleanup_old_logs()
        
        logger.debug("Logging setup completed successfully")
        return log_file
        
    except Exception as e:
        error_msg = f"Logging setup failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise LoggingConfigError(error_msg) from e


def _cleanup_old_logs(files_to_keep: int = 10):
    """
    Clean up old log files.
    
    Removes old log files to prevent unlimited disk usage growth.
    Keeps the most recent files based on filename timestamp.
    
    Args:
        files_to_keep: Number of most recent log files to retain
    """
    try:
        from pathlib import Path
        
        logs_dir = Path.home() / ".ddPrimer" / "logs"
        if not logs_dir.exists():
            return
        
        log_files = list(logs_dir.glob("ddPrimer_*.log"))
        log_files.sort(reverse=True)
        
        files_to_remove = log_files[files_to_keep:]
        for log_file in files_to_remove:
            log_file.unlink()
            logger.debug(f"Cleaned up old log file: {log_file}")
                    
    except Exception as e:
        logger.warning(f"Failed to clean up old logs: {e}")


def get_current_log_file() -> Optional[str]:
    """
    Get the path to the current run's log file.
    
    Returns:
        str: Path to current log file, or None if logging not set up
        
    Example:
        >>> current_log = get_current_log_file()
        >>> print(f"Current log: {current_log}")
    """
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return None


def list_recent_logs(count: int = 10) -> List[str]:
    """
    List the most recent log files.
    
    Args:
        count: Number of recent log files to return
        
    Returns:
        List of log file paths, sorted by timestamp (newest first)
        
    Example:
        >>> recent_logs = list_recent_logs(count=5)
        >>> for log_file in recent_logs:
        ...     print(log_file)
    """
    from pathlib import Path
    
    logs_dir = Path.home() / ".ddPrimer" / "logs"
    if not logs_dir.exists():
        return []
    
    log_files = list(logs_dir.glob("ddPrimer_*.log"))
    log_files.sort(reverse=True)
    
    return [str(f) for f in log_files[:count]]


def _normalize_debug_input(debug: Union[bool, List[str], str]) -> tuple[bool, Optional[List[str]]]:
    """
    Normalize various debug input formats to (debug_enabled, debug_modules).
    
    Args:
        debug: Debug input in various formats
        
    Returns:
        Tuple of (debug_enabled: bool, debug_modules: Optional[List[str]])
        
    Example:
        >>> enabled, modules = _normalize_debug_input(['pipeline', 'blast'])
        >>> print(enabled, modules)
        True ['pipeline', 'blast']
    """
    try:
        if isinstance(debug, bool):
            debug_enabled = debug
            debug_modules = None
        elif isinstance(debug, str):
            debug_enabled = True
            debug_modules = [debug]
        elif isinstance(debug, list):
            debug_enabled = True
            debug_modules = debug
        else:
            debug_enabled = False
            debug_modules = None
        
        return debug_enabled, debug_modules
        
    except Exception as e:
        error_msg = f"Failed to normalize debug input: {debug}"
        logger.error(error_msg)
        logger.debug(f"Error details: {str(e)}", exc_info=True)
        raise LoggingConfigError(error_msg) from e


def _resolve_module_name(filename: str) -> Optional[str]:
    """
    Resolve a filename to its full module path.
    
    Args:
        filename: Filename like 'pipeline', 'snp_processor', etc.
        
    Returns:
        Full module path or None if not found
        
    Example:
        >>> module_name = _resolve_module_name('pipeline')
        >>> print(module_name)
        ddprimer.pipeline
    """
    # Try exact match first
    if filename in ModuleDebugConfig.FILENAME_TO_MODULE:
        return ModuleDebugConfig.FILENAME_TO_MODULE[filename]
    
    # If it's already a full module name, check if it exists
    if filename in ModuleDebugConfig.MODULE_DEBUG_LEVELS:
        return filename
        
    return None


class LoggingConfigError(Exception):
    """Error during logging configuration setup."""
    pass