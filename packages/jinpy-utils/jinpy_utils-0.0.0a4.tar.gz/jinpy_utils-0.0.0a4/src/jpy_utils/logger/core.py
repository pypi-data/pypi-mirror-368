"""Core logger implementation following SOLID principles.

This module provides the main Logger class with singleton support,
global configuration, and high-performance async/sync logging.
"""

import asyncio
import inspect
import sys
import threading
import uuid
import weakref
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager, suppress
from typing import Any, ClassVar, Optional

from jpy_utils.logger.backends import BackendFactory, BackendInterface, LogEntry
from jpy_utils.logger.config import GlobalLoggerConfig, LoggerConfig
from jpy_utils.logger.enums import LogLevel
from jpy_utils.logger.exceptions import (
    JPYLoggerConfigurationError,
    JPYLoggerError,
    JPYLoggerPerformanceError,
)
from jpy_utils.utils.timing import get_current_datetime


class LoggerManager:
    """Singleton manager for global logger configuration and instances."""

    _instance: Optional["LoggerManager"] = None
    _lock = threading.Lock()
    _instances: ClassVar[dict[str, "Logger"]] = {}
    _global_config: GlobalLoggerConfig | None = None

    def __new__(cls) -> "LoggerManager":
        """Ensure singleton pattern."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize manager if not already done."""
        if not getattr(self, "_initialized", False):
            self._initialized = True
            self._cleanup_registry: set[weakref.ReferenceType] = set()
            self._background_tasks: set[asyncio.Task] = set()

    def set_global_config(self, config: GlobalLoggerConfig) -> None:
        """Set global configuration."""
        with self._lock:
            self._global_config = config

            # Update existing loggers if needed
            for logger in self._instances.values():
                logger._update_global_config(config)

    def get_global_config(self) -> GlobalLoggerConfig | None:
        """Get global configuration."""
        return self._global_config

    def get_logger(
        self,
        name: str,
        config: LoggerConfig | None = None,
        force_new: bool = False,
    ) -> "Logger":
        """Get logger instance with optional singleton behavior."""
        if not self._global_config:
            raise JPYLoggerConfigurationError(
                message="Global configuration not set. Call set_global_config() first.",
                config_section="global",
            )

        # Check if singleton is enabled and instance exists
        if (
            self._global_config.enable_singleton
            and not force_new
            and name in self._instances
        ):
            return self._instances[name]

        # Create new instance
        logger = Logger(
            name,
            config or LoggerConfig(name=name),
            self._global_config,
        )

        # Store if singleton is enabled or explicitly requested
        if self._global_config.enable_singleton or not force_new:
            with self._lock:
                self._instances[name] = logger

                # Register for cleanup
                ref = weakref.ref(logger, self._cleanup_instance)
                self._cleanup_registry.add(ref)

        return logger

    def _cleanup_instance(self, ref: weakref.ReferenceType) -> None:
        """Cleanup dead references."""
        self._cleanup_registry.discard(ref)

    def shutdown_all(self) -> None:
        """Shutdown all logger instances.

        If an event loop is running, schedule asynchronous closes. Otherwise,
        close each logger using ``asyncio.run`` to ensure cleanup occurs in
        synchronous contexts too.
        """
        with self._lock:
            for logger in list(self._instances.values()):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    asyncio.run(logger.close())
                else:
                    task = loop.create_task(logger.close())
                    self._background_tasks.add(task)
                    task.add_done_callback(self._background_tasks.discard)
                    # best-effort: do not await here
            self._instances.clear()
            self._cleanup_registry.clear()

    def get_all_loggers(self) -> list["Logger"]:
        """Get all active logger instances."""
        with self._lock:
            return list(self._instances.values())


