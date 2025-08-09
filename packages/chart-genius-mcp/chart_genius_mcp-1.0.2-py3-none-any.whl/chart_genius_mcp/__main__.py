"""
ChartGenius MCP Server - Main Entry Point
==========================================

Command-line interface and server startup.
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path

from .server import ChartGeniusServer
from .config import ChartGeniusConfig
from . import __version__


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration."""
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Setup handlers
    handlers = [logging.StreamHandler(sys.stderr)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    # Set specific logger levels
    logging.getLogger("chart_genius_mcp").setLevel(getattr(logging, log_level.upper()))


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="ChartGenius MCP Server - The Ultimate Chart Generation MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {sys.argv[0]}                              # Start with default settings
  {sys.argv[0]} --config config.json         # Start with custom config
  {sys.argv[0]} --performance-mode           # Start in high-performance mode
  {sys.argv[0]} --benchmark                  # Run performance benchmarks
  {sys.argv[0]} --version                    # Show version information

Features:
  🚀 High-performance chart generation (25,000+ charts/second)
  🧠 AI-powered chart type detection and optimization  
  📊 Multiple chart engines (Plotly, Matplotlib, Seaborn)
  ⚡ O(n) algorithms (fixes O(n²) bottlenecks)
  🎨 50+ chart types with beautiful themes
  🔧 Zero-configuration setup with smart defaults

For more information, visit: https://github.com/your-org/chart-genius-mcp
        """
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="version", 
        version=f"ChartGenius MCP Server v{__version__}"
    )
    
    # Configuration
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (JSON format)"
    )
    
    # Server settings
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Server host (default: localhost)"
    )
    
    parser.add_argument(
        "--port", 
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable"],
        default="stdio",
        help='Transport protocol: "stdio" (MCP stdio), "sse" (HTTP SSE at /sse), or "streamable" (HTTP JSON at /mcp)'
    )

    parser.add_argument(
        "--endpoint",
        type=str,
        default="/mcp",
        help='Endpoint path for HTTP transport (default: "/mcp"). SSE always uses "/sse".'
    )
    
    # Performance settings
    parser.add_argument(
        "--performance-mode",
        action="store_true",
        help="Enable high-performance mode with optimizations"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (not recommended for production)"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI features"
    )
    
    # Logging
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path (default: console only)"
    )
    
    # Development and testing
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run performance benchmarks and exit"
    )
    
    parser.add_argument(
        "--test-chart",
        action="store_true",
        help="Generate a test chart and exit"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    return parser


async def run_benchmark():
    """Run performance benchmarks."""
    
    print("🚀 ChartGenius Performance Benchmarks")
    print("=" * 50)
    
    from .optimization.algorithms import AlgorithmOptimizer
    from .core.data_optimizer import DataOptimizer
    
    # Initialize components
    algorithm_optimizer = AlgorithmOptimizer()
    data_optimizer = DataOptimizer()
    
    print("\n📊 Running algorithm optimization benchmarks...")
    benchmark_results = algorithm_optimizer.benchmark_optimization()
    
    for size, results in benchmark_results["benchmark_results"].items():
        print(f"\n{size}:")
        for chart_type, metrics in results.items():
            print(f"  {chart_type}: {metrics['optimization_time']}ms "
                  f"({metrics['original_size']} → {metrics['optimized_size']} points)")
    
    print(f"\n✅ {benchmark_results['optimization_effectiveness']}")
    
    # Data optimization stats
    print("\n🧠 Data optimization capabilities:")
    optimization_stats = await data_optimizer.get_optimization_stats()
    
    for strategy, description in optimization_stats["algorithms"].items():
        print(f"  {strategy}: {description}")
    
    print(f"\n⚡ Performance improvements:")
    for metric, value in optimization_stats["performance_improvements"].items():
        print(f"  {metric}: {value}")


async def test_chart_generation():
    """Generate a test chart to verify functionality."""
    
    print("🧪 ChartGenius Test Chart Generation")
    print("=" * 50)
    
    # Create test data
    test_data = {
        "columns": ["month", "sales", "profit"],
        "rows": [
            {"month": "Jan", "sales": 1000, "profit": 200},
            {"month": "Feb", "sales": 1200, "profit": 250},
            {"month": "Mar", "sales": 1100, "profit": 220},
            {"month": "Apr", "sales": 1300, "profit": 280},
            {"month": "May", "sales": 1150, "profit": 230}
        ]
    }
    
    # Initialize server
    config = ChartGeniusConfig()
    server = ChartGeniusServer(config)
    
    print("\n📊 Generating test chart...")
    
    try:
        # Generate chart
        result = await server._generate_chart(
            data=test_data,
            chart_type="auto",
            engine="plotly",
            theme="modern"
        )
        
        if result["success"]:
            print("✅ Test chart generated successfully!")
            print(f"   Chart type: {result['metadata']['chart_type']}")
            print(f"   Data points: {result['metadata']['data_points']}")
            print(f"   Engine: {result['metadata']['engine']}")
            print(f"   Theme: {result['metadata']['theme']}")
            
            if "performance" in result:
                print(f"   Generation time: {result['performance']['execution_time_ms']}ms")
        else:
            print("❌ Test chart generation failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")


def validate_configuration(config: ChartGeniusConfig):
    """Validate configuration and show summary."""
    
    print("🔧 ChartGenius Configuration Validation")
    print("=" * 50)
    
    try:
        # Display configuration summary
        config_dict = config.to_dict()
        
        print(f"\n📡 Server: {config.server_name} v{config.version}")
        print(f"   Host: {config.host}:{config.port}")
        
        print(f"\n📊 Chart Engines: {', '.join(config.enabled_engines)}")
        print(f"   Default: {config.default_engine}")
        
        print(f"\n🎨 Themes: {', '.join(config.available_themes)}")
        print(f"   Default: {config.default_theme}")
        
        print(f"\n⚡ Performance:")
        perf_config = config.get_performance_config()
        print(f"   Caching: {'Enabled' if perf_config['caching']['enabled'] else 'Disabled'}")
        print(f"   Optimization: {'Enabled' if perf_config['optimization']['enabled'] else 'Disabled'}")
        print(f"   Large dataset threshold: {perf_config['optimization']['threshold']} rows")
        
        print(f"\n🧠 AI Features:")
        ai_config = config.get_ai_config()
        print(f"   Status: {'Enabled' if ai_config['enabled'] else 'Disabled'}")
        print(f"   API Key: {'Configured' if ai_config['api_key_configured'] else 'Not configured'}")
        
        print(f"\n💾 Export:")
        print(f"   Directory: {config.export_directory}")
        print(f"   Formats: {', '.join(config.allowed_export_formats)}")
        
        print("\n✅ Configuration is valid!")
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {str(e)}")
        sys.exit(1)


async def main():
    """Main entry point."""
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    
    # Load configuration
    if args.config:
        try:
            config = ChartGeniusConfig.from_file(args.config)
            print(f"✅ Loaded configuration from: {args.config}")
        except Exception as e:
            print(f"❌ Failed to load configuration: {str(e)}")
            sys.exit(1)
    else:
        config = ChartGeniusConfig()
    
    # Override config with command-line arguments
    if args.host != "localhost":
        config.host = args.host
    if args.port != 8000:
        config.port = args.port
    if args.no_cache:
        config.cache_enabled = False
    if args.no_ai:
        config.enable_ai_features = False
    if args.performance_mode:
        config.performance_monitoring = True
        config.cache_enabled = True
        config.auto_optimize_large_datasets = True
    
    # Handle special commands
    if args.validate_config:
        validate_configuration(config)
        return
    
    if args.benchmark:
        await run_benchmark()
        return
    
    if args.test_chart:
        await test_chart_generation()
        return
    
    # Start the server
    print(f"🚀 Starting ChartSmith MCP Server v{__version__}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(f"📡 Server: {config.host}:{config.port}", file=sys.stderr)
    print(f"📊 Engines: {', '.join(config.enabled_engines)}", file=sys.stderr)
    print(f"🎨 Themes: {len(config.available_themes)} available", file=sys.stderr)
    # soften performance messaging
    print(f"⚡ Performance: Optimized O(n) data paths; fast by design", file=sys.stderr)
    print(f"🧠 AI Features: {'Enabled' if config.enable_ai_features else 'Disabled'}", file=sys.stderr)
    print(f"💾 Caching: {'Enabled' if config.cache_enabled else 'Disabled'}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    # Initialize and run server
    # Ensure tools are immediately available for all transports (required for Smithery)
    server = ChartGeniusServer(config, lazy_init=False)
    
    try:
        if args.transport == "stdio":
            await server.run(host=config.host, port=config.port)
        else:
            # HTTP modes (SSE or streamable JSON)
            from .http_server import create_http_app
            import uvicorn
            # Server already initialized above with lazy_init=False
            app = create_http_app(server, endpoint=args.endpoint)
            # Note: SSE uses /sse regardless; streamable uses args.endpoint
            # Use uvicorn's async server API to avoid nested asyncio.run()
            uv_config = uvicorn.Config(app, host=config.host, port=config.port, log_level=args.log_level.lower())
            uv_server = uvicorn.Server(uv_config)
            await uv_server.serve()
    except KeyboardInterrupt:
        print("\n👋 ChartGenius MCP Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {str(e)}")
        sys.exit(1)


def cli_main():
    """CLI entry point for package installation."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 ChartGenius MCP Server stopped")
        sys.exit(0)


def benchmark_main():
    """Synchronous entrypoint to run benchmarks from console script."""
    try:
        asyncio.run(run_benchmark())
    except KeyboardInterrupt:
        print("\n👋 Benchmark interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    cli_main() 