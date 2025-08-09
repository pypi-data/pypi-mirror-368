"""
Configuration - ChartGenius MCP Server Settings
===============================================

Centralized configuration for optimal performance and customization.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

# Performance constants
DEFAULT_TARGET_CHART_GENERATION_TIME_MS = 100
DEFAULT_MAX_CHART_GENERATION_TIME_MS = 5000
DEFAULT_MEMORY_LIMIT_MB = 1024
DEFAULT_CACHE_TTL = 3600  # 1 hour
DEFAULT_CACHE_MAX_SIZE = 1000
DEFAULT_MAX_CONCURRENT_CHARTS = 10
DEFAULT_LARGE_DATASET_THRESHOLD = 1000
DEFAULT_MAX_DATA_POINTS = 10000


@dataclass
class ChartGeniusConfig:
    """
    Configuration class for ChartGenius MCP Server.
    
    Provides smart defaults while allowing full customization for
    performance optimization and feature control.
    """
    
    # Core server settings
    server_name: str = "chart-genius"
    version: str = "1.0.0"
    host: str = "localhost"
    port: int = 8000
    
    # Performance settings
    performance_monitoring: bool = True
    cache_enabled: bool = True
    cache_ttl: int = DEFAULT_CACHE_TTL
    max_concurrent_charts: int = DEFAULT_MAX_CONCURRENT_CHARTS
    
    # Data optimization settings
    auto_optimize_large_datasets: bool = True
    large_dataset_threshold: int = DEFAULT_LARGE_DATASET_THRESHOLD
    max_data_points: int = DEFAULT_MAX_DATA_POINTS
    optimization_strategy: str = "intelligent"  # intelligent, sample, aggregate
    
    # Chart generation settings
    default_engine: str = "plotly"
    default_theme: str = "modern"
    default_format: str = "json"
    enable_ai_features: bool = True
    
    # Supported engines and their capabilities
    enabled_engines: List[str] = field(default_factory=lambda: [
        "plotly", "matplotlib", "seaborn"
    ])
    
    # Cache settings
    cache_type: str = "memory"  # memory, redis, file
    cache_max_size: int = DEFAULT_CACHE_MAX_SIZE  # Maximum cached items
    redis_url: Optional[str] = None
    cache_directory: Optional[str] = None
    
    # AI settings
    ai_chart_detection: bool = True
    ai_insight_generation: bool = True
    openai_api_key: Optional[str] = None
    ai_model: str = "gpt-4"
    
    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_performance_logging: bool = True
    
    # Security settings
    enable_cors: bool = True
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    max_request_size: int = 100 * 1024 * 1024  # 100MB
    
    # Export settings
    export_directory: Optional[str] = None
    max_export_size: int = 50 * 1024 * 1024  # 50MB
    allowed_export_formats: List[str] = field(default_factory=lambda: [
        "png", "svg", "pdf", "html", "json"
    ])
    
    # Theme settings
    available_themes: List[str] = field(default_factory=lambda: [
        "modern", "corporate", "dark", "accessible", "colorful", "minimal"
    ])
    
    # Performance benchmarks and limits
    target_chart_generation_time_ms: int = DEFAULT_TARGET_CHART_GENERATION_TIME_MS
    max_chart_generation_time_ms: int = DEFAULT_MAX_CHART_GENERATION_TIME_MS
    memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB
    
    def __post_init__(self):
        """Initialize configuration after creation."""
        self._load_from_environment()
        self._validate_configuration()
        self._setup_directories()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        
        # Server settings
        self.host = os.getenv("CHART_GENIUS_HOST", self.host)
        self.port = int(os.getenv("CHART_GENIUS_PORT", self.port))
        
        # Performance settings
        self.cache_enabled = os.getenv("CHART_CACHE_ENABLED", "true").lower() == "true"
        self.cache_ttl = int(os.getenv("CHART_CACHE_TTL", self.cache_ttl))
        self.performance_monitoring = os.getenv("CHART_PERFORMANCE_MONITORING", "true").lower() == "true"
        
        # Data optimization
        self.auto_optimize_large_datasets = os.getenv("CHART_AUTO_OPTIMIZE", "true").lower() == "true"
        self.large_dataset_threshold = int(os.getenv("CHART_LARGE_DATASET_THRESHOLD", self.large_dataset_threshold))
        self.max_data_points = int(os.getenv("CHART_MAX_DATA_POINTS", self.max_data_points))
        self.optimization_strategy = os.getenv("CHART_OPTIMIZATION_STRATEGY", self.optimization_strategy)
        
        # Chart settings
        self.default_engine = os.getenv("CHART_DEFAULT_ENGINE", self.default_engine)
        self.default_theme = os.getenv("CHART_DEFAULT_THEME", self.default_theme)
        self.default_format = os.getenv("CHART_DEFAULT_FORMAT", self.default_format)
        
        # AI settings
        self.enable_ai_features = os.getenv("CHART_AI_FEATURES", "true").lower() == "true"
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.ai_model = os.getenv("CHART_AI_MODEL", self.ai_model)
        
        # Cache settings
        self.cache_type = os.getenv("CHART_CACHE_TYPE", self.cache_type)
        self.redis_url = os.getenv("REDIS_URL", self.redis_url)
        self.cache_directory = os.getenv("CHART_CACHE_DIRECTORY", self.cache_directory)
        
        # Logging
        self.log_level = os.getenv("CHART_LOG_LEVEL", self.log_level)
        self.log_file = os.getenv("CHART_LOG_FILE", self.log_file)
        
        # Export settings
        self.export_directory = os.getenv("CHART_EXPORT_DIRECTORY", self.export_directory)
    
    def _validate_configuration(self):
        """Validate configuration settings."""
        
        # Validate engines
        supported_engines = ["plotly", "matplotlib", "seaborn", "d3"]
        for engine in self.enabled_engines:
            if engine not in supported_engines:
                raise ValueError(f"Unsupported engine: {engine}. Supported: {supported_engines}")
        
        # Validate optimization strategy
        valid_strategies = ["intelligent", "sample", "aggregate"]
        if self.optimization_strategy not in valid_strategies:
            raise ValueError(f"Invalid optimization strategy: {self.optimization_strategy}. Valid: {valid_strategies}")
        
        # Validate cache type
        valid_cache_types = ["memory", "redis", "file"]
        if self.cache_type not in valid_cache_types:
            raise ValueError(f"Invalid cache type: {self.cache_type}. Valid: {valid_cache_types}")
        
        # Validate Redis URL if using Redis cache
        if self.cache_type == "redis" and not self.redis_url:
            raise ValueError("Redis URL required when using Redis cache")
        
        # Validate thresholds
        if self.large_dataset_threshold <= 0:
            raise ValueError("Large dataset threshold must be positive")
        
        if self.max_data_points < self.large_dataset_threshold:
            raise ValueError("Max data points must be >= large dataset threshold")
        
        # Validate AI settings
        if self.enable_ai_features and not self.openai_api_key:
            self.enable_ai_features = False
            print("Warning: AI features disabled due to missing OpenAI API key")
    
    def _setup_directories(self):
        """Setup required directories."""
        
        # Setup cache directory
        if self.cache_type == "file" and not self.cache_directory:
            self.cache_directory = str(Path.home() / ".chart-genius" / "cache")
        
        if self.cache_directory:
            Path(self.cache_directory).mkdir(parents=True, exist_ok=True)
        
        # Setup export directory
        if not self.export_directory:
            self.export_directory = str(Path.home() / ".chart-genius" / "exports")
        
        Path(self.export_directory).mkdir(parents=True, exist_ok=True)
        
        # Setup log directory if log file specified
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_engine_config(self, engine: str) -> Dict[str, Any]:
        """Get configuration for a specific chart engine."""
        
        engine_configs = {
            "plotly": {
                "renderer": "json",
                "include_plotlyjs": False,
                "config": {
                    "displayModeBar": True,
                    "responsive": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": "chart",
                        "height": 600,
                        "width": 800,
                        "scale": 2
                    }
                }
            },
            "matplotlib": {
                "backend": "Agg",
                "dpi": 300,
                "figsize": (10, 6),
                "style": "seaborn-v0_8",
                "transparent": False
            },
            "seaborn": {
                "style": "whitegrid",
                "palette": "husl",
                "context": "notebook",
                "font_scale": 1.0
            },
            "d3": {
                "version": "7",
                "output_format": "svg",
                "responsive": True
            }
        }
        
        return engine_configs.get(engine, {})
    
    def get_theme_config(self, theme: str) -> Dict[str, Any]:
        """Get configuration for a specific theme."""
        
        theme_configs = {
            "modern": {
                "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
                "background": "#ffffff",
                "grid": "#f0f0f0",
                "text": "#333333",
                "font_family": "Arial, sans-serif",
                "border_radius": 8
            },
            "corporate": {
                "colors": ["#2E86C1", "#F39C12", "#28B463", "#E74C3C", "#8E44AD"],
                "background": "#ffffff",
                "grid": "#e8e8e8",
                "text": "#2c3e50",
                "font_family": "Helvetica, Arial, sans-serif",
                "border_radius": 4
            },
            "dark": {
                "colors": ["#00d4ff", "#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24"],
                "background": "#2c3e50",
                "grid": "#34495e",
                "text": "#ecf0f1",
                "font_family": "Arial, sans-serif",
                "border_radius": 8
            },
            "accessible": {
                "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
                "background": "#ffffff",
                "grid": "#000000",
                "text": "#000000",
                "font_family": "Arial, sans-serif",
                "border_radius": 0,
                "high_contrast": True
            },
            "colorful": {
                "colors": ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24", "#f0932b"],
                "background": "#ffffff",
                "grid": "#f8f9fa",
                "text": "#2c3e50",
                "font_family": "Comic Sans MS, cursive",
                "border_radius": 12
            },
            "minimal": {
                "colors": ["#333333", "#666666", "#999999", "#cccccc", "#000000"],
                "background": "#ffffff",
                "grid": "#f5f5f5",
                "text": "#333333",
                "font_family": "Monaco, monospace",
                "border_radius": 0
            }
        }
        
        return theme_configs.get(theme, theme_configs["modern"])
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance-related configuration."""
        
        return {
            "optimization": {
                "enabled": self.auto_optimize_large_datasets,
                "threshold": self.large_dataset_threshold,
                "max_points": self.max_data_points,
                "strategy": self.optimization_strategy
            },
            "caching": {
                "enabled": self.cache_enabled,
                "type": self.cache_type,
                "ttl": self.cache_ttl,
                "max_size": self.cache_max_size
            },
            "limits": {
                "max_concurrent_charts": self.max_concurrent_charts,
                "target_generation_time_ms": self.target_chart_generation_time_ms,
                "max_generation_time_ms": self.max_chart_generation_time_ms,
                "memory_limit_mb": self.memory_limit_mb
            },
            "monitoring": {
                "enabled": self.performance_monitoring,
                "detailed_logging": self.enable_performance_logging
            }
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI-related configuration."""
        
        return {
            "enabled": self.enable_ai_features,
            "chart_detection": self.ai_chart_detection,
            "insight_generation": self.ai_insight_generation,
            "model": self.ai_model,
            "api_key_configured": bool(self.openai_api_key)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        
        return {
            "server": {
                "name": self.server_name,
                "version": self.version,
                "host": self.host,
                "port": self.port
            },
            "engines": {
                "enabled": self.enabled_engines,
                "default": self.default_engine
            },
            "themes": {
                "available": self.available_themes,
                "default": self.default_theme
            },
            "performance": self.get_performance_config(),
            "ai": self.get_ai_config(),
            "export": {
                "directory": self.export_directory,
                "formats": self.allowed_export_formats,
                "max_size_mb": self.max_export_size // (1024 * 1024)
            }
        }
    
    @classmethod
    def from_file(cls, config_path: str) -> "ChartGeniusConfig":
        """Load configuration from file."""
        
        import json
        from pathlib import Path
        
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r') as f:
            config_data = json.load(f)
        
        # Create instance with loaded data
        instance = cls()
        
        # Update configuration with loaded data
        for key, value in config_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        return instance
    
    def save_to_file(self, config_path: str):
        """Save configuration to file."""
        
        import json
        from pathlib import Path
        
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# Default configuration instance
default_config = ChartGeniusConfig() 