from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


SUPPORTED_ENGINES = ("plotly", "matplotlib", "seaborn")
SUPPORTED_THEMES = ("modern", "corporate", "dark", "accessible")
SUPPORTED_EXPORTS = ("json", "html", "png", "svg", "pdf")
SUPPORTED_CHART_TYPES = (
    "auto",  # special value allowed for detection
    "bar",
    "line",
    "scatter",
    "pie",
    "heatmap",
    "histogram",
    "area",
    "box",
    "violin",
    "bubble",
    "treemap",
    "sunburst",
    "funnel",
    "waterfall",
    "radar",
    "sankey",
    "choropleth",
)


class DataModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    columns: Optional[List[str]] = Field(default=None, description="Optional list of column names")
    rows: List[Dict[str, Any]]

    @field_validator("rows")
    @classmethod
    def validate_rows_not_empty(cls, v: List[Dict[str, Any]]):
        if not isinstance(v, list):
            raise ValueError("data.rows must be a list of objects")
        return v


class GenerateChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: DataModel
    chart_type: Literal[
        "auto",
        "bar",
        "line",
        "scatter",
        "pie",
        "heatmap",
        "histogram",
        "area",
        "box",
        "violin",
        "bubble",
        "treemap",
        "sunburst",
        "funnel",
        "waterfall",
        "radar",
        "sankey",
        "choropleth",
    ] = "auto"
    engine: Literal["plotly", "matplotlib", "seaborn"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    optimize_large_data: bool = True
    format: Literal["json", "html", "png", "svg"] = "json"

    # Optional field mapping
    x: Optional[str] = None
    y: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    group: Optional[str] = None


class AnalyzeAndVisualizeInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: DataModel
    question: str
    context: Literal["business", "technical", "executive"] = "business"


class DetectOptimalChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: DataModel
    analysis_goal: Optional[str] = None


class OptimizeLargeDatasetInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: DataModel
    max_points: int = 1000
    strategy: Literal["intelligent", "sample", "aggregate"] = "intelligent"


class CreateDashboardInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    charts: List[Dict[str, Any]]
    layout: Literal["grid", "masonry", "tabs", "hex_inspired"] = "grid"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"


class ExportChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chart_data: Dict[str, Any]
    format: Literal["png", "svg", "pdf", "html", "json"] = "png"
    quality: Literal["high", "medium", "web_optimized"] = "high"
    dimensions: Optional[Dict[str, int]] = None


class GenerateChartInsightsInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chart_data: Dict[str, Any]
    data: DataModel
    insight_types: Optional[List[Literal["trends", "outliers", "correlations", "patterns"]]] = Field(
        default_factory=lambda: ["trends", "outliers", "correlations"]
    )


class GetPerformanceStatsInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    include_history: bool = False


class GenerateChartBatchInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    datasets: List[Dict[str, Any]]
    chart_configs: List[Dict[str, Any]]
    parallel: bool = True


class ManageCacheInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action: Literal["clear", "stats", "optimize"] = "stats"


class GenerateChartAutoInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: DataModel
    user_text: str = Field(description="User goal or question in natural language")
    context: Literal["business", "technical", "executive"] = "business"
    allow_chart_types: Optional[List[Literal[
        "bar", "line", "scatter", "pie", "heatmap", "histogram", "area", "box", "violin", "bubble",
        "treemap", "sunburst", "funnel", "waterfall", "radar", "sankey", "choropleth"
    ]]] = None
    engine: Literal["plotly", "matplotlib", "seaborn"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


# Per-chart tool inputs (strict schemas)
class BarChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    x: str
    y: str
    color: Optional[str] = None
    group: Optional[str] = None
    engine: Literal["plotly", "matplotlib", "seaborn"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


class LineChartInput(BarChartInput):
    pass


class ScatterChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    x: str
    y: str
    size: Optional[str] = None
    color: Optional[str] = None
    group: Optional[str] = None
    engine: Literal["plotly", "matplotlib", "seaborn"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


class HistogramChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    x: str
    color: Optional[str] = None
    engine: Literal["plotly", "matplotlib", "seaborn"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


class AreaChartInput(BarChartInput):
    pass


class BoxChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    y: str
    x: Optional[str] = None
    color: Optional[str] = None
    group: Optional[str] = None
    engine: Literal["plotly", "matplotlib", "seaborn"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


class ViolinChartInput(BoxChartInput):
    pass


class BubbleChartInput(ScatterChartInput):
    pass


class PieChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    names: str
    values: str
    engine: Literal["plotly", "matplotlib", "seaborn"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


class HeatmapChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    x: str
    y: str
    value: str
    engine: Literal["plotly", "matplotlib", "seaborn"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


class TreemapChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    path: List[str]
    value: str
    engine: Literal["plotly"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


class SunburstChartInput(TreemapChartInput):
    pass


class SankeyChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    source: str
    target: str
    value: str
    engine: Literal["plotly"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json"


class ChoroplethChartInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    data: DataModel
    location: str
    value: str
    locationmode: Optional[Literal["ISO-3", "USA-states", "country names"]] = None
    scope: Optional[str] = None
    engine: Literal["plotly"] = "plotly"
    theme: Literal["modern", "corporate", "dark", "accessible"] = "modern"
    format: Literal["json", "html", "png", "svg"] = "json" 