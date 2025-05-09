"""Command-line interface for the Origyn application."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from .workflows import create_oem_workflow
from .config import validate_config
from .utils import setup_logging

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Origyn - Identify Original Equipment Manufacturers for spare parts.")
    
    parser.add_argument(
        "query",
        help="Part query to process (e.g., part number or description)",
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output file to save results (JSON format)",
        type=str,
        default=None,
    )
    
    parser.add_argument(
        "--log-level",
        help="Set the logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
    )
    
    parser.add_argument(
        "--log-file",
        help="Log file to save logs",
        type=str,
        default=None,
    )
    
    parser.add_argument(
        "--json",
        "-j",
        help="Output results in JSON format",
        action="store_true",
        default=False,
    )
    
    parser.add_argument(
        "--pretty",
        "-p",
        help="Pretty-print JSON output (only used with --json)",
        action="store_true",
        default=False,
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the CLI application."""
    args = parse_args()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    setup_logging(level=log_level, log_file=args.log_file)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting OEM Finder CLI with query: {args.query}")
    
    try:
        # Validate configuration
        validate_config()
        
        # Create and run workflow
        workflow = create_oem_workflow()
        result = workflow.run(args.query)
        
        # Convert result to dictionary
        result_dict = result.model_dump()
        
        # Display results based on output format
        if args.json:
            # JSON output
            if args.pretty:
                print(json.dumps(result_dict, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(result_dict, ensure_ascii=False))
        else:
            # Human-readable output
            print("\nOrigyn Results:")
            print(f"Query: {result.original_query}")
            print(f"OEM: {result.oem}")
            print(f"Part Category: {result.part_category}")
            print(f"UNSPSC Code: {result.unspsc_code}")
            print(f"UNSPSC Family: {result.unspsc_family}")
        
        # Save results if output file specified
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_path}")
            
            if not args.json:
                print(f"\nResults saved to {output_path}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error in OEM Finder: {str(e)}", exc_info=True)
        
        if args.json:
            error_result = {
                "error": str(e),
                "original_query": args.query,
                "oem": "NA",
                "part_category": "NA",
                "unspsc_code": "NA",
                "unspsc_family": "NA"
            }
            print(json.dumps(error_result, indent=2 if args.pretty else None, ensure_ascii=False))
        else:
            print(f"Error: {str(e)}")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())