"""
Seaborn Chart Engine - Statistical visualization specialist
=========================================================

High-performance Seaborn-based chart generation engine.
"""

import asyncio
import time
import pandas as pd
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import io
import base64
import concurrent.futures

from ..exceptions import ChartGenerationError

# Use non-interactive backend
matplotlib.use('Agg')


class SeabornEngine:
    """Seaborn chart generation engine with performance optimizations."""
    
    def __init__(self):
        """Initialize Seaborn engine."""
        self.name = "seaborn"
        self.capabilities = {
            "interactive": False,
            "3d": False,
            "animation": False,
            "streaming": False,
            "formats": ["png", "svg", "pdf"]
        }
        
        # Set seaborn style
        sns.set_style("whitegrid")
    
    async def generate_chart(
        self,
        data: pd.DataFrame,
        chart_type: str,
        theme: str = "modern",
        format: str = "png",
        x: Optional[str] = None,
        y: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        group: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a chart using Seaborn."""
        
        try:
            start_time = time.time()
            
            # Convert DataFrame to the format we expect
            if hasattr(data, 'to_dict'):
                chart_data = data
            else:
                chart_data = pd.DataFrame(data)
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Generate chart based on type
            hue = color or group
            if chart_type == "bar":
                self._create_bar_chart(chart_data, theme, x=x, y=y, hue=hue)
            elif chart_type == "line":
                self._create_line_chart(chart_data, theme, x=x, y=y, hue=hue)
            elif chart_type == "scatter":
                self._create_scatter_chart(chart_data, theme, x=x, y=y, hue=hue, size=size)
            elif chart_type == "pie":
                # Seaborn doesn't have pie charts, fall back to matplotlib
                self._create_pie_chart(chart_data, theme)
            elif chart_type == "heatmap":
                # If server passed x/y/value via kwargs, they will be in DataFrame columns as 'x','y','value'
                self._create_heatmap_chart(chart_data, theme)
            elif chart_type == "histogram":
                 self._create_histogram_chart(chart_data, theme, x=x, hue=hue)
            elif chart_type == "area":
                 self._create_area_chart(chart_data, theme, x=x, y=y, hue=hue)
            elif chart_type == "box":
                 self._create_box_chart(chart_data, theme, x=x, y=y, hue=hue)
            elif chart_type == "violin":
                 self._create_violin_chart(chart_data, theme, x=x, y=y, hue=hue)
            elif chart_type == "bubble":
                 self._create_bubble_chart(chart_data, theme, x=x, y=y, size=size, hue=hue)
            else:
                raise ChartGenerationError(
                    f"Unsupported chart type for Seaborn: {chart_type}",
                    chart_type=chart_type,
                    engine=self.name
                )
            
            # Apply theme
            self._apply_theme(theme)
            # Ensure consistent legend placement when grouping is used
            if hue:
                plt.legend(loc="best", frameon=False)
            
            # Convert to requested format using process pool
            fmt = format if format in {"png", "svg", "pdf"} else "png"
            def _render(fig_format: str) -> str:
                buf = io.BytesIO()
                plt.savefig(buf, format=fig_format, dpi=300, bbox_inches='tight')
                buf.seek(0)
                return base64.b64encode(buf.getvalue()).decode()

            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = await loop.run_in_executor(pool, _render, fmt)
            plt.close()
            
            generation_time = (time.time() - start_time) * 1000
            
            return {
                "chart_data": result,
                "metadata": {
                    "engine": self.name,
                    "chart_type": chart_type,
                    "theme": theme,
                    "format": fmt,
                    "generation_time_ms": generation_time
                }
            }
            
        except Exception as e:
            plt.close('all')  # Clean up any figures
            raise ChartGenerationError(
                f"Seaborn chart generation failed: {str(e)}",
                chart_type=chart_type,
                engine=self.name
            )
    
    def _create_bar_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, hue: Optional[str]=None):
        """
        Create a bar chart using Seaborn.
        
        Args:
            data: DataFrame containing the data to plot
            theme: Theme to apply to the chart
            
        Raises:
            ChartGenerationError: If data has fewer than 2 columns
        """
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Bar chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        sns.barplot(data=data, x=x_col, y=y_col, hue=hue)
        plt.title(f"{y_col} by {x_col}")
    
    def _create_line_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, hue: Optional[str]=None):
        """
        Create a line chart using Seaborn.
        
        Args:
            data: DataFrame containing the data to plot
            theme: Theme to apply to the chart
            
        Raises:
            ChartGenerationError: If data has fewer than 2 columns
        """
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Line chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        sns.lineplot(data=data, x=x_col, y=y_col, marker='o', hue=hue)
        plt.title(f"{y_col} over {x_col}")
    
    def _create_scatter_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, hue: Optional[str]=None, size: Optional[str]=None):
        """
        Create a scatter chart using Seaborn.
        
        Args:
            data: DataFrame containing the data to plot
            theme: Theme to apply to the chart
            
        Raises:
            ChartGenerationError: If data has fewer than 2 columns
        """
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Scatter chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        sns.scatterplot(data=data, x=x_col, y=y_col, hue=hue, size=size if size in data.columns else None)
        plt.title(f"{y_col} vs {x_col}")
    
    def _create_pie_chart(self, data: pd.DataFrame, theme: str):
        """
        Create a pie chart using matplotlib (since seaborn doesn't have pie charts).
        
        Args:
            data: DataFrame containing the data to plot
            theme: Theme to apply to the chart
            
        Raises:
            ChartGenerationError: If data has fewer than 2 columns
        """
        if len(data.columns) < 2:
            raise ChartGenerationError("Pie chart requires at least 2 columns")
        
        labels_col = data.columns[0]
        values_col = data.columns[1]
        
        plt.pie(data[values_col], labels=data[labels_col], autopct='%1.1f%%')
        plt.title("Pie Chart")
    
    def _create_heatmap_chart(self, data: pd.DataFrame, theme: str):
        """Create a heatmap; pivot if x/y/value present else correlation."""
        cols = set(data.columns)
        # If any of mapping columns present, require all
        if ("x" in cols) or ("y" in cols) or ("value" in cols):
            if not {"x", "y", "value"}.issubset(cols):
                missing = [c for c in ["x", "y", "value"] if c not in cols]
                raise ChartGenerationError(f"Failed to build heatmap from x/y/value: missing {missing}")
            try:
                pivot = data.pivot_table(index="y", columns="x", values="value", aggfunc='mean')
                sns.heatmap(pivot, cmap='RdBu_r')
                plt.title("Heatmap")
                return
            except Exception as e:
                raise ChartGenerationError(f"Failed to build heatmap from x/y/value: {e}")
        # Fallback correlation
        numeric_data = data.select_dtypes(include=['number'])
        if len(numeric_data.columns) < 2:
            raise ChartGenerationError("Heatmap requires at least 2 numeric columns")
        corr_matrix = numeric_data.corr()
        sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0)
        plt.title("Correlation Heatmap")
    
    def _apply_theme(self, theme: str):
        """Apply theme styling to the figure."""
        
        palette_map = {
            "modern": ["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"],
            "corporate": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
            "dark": ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa"],
            "accessible": ["#000000", "#1f77b4", "#ff7f0e", "#2ca02c"],
        }
        palette = palette_map.get(theme, palette_map["modern"])

        if theme == "dark":
            sns.set_style("darkgrid")
            plt.rcParams.update({
                'figure.facecolor': '#2c3e50',
                'axes.facecolor': '#34495e',
                'text.color': '#ecf0f1',
                'axes.labelcolor': '#ecf0f1',
                'xtick.color': '#ecf0f1',
                'ytick.color': '#ecf0f1'
            })
        else:
            # Default to light theme
            sns.set_style("whitegrid")
            plt.rcParams.update({
                'figure.facecolor': 'white',
                'axes.facecolor': 'white'
            })
        sns.set_palette(palette)

    def _create_histogram_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, hue: Optional[str]=None):
        col = x
        if not col:
            num_cols = list(data.select_dtypes(include=['number']).columns)
            if not num_cols:
                raise ChartGenerationError("Histogram requires at least 1 numeric column")
            col = num_cols[0]
        sns.histplot(data=data, x=col, bins=30, hue=hue, color="#2563eb", edgecolor="#1e293b")
        plt.title(f"Histogram of {col}")

    def _create_area_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, hue: Optional[str]=None):
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Area chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        sns.lineplot(data=data, x=x_col, y=y_col, marker='o', hue=hue)
        plt.fill_between(data[x_col], data[y_col], alpha=0.3, color="#60a5fa")
        plt.title(f"{y_col} over {x_col}")

    def _create_box_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, hue: Optional[str]=None):
        if y is None:
            numeric_cols = list(data.select_dtypes(include=['number']).columns)
            if not numeric_cols:
                raise ChartGenerationError("Box plot requires at least 1 numeric column")
            y = numeric_cols[0]
        sns.boxplot(data=data, x=x, y=y, hue=hue)
        plt.title("Box Plot")

    def _create_violin_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, hue: Optional[str]=None):
        if y is None:
            numeric_cols = list(data.select_dtypes(include=['number']).columns)
            if not numeric_cols:
                raise ChartGenerationError("Violin plot requires at least 1 numeric column")
            y = numeric_cols[0]
        sns.violinplot(data=data, x=x, y=y, hue=hue, cut=0, inner="box")
        plt.title("Violin Plot")

    def _create_bubble_chart(self, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, size: Optional[str]=None, hue: Optional[str]=None):
        if not (x and y):
            num_cols = list(data.select_dtypes(include=['number']).columns)
            if len(num_cols) < 2:
                raise ChartGenerationError("Bubble chart requires at least 2 numeric columns")
            x = x or num_cols[0]
            y = y or num_cols[1]
            if not size and len(num_cols) >= 3:
                size = num_cols[2]
        sns.scatterplot(data=data, x=x, y=y, size=size if size in data.columns else None, hue=hue)
        plt.title("Bubble Chart") 