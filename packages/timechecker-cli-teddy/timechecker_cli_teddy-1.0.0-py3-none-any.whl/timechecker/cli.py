"""CLI interface for timechecker."""

import argparse
import logging
import sys
from .core import TimeChecker

def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Get current time in different timezones",
        prog="tmt"
    )
    
    parser.add_argument(
        "-p", "--timezone",
        choices=["PST", "EST", "BST", "WAT", "CET"],
        help="Timezone code (PST, EST, BST, WAT, CET)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--list",
        action="store_true", 
        help="List all supported timezones"
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        checker = TimeChecker()
        
        if args.list:
            print("Supported timezones:")
            for tz in checker.list_timezones():
                print(f"  {tz}")
            return
        
        if not args.timezone:
            parser.error("Please specify a timezone with -p or use --list to see options")
        
        time_str = checker.get_time(args.timezone)
        print(f"{args.timezone}: {time_str}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()