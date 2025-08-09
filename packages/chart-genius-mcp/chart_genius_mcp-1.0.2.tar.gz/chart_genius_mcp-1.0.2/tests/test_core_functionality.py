"""
Test Core Chart Generation Functionality
=======================================

Tests for basic chart generation, data processing, and core features.
"""

import pytest
import time
import pandas as pd
from unittest.mock import patch, Mock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chart_genius_mcp.server import ChartGeniusServer
from chart_genius_mcp.exceptions import ChartGenerationError, DataOptimizationError
from conftest import assert_chart_result_valid, assert_performance_acceptable


class TestBasicChartGeneration:
    """Test basic chart generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_simple_chart(self, chart_server, small_dataset):
        """Test generating a simple chart with small dataset."""
        result = await chart_server._generate_chart(
            data=small_dataset,
            chart_type="bar",
            engine="plotly",
            theme="modern"
        )
        
        assert_chart_result_valid(result)
        assert result["metadata"]["chart_type"] == "bar"
        assert result["metadata"]["engine"] == "plotly"
        assert result["metadata"]["theme"] == "modern"
        assert result["metadata"]["data_points"] == 5
    
    @pytest.mark.asyncio
    async def test_auto_chart_detection(self, chart_server, small_dataset, mock_chart_detector):
        """Test automatic chart type detection."""
        with patch.object(chart_server, 'chart_detector', mock_chart_detector):
            result = await chart_server._generate_chart(
                data=small_dataset,
                chart_type="auto",
                engine="plotly"
            )
        
        assert_chart_result_valid(result)
        # Chart detector should have been called
        mock_chart_detector.detect_chart_type.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_different_chart_types(self, chart_server, small_dataset):
        """Test generation of different chart types."""
        chart_types = ["bar", "line", "scatter", "pie"]
        
        for chart_type in chart_types:
            result = await chart_server._generate_chart(
                data=small_dataset,
                chart_type=chart_type,
                engine="plotly"
            )
            
            assert_chart_result_valid(result)
            assert result["metadata"]["chart_type"] == chart_type
    
    @pytest.mark.asyncio
    async def test_different_engines(self, chart_server, small_dataset):
        """Test chart generation with different engines."""
        engines = ["plotly", "matplotlib", "seaborn"]
        
        for engine in engines:
            result = await chart_server._generate_chart(
                data=small_dataset,
                chart_type="bar",
                engine=engine
            )
            
            assert_chart_result_valid(result)
            assert result["metadata"]["engine"] == engine
    
    @pytest.mark.asyncio
    async def test_different_themes(self, chart_server, small_dataset):
        """Test chart generation with different themes."""
        themes = ["modern", "corporate", "dark", "accessible"]
        
        for theme in themes:
            result = await chart_server._generate_chart(
                data=small_dataset,
                chart_type="bar",
                theme=theme
            )
            
            assert_chart_result_valid(result)
            assert result["metadata"]["theme"] == theme
    
    @pytest.mark.asyncio
    async def test_empty_dataset_handling(self, chart_server, empty_dataset):
        """Test handling of empty datasets."""
        with pytest.raises(ChartGenerationError):
            await chart_server._generate_chart(
                data=empty_dataset,
                chart_type="bar"
            )
    
    @pytest.mark.asyncio
    async def test_malformed_data_handling(self, chart_server, malformed_dataset):
        """Test handling of malformed datasets."""
        # Should handle malformed data gracefully
        result = await chart_server._generate_chart(
            data=malformed_dataset,
            chart_type="bar"
        )
        
        # Should either succeed with cleaned data or raise appropriate error
        assert result is not None


class TestPerformanceOptimization:
    """Test performance optimization features."""
    
    @pytest.mark.asyncio
    async def test_large_dataset_optimization(self, chart_server, large_dataset):
        """Test optimization of large datasets."""
        start_time = time.time()
        
        result = await chart_server._generate_chart(
            data=large_dataset,
            chart_type="bar",
            optimize_large_data=True
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        assert_chart_result_valid(result)
        assert result["metadata"]["optimized"] is True
        assert_performance_acceptable(execution_time, max_time_ms=2000)
    
    @pytest.mark.asyncio
    async def test_optimization_disabled(self, chart_server, large_dataset):
        """Test behavior when optimization is disabled."""
        result = await chart_server._generate_chart(
            data=large_dataset,
            chart_type="bar",
            optimize_large_data=False
        )
        
        assert_chart_result_valid(result)
        assert result["metadata"]["optimized"] is False
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_targets(self, chart_server, medium_dataset):
        """Test that performance targets are met."""
        start_time = time.time()
        
        result = await chart_server._generate_chart(
            data=medium_dataset,
            chart_type="bar"
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        assert_chart_result_valid(result)
        # Should complete within target time
        assert_performance_acceptable(execution_time, max_time_ms=500)
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_stress_testing(self, chart_server, performance_datasets):
        """Stress test with multiple dataset sizes."""
        results = {}
        
        for size_name, dataset in performance_datasets.items():
            start_time = time.time()
            
            result = await chart_server._generate_chart(
                data=dataset,
                chart_type="bar"
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            assert_chart_result_valid(result)
            results[size_name] = execution_time
        
        # Verify performance scales reasonably (allow small jitter)
        assert results["size_100"] <= results["size_1000"] + 2.0
        
        # Even largest dataset should complete quickly
        assert_performance_acceptable(results["size_5000"], max_time_ms=1500)


class TestDataOptimization:
    """Test data optimization algorithms."""
    
    @pytest.mark.asyncio
    async def test_intelligent_optimization(self, data_optimizer, pandas_dataframe):
        """Test intelligent optimization strategy."""
        original_size = len(pandas_dataframe)
        
        optimized_df = await data_optimizer.optimize_dataframe(
            df=pandas_dataframe,
            max_points=100,
            strategy="intelligent"
        )
        
        assert len(optimized_df) <= 100
        assert len(optimized_df) < original_size
        # Should preserve important columns
        assert not optimized_df.empty
    
    @pytest.mark.asyncio
    async def test_sample_optimization(self, data_optimizer, pandas_dataframe):
        """Test sample optimization strategy."""
        optimized_df = await data_optimizer.optimize_dataframe(
            df=pandas_dataframe,
            max_points=50,
            strategy="sample"
        )
        
        assert len(optimized_df) <= 50
        assert optimized_df.columns.tolist() == pandas_dataframe.columns.tolist()
    
    @pytest.mark.asyncio
    async def test_aggregate_optimization(self, data_optimizer, pandas_dataframe):
        """Test aggregate optimization strategy."""
        optimized_df = await data_optimizer.optimize_dataframe(
            df=pandas_dataframe,
            max_points=30,
            strategy="aggregate"
        )
        
        assert len(optimized_df) <= 30
        # Should have aggregated statistics
        assert not optimized_df.empty
    
    @pytest.mark.asyncio
    async def test_optimization_with_small_data(self, data_optimizer):
        """Test that small datasets are not unnecessarily optimized."""
        small_df = pd.DataFrame({
            "x": [1, 2, 3, 4, 5],
            "y": [10, 20, 30, 40, 50]
        })
        
        optimized_df = await data_optimizer.optimize_dataframe(
            df=small_df,
            max_points=1000,
            strategy="intelligent"
        )
        
        # Should return unchanged
        assert len(optimized_df) == len(small_df)
        pd.testing.assert_frame_equal(optimized_df, small_df)


class TestAlgorithmOptimization:
    """Test algorithm optimization features."""
    
    def test_categorical_chart_optimization(self, algorithm_optimizer, pandas_dataframe):
        """Test optimization for categorical charts."""
        optimized_df = algorithm_optimizer.optimize_chart_data(
            df=pandas_dataframe,
            chart_type="bar"
        )
        
        assert not optimized_df.empty
        # Should have aggregated data by categories
        assert len(optimized_df) <= len(pandas_dataframe)
    
    def test_scatter_chart_optimization(self, algorithm_optimizer, pandas_dataframe):
        """Test optimization for scatter charts."""
        optimized_df = algorithm_optimizer.optimize_chart_data(
            df=pandas_dataframe,
            chart_type="scatter"
        )
        
        # Should have added statistical columns
        statistical_columns = [col for col in optimized_df.columns if "_zscore" in col or "_is_outlier" in col]
        assert len(statistical_columns) > 0
    
    def test_pie_chart_optimization(self, algorithm_optimizer):
        """Test optimization for pie charts."""
        # Create test data with duplicates
        test_df = pd.DataFrame({
            "category": ["A", "B", "A", "C", "B", "A"],
            "value": [10, 20, 15, 30, 25, 12]
        })
        
        optimized_df = algorithm_optimizer.optimize_chart_data(
            df=test_df,
            chart_type="pie"
        )
        
        # Should have aggregated duplicates
        assert len(optimized_df) == 3  # A, B, C
        assert "percentage" in optimized_df.columns
        assert "cumulative" in optimized_df.columns
    
    def test_lookup_structure_creation(self, algorithm_optimizer):
        """Test creation of optimized lookup structures."""
        test_data = [
            {"category": "A", "value": 10, "score": 0.8},
            {"category": "B", "value": 20, "score": 0.9},
            {"category": "A", "value": 15, "score": 0.7},
        ]
        
        lookup = algorithm_optimizer.create_optimized_lookup_structure(
            data=test_data,
            x_column="category",
            y_columns=["value", "score"]
        )
        
        assert "index" in lookup
        assert "categories" in lookup
        assert lookup["complexity"] == "O(1)"
        
        # Test lookup functionality
        assert "A" in lookup["index"]
        assert "B" in lookup["index"]
        assert lookup["index"]["A"]["value"] == 25  # Aggregated: 10 + 15


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_invalid_chart_type(self, chart_server, small_dataset):
        """Test handling of invalid chart types."""
        with pytest.raises(ChartGenerationError):
            await chart_server._generate_chart(
                data=small_dataset,
                chart_type="invalid_type"
            )
    
    @pytest.mark.asyncio
    async def test_invalid_engine(self, chart_server, small_dataset):
        """Test handling of invalid engines."""
        with pytest.raises(ChartGenerationError):
            await chart_server._generate_chart(
                data=small_dataset,
                chart_type="bar",
                engine="invalid_engine"
            )
    
    @pytest.mark.asyncio
    async def test_missing_data_columns(self, chart_server):
        """Test handling of missing required data columns."""
        invalid_data = {
            "columns": [],
            "rows": []
        }
        
        with pytest.raises(ChartGenerationError):
            await chart_server._generate_chart(
                data=invalid_data,
                chart_type="bar"
            )
    
    @pytest.mark.asyncio
    async def test_data_type_mismatch(self, chart_server):
        """Test handling of data type mismatches."""
        mixed_data = {
            "columns": ["x", "y"],
            "rows": [
                {"x": "text", "y": "not_a_number"},
                {"x": 1, "y": "still_not_a_number"}
            ]
        }
        
        # Should handle gracefully or raise appropriate error
        try:
            result = await chart_server._generate_chart(
                data=mixed_data,
                chart_type="scatter"
            )
            # If it succeeds, should have valid structure
            assert_chart_result_valid(result)
        except ChartGenerationError:
            # Acceptable to fail with clear error
            pass
    
    @pytest.mark.asyncio
    async def test_optimization_failure_fallback(self, data_optimizer):
        """Test fallback when optimization fails."""
        # Create problematic data that might cause optimization to fail
        problematic_df = pd.DataFrame({
            "x": [None, None, None],
            "y": [float('inf'), float('-inf'), float('nan')]
        })
        
        # Should not raise exception, should fallback gracefully
        result = await data_optimizer.optimize_dataframe(
            df=problematic_df,
            max_points=10,
            strategy="intelligent"
        )
        
        assert result is not None
        assert isinstance(result, pd.DataFrame)


class TestConcurrency:
    """Test concurrent chart generation."""
    
    @pytest.mark.asyncio
    async def test_concurrent_chart_generation(self, chart_server, small_dataset):
        """Test generating multiple charts concurrently."""
        import asyncio
        
        async def generate_chart():
            return await chart_server._generate_chart(
                data=small_dataset,
                chart_type="bar"
            )
        
        # Generate 5 charts concurrently
        tasks = [generate_chart() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for result in results:
            assert_chart_result_valid(result)
    
    @pytest.mark.asyncio
    async def test_batch_chart_generation(self, chart_server, small_dataset):
        """Test batch chart generation functionality."""
        datasets = [small_dataset] * 3
        configs = [{"chart_type": "bar"}, {"chart_type": "line"}, {"chart_type": "scatter"}]
        
        result = await chart_server._generate_chart_batch(
            datasets=datasets,
            chart_configs=configs,
            parallel=True
        )
        
        assert result["success"] is True
        assert len(result["charts"]) == 3
        assert result["batch_stats"]["total_charts"] == 3
        assert result["batch_stats"]["parallel_execution"] is True 