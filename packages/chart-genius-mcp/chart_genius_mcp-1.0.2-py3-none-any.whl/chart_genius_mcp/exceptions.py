"""
ChartGenius MCP Exceptions
==========================

Custom exception classes for ChartGenius MCP server.
"""


class ChartGeniusError(Exception):
    """Base exception for all ChartGenius MCP errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "CHART_GENIUS_ERROR"
        self.details = details or {}


class ChartGenerationError(ChartGeniusError):
    """Exception raised when chart generation fails."""
    
    def __init__(self, message: str, chart_type: str = None, engine: str = None, **kwargs):
        super().__init__(message, error_code="CHART_GENERATION_ERROR", **kwargs)
        self.chart_type = chart_type
        self.engine = engine


class DataOptimizationError(ChartGeniusError):
    """Exception raised when data optimization fails."""
    
    def __init__(self, message: str, strategy: str = None, data_size: int = None, **kwargs):
        super().__init__(message, error_code="DATA_OPTIMIZATION_ERROR", **kwargs)
        self.strategy = strategy
        self.data_size = data_size


class EngineNotFoundError(ChartGeniusError):
    """Exception raised when a chart engine is not found or available."""
    
    def __init__(self, engine: str, available_engines: list = None):
        message = f"Chart engine '{engine}' not found"
        if available_engines:
            message += f". Available engines: {', '.join(available_engines)}"
        
        super().__init__(message, error_code="ENGINE_NOT_FOUND")
        self.engine = engine
        self.available_engines = available_engines or []


class ThemeNotFoundError(ChartGeniusError):
    """Exception raised when a theme is not found."""
    
    def __init__(self, theme: str, available_themes: list = None):
        message = f"Theme '{theme}' not found"
        if available_themes:
            message += f". Available themes: {', '.join(available_themes)}"
        
        super().__init__(message, error_code="THEME_NOT_FOUND")
        self.theme = theme
        self.available_themes = available_themes or []


class ConfigurationError(ChartGeniusError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key


class CacheError(ChartGeniusError):
    """Exception raised for caching-related errors."""
    
    def __init__(self, message: str, operation: str = None, **kwargs):
        super().__init__(message, error_code="CACHE_ERROR", **kwargs)
        self.operation = operation


class AIServiceError(ChartGeniusError):
    """Exception raised for AI service-related errors."""
    
    def __init__(self, message: str, service: str = None, **kwargs):
        super().__init__(message, error_code="AI_SERVICE_ERROR", **kwargs)
        self.service = service


class ValidationError(ChartGeniusError):
    """Exception raised for data validation errors."""
    
    def __init__(self, message: str, field: str = None, value = None, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        self.value = value


class PerformanceError(ChartGeniusError):
    """Exception raised when performance thresholds are exceeded."""
    
    def __init__(self, message: str, operation: str = None, duration_ms: float = None, **kwargs):
        super().__init__(message, error_code="PERFORMANCE_ERROR", **kwargs)
        self.operation = operation
        self.duration_ms = duration_ms


class ResourceLimitError(ChartGeniusError):
    """Exception raised when resource limits are exceeded."""
    
    def __init__(self, message: str, resource: str = None, limit = None, current = None, **kwargs):
        super().__init__(message, error_code="RESOURCE_LIMIT_ERROR", **kwargs)
        self.resource = resource
        self.limit = limit
        self.current = current 