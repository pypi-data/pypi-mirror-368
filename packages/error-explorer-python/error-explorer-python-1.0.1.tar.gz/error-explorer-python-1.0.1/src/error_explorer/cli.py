"""Command-line interface for Error Explorer Python SDK."""

import argparse
import sys
from typing import Optional


def test_connection(webhook_url: str, project_name: str) -> bool:
    """Test connection to Error Explorer.
    
    Args:
        webhook_url: Webhook URL to test
        project_name: Project name to use
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from . import init, capture_message
        
        print(f"Testing connection to {webhook_url}...")
        
        # Initialize client
        client = init(
            webhook_url=webhook_url,
            project_name=project_name,
            environment="test"
        )
        
        # Send test message
        capture_message("Test message from Error Explorer Python SDK CLI", "info", {
            "test": True,
            "cli_version": "1.0.0"
        })
        
        print("✅ Test message sent successfully!")
        print("Check your Error Explorer dashboard to see the test message.")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Error Explorer Python SDK CLI",
        prog="error-explorer"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test connection to Error Explorer")
    test_parser.add_argument(
        "webhook_url",
        help="Error Explorer webhook URL"
    )
    test_parser.add_argument(
        "project_name",
        help="Project name"
    )
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "test":
        success = test_connection(args.webhook_url, args.project_name)
        sys.exit(0 if success else 1)
    elif args.command == "version":
        from . import __version__
        print(f"Error Explorer Python SDK v{__version__}")
        print(f"Python {sys.version}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()