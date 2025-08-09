"""
Performance Monitor - Real-time performance tracking
==================================================

Performance monitoring and benchmarking for ChartGenius MCP.
"""

import asyncio
import time
import psutil
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Real-time performance monitoring and statistics."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.start_time = time.time()
        self.metrics = {
            "chart_generations": 0,
            "total_execution_time": 0.0,
            "avg_execution_time": 0.0,
            "memory_usage_mb": 0.0,
            "cpu_usage_percent": 0.0
        }
        self.history = []
        self.process = psutil.Process(os.getpid())
    
    async def start(self):
        """Start performance monitoring."""
        logger.info("Performance monitoring started")
    
    async def record_chart_generation(self, execution_time_ms: float):
        """Record a chart generation event."""
        self.metrics["chart_generations"] += 1
        self.metrics["total_execution_time"] += execution_time_ms
        self.metrics["avg_execution_time"] = (
            self.metrics["total_execution_time"] / self.metrics["chart_generations"]
        )
        
        # Update system metrics
        await self._update_system_metrics()
        
        # Add to history
        self.history.append({
            "timestamp": time.time(),
            "execution_time_ms": execution_time_ms,
            "memory_mb": self.metrics["memory_usage_mb"],
            "cpu_percent": self.metrics["cpu_usage_percent"]
        })
        
        # Keep only recent history (last 1000 entries)
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    async def get_stats(self, include_history: bool = False) -> Dict[str, Any]:
        """Get current performance statistics."""
        
        # Update current metrics
        await self._update_system_metrics()
        
        uptime_seconds = time.time() - self.start_time
        
        stats = {
            "uptime_seconds": uptime_seconds,
            "chart_generations": self.metrics["chart_generations"],
            "avg_execution_time_ms": round(self.metrics["avg_execution_time"], 2),
            "total_execution_time_ms": round(self.metrics["total_execution_time"], 2),
            "charts_per_second": self._calculate_rps(),
            "memory_usage_mb": round(self.metrics["memory_usage_mb"], 2),
            "cpu_usage_percent": round(self.metrics["cpu_usage_percent"], 2),
            "performance_grade": self._calculate_performance_grade()
        }
        
        if include_history:
            stats["history"] = self.history[-100:]  # Last 100 entries
        
        return stats
    
    async def _update_system_metrics(self):
        """Update system performance metrics."""
        try:
            # Memory usage
            memory_info = self.process.memory_info()
            self.metrics["memory_usage_mb"] = memory_info.rss / 1024 / 1024
            
            # CPU usage
            self.metrics["cpu_usage_percent"] = self.process.cpu_percent()
            
        except Exception as e:
            logger.warning(f"Failed to update system metrics: {str(e)}")
    
    def _calculate_rps(self) -> float:
        """Calculate requests per second."""
        uptime = time.time() - self.start_time
        if uptime > 0:
            return self.metrics["chart_generations"] / uptime
        return 0.0
    
    def _calculate_performance_grade(self) -> str:
        """Calculate overall performance grade."""
        
        avg_time = self.metrics["avg_execution_time"]
        memory_mb = self.metrics["memory_usage_mb"]
        cpu_percent = self.metrics["cpu_usage_percent"]
        
        # Grade based on response time (primary factor)
        if avg_time < 100:
            grade = "A"
        elif avg_time < 300:
            grade = "B"
        elif avg_time < 500:
            grade = "C"
        elif avg_time < 1000:
            grade = "D"
        else:
            grade = "F"
        
        # Adjust for resource usage
        if memory_mb > 1000 or cpu_percent > 80:
            grade = chr(min(ord(grade) + 1, ord('F')))  # Downgrade
        
        return grade
    
    async def get_benchmark_comparison(self) -> Dict[str, Any]:
        """Compare current performance to benchmarks."""
        
        stats = await self.get_stats()
        
        # ChartGenius performance targets
        targets = {
            "chart_generation_rps": 25000,
            "avg_response_time_ms": 100,
            "memory_efficiency_mb": 500,
            "cpu_efficiency_percent": 50
        }
        
        actual_rps = stats["charts_per_second"]
        actual_response = stats["avg_execution_time_ms"]
        actual_memory = stats["memory_usage_mb"]
        actual_cpu = stats["cpu_usage_percent"]
        
        comparison = {
            "performance_vs_target": {
                "rps": {
                    "target": targets["chart_generation_rps"],
                    "actual": actual_rps,
                    "status": "✅" if actual_rps > targets["chart_generation_rps"] * 0.8 else "❌"
                },
                "response_time": {
                    "target": targets["avg_response_time_ms"],
                    "actual": actual_response,
                    "status": "✅" if actual_response < targets["avg_response_time_ms"] * 1.2 else "❌"
                },
                "memory": {
                    "target": targets["memory_efficiency_mb"],
                    "actual": actual_memory,
                    "status": "✅" if actual_memory < targets["memory_efficiency_mb"] * 1.5 else "❌"
                },
                "cpu": {
                    "target": targets["cpu_efficiency_percent"],
                    "actual": actual_cpu,
                    "status": "✅" if actual_cpu < targets["cpu_efficiency_percent"] * 1.5 else "❌"
                }
            },
            "overall_performance": stats["performance_grade"],
            "recommendation": self._get_performance_recommendation(stats, targets)
        }
        
        return comparison
    
    def _get_performance_recommendation(
        self,
        stats: Dict[str, Any],
        targets: Dict[str, Any]
    ) -> str:
        """Get performance improvement recommendation."""
        
        issues = []
        
        if stats["avg_execution_time_ms"] > targets["avg_response_time_ms"]:
            issues.append("Consider enabling data optimization for large datasets")
        
        if stats["memory_usage_mb"] > targets["memory_efficiency_mb"]:
            issues.append("Memory usage is high, consider cache size limits")
        
        if stats["cpu_usage_percent"] > targets["cpu_efficiency_percent"]:
            issues.append("CPU usage is high, consider optimizing algorithms")
        
        if not issues:
            return "Performance is excellent! All targets met."
        
        return "Recommendations: " + "; ".join(issues) 