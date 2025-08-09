"""
Matplotlib Chart Engine - Publication-quality static charts
==========================================================

High-performance Matplotlib-based chart generation engine.
"""

import asyncio
import time
import pandas as pd
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import concurrent.futures

from ..exceptions import ChartGenerationError

# Use non-interactive backend
matplotlib.use('Agg')


class MatplotlibEngine:
    """Matplotlib chart generation engine with performance optimizations."""
    
    def __init__(self):
        """Initialize Matplotlib engine."""
        self.name = "matplotlib"
        self.capabilities = {
            "interactive": False,
            "3d": True,
            "animation": True,
            "streaming": False,
            "formats": ["png", "svg", "pdf", "eps"]
        }
    
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
        """Generate a chart using Matplotlib."""
        
        try:
            start_time = time.time()
            
            # Convert DataFrame to the format we expect
            if hasattr(data, 'to_dict'):
                chart_data = data
            else:
                chart_data = pd.DataFrame(data)
            
            # Create figure
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Generate chart based on type
            eff_color = color or group
            if chart_type == "bar":
                self._create_bar_chart(ax, chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "line":
                self._create_line_chart(ax, chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "scatter":
                self._create_scatter_chart(ax, chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "pie":
                self._create_pie_chart(ax, chart_data, theme)
            elif chart_type == "heatmap":
                self._create_heatmap_chart(ax, chart_data, theme)
            elif chart_type == "histogram":
                 self._create_histogram_chart(ax, chart_data, theme, x=x, color=eff_color)
            elif chart_type == "area":
                 self._create_area_chart(ax, chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "box":
                 self._create_box_chart(ax, chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "violin":
                 self._create_violin_chart(ax, chart_data, theme, x=x, y=y, color=eff_color)
            elif chart_type == "bubble":
                 self._create_bubble_chart(ax, chart_data, theme, x=x, y=y, size=size, color=eff_color)
            else:
                raise ChartGenerationError(
                    f"Unsupported chart type for Matplotlib: {chart_type}",
                    chart_type=chart_type,
                    engine=self.name
                )
            
            # Apply theme
            self._apply_theme(fig, ax, theme)
            # If labels exist, show legend consistently
            handles, labels = ax.get_legend_handles_labels()
            if labels:
                ax.legend(loc="best", frameon=False)
            
            # Convert to requested format using process pool to avoid GIL issues
            fmt = format if format in {"png", "svg", "pdf"} else "png"
            def _render(fig_format: str) -> str:
                buf = io.BytesIO()
                plt.savefig(buf, format=fig_format, dpi=300, bbox_inches='tight')
                buf.seek(0)
                return base64.b64encode(buf.getvalue()).decode()

            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = await loop.run_in_executor(pool, _render, fmt)
            plt.close(fig)
            
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
                f"Matplotlib chart generation failed: {str(e)}",
                chart_type=chart_type,
                engine=self.name
            )
    
    def _create_bar_chart(self, ax, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None):
        """Create a bar chart."""
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Bar chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        if color and color in data.columns:
            for key, grp in data.groupby(color):
                ax.bar(grp[x_col], grp[y_col], label=str(key))
            ax.legend()
        else:
            ax.bar(data[x_col], data[y_col])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} by {x_col}")
    
    def _create_line_chart(self, ax, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None):
        """Create a line chart."""
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Line chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        if color and color in data.columns:
            for key, grp in data.groupby(color):
                ax.plot(grp[x_col], grp[y_col], marker='o', label=str(key))
            ax.legend()
        else:
            ax.plot(data[x_col], data[y_col], marker='o')
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} over {x_col}")
    
    def _create_scatter_chart(self, ax, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None):
        """Create a scatter chart."""
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Scatter chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        if color and color in data.columns:
            for key, grp in data.groupby(color):
                ax.scatter(grp[x_col], grp[y_col], label=str(key))
            ax.legend()
        else:
            ax.scatter(data[x_col], data[y_col])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} vs {x_col}")
    
    def _create_pie_chart(self, ax, data: pd.DataFrame, theme: str):
        """Create a pie chart."""
        if len(data.columns) < 2:
            raise ChartGenerationError("Pie chart requires at least 2 columns")
        
        labels_col = data.columns[0]
        values_col = data.columns[1]
        
        ax.pie(data[values_col], labels=data[labels_col], autopct='%1.1f%%')
        ax.set_title("Pie Chart")
    
    def _create_heatmap_chart(self, ax, data: pd.DataFrame, theme: str):
        """Create a heatmap."""
        # If mapping columns present, require all three for pivot
        cols = set(data.columns)
        if ("x" in cols) or ("y" in cols) or ("value" in cols):
            if not {"x", "y", "value"}.issubset(cols):
                missing = [c for c in ["x", "y", "value"] if c not in cols]
                raise ChartGenerationError(f"Heatmap mapping error: columns not found in data: {missing}")
            try:
                pivot = data.pivot_table(index="y", columns="x", values="value", aggfunc='mean')
                im = ax.imshow(pivot.values, cmap='RdBu_r', aspect='auto')
                ax.set_xticks(range(len(pivot.columns)))
                ax.set_yticks(range(len(pivot.index)))
                ax.set_xticklabels(pivot.columns)
                ax.set_yticklabels(pivot.index)
                ax.set_title("Heatmap")
                plt.colorbar(im, ax=ax)
                return
            except Exception as e:
                raise ChartGenerationError(f"Failed to build heatmap from x/y/value: {e}")
        # Fallback to correlation heatmap
        numeric_data = data.select_dtypes(include=['number'])
        if len(numeric_data.columns) < 2:
            raise ChartGenerationError("Heatmap requires at least 2 numeric columns")
        corr_matrix = numeric_data.corr()
        im = ax.imshow(corr_matrix, cmap='RdBu_r', aspect='auto')
        ax.set_xticks(range(len(corr_matrix.columns)))
        ax.set_yticks(range(len(corr_matrix.columns)))
        ax.set_xticklabels(corr_matrix.columns)
        ax.set_yticklabels(corr_matrix.columns)
        ax.set_title("Correlation Heatmap")
        plt.colorbar(im, ax=ax)

    def _create_histogram_chart(self, ax, data: pd.DataFrame, theme: str, x: Optional[str]=None, color: Optional[str]=None):
        col = x
        if not col:
            numeric_cols = list(data.select_dtypes(include=['number']).columns)
            if not numeric_cols:
                raise ChartGenerationError("Histogram requires at least 1 numeric column")
            col = numeric_cols[0]
        ax.hist(data[col].dropna(), bins=30, color="#2563eb", edgecolor="#1e293b", alpha=0.85)
        ax.set_title(f"Histogram of {col}")

    def _create_area_chart(self, ax, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None):
        if len(data.columns) < 2 and (x is None or y is None):
            raise ChartGenerationError("Area chart requires at least 2 columns")
        x_col = x or data.columns[0]
        y_col = y or data.columns[1]
        ax.fill_between(data[x_col], data[y_col], step=None, alpha=0.6, color="#2563eb")
        ax.plot(data[x_col], data[y_col], color="#1e40af")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{y_col} over {x_col}")

    def _create_box_chart(self, ax, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None):
        numeric_cols = list(data.select_dtypes(include=['number']).columns)
        if not numeric_cols:
            raise ChartGenerationError("Box plot requires at least 1 numeric column")
        if x and y:
            categories = data[x].unique().tolist()
            grouped = [data.loc[data[x] == cat, y].dropna() for cat in categories]
            ax.boxplot(grouped, labels=categories)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
        else:
            cat_cols = [c for c in data.columns if c not in numeric_cols]
            if cat_cols:
                categories = data[cat_cols[0]].unique().tolist()
                grouped = [data.loc[data[cat_cols[0]] == cat, numeric_cols[0]].dropna() for cat in categories]
                ax.boxplot(grouped, labels=categories)
                ax.set_xlabel(cat_cols[0])
                ax.set_ylabel(numeric_cols[0])
            else:
                ax.boxplot(data[numeric_cols[0]].dropna())
                ax.set_ylabel(numeric_cols[0])
        ax.set_title("Box Plot")

    def _create_violin_chart(self, ax, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, color: Optional[str]=None):
        """Create a violin plot."""
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            raise ChartGenerationError("Violin plot requires at least 1 numeric column")
        if x and y:
            ax.set_title("Violin Plot")
            # Use seaborn-like aesthetic via matplotlib with alpha edge
            parts = ax.violinplot([data[y][data[x] == v].dropna() for v in data[x].unique()], showmeans=False, showmedians=True)
            for pc in parts['bodies']:
                pc.set_facecolor('#60a5fa')
                pc.set_alpha(0.5)
                pc.set_edgecolor('#1e293b')
            ax.set_xticks(range(1, len(data[x].unique())+1))
            ax.set_xticklabels([str(v) for v in data[x].unique()])
        else:
            parts = ax.violinplot([data[numeric_cols[0]].dropna()], showmeans=False, showmedians=True)
            for pc in parts['bodies']:
                pc.set_facecolor('#60a5fa')
                pc.set_alpha(0.5)
                pc.set_edgecolor('#1e293b')
        ax.set_ylabel(y or numeric_cols[0])
        ax.set_title("Violin Plot")

    def _create_bubble_chart(self, ax, data: pd.DataFrame, theme: str, x: Optional[str]=None, y: Optional[str]=None, size: Optional[str]=None, color: Optional[str]=None):
        if not (x and y):
            numeric_cols = list(data.select_dtypes(include=['number']).columns)
            if len(numeric_cols) < 2:
                raise ChartGenerationError("Bubble chart requires at least 2 numeric columns")
            x = x or numeric_cols[0]
            y = y or numeric_cols[1]
            if not size and len(numeric_cols) >= 3:
                size = numeric_cols[2]
        sizes = (data[size] * 10).fillna(10) if size and size in data.columns else 50
        if color and color in data.columns:
            for key, grp in data.groupby(color):
                ax.scatter(grp[x], grp[y], s=(grp[size]*10 if size else 50), alpha=0.7, label=str(key))
            ax.legend()
        else:
            ax.scatter(data[x], data[y], s=sizes, alpha=0.7)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title("Bubble Chart")

    def _apply_theme(self, fig, ax, theme: str):
        """Apply theme styling to the figure."""
        plt.style.use('default')
        # Color cycles similar to Plotly themes
        palette_map = {
            "modern": ["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"],
            "corporate": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
            "dark": ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa"],
            "accessible": ["#000000", "#1f77b4", "#ff7f0e", "#2ca02c"],
        }
        colors = palette_map.get(theme, palette_map["modern"])
        ax.set_prop_cycle(color=colors)
        if theme == "dark":
            fig.patch.set_facecolor('#0f172a')
            ax.set_facecolor('#1e293b')
            ax.tick_params(colors='#e2e8f0')
            for spine in ax.spines.values():
                spine.set_color('#334155')
            ax.title.set_color('#e2e8f0')
            ax.xaxis.label.set_color('#e2e8f0')
            ax.yaxis.label.set_color('#e2e8f0')
        else:
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            for spine in ax.spines.values():
                spine.set_color('#e5e7eb') 