class Logger:
    """
    High-performance structured logger with async/sync support.

    Features:
    - SOLID principles compliance
    - Singleton and instance modes
    - Multiple backend support
    - Async/sync operations
    - Context management
    - Performance optimization
    - Security features
    - 12-factor app compliance

    Example:
        ```
        # Global configuration
        global_config = GlobalLoggerConfig.from_env()
        LoggerManager().set_global_config(global_config)

        # Get logger instance
        logger = Logger.get_logger("myapp")

        # Basic logging
        logger.info("Application started", {"version": "1.0.0"})
        await logger.ainfo("Async operation completed")

        # Context management
        with logger.context(user_id=123):
            logger.info("User action")
        ```
    """

    def __init__(
        self,
        name: str,
        config: LoggerConfig,
        global_config: GlobalLoggerConfig,
    ):
        """
        Initialize logger instance.

        Args:
            name: Logger name
            config: Logger-specific configuration
            global_config: Global logger configuration
        """
        self.name = name
        self.config = config
        self.global_config = global_config

        # State management
        self._closed = False
        self._context: dict[str, Any] = config.context.copy()
        self._correlation_id = config.correlation_id

        # Performance tracking
        self._stats: dict[str, Any] = {
            "messages_logged": 0,
            "messages_dropped": 0,
            "bytes_processed": 0,
            "start_time": get_current_datetime(),
            "last_log_time": None,
        }

        # Initialize backends
        self._backends: list[BackendInterface] = []
        self._initialize_backends()

        # Async processing
        self._async_queue: asyncio.Queue | None = None
        self._processor_task: asyncio.Task | None = None
        self._setup_async_processing()

        # Security and sanitization
        self._sensitive_fields = set(global_config.sensitive_fields)

    def _initialize_backends(self) -> None:
        """Initialize backends based on configuration."""
        try:
            # Determine which backends to use
            if self.config.backends:
                # Use specific backends
                backend_configs = [
                    backend
                    for backend in self.global_config.backends
                    if backend.name in self.config.backends and backend.enabled
                ]
            else:
                # Use all enabled global backends
                backend_configs = [
                    backend
                    for backend in self.global_config.backends
                    if backend.enabled
                ]

            if not backend_configs:
                raise JPYLoggerConfigurationError(
                    message="No enabled backends found",
                    config_section="backends",
                )

            # Create backend instances
            for backend_config in backend_configs:
                try:
                    backend = BackendFactory.create_backend(backend_config)
                    self._backends.append(backend)
                except Exception as e:
                    raise JPYLoggerConfigurationError(
                        message=f"Failed to initialize backend {backend_config.name}: {e}",
                        config_section="backends",
                        config_value=backend_config.name,
                    ) from e

        except Exception as e:
            raise JPYLoggerError(
                message=f"Backend initialization failed: {e}",
                logger_name=self.name,
                operation="initialize_backends",
            ) from e

    def _setup_async_processing(self) -> None:
        """Setup async processing queue and background task if supported."""
        if any(hasattr(backend, "_async_capable") for backend in self._backends):
            self._async_queue = asyncio.Queue(
                maxsize=self.global_config.async_queue_size
            )
            try:
                asyncio.get_running_loop()
                self._processor_task = asyncio.create_task(
                    self._process_async_queue(),
                )
            except RuntimeError:
                # No running loop; task will be created lazily by caller if needed
                self._processor_task = None

    async def _process_async_queue(self) -> None:
        """Process async logging queue."""
        while not self._closed:
            try:
                # Get entry with timeout to allow periodic cleanup
                if self._async_queue is None:
                    raise ValueError("self._async_queue can not be None")

                entry = await asyncio.wait_for(
                    self._async_queue.get(),
                    timeout=1.0,
                )

                await self._write_to_backends_async(entry)
                self._async_queue.task_done()

            except TimeoutError:
                continue
            except Exception as e:
                self._handle_processing_error(e)

    def _handle_processing_error(self, error: Exception) -> None:
        """Handle async processing errors."""
        self._stats["messages_dropped"] = int(self._stats["messages_dropped"]) + 1

        # Log to stderr to avoid recursion
        print(f"Logger {self.name} processing error: {error}", file=sys.stderr)

    def _get_effective_level(self) -> LogLevel:
        """Get effective log level."""
        return self.config.level or self.global_config.default_level

    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged based on level."""
        return level >= self._get_effective_level()

    def _sanitize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Sanitize sensitive data from context."""
        if not self.global_config.enable_sanitization:
            return context

        sanitized = {}
        for key, value in context.items():
            if any(sensitive in key.lower() for sensitive in self._sensitive_fields):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value

        return sanitized

    def _create_log_entry(
        self,
        level: LogLevel,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> LogEntry:
        """Create structured log entry with context and metadata."""
        # Merge contexts: instance -> method parameter
        merged_context = self._context.copy()
        if context:
            # Check context size limit
            context_str = str(context)
            if len(context_str) > self.global_config.max_context_size:
                context = {
                    "_context_truncated": True,
                    "_original_size": len(context_str),
                    "_truncated_at": get_current_datetime().isoformat(),
                }

            merged_context.update(context)

        # Sanitize context
        if merged_context:
            merged_context = self._sanitize_context(merged_context)

        # Generate correlation ID if needed
        correlation_id = self._correlation_id
        if self.global_config.enable_correlation_ids and not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Get caller information
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back if frame and frame.f_back else None

        module_name = None
        function_name = None
        line_number = None

        if caller_frame:
            module_name = caller_frame.f_globals.get("__name__")
            function_name = caller_frame.f_code.co_name
            line_number = caller_frame.f_lineno

        return LogEntry(
            timestamp=get_current_datetime(),
            level=level,
            message=message,
            logger_name=self.name,
            correlation_id=correlation_id,
            context=merged_context,
            module=module_name,
            function=function_name,
            line_number=line_number,
        )

    async def _write_to_backends_async(self, entry: LogEntry) -> None:
        """Write entry to all backends asynchronously."""
        tasks = []
        for backend in self._backends:
            if backend.is_healthy():
                tasks.append(self._safe_backend_write_async(backend, entry))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_backend_write_async(
        self, backend: BackendInterface, entry: LogEntry
    ) -> None:
        """Safely write to backend with error handling."""
        try:
            await backend.write_async(entry)
        except Exception as e:
            self._stats["messages_dropped"] = int(self._stats["messages_dropped"]) + 1
            # Log backend error without recursion
            print(f"Backend {backend.name} error: {e}", file=sys.stderr)

    def _write_to_backends_sync(self, entry: LogEntry) -> None:
        """Write entry to all backends synchronously."""
        for backend in self._backends:
            try:
                if backend.is_healthy():
                    backend.write_sync(entry)
            except Exception as e:
                self._stats["messages_dropped"] = (
                    int(self._stats["messages_dropped"]) + 1
                )
                # Log backend error without recursion
                print(f"Backend {backend.name} error: {e}", file=sys.stderr)

    def _update_stats(self, entry: LogEntry) -> None:
        """Update logger statistics."""
        self._stats["messages_logged"] = int(self._stats["messages_logged"]) + 1
        self._stats["bytes_processed"] = int(self._stats["bytes_processed"]) + len(
            str(entry.to_dict())
        )
        self._stats["last_log_time"] = get_current_datetime()

        # Performance monitoring
        if self.global_config.enable_performance_metrics:
            current_time = get_current_datetime()
            if self._stats["last_log_time"] is not None:
                time_diff = (
                    current_time - self._stats["last_log_time"]
                ).total_seconds()
                if time_diff > 1.0:  # Alert if logging takes too long
                    raise JPYLoggerPerformanceError(
                        message="Logging performance degraded",
                        logger_name=self.name,
                        performance_metric="log_latency",
                        threshold_value=1.0,
                        actual_value=time_diff,
                    )

    # Synchronous logging methods
    def log(
        self,
        level: LogLevel,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Log message at specified level synchronously.

        Args:
            level: Log level
            message: Log message
            context: Additional context data
        """
        if not self._should_log(level) or self._closed:
            return

        try:
            entry = self._create_log_entry(level, message, context)
            self._write_to_backends_sync(entry)
            self._update_stats(entry)
        except Exception as e:
            raise JPYLoggerError(
                message=f"Synchronous logging failed: {e}",
                logger_name=self.name,
                operation="log",
            ) from e

    def trace(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log trace message synchronously."""
        self.log(LogLevel.TRACE, message, context)

    def debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log debug message synchronously."""
        self.log(LogLevel.DEBUG, message, context)

    def info(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log info message synchronously."""
        self.log(LogLevel.INFO, message, context)

    def warning(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log warning message synchronously."""
        self.log(LogLevel.WARNING, message, context)

    def error(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log error message synchronously."""
        self.log(LogLevel.ERROR, message, context)

    def critical(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log critical message synchronously."""
        self.log(LogLevel.CRITICAL, message, context)

    # Asynchronous logging methods
    async def alog(
        self, level: LogLevel, message: str, context: dict[str, Any] | None = None
    ) -> None:
        """
        Log message at specified level asynchronously.

        Args:
            level: Log level
            message: Log message
            context: Additional context data
        """
        if not self._should_log(level) or self._closed:
            return

        try:
            entry = self._create_log_entry(level, message, context)

            # Use async queue if available and not full
            if self._async_queue and not self._async_queue.full():
                await self._async_queue.put(entry)
            else:
                # Fallback to direct write
                await self._write_to_backends_async(entry)

            self._update_stats(entry)
        except Exception as e:
            raise JPYLoggerError(
                message=f"Asynchronous logging failed: {e}",
                logger_name=self.name,
                operation="alog",
            ) from e

    async def atrace(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log trace message asynchronously."""
        await self.alog(LogLevel.TRACE, message, context)

    async def adebug(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log debug message asynchronously."""
        await self.alog(LogLevel.DEBUG, message, context)

    async def ainfo(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log info message asynchronously."""
        await self.alog(LogLevel.INFO, message, context)

    async def awarning(
        self, message: str, context: dict[str, Any] | None = None
    ) -> None:
        """Log warning message asynchronously."""
        await self.alog(LogLevel.WARNING, message, context)

    async def aerror(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log error message asynchronously."""
        await self.alog(LogLevel.ERROR, message, context)

    async def acritical(
        self, message: str, context: dict[str, Any] | None = None
    ) -> None:
        """Log critical message asynchronously."""
        await self.alog(LogLevel.CRITICAL, message, context)

    # Context management
    @contextmanager
    def context(self, **kwargs: Any) -> Generator[None, None, None]:
        """
        Context manager for adding temporary context to logs.

        Args:
            **kwargs: Context key-value pairs
        """
        old_context = self._context.copy()
        self._context.update(kwargs)
        try:
            yield
        finally:
            self._context = old_context

    @asynccontextmanager
    async def acontext(self, **kwargs: Any) -> AsyncGenerator[None, None]:
        """
        Async context manager for adding temporary context to logs.

        Args:
            **kwargs: Context key-value pairs
        """
        old_context = self._context.copy()
        self._context.update(kwargs)
        try:
            yield
        finally:
            self._context = old_context

    def bind(self, **kwargs: Any) -> "Logger":
        """
        Create a child logger with bound context.

        Args:
            **kwargs: Context to bind to new logger

        Returns:
            New logger instance with bound context
        """
        child_config = LoggerConfig(
            name=f"{self.name}.child",
            level=self.config.level,
            backends=self.config.backends,
            context={**self._context, **kwargs},
            correlation_id=self._correlation_id,
        )

        return Logger(child_config.name, child_config, self.global_config)

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for this logger instance."""
        self._correlation_id = correlation_id

    def get_correlation_id(self) -> str | None:
        """Get current correlation ID."""
        return self._correlation_id

    def set_level(self, level: LogLevel) -> None:
        """Set log level for this logger."""
        self.config.level = level

    def get_level(self) -> LogLevel:
        """Get current log level."""
        return self._get_effective_level()

    def is_enabled_for(self, level: LogLevel) -> bool:
        """Check if logging is enabled for given level."""
        return level >= self._get_effective_level()

    # Performance and maintenance
    async def flush(self) -> None:
        """Flush all pending log entries."""
        if self._async_queue:
            await self._async_queue.join()

        # Flush all backends
        flush_tasks = []
        for backend in self._backends:
            if hasattr(backend, "flush"):
                flush_tasks.append(backend.flush())

        if flush_tasks:
            await asyncio.gather(*flush_tasks, return_exceptions=True)

    def get_stats(self) -> dict[str, Any]:
        """Get logger statistics."""
        stats = self._stats.copy()
        stats["backend_count"] = len(self._backends)
        stats["healthy_backends"] = sum(1 for b in self._backends if b.is_healthy())
        start_time = self._stats["start_time"]
        stats["uptime_seconds"] = (get_current_datetime() - start_time).total_seconds()
        return stats

    def get_backend_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all backends."""
        return {
            backend.name: backend.get_stats()
            for backend in self._backends
            if hasattr(backend, "get_stats")
        }

    def _update_global_config(self, config: GlobalLoggerConfig) -> None:
        """Update logger when global config changes."""
        self.global_config = config
        self._sensitive_fields = set(config.sensitive_fields)

    async def close(self) -> None:
        """Close logger and cleanup resources."""
        if self._closed:
            return

        self._closed = True

        # Cancel async processor
        if self._processor_task:
            self._processor_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._processor_task

        # Flush and close all backends
        await self.flush()
        close_tasks = []
        for backend in self._backends:
            close_tasks.append(backend.close())

        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)

    # Class methods for convenience
    @classmethod
    def get_logger(
        cls, name: str, config: LoggerConfig | None = None, force_new: bool = False
    ) -> "Logger":
        """Get logger instance through manager."""
        return LoggerManager().get_logger(name, config, force_new)

    @classmethod
    def set_global_config(cls, config: GlobalLoggerConfig) -> None:
        """Set global configuration."""
        LoggerManager().set_global_config(config)

    @classmethod
    def from_env(cls, name: str, env_prefix: str = "LOGGER_") -> "Logger":
        """Create logger from environment variables."""
        global_config = GlobalLoggerConfig.from_env(env_prefix)
        cls.set_global_config(global_config)
        return cls.get_logger(name)

    def __del__(self) -> None:
        """Avoid async work in finalizer.

        Resource cleanup should be explicit via ``close()`` or
        ``LoggerManager.shutdown_all()``. Doing asynchronous work in
        ``__del__`` is unreliable and may emit warnings depending on
        interpreter shutdown timing and event loop state.
        """
        return None


# Convenience functions
def get_logger(
    name: str, config: LoggerConfig | None = None, force_new: bool = False
) -> Logger:
    """Get logger instance."""
    return Logger.get_logger(name, config, force_new)


def set_global_config(config: GlobalLoggerConfig) -> None:
    """Set global logger configuration."""
    Logger.set_global_config(config)


def configure_from_env(env_prefix: str = "LOGGER_") -> None:
    """Configure global logger from environment variables."""
    config = GlobalLoggerConfig.from_env(env_prefix)
    set_global_config(config)


def shutdown_all_loggers() -> None:
    """Shutdown all logger instances."""
    LoggerManager().shutdown_all()
