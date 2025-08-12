import argparse
import signal
import sys
import traceback
import logging

from .worker_service import WorkerService


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    logging.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Nedo Vision Worker Service Library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check system dependencies and requirements
  nedo-worker doctor

  # Start worker service with required parameters
  nedo-worker run --token your-token-here --rtmp-server rtmp://server.com:1935/live

  # Start with custom server host
  nedo-worker run --token your-token-here --rtmp-server rtmp://server.com:1935/live --server-host custom.server.com

  # Start with custom storage path
  nedo-worker run --token your-token-here --rtmp-server rtmp://server.com:1935/live --storage-path /path/to/storage
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Doctor command
    doctor_parser = subparsers.add_parser(
        'doctor', 
        help='Check system dependencies and requirements',
        description='Run diagnostic checks for FFmpeg, OpenCV, gRPC and other dependencies'
    )
    
    # Run command
    run_parser = subparsers.add_parser(
        'run',
        help='Start the worker service',
        description='Start the Nedo Vision Worker Service'
    )
    
    run_parser.add_argument(
        "--server-host",
        default="be.vision.sindika.co.id",
        help="Server hostname for communication (default: be.vision.sindika.co.id)"
    )
    
    run_parser.add_argument(
        "--token",
        required=True,
        help="Authentication token for the worker (obtained from frontend)"
    )
    
    run_parser.add_argument(
        "--system-usage-interval",
        type=int,
        default=30,
        help="System usage reporting interval in seconds (default: 30)"
    )
    
    run_parser.add_argument(
        "--rtmp-server",
        required=True,
        help="RTMP server URL for video streaming (e.g., rtmp://server.com:1935/live)"
    )
    
    run_parser.add_argument(
        "--storage-path",
        default="data",
        help="Storage path for databases and files (default: data)"
    )
    
    # Add legacy arguments for backward compatibility (when no subcommand is used)
    parser.add_argument(
        "--token",
        help="(Legacy) Authentication token for the worker (obtained from frontend)"
    )
    
    parser.add_argument(
        "--server-host",
        default="be.vision.sindika.co.id",
        help="(Legacy) Server hostname for communication (default: be.vision.sindika.co.id)"
    )
    
    parser.add_argument(
        "--system-usage-interval",
        type=int,
        default=30,
        help="(Legacy) System usage reporting interval in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--rtmp-server",
        help="(Legacy) RTMP server URL for video streaming (e.g., rtmp://server.com:1935/live)"
    )
    
    parser.add_argument(
        "--storage-path",
        default="data",
        help="(Legacy) Storage path for databases and files (default: data)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="nedo-vision-worker 1.1.1"
    )
    
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="(Deprecated) Run system diagnostics - use 'nedo-worker doctor' instead"
    )
    
    args = parser.parse_args()
    
    # Handle subcommands
    if args.command == 'doctor':
        from .doctor import main as doctor_main
        sys.exit(doctor_main())
    elif args.command == 'run':
        run_worker_service(args)
    elif args.doctor:  # Legacy mode - deprecated --doctor flag
        print("⚠️  Warning: Using deprecated --doctor flag. Use 'nedo-worker doctor' instead.")
        from .doctor import main as doctor_main
        sys.exit(doctor_main())
    elif args.token and args.rtmp_server:  # Legacy mode - if token and rtmp_server are provided without subcommand
        print("⚠️  Warning: Using legacy command format. Consider using 'nedo-worker run --token ... --rtmp-server ...' instead.")
        run_worker_service(args)
    else:
        # If no subcommand provided and no token, show help
        parser.print_help()
        sys.exit(1)


def run_worker_service(args):
    """Run the worker service with the provided arguments."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger = logging.getLogger(__name__)
    
    try:
        # Create and start the worker service
        service = WorkerService(
            server_host=args.server_host,
            token=args.token,
            system_usage_interval=args.system_usage_interval,
            rtmp_server=args.rtmp_server,
            storage_path=args.storage_path
        )
        
        logger.info("🚀 Starting Nedo Vision Worker Service...")
        logger.info(f"🌐 Server: {args.server_host}")
        logger.info(f"🔑 Token: {args.token[:8]}...")
        logger.info(f"⏱️ System Usage Interval: {args.system_usage_interval}s")
        logger.info(f"📡 RTMP Server: {args.rtmp_server}")
        logger.info(f"💾 Storage Path: {args.storage_path}")
        logger.info("Press Ctrl+C to stop the service")
        
        # Start the service
        service.run()
        
        # Keep the service running
        try:
            while getattr(service, 'running', False):
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown requested...")
        finally:
            service.stop()
            logger.info("✅ Service stopped successfully")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 