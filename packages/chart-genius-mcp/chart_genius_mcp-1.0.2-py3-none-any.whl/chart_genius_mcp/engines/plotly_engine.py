"""
Plotly Chart Engine - Interactive chart generation
=================================================

High-performance Plotly-based chart generation engine.
"""

import asyncio
import time
import pandas as pd
from typing import Dict, Any, Optional, List
import plotly.graph_objects as go
import plotly.express as px
import base64

from ..exceptions import ChartGenerationError


class PlotlyEngine:
    """Plotly chart generation engine with performance optimizations."""
    
    def __init__(self):
        """Initialize Plotly engine."""
        self.name = "plotly"
        self.capabilities = {
            "interactive": True,
            "3d": True,
            "animation": True,
            "streaming": True,
            "formats": ["json", "html", "png", "svg", "pdf"]
        }
    
    async def generate_chart(
        self,
        data: pd.DataFrame,
        chart_type: str,
        theme: str = "modern",
        format: str = "json",
        x: Optional[str] = None,
        y: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        group: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a chart using Plotly."""
        
        try:
            start_time = time.time()
            
            # Convert DataFrame to the format we expect
            if hasattr(data, 'to_dict'):
                # It's a DataFrame
                chart_data = data
            else:
                # It's already optimized data
                chart_data = pd.DataFrame(data)
            
            # Generate chart based on type
            eff_color = color or group
            if chart_type == "bar":
                fig = self._create_bar_chart(chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "line":
                fig = self._create_line_chart(chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "scatter":
                fig = self._create_scatter_chart(chart_data, theme, x=x, y=y, color=eff_color, size=size)
            elif chart_type == "pie":
                fig = self._create_pie_chart(chart_data, theme, names=kwargs.get("names"), values=kwargs.get("values"))
            elif chart_type == "heatmap":
                fig = self._create_heatmap_chart(chart_data, theme, x=x, y=y, value=kwargs.get("value"))
            elif chart_type == "histogram":
                fig = self._create_histogram_chart(chart_data, theme, x=x, color=eff_color)
            elif chart_type == "area":
                fig = self._create_area_chart(chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "box":
                fig = self._create_box_chart(chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "violin":
                fig = self._create_violin_chart(chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "bubble":
                fig = self._create_bubble_chart(chart_data, theme, x=x, y=y, size=size, color=eff_color)
            elif chart_type == "treemap":
                fig = self._create_treemap_chart(chart_data, theme, path=kwargs.get("path"), value=kwargs.get("value"))
            elif chart_type == "sunburst":
                fig = self._create_sunburst_chart(chart_data, theme, path=kwargs.get("path"), value=kwargs.get("value"))
            elif chart_type == "funnel":
                fig = self._create_funnel_chart(chart_data, theme)
            elif chart_type == "waterfall":
                fig = self._create_waterfall_chart(chart_data, theme)
            elif chart_type == "radar":
                fig = self._create_radar_chart(chart_data, theme)
            elif chart_type == "sankey":
                fig = self._create_sankey_chart(chart_data, theme)
            elif chart_type == "choropleth":
                fig = self._create_choropleth_chart(chart_data, theme, location=kwargs.get("location"), value=kwargs.get("value"), locationmode=kwargs.get("locationmode"), scope=kwargs.get("scope"))
            else:
                raise ChartGenerationError(f"Unsupported chart type for Plotly: {chart_type}", chart_type=chart_type, engine=self.name)
            
            # Apply theme
            fig = self._apply_theme(fig, theme)
            # Apply additional visual polish
            self._polish_traces(fig, chart_type)
            
            # Convert to requested format
            if format == "json":
                result = fig.to_json()
            elif format == "html":
                result = fig.to_html()
            elif format in ("png", "svg"):
                try:
                    image_bytes = fig.to_image(format=format)
                    result = base64.b64encode(image_bytes).decode()
                except Exception as export_err:
                    # Fallback to JSON if image export not available
                    result = fig.to_json()
                    format = "json"
            else:
                result = fig.to_json()  # Default to JSON
            
            generation_time = (time.time() - start_time) * 1000
            
            return {
                "chart_data": result,
                "metadata": {
                    "engine": self.name,
                    "chart_type": chart_type,
                    "theme": theme,
                    "format": format,
                    "generation_time_ms": generation_time
                }
            }
            
        except Exception as e:
            raise ChartGenerationError(
                f"Plotly chart generation failed: {str(e)}",
                chart_type=chart_type,
                engine=self.name
            )
    
    def _create_bar_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None) -> go.Figure:
        """Create a bar chart."""
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Bar chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        
        fig = px.bar(data, x=x_col, y=y_col, color=color, title=f"{y_col} by {x_col}")
        
        return fig
    
    def _create_line_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None) -> go.Figure:
        """Create a line chart."""
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Line chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        
        fig = px.line(data, x=x_col, y=y_col, color=color, title=f"{y_col} over {x_col}")
        
        return fig
    
    def _create_scatter_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None, size: Optional[str]=None) -> go.Figure:
        """Create a scatter chart."""
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Scatter chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        
        fig = px.scatter(data, x=x_col, y=y_col, color=color, size=size, title=f"{y_col} vs {x_col}")
        
        return fig
    
    def _create_pie_chart(self, data: pd.DataFrame, theme: str, names: Optional[str]=None, values: Optional[str]=None) -> go.Figure:
        """Create a pie chart."""
        if names and values:
            if names not in data.columns or values not in data.columns:
                raise ChartGenerationError("Pie mapping error: provided names/values not in data columns")
            labels_col = names
            values_col = values
        else:
            if len(data.columns) < 2:
                raise ChartGenerationError("Pie chart requires at least 2 columns")
            labels_col = data.columns[0]
            values_col = data.columns[1]
        
        fig = px.pie(
            data,
            names=labels_col,
            values=values_col,
            title="Pie Chart"
        )
        
        return fig
    
    def _create_heatmap_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, value: Optional[str]=None) -> go.Figure:
        """Create a heatmap."""
        # If explicit mappings requested, validate strictly
        if x or y or value:
            if not (x and y and value):
                raise ChartGenerationError("Heatmap requires x, y, and value when explicit mapping is provided")
            missing = [col for col in [x, y, value] if col not in data.columns]
            if missing:
                raise ChartGenerationError(f"Heatmap mapping error: columns not found in data: {missing}")
            try:
                pivot = data.pivot_table(index=y, columns=x, values=value, aggfunc='mean')
                fig = px.imshow(pivot, title="Heatmap", color_continuous_scale="RdBu_r")
                return fig
            except Exception as e:
                raise ChartGenerationError(f"Failed to build heatmap from x/y/value: {e}")
        # Fallback to correlation heatmap
        numeric_data = data.select_dtypes(include=['number'])
        if len(numeric_data.columns) < 2:
            raise ChartGenerationError("Heatmap requires at least 2 numeric columns")
        corr_matrix = numeric_data.corr()
        fig = px.imshow(corr_matrix, title="Correlation Heatmap", color_continuous_scale="RdBu_r")
        return fig

    def _create_histogram_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, color: Optional[str]=None) -> go.Figure:
        """Create a histogram from first numeric column."""
        col = x
        if not col:
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) == 0:
                raise ChartGenerationError("Histogram requires at least 1 numeric column")
            col = numeric_cols[0]
        fig = px.histogram(data, x=col, nbins=30, color=color, title=f"Histogram of {col}")
        return fig

    def _create_area_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None) -> go.Figure:
        """Create an area chart (line with fill)."""
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Area chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        fig = px.area(data, x=x_col, y=y_col, color=color, title=f"{y_col} over {x_col}")
        return fig

    def _create_box_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None) -> go.Figure:
        """Create a box plot. If categorical present, use first as x and first numeric as y; else use melt."""
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            raise ChartGenerationError("Box plot requires at least 1 numeric column")
        if x and y:
            fig = px.box(data, x=x, y=y, color=color, title="Box Plot")
        else:
            cat_cols = [c for c in data.columns if c not in numeric_cols]
            if cat_cols:
                fig = px.box(data, x=cat_cols[0], y=numeric_cols[0], color=color, title="Box Plot")
            else:
                # No categories; show distribution of first numeric
                fig = px.box(data, y=numeric_cols[0], color=color, title=f"Box Plot of {numeric_cols[0]}")
        return fig

    def _create_violin_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None) -> go.Figure:
        """Create a violin plot."""
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            raise ChartGenerationError("Violin plot requires at least 1 numeric column")
        if x and y:
            fig = px.violin(data, x=x, y=y, color=color, box=True, points='outliers', title="Violin Plot")
        else:
            cat_cols = [c for c in data.columns if c not in numeric_cols]
            if cat_cols:
                fig = px.violin(data, x=cat_cols[0], y=numeric_cols[0], color=color, box=True, points='outliers', title="Violin Plot")
            else:
                fig = px.violin(data, y=numeric_cols[0], color=color, box=True, points='outliers', title=f"Violin Plot of {numeric_cols[0]}")
        return fig

    def _create_bubble_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, size: Optional[str]=None, color: Optional[str]=None) -> go.Figure:
        """Create a bubble chart (scatter with size)."""
        if not (x and y):
            numeric_cols = list(data.select_dtypes(include=['number']).columns)
            if len(numeric_cols) < 2:
                raise ChartGenerationError("Bubble chart requires at least 2 numeric columns")
            x = x or numeric_cols[0]
            y = y or numeric_cols[1]
            if not size and len(numeric_cols) >= 3:
                size = numeric_cols[2]
        fig = px.scatter(data, x=x, y=y, size=size, color=color, title="Bubble Chart")
        return fig
    
    def _apply_theme(self, fig: go.Figure, theme: str) -> go.Figure:
        """Apply theme styling to the figure."""
        
        theme_configs = {
            "modern": {
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "font_family": "Inter, Arial, sans-serif",
                "font_color": "#333333",
                "template": "plotly_white",
                "colorway": [
                    "#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316"
                ],
            },
            "corporate": {
                "plot_bgcolor": "white", 
                "paper_bgcolor": "white",
                "font_family": "Helvetica, Arial, sans-serif",
                "font_color": "#2c3e50",
                "template": "plotly_white",
                "colorway": [
                    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"
                ],
            },
            "dark": {
                "plot_bgcolor": "#1e293b",
                "paper_bgcolor": "#0f172a", 
                "font_family": "Inter, Arial, sans-serif",
                "font_color": "#e2e8f0",
                "template": "plotly_dark",
                "colorway": [
                    "#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa", "#22d3ee", "#fb923c"
                ],
            },
            "accessible": {
                "plot_bgcolor": "white",
                "paper_bgcolor": "white",
                "font_family": "Arial, sans-serif", 
                "font_color": "black",
                "template": "plotly_white",
                "colorway": [
                    "#000000", "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"
                ],
            }
        }
        
        config = theme_configs.get(theme, theme_configs["modern"])
        
        fig.update_layout(
            template=config["template"],
            plot_bgcolor=config["plot_bgcolor"],
            paper_bgcolor=config["paper_bgcolor"],
            font_family=config["font_family"],
            font_color=config["font_color"],
            margin=dict(l=40, r=20, t=50, b=40),
            colorway=config.get("colorway"),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            title=dict(x=0.0),
        )
        
        # Improve axes readability
        fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
        
        return fig

    def _polish_traces(self, fig: go.Figure, chart_type: str) -> None:
        """Apply consistent hover, gaps, smoothing, and marker tweaks."""
        try:
            # Bar spacing
            if chart_type == "bar":
                fig.update_layout(bargap=0.2, bargroupgap=0.1)
                fig.update_traces(marker_line_width=0)
            
            # Smoother lines and clearer markers for line/area/scatter
            if chart_type in {"line", "area", "scatter"}:
                fig.update_traces(selector=dict(type="scatter"), line=dict(width=2.5, shape="spline"))
                fig.update_traces(selector=dict(mode="markers"), marker=dict(size=7, opacity=0.9))
                if chart_type == "area":
                    fig.update_traces(opacity=0.85)
            
            # Standardize hover content across traces
            fig.update_traces(hovertemplate="x: %{x}<br>y: %{y}<extra></extra>")
        except Exception:
            # Best-effort polish; never fail chart generation due to styling
            pass 

    # Advanced charts
    def _create_treemap_chart(self, data: pd.DataFrame, theme: str, path: Optional[List[str]]=None, value: Optional[str]=None) -> go.Figure:
        cat_cols = list(data.select_dtypes(exclude=['number']).columns)
        num_cols = list(data.select_dtypes(include=['number']).columns)
        if not cat_cols or not num_cols:
            raise ChartGenerationError("Treemap needs at least 1 categorical and 1 numeric column")
        eff_path = path or [cat_cols[0]]
        eff_value = value or num_cols[0]
        fig = px.treemap(data, path=eff_path, values=eff_value, title="Treemap")
        return fig

    def _create_sunburst_chart(self, data: pd.DataFrame, theme: str, path: Optional[List[str]]=None, value: Optional[str]=None) -> go.Figure:
        cat_cols = list(data.select_dtypes(exclude=['number']).columns)
        num_cols = list(data.select_dtypes(include=['number']).columns)
        if not cat_cols or not num_cols:
            raise ChartGenerationError("Sunburst needs at least 1 categorical and 1 numeric column")
        eff_path = path or [cat_cols[0]]
        eff_value = value or num_cols[0]
        fig = px.sunburst(data, path=eff_path, values=eff_value, title="Sunburst")
        return fig

    def _create_funnel_chart(self, data: pd.DataFrame, theme: str) -> go.Figure:
        cat_cols = list(data.select_dtypes(exclude=['number']).columns)
        num_cols = list(data.select_dtypes(include=['number']).columns)
        if not cat_cols or not num_cols:
            raise ChartGenerationError("Funnel needs at least 1 categorical and 1 numeric column")
        fig = px.funnel(data, y=cat_cols[0], x=num_cols[0], title="Funnel")
        return fig

    def _create_waterfall_chart(self, data: pd.DataFrame, theme: str) -> go.Figure:
        # Expect categorical labels and values; treat all as relative steps
        cat_cols = list(data.select_dtypes(exclude=['number']).columns)
        num_cols = list(data.select_dtypes(include=['number']).columns)
        if not cat_cols or not num_cols:
            raise ChartGenerationError("Waterfall needs 1 categorical and 1 numeric column")
        x_vals = data[cat_cols[0]].astype(str).tolist()
        y_vals = data[num_cols[0]].tolist()
        fig = go.Figure(go.Waterfall(x=x_vals, y=y_vals, measure=["relative"] * len(y_vals)))
        fig.update_layout(title="Waterfall")
        return fig

    def _create_radar_chart(self, data: pd.DataFrame, theme: str) -> go.Figure:
        cols = list(data.columns)
        if "theta" in cols and "r" in cols:
            fig = px.line_polar(data, theta="theta", r="r", line_close=True, title="Radar")
            return fig
        # Otherwise, compute mean of numeric columns and plot one trace
        num_cols = list(data.select_dtypes(include=['number']).columns)
        if len(num_cols) < 3:
            raise ChartGenerationError("Radar needs at least 3 numeric columns or explicit theta/r columns")
        means = data[num_cols].mean().values
        fig = px.line_polar(r=means, theta=num_cols, line_close=True, title="Radar")
        return fig

    def _create_sankey_chart(self, data: pd.DataFrame, theme: str) -> go.Figure:
        required = {"source", "target", "value"}
        if not required.issubset(set(data.columns)):
            raise ChartGenerationError("Sankey requires columns: source, target, value")
        sources = data["source"].astype(str).tolist()
        targets = data["target"].astype(str).tolist()
        values = data["value"].astype(float).tolist()
        labels = list(sorted(set(sources + targets)))
        index = {lbl: i for i, lbl in enumerate(labels)}
        src_idx = [index[s] for s in sources]
        tgt_idx = [index[t] for t in targets]
        link = dict(source=src_idx, target=tgt_idx, value=values)
        node = dict(label=labels)
        fig = go.Figure(go.Sankey(node=node, link=link))
        fig.update_layout(title_text="Sankey", font_size=12)
        return fig

    def _create_choropleth_chart(self, data: pd.DataFrame, theme: str, location: Optional[str]=None, value: Optional[str]=None, locationmode: Optional[str]=None, scope: Optional[str]=None) -> go.Figure:
        loc = location if location in data.columns else ("location" if "location" in data.columns else ("iso_alpha" if "iso_alpha" in data.columns else None))
        if not loc:
            raise ChartGenerationError("Choropleth requires a location column (e.g., 'location' or 'iso_alpha')")
        val = value if value in data.columns else None
        if val is None:
            num_cols = list(data.select_dtypes(include=['number']).columns)
            if not num_cols:
                raise ChartGenerationError("Choropleth needs a numeric value column")
            val = num_cols[0]
        # Guess locationmode if not specified and values look like ISO-3 codes (A-Z length 3)
        inferred_mode = None
        if locationmode:
            inferred_mode = locationmode
        else:
            try:
                sample = data[loc].astype(str).dropna().head(3).tolist()
                if sample and all(len(s) == 3 and s.isalpha() and s.isupper() for s in sample):
                    inferred_mode = "ISO-3"
            except Exception:
                pass
        fig = px.choropleth(data, locations=loc, color=val, color_continuous_scale="Blues", title="Choropleth")
        if inferred_mode:
            fig.update_traces(locationmode=inferred_mode)
            fig.update_geos(fitbounds="locations")
        if scope:
            fig.update_geos(scope=scope)
        return fig 