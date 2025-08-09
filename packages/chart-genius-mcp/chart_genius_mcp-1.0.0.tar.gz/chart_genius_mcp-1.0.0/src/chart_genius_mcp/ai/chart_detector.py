"""
Smart Chart Detector - AI-powered chart type detection
======================================================

Intelligent chart type detection based on data patterns and characteristics.
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SmartChartDetector:
    """
    AI-powered chart type detection based on data analysis.
    
    Analyzes data patterns, types, and distributions to recommend
    the most appropriate chart type for visualization.
    """
    
    def __init__(self):
        """Initialize the smart chart detector."""
        self.chart_type_rules = self._initialize_detection_rules()
    
    async def detect_chart_type(
        self,
        data: pd.DataFrame,
        goal: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect the optimal chart type for the given data.
        
        Args:
            data: DataFrame to analyze
            goal: Optional analysis goal (trends, comparison, distribution, etc.)
            
        Returns:
            Dict with recommended chart type, confidence, and reasoning
        """
        try:
            # Analyze data characteristics
            analysis = self._analyze_data_characteristics(data)
            
            # Apply detection rules
            recommendations = self._apply_detection_rules(analysis, goal)
            
            # Select best recommendation
            best_recommendation = recommendations[0] if recommendations else {
                "recommended_type": "bar",
                "confidence": 0.5,
                "reasoning": "Default fallback to bar chart"
            }
            
            # Add alternatives
            alternatives = [
                {
                    "type": rec["recommended_type"],
                    "confidence": rec["confidence"],
                    "reasoning": rec["reasoning"]
                }
                for rec in recommendations[1:3]  # Top 2 alternatives
            ]
            
            return {
                "recommended_type": best_recommendation["recommended_type"],
                "confidence": best_recommendation["confidence"],
                "reasoning": best_recommendation["reasoning"],
                "alternatives": alternatives,
                "data_analysis": analysis
            }
            
        except Exception as e:
            logger.warning(f"Chart detection failed: {str(e)}, using fallback")
            return {
                "recommended_type": "bar",
                "confidence": 0.5,
                "reasoning": f"Detection failed ({str(e)}), using default bar chart",
                "alternatives": [],
                "data_analysis": {}
            }
    
    async def analyze_question(
        self,
        question: str,
        data: pd.DataFrame,
        context: str = "business"
    ) -> Dict[str, Any]:
        """
        Analyze a natural language question to determine optimal visualization.
        
        Args:
            question: Natural language question about the data
            data: DataFrame to visualize
            context: Context (business, technical, executive)
            
        Returns:
            Dict with chart recommendation based on question analysis
        """
        try:
            # Simple keyword-based analysis (would use LLM in production)
            question_lower = question.lower()
            
            # Detect intent from keywords
            if any(word in question_lower for word in ["trend", "over time", "change", "growth"]):
                chart_type = "line"
                reasoning = "Question asks about trends over time"
                confidence = 0.9
            elif any(word in question_lower for word in ["compare", "comparison", "versus", "vs"]):
                chart_type = "bar"
                reasoning = "Question asks for comparison between categories"
                confidence = 0.85
            elif any(word in question_lower for word in ["correlation", "relationship", "related"]):
                chart_type = "scatter"
                reasoning = "Question asks about relationships between variables"
                confidence = 0.8
            elif any(word in question_lower for word in ["distribution", "spread", "range"]):
                chart_type = "histogram"
                reasoning = "Question asks about data distribution"
                confidence = 0.8
            elif any(word in question_lower for word in ["proportion", "percentage", "share", "part"]):
                chart_type = "pie"
                reasoning = "Question asks about proportions or parts of a whole"
                confidence = 0.75
            else:
                # Fall back to data-driven detection
                detection_result = await self.detect_chart_type(data)
                chart_type = detection_result["recommended_type"]
                reasoning = f"Based on data analysis: {detection_result['reasoning']}"
                confidence = detection_result["confidence"] * 0.7  # Lower confidence for fallback
            
            return {
                "recommended_chart": chart_type,
                "recommended_engine": "plotly",  # Default to plotly
                "recommended_theme": self._select_theme_for_context(context),
                "reasoning": reasoning,
                "confidence": confidence,
                "question_analysis": {
                    "intent": self._extract_intent(question_lower),
                    "keywords": self._extract_keywords(question_lower),
                    "context": context
                }
            }
            
        except Exception as e:
            logger.warning(f"Question analysis failed: {str(e)}")
            return {
                "recommended_chart": "bar",
                "recommended_engine": "plotly",
                "recommended_theme": "modern",
                "reasoning": f"Question analysis failed ({str(e)}), using default",
                "confidence": 0.5
            }
    
    def _initialize_detection_rules(self) -> List[Dict[str, Any]]:
        """Initialize chart type detection rules."""
        return [
            {
                "chart_type": "line",
                "conditions": ["has_temporal_data", "numeric_y_axis"],
                "confidence_boost": 0.9,
                "reasoning": "Time series data is best visualized with line charts"
            },
            {
                "chart_type": "bar",
                "conditions": ["categorical_x_axis", "numeric_y_axis", "moderate_categories"],
                "confidence_boost": 0.8,
                "reasoning": "Categorical data with numeric values works well with bar charts"
            },
            {
                "chart_type": "scatter",
                "conditions": ["numeric_x_axis", "numeric_y_axis", "correlation_potential"],
                "confidence_boost": 0.85,
                "reasoning": "Two numeric variables can show relationships with scatter plots"
            },
            {
                "chart_type": "pie",
                "conditions": ["categorical_x_axis", "numeric_y_axis", "few_categories", "positive_values"],
                "confidence_boost": 0.7,
                "reasoning": "Small number of categories with positive values suit pie charts"
            },
            {
                "chart_type": "heatmap",
                "conditions": ["multiple_numeric_columns", "correlation_matrix_suitable"],
                "confidence_boost": 0.75,
                "reasoning": "Multiple numeric variables can be visualized as correlation heatmap"
            },
            {
                "chart_type": "histogram",
                "conditions": ["single_numeric_column", "distribution_analysis"],
                "confidence_boost": 0.8,
                "reasoning": "Single numeric variable distribution is best shown with histogram"
            }
        ]
    
    def _analyze_data_characteristics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze characteristics of the data."""
        
        analysis = {
            "rows": len(data),
            "columns": len(data.columns),
            "numeric_columns": len(data.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(data.select_dtypes(include=["object"]).columns),
            "datetime_columns": len(data.select_dtypes(include=["datetime64"]).columns),
            "null_percentage": (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
        }
        
        # Analyze column types
        if len(data.columns) >= 2:
            first_col = data.columns[0]
            second_col = data.columns[1]
            
            analysis.update({
                "first_column_type": str(data[first_col].dtype),
                "second_column_type": str(data[second_col].dtype),
                "first_column_unique_values": data[first_col].nunique(),
                "second_column_unique_values": data[second_col].nunique(),
            })
        
        # Detect patterns
        analysis.update({
            "has_temporal_data": self._has_temporal_data(data),
            "categorical_x_axis": self._is_categorical_column(data, 0),
            "numeric_y_axis": self._is_numeric_column(data, 1),
            "numeric_x_axis": self._is_numeric_column(data, 0),
            "moderate_categories": self._has_moderate_categories(data, 0),
            "few_categories": self._has_few_categories(data, 0),
            "positive_values": self._has_positive_values(data, 1),
            "multiple_numeric_columns": analysis["numeric_columns"] >= 3,
            "correlation_potential": self._has_correlation_potential(data),
            "correlation_matrix_suitable": analysis["numeric_columns"] >= 2,
            "single_numeric_column": analysis["numeric_columns"] == 1,
            "distribution_analysis": True  # Always possible
        })
        
        return analysis
    
    def _apply_detection_rules(
        self,
        analysis: Dict[str, Any],
        goal: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Apply detection rules to recommend chart types."""
        
        recommendations = []
        
        for rule in self.chart_type_rules:
            # Check if all conditions are met
            conditions_met = all(
                analysis.get(condition, False)
                for condition in rule["conditions"]
            )
            
            if conditions_met:
                confidence = rule["confidence_boost"]
                
                # Adjust confidence based on goal
                if goal:
                    confidence = self._adjust_confidence_for_goal(
                        confidence, rule["chart_type"], goal
                    )
                
                recommendations.append({
                    "recommended_type": rule["chart_type"],
                    "confidence": confidence,
                    "reasoning": rule["reasoning"]
                })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        # If no recommendations, provide defaults
        if not recommendations:
            recommendations = [
                {
                    "recommended_type": "bar",
                    "confidence": 0.6,
                    "reasoning": "Default recommendation for categorical data"
                }
            ]
        
        return recommendations
    
    def _has_temporal_data(self, data: pd.DataFrame) -> bool:
        """Check if data has temporal characteristics."""
        if len(data.columns) == 0:
            return False
        
        first_col = data.columns[0]
        
        # Check if column is datetime
        if pd.api.types.is_datetime64_any_dtype(data[first_col]):
            return True
        
        # Check if column name suggests time
        time_keywords = ["date", "time", "year", "month", "day", "timestamp"]
        col_name_lower = first_col.lower()
        
        return any(keyword in col_name_lower for keyword in time_keywords)
    
    def _is_categorical_column(self, data: pd.DataFrame, col_index: int) -> bool:
        """Check if column is categorical."""
        if col_index >= len(data.columns):
            return False
        
        col = data.columns[col_index]
        return pd.api.types.is_object_dtype(data[col]) or data[col].nunique() < len(data) * 0.5
    
    def _is_numeric_column(self, data: pd.DataFrame, col_index: int) -> bool:
        """Check if column is numeric."""
        if col_index >= len(data.columns):
            return False
        
        col = data.columns[col_index]
        return pd.api.types.is_numeric_dtype(data[col])
    
    def _has_moderate_categories(self, data: pd.DataFrame, col_index: int) -> bool:
        """Check if column has moderate number of categories (good for bar chart)."""
        if col_index >= len(data.columns):
            return False
        
        col = data.columns[col_index]
        unique_count = data[col].nunique()
        return 2 <= unique_count <= 20
    
    def _has_few_categories(self, data: pd.DataFrame, col_index: int) -> bool:
        """Check if column has few categories (good for pie chart)."""
        if col_index >= len(data.columns):
            return False
        
        col = data.columns[col_index]
        unique_count = data[col].nunique()
        return 2 <= unique_count <= 8
    
    def _has_positive_values(self, data: pd.DataFrame, col_index: int) -> bool:
        """Check if numeric column has positive values (good for pie chart)."""
        if col_index >= len(data.columns):
            return False
        
        col = data.columns[col_index]
        if not pd.api.types.is_numeric_dtype(data[col]):
            return False
        
        return (data[col] >= 0).all()
    
    def _has_correlation_potential(self, data: pd.DataFrame) -> bool:
        """Check if data has potential for correlation analysis."""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        return len(numeric_cols) >= 2
    
    def _adjust_confidence_for_goal(
        self,
        base_confidence: float,
        chart_type: str,
        goal: str
    ) -> float:
        """Adjust confidence based on analysis goal."""
        
        goal_chart_mapping = {
            "trends": {"line": 0.2, "bar": -0.1},
            "comparison": {"bar": 0.2, "line": -0.1},
            "distribution": {"histogram": 0.3, "bar": -0.1},
            "correlation": {"scatter": 0.3, "heatmap": 0.2},
            "composition": {"pie": 0.2, "bar": 0.1}
        }
        
        adjustment = goal_chart_mapping.get(goal, {}).get(chart_type, 0)
        return min(1.0, max(0.1, base_confidence + adjustment))
    
    def _select_theme_for_context(self, context: str) -> str:
        """Select appropriate theme based on context."""
        theme_mapping = {
            "business": "corporate",
            "technical": "modern",
            "executive": "corporate",
            "academic": "modern",
            "presentation": "corporate"
        }
        
        return theme_mapping.get(context, "modern")
    
    def _extract_intent(self, question: str) -> str:
        """Extract intent from question."""
        if any(word in question for word in ["trend", "change", "over time"]):
            return "temporal_analysis"
        elif any(word in question for word in ["compare", "versus", "difference"]):
            return "comparison"
        elif any(word in question for word in ["correlation", "relationship"]):
            return "relationship_analysis"
        elif any(word in question for word in ["distribution", "spread"]):
            return "distribution_analysis"
        else:
            return "general_analysis"
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Extract relevant keywords from question."""
        chart_keywords = [
            "trend", "compare", "comparison", "correlation", "relationship",
            "distribution", "spread", "over time", "versus", "vs", "proportion",
            "percentage", "share", "growth", "change"
        ]
        
        found_keywords = [
            keyword for keyword in chart_keywords
            if keyword in question
        ]
        
        return found_keywords 