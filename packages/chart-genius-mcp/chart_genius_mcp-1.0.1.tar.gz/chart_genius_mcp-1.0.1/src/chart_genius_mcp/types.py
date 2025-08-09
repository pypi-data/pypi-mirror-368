"""
Type definitions for ChartGenius MCP
==================================

Common types and data structures used throughout ChartGenius MCP.
"""

from typing import Dict, List, Any, Optional, Union, Literal
from dataclasses import dataclass
from enum import Enum


class ChartType(str, Enum):
    """Supported chart types."""
    BAR = "bar"
    LINE = "line" 
    SCATTER = "scatter"
    PIE = "pie"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    AREA = "area"
    BOX = "box"
    VIOLIN = "violin"
    BUBBLE = "bubble"


class Engine(str, Enum):
    """Supported chart engines."""
    PLOTLY = "plotly"
    MATPLOTLIB = "matplotlib"
    SEABORN = "seaborn"


class Theme(str, Enum):
    """Supported chart themes."""
    MODERN = "modern"
    CORPORATE = "corporate"
    DARK = "dark"
    ACCESSIBLE = "accessible"


class DataFormat(str, Enum):
    """Supported data formats."""
    JSON = "json"
    DATAFRAME = "dataframe"
    CSV = "csv"
    DICT = "dict"


class ExportFormat(str, Enum):
    """Supported export formats."""
    JSON = "json"
    HTML = "html"
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


@dataclass
class ChartConfig:
    """Configuration for chart generation."""
    chart_type: str = "bar"
    engine: str = "plotly"
    theme: str = "modern"
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    width: int = 800
    height: int = 600
    format: str = "json"
    optimize_large_data: bool = True
    enable_ai_detection: bool = False
    cache_enabled: bool = True
    interactive: bool = True
    

@dataclass
class DataPoint:
    """A single data point."""
    x: Union[str, int, float]
    y: Union[int, float]
    label: Optional[str] = None
    color: Optional[str] = None
    size: Optional[float] = None


@dataclass
class DataSeries:
    """A data series for charting."""
    name: str
    data: List[DataPoint]
    color: Optional[str] = None
    type: Optional[str] = None


@dataclass
class ChartMetadata:
    """Metadata about a generated chart."""
    chart_type: str
    engine: str
    theme: str
    data_points: int
    generation_time_ms: float
    optimized: bool = False
    ai_detected: bool = False
    cache_hit: bool = False
    file_size_bytes: Optional[int] = None
    complexity_score: Optional[float] = None


@dataclass 
class ChartResult:
    """Result of chart generation."""
    success: bool
    chart_data: Union[str, bytes, Dict[str, Any]]
    metadata: ChartMetadata
    error: Optional[str] = None
    warnings: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class OptimizationResult:
    """Result of data optimization."""
    original_size: int
    optimized_size: int
    optimization_time_ms: float
    strategy: str
    reduction_ratio: float
    memory_saved_mb: float


@dataclass
class PerformanceStats:
    """Performance statistics."""
    charts_generated: int
    avg_generation_time_ms: float
    total_execution_time_ms: float
    cache_hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float
    performance_grade: str


@dataclass
class AIDetectionResult:
    """Result of AI-powered chart detection."""
    recommended_type: str
    confidence: float
    reasoning: str
    alternatives: List[Dict[str, Any]]
    data_analysis: Dict[str, Any]


# Type aliases for common use cases
ChartData = Union[Dict[str, Any], List[Dict[str, Any]]]
ChartOptions = Dict[str, Any]
ColorPalette = List[str]
DataFilters = Dict[str, Any] 