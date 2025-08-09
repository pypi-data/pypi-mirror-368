"""
ChartGenius MCP Test Configuration
=================================

Pytest fixtures and configuration for comprehensive testing.
"""

import pytest
import pytest_asyncio
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock
import tempfile
import shutil
from pathlib import Path
import os

from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.config import ChartGeniusConfig
from chart_genius_mcp.core.data_optimizer import DataOptimizer
from chart_genius_mcp.optimization.algorithms import AlgorithmOptimizer
from chart_genius_mcp.ai.chart_detector import SmartChartDetector
from chart_genius_mcp.ai.insight_generator import InsightGenerator


# Test configuration
pytest_plugins = ["pytest_asyncio"]

# Default performance threshold to reduce flakiness unless explicitly overridden
os.environ.setdefault("PERF_SPEEDUP_MIN", "1.0")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Create a test configuration with safe defaults."""
    config = ChartGeniusConfig()
    
    # Override with test-safe settings
    config.cache_enabled = False  # Disable cache for testing
    config.performance_monitoring = False
    config.enable_ai_features = False  # Disable AI to avoid API calls
    config.log_level = "WARNING"  # Reduce log noise
    
    return config


@pytest.fixture
def test_config_with_cache():
    """Create a test configuration with caching enabled."""
    config = ChartGeniusConfig()
    
    # Use memory cache for testing
    config.cache_enabled = True
    config.cache_type = "memory"
    config.cache_max_size = 100
    config.performance_monitoring = False
    config.enable_ai_features = False
    
    return config


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest_asyncio.fixture
async def chart_server(test_config):
    """Create a ChartGenius server instance for testing."""
    server = ChartGeniusServer(test_config)
    yield server
    # Cleanup if needed


@pytest_asyncio.fixture
async def chart_server_with_cache(test_config_with_cache):
    """Create a ChartGenius server instance with caching for testing."""
    server = ChartGeniusServer(test_config_with_cache)
    yield server


@pytest.fixture
def data_optimizer():
    """Create a DataOptimizer instance for testing."""
    return DataOptimizer()


@pytest.fixture
def algorithm_optimizer():
    """Create an AlgorithmOptimizer instance for testing."""
    return AlgorithmOptimizer()


@pytest.fixture
def mock_chart_detector():
    """Create a mock SmartChartDetector for testing."""
    detector = Mock(spec=SmartChartDetector)
    
    # Mock the detect_chart_type method
    detector.detect_chart_type = AsyncMock(return_value={
        "recommended_type": "bar",
        "confidence": 0.95,
        "reasoning": "Data has categorical x-axis and numeric y-axis",
        "alternatives": [
            {"type": "line", "confidence": 0.80},
            {"type": "scatter", "confidence": 0.60}
        ]
    })
    
    # Mock the analyze_question method
    detector.analyze_question = AsyncMock(return_value={
        "recommended_chart": "bar",
        "recommended_engine": "plotly",
        "recommended_theme": "modern",
        "reasoning": "Best for categorical comparison",
        "confidence": 0.90
    })
    
    return detector


@pytest.fixture
def mock_insight_generator():
    """Create a mock InsightGenerator for testing."""
    generator = Mock(spec=InsightGenerator)
    
    generator.generate_insights = AsyncMock(return_value=[
        {
            "type": "trend",
            "description": "Sales show upward trend",
            "confidence": 0.85,
            "data": {"trend_slope": 0.15}
        },
        {
            "type": "outlier",
            "description": "March shows unusual spike",
            "confidence": 0.92,
            "data": {"outlier_value": 1500, "expected_range": [800, 1200]}
        }
    ])
    
    return generator


# Sample test data fixtures
@pytest.fixture
def small_dataset():
    """Small dataset for basic testing."""
    return {
        "columns": ["month", "sales", "profit"],
        "rows": [
            {"month": "Jan", "sales": 1000, "profit": 200},
            {"month": "Feb", "sales": 1200, "profit": 250},
            {"month": "Mar", "sales": 1100, "profit": 220},
            {"month": "Apr", "sales": 1300, "profit": 280},
            {"month": "May", "sales": 1150, "profit": 230}
        ]
    }


@pytest.fixture
def medium_dataset():
    """Medium dataset for performance testing."""
    np.random.seed(42)  # For reproducible tests
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = [2020, 2021, 2022, 2023]
    categories = ["Product A", "Product B", "Product C", "Product D"]
    
    rows = []
    for year in years:
        for month in months:
            for category in categories:
                rows.append({
                    "year": year,
                    "month": month,
                    "category": category,
                    "sales": np.random.randint(500, 2000),
                    "profit": np.random.randint(50, 400),
                    "units": np.random.randint(10, 100),
                    "rating": np.random.uniform(3.0, 5.0)
                })
    
    return {
        "columns": ["year", "month", "category", "sales", "profit", "units", "rating"],
        "rows": rows
    }


@pytest.fixture
def large_dataset():
    """Large dataset for stress testing."""
    np.random.seed(42)
    
    rows = []
    for i in range(10000):
        rows.append({
            "id": i,
            "category": f"Cat_{i % 20}",
            "value": np.random.randint(1, 1000),
            "score": np.random.uniform(0, 100),
            "timestamp": f"2023-01-{(i % 30) + 1:02d}",
            "region": ["North", "South", "East", "West"][i % 4]
        })
    
    return {
        "columns": ["id", "category", "value", "score", "timestamp", "region"],
        "rows": rows
    }


@pytest.fixture
def empty_dataset():
    """Empty dataset for edge case testing."""
    return {
        "columns": ["x", "y"],
        "rows": []
    }


@pytest.fixture
def malformed_dataset():
    """Malformed dataset for error handling testing."""
    return {
        "columns": ["a", "b", "c"],
        "rows": [
            {"a": 1, "b": 2},  # Missing column 'c'
            {"a": "text", "b": None, "c": 3},  # Mixed types and None
            {"a": 1, "b": 2, "c": 3, "d": 4},  # Extra column
        ]
    }


@pytest.fixture
def pandas_dataframe(medium_dataset):
    """Convert medium dataset to pandas DataFrame."""
    return pd.DataFrame(medium_dataset["rows"])


@pytest.fixture
def correlation_data():
    """Dataset specifically for correlation/heatmap testing."""
    np.random.seed(42)
    
    # Generate correlated data
    n_samples = 1000
    x1 = np.random.normal(0, 1, n_samples)
    x2 = x1 + np.random.normal(0, 0.5, n_samples)  # Correlated with x1
    x3 = np.random.normal(0, 1, n_samples)  # Independent
    x4 = -x1 + np.random.normal(0, 0.3, n_samples)  # Negatively correlated with x1
    
    rows = []
    for i in range(n_samples):
        rows.append({
            "var1": x1[i],
            "var2": x2[i],
            "var3": x3[i],
            "var4": x4[i]
        })
    
    return {
        "columns": ["var1", "var2", "var3", "var4"],
        "rows": rows
    }


@pytest.fixture
def time_series_data():
    """Time series dataset for temporal chart testing."""
    import datetime
    
    start_date = datetime.datetime(2023, 1, 1)
    rows = []
    
    for i in range(365):
        date = start_date + datetime.timedelta(days=i)
        # Add seasonal pattern and trend
        seasonal = 10 * np.sin(2 * np.pi * i / 365.25)
        trend = 0.01 * i
        noise = np.random.normal(0, 2)
        value = 100 + trend + seasonal + noise
        
        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "value": value,
            "day_of_week": date.strftime("%A"),
            "month": date.strftime("%B")
        })
    
    return {
        "columns": ["date", "value", "day_of_week", "month"],
        "rows": rows
    }


# Performance testing fixtures
@pytest.fixture
def performance_datasets():
    """Multiple datasets of different sizes for performance testing."""
    datasets = {}
    
    for size in [100, 500, 1000, 5000]:
        np.random.seed(42)
        rows = []
        
        for i in range(size):
            rows.append({
                "id": i,
                "category": f"Cat_{i % 10}",
                "value": np.random.randint(1, 100),
                "score": np.random.uniform(0, 1)
            })
        
        datasets[f"size_{size}"] = {
            "columns": ["id", "category", "value", "score"],
            "rows": rows
        }
    
    return datasets


# Mock fixtures for external dependencies
@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API responses for AI testing."""
    mock = Mock()
    
    # Mock chat completion response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = """
    {
        "recommended_chart": "bar",
        "confidence": 0.9,
        "reasoning": "Categorical data is best visualized with bar charts"
    }
    """
    
    mock.chat.completions.create = AsyncMock(return_value=mock_response)
    
    return mock


@pytest.fixture
def mock_redis():
    """Mock Redis client for caching tests."""
    mock = Mock()
    
    # Mock Redis operations
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.exists = AsyncMock(return_value=False)
    mock.keys = AsyncMock(return_value=[])
    
    return mock


# Test markers and configurations
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )
    config.addinivalue_line(
        "markers", "ai: marks tests that require AI features"
    )
    config.addinivalue_line(
        "markers", "cache: marks tests that require caching"
    )


# Helper functions for tests
def assert_chart_result_valid(result: Dict[str, Any]):
    """Assert that a chart result has the expected structure."""
    assert "success" in result
    assert result["success"] is True
    assert "chart" in result
    assert "metadata" in result
    
    metadata = result["metadata"]
    assert "chart_type" in metadata
    assert "engine" in metadata
    assert "theme" in metadata
    assert "data_points" in metadata


def assert_performance_acceptable(execution_time_ms: float, max_time_ms: float = 1000):
    """Assert that performance is within acceptable limits."""
    assert execution_time_ms < max_time_ms, f"Execution took {execution_time_ms}ms, expected < {max_time_ms}ms"


def assert_optimization_effective(original_size: int, optimized_size: int, max_ratio: float = 0.8):
    """Assert that data optimization was effective."""
    ratio = optimized_size / original_size
    assert ratio <= max_ratio, f"Optimization ratio {ratio:.2f} exceeds maximum {max_ratio}"


# Async test helpers
async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
    """Wait for a condition to become true within a timeout."""
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
            return True
        await asyncio.sleep(interval)
    
    return False 