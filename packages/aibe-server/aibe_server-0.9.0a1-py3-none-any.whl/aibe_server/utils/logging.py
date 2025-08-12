"""
Unified Logging System for Browser-AI Interface Server
Replaces the previous dual logging system with a clean, configurable solution
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

class LogLevel(Enum):
    """Logging levels in order of priority"""
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40

class UnifiedLogger:
    """
    Unified logging system with:
    - Single log file with timestamps
    - Multi-level support (ERROR/WARN/INFO/DEBUG)
    - Config file controlled
    - System health monitoring
    - Smart deduplication
    - Console error output
    """
    
    def __init__(self, server_dir: str, config_file: str = "logging.json"):
        self.server_dir = Path(server_dir)
        self.config_file = self.server_dir / config_file
        self.config = self._load_config()
        
        # Set up log file
        self.log_file = self.server_dir / self.config["file"]
        self._initialize_log_file()
        
        # Deduplication tracking
        self.last_message = None
        self.duplicate_count = 0
        self.max_duplicates = self.config.get("max_duplicates", 3)
        
        # System health tracking
        self.health_stats = {
            "observer_events": 0,
            "actor_commands": 0,
            "sessions_active": 0,
            "errors_count": 0,
            "warnings_count": 0,
            "last_summary": time.time()
        }
        
        # Thread lock for thread-safe logging
        self._lock = threading.Lock()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load logging configuration from JSON file"""
        default_config = {
            "level": "INFO",
            "file": "server.log",
            "summary_interval": 30,
            "console_errors": True,
            "deduplication": True,
            "max_duplicates": 3,
            "timestamp_format": "%Y-%m-%d %H:%M:%S.%f"
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**default_config, **config}
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            print(f"Error loading logging config: {e}, using defaults")
            return default_config
    
    def _initialize_log_file(self):
        """Initialize log file with startup marker"""
        try:
            startup_time = datetime.now().strftime(self.config["timestamp_format"])[:-3]
            startup_message = f"=== SERVER STARTUP {startup_time} ==="
            
            # Reset log file on startup (for development)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(startup_message)
                
        except Exception as e:
            print(f"Error initializing log file: {e}")
    
    def _format_timestamp(self) -> str:
        """Generate formatted timestamp"""
        return datetime.now().strftime(self.config["timestamp_format"])[:-3]
    
    def _normalize_message(self, message: str) -> str:
        """Normalize message for deduplication by removing dynamic content"""
        import re
        
        # Remove timestamps
        message = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}', '[TIMESTAMP]', message)
        
        # Remove session IDs and UUIDs  
        message = re.sub(r'\b[a-zA-Z0-9_]{20,}\b', '[ID]', message)
        
        # Remove numbers in "Consumed X events, Y total processed"
        message = re.sub(r'Consumed \d+ events, \d+ total processed', 'Consumed [N] events, [N] total processed', message)
        
        # Remove numbers in "Retrieved X recent events"
        message = re.sub(r'Retrieved \d+ recent events', 'Retrieved [N] recent events', message)
        
        # Remove numbers in "Retrieved X pending commands"  
        message = re.sub(r'Retrieved \d+ pending commands', 'Retrieved [N] pending commands', message)
        
        # Remove other counts (but preserve important non-numeric patterns)
        message = re.sub(r'\b\d+\b', '[NUM]', message)
        
        return message.strip()
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged based on current log level"""
        current_level = LogLevel[self.config["level"]]
        return level.value >= current_level.value
    
    def _write_to_file(self, formatted_message: str):
        """Write message to log file"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_message + '\n')
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def _output_to_console(self, level: LogLevel, message: str):
        """Output message to console based on level and config"""
        if level in [LogLevel.ERROR, LogLevel.WARN] and self.config["console_errors"]:
            # Format for console (no timestamp for cleaner output)
            level_prefix = f"[{level.name}]" if level in [LogLevel.ERROR, LogLevel.WARN] else ""
            console_message = f"{level_prefix} {message}".strip()
            print(console_message)
    
    def _handle_deduplication(self, normalized_message: str, level: LogLevel, original_message: str) -> bool:
        """Handle message deduplication. Returns True if message should be skipped"""
        if not self.config["deduplication"]:
            return False
            
        with self._lock:
            if normalized_message == self.last_message:
                self.duplicate_count += 1
                
                # For first few duplicates, still log them
                if self.duplicate_count < self.max_duplicates:
                    return False
                    
                # Beyond threshold, skip logging but track
                return True
            else:
                # New message - log duplicate summary if needed
                if self.duplicate_count >= self.max_duplicates:
                    timestamp = self._format_timestamp()
                    summary = f"[{timestamp}] [System] ... {self.duplicate_count} similar messages suppressed"
                    self._write_to_file(summary)
                    
                # Reset tracking
                self.last_message = normalized_message
                self.duplicate_count = 0
                return False
    
    def _update_health_stats(self, message: str):
        """Update system health statistics based on log message"""
        message_lower = message.lower()
        
        if "observer event" in message_lower or "session event" in message_lower:
            self.health_stats["observer_events"] += 1
        elif "actor command" in message_lower or "actor event" in message_lower:
            self.health_stats["actor_commands"] += 1
        elif "session init" in message_lower:
            self.health_stats["sessions_active"] += 1
        elif "error" in message_lower:
            self.health_stats["errors_count"] += 1
        elif "warning" in message_lower or "warn" in message_lower:
            self.health_stats["warnings_count"] += 1
    
    def _check_summary(self):
        """Check if it's time to generate a health summary"""
        current_time = time.time()
        interval = self.config.get("summary_interval", 30)
        
        if current_time - self.health_stats["last_summary"] >= interval:
            self._generate_health_summary()
            self.health_stats["last_summary"] = current_time
    
    def _generate_health_summary(self):
        """Generate periodic health summary for INFO level"""
        if not self._should_log(LogLevel.INFO):
            return
            
        timestamp = self._format_timestamp()
        
        # Create health summary
        summary_lines = [
            f"[{timestamp}] [System Health] === PERIODIC SYSTEM HEALTH SUMMARY ===",
            f"[{timestamp}] [System Health] Observer events: {self.health_stats['observer_events']} received",
            f"[{timestamp}] [System Health] Actor commands: {self.health_stats['actor_commands']} sent", 
            f"[{timestamp}] [System Health] Active sessions: {self.health_stats['sessions_active']}",
            f"[{timestamp}] [System Health] Errors: {self.health_stats['errors_count']}, Warnings: {self.health_stats['warnings_count']}"
        ]
        
        # Write to file
        for line in summary_lines:
            self._write_to_file(line)
            
        # Also output to console for visibility
        print("\n".join([line.split("] ", 2)[-1] for line in summary_lines]))
        print()  # Extra line for readability
        
        # Reset counters after summary
        self.health_stats["observer_events"] = 0
        self.health_stats["actor_commands"] = 0
        self.health_stats["errors_count"] = 0
        self.health_stats["warnings_count"] = 0
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        Main logging method
        
        Args:
            message: Message to log
            level: Logging level (DEBUG, INFO, WARN, ERROR)
        """
        # Check if we should log this level
        if not self._should_log(level):
            return
        
        # Update health statistics
        self._update_health_stats(message)
        
        # Check for periodic summary
        if level == LogLevel.INFO:
            self._check_summary()
        
        # Normalize message for deduplication
        normalized_message = self._normalize_message(message)
        
        # Handle deduplication
        if self._handle_deduplication(normalized_message, level, message):
            return  # Skip this duplicate message
        
        # Format message with timestamp and level
        timestamp = self._format_timestamp()
        level_prefix = f"[{level.name}]" if level in [LogLevel.ERROR, LogLevel.WARN] else ""
        
        # Determine source context from message
        if "[" in message and "]" in message:
            # Message already has context
            formatted_message = f"[{timestamp}] {level_prefix} {message}".strip()
        else:
            # Add generic context
            formatted_message = f"[{timestamp}] {level_prefix} [Server] {message}".strip()
        
        # Clean up double spaces
        formatted_message = " ".join(formatted_message.split())
        
        # Write to file
        self._write_to_file(formatted_message)
        
        # Output to console if appropriate
        self._output_to_console(level, message)

# Global logger instance
_logger: Optional[UnifiedLogger] = None

def initialize_logger(server_dir: str, is_detached: bool = False):
    """Initialize the global logger instance"""
    global _logger
    _logger = UnifiedLogger(server_dir)

def log(message: str, skip_console: bool = False):
    """
    Global logging function - maintains compatibility with existing code
    
    Args:
        message: Message to log
        skip_console: Ignored (kept for backward compatibility)
    """
    if _logger is None:
        # Fallback if logger not initialized
        print(message)
        return
    
    # Default to INFO level for backward compatibility
    _logger.log(message, LogLevel.INFO)

def log_debug(message: str):
    """Log DEBUG level message"""
    if _logger:
        _logger.log(message, LogLevel.DEBUG)

def log_info(message: str):
    """Log INFO level message"""
    if _logger:
        _logger.log(message, LogLevel.INFO)

def log_warn(message: str):
    """Log WARN level message"""
    if _logger:
        _logger.log(message, LogLevel.WARN)

def log_error(message: str):
    """Log ERROR level message"""
    if _logger:
        _logger.log(message, LogLevel.ERROR)

def get_log_file() -> Optional[Path]:
    """Get the current log file path"""
    return _logger.log_file if _logger else None

def reload_config():
    """Reload logging configuration from file"""
    if _logger:
        _logger.config = _logger._load_config()