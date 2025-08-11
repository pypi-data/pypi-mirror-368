"""
Command-line interface for Quick-API
"""

import argparse
import sys
import os
from typing import Optional
from .core import create_api


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Quick-API: Turn a Model into an API in One Line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  quick-api serve model.pkl
  quick-api serve model.h5 --host 0.0.0.0 --port 8080
  quick-api serve model.joblib --title "My ML API" --workers 4
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Serve a model as an API')
    serve_parser.add_argument('model_path', help='Path to the model file')
    serve_parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    serve_parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    serve_parser.add_argument('--title', default='Quick-API', help='API title')
    serve_parser.add_argument('--description', default='Machine Learning Model API', help='API description')
    serve_parser.add_argument('--version', default='1.0.0', help='API version')
    serve_parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    serve_parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get information about a model')
    info_parser.add_argument('model_path', help='Path to the model file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'serve':
        serve_model(args)
    elif args.command == 'info':
        show_model_info(args)


def serve_model(args):
    """Serve a model as an API"""
    if not os.path.exists(args.model_path):
        print(f"Error: Model file not found: {args.model_path}")
        sys.exit(1)
    
    try:
        print(f"Loading model from: {args.model_path}")
        api = create_api(
            model_path=args.model_path,
            host=args.host,
            port=args.port,
            title=args.title,
            description=args.description,
            version=args.version,
        )
        
        print(f"Starting API server...")
        print(f"API will be available at: http://{args.host}:{args.port}")
        print(f"Documentation available at: http://{args.host}:{args.port}/docs")
        
        api.run(
            reload=args.reload,
            workers=args.workers
        )
        
    except Exception as e:
        print(f"Error starting API: {e}")
        sys.exit(1)


def show_model_info(args):
    """Show information about a model"""
    if not os.path.exists(args.model_path):
        print(f"Error: Model file not found: {args.model_path}")
        sys.exit(1)
    
    try:
        from .model_loader import ModelLoader
        
        print(f"Analyzing model: {args.model_path}")
        loader = ModelLoader(args.model_path)
        info = loader.get_model_info()
        
        print("\nModel Information:")
        print("-" * 40)
        for key, value in info.items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"Error analyzing model: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
