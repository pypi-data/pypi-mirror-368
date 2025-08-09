"""
Insight Generator - AI-powered data insights
===========================================

Automated insight generation for chart data analysis.
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class InsightGenerator:
    """AI-powered insight generation for data analysis."""
    
    def __init__(self):
        """Initialize the insight generator."""
        pass
    
    async def generate_insights(
        self,
        data: pd.DataFrame,
        chart_data: Optional[Dict] = None,
        chart_type: Optional[str] = None,
        question: Optional[str] = None,
        insight_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate insights about the data."""
        
        try:
            insights = []
            
            if not insight_types:
                insight_types = ["trends", "outliers", "correlations"]
            
            for insight_type in insight_types:
                if insight_type == "trends":
                    trend_insights = self._analyze_trends(data)
                    insights.extend(trend_insights)
                elif insight_type == "outliers":
                    outlier_insights = self._detect_outliers(data)
                    insights.extend(outlier_insights)
                elif insight_type == "correlations":
                    correlation_insights = self._analyze_correlations(data)
                    insights.extend(correlation_insights)
            
            return insights
            
        except Exception as e:
            logger.warning(f"Insight generation failed: {str(e)}")
            return [{
                "type": "error",
                "description": f"Could not generate insights: {str(e)}",
                "confidence": 0.0
            }]
    
    def _analyze_trends(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze trends in the data."""
        insights = []
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if len(data) > 2:
                # Simple trend analysis
                values = data[col].dropna()
                if len(values) > 1:
                    slope = np.polyfit(range(len(values)), values, 1)[0]
                    
                    if abs(slope) > 0.1:  # Significant trend
                        direction = "increasing" if slope > 0 else "decreasing"
                        insights.append({
                            "type": "trend",
                            "description": f"{col} shows {direction} trend",
                            "confidence": 0.8,
                            "data": {"slope": slope, "column": col}
                        })
        
        return insights
    
    def _detect_outliers(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect outliers in the data."""
        insights = []
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            values = data[col].dropna()
            if len(values) > 3:
                q1 = values.quantile(0.25)
                q3 = values.quantile(0.75)
                iqr = q3 - q1
                
                outliers = values[(values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)]
                
                if len(outliers) > 0:
                    insights.append({
                        "type": "outlier",
                        "description": f"{col} has {len(outliers)} outlier(s)",
                        "confidence": 0.9,
                        "data": {
                            "outlier_count": len(outliers),
                            "outlier_values": outliers.tolist()[:5],  # Top 5
                            "column": col
                        }
                    })
        
        return insights
    
    def _analyze_correlations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Analyze correlations between numeric columns."""
        insights = []
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) >= 2:
            corr_matrix = data[numeric_cols].corr()
            
            # Find strong correlations
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols):
                    if i < j:  # Avoid duplicates
                        correlation = corr_matrix.loc[col1, col2]
                        
                        if abs(correlation) > 0.7:  # Strong correlation
                            direction = "positive" if correlation > 0 else "negative"
                            insights.append({
                                "type": "correlation",
                                "description": f"Strong {direction} correlation between {col1} and {col2}",
                                "confidence": min(0.95, abs(correlation)),
                                "data": {
                                    "correlation": correlation,
                                    "columns": [col1, col2]
                                }
                            })
        
        return insights 