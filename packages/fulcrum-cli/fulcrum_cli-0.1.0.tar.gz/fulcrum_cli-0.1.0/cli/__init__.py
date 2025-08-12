#!/usr/bin/env python3
"""Main CLI interface for Fulcrum tools."""

import argparse
import sys

from dotenv import load_dotenv

from .uploader import upload_inspect_log


def upload_inspect_command(args):
    """Handle the upload-inspect subcommand."""
    upload_inspect_log(
        log_file=args.log_file,
        api=args.api,
        batch_size=args.batch_size,
        env_name=args.env_name,
    )


def main():
    """Main entry point for the Fulcrum CLI."""
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        prog="fulcrum",
        description="Fulcrum CLI - Tools for agent observability and analysis",
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )
    
    # upload-inspect subcommand
    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload Inspect AI log files to Fulcrum",
        description="Upload evaluation logs from Inspect AI to Fulcrum for analysis",
    )
    upload_parser.add_argument(
        "log_file",
        type=str,
        help="Path to Inspect .eval or .json log file",
    )
    upload_parser.add_argument(
        "--api",
        default="http://localhost:8000",
        help="Backend API root URL (default: http://localhost:8000)",
    )
    upload_parser.add_argument(
        "--batch-size",
        type=int,
        default=400,
        help="Number of trajectories to upload in each batch (default: 400)",
    )
    upload_parser.add_argument(
        "--env-name",
        type=str,
        help="Override the environment name (defaults to sanitized task name from log)",
    )
    upload_parser.set_defaults(func=upload_inspect_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if hasattr(args, 'func'):
        try:
            args.func(args)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
