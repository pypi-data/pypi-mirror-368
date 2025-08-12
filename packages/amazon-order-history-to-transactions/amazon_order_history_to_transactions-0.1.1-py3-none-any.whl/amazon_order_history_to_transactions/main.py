#!/usr/bin/env python3
"""
Amazon Order History Converter

Converts Amazon order history CSV data (individual items per row) into 
consolidated transaction format (one row per order/transaction group).
"""

import argparse
import logging
import sys
from pathlib import Path

from .data_processor import OrderHistoryProcessor


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert Amazon order history CSV to consolidated transaction format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.csv output.csv
  %(prog)s --verbose Retail.OrderHistory.1.csv transactions.csv
        """
    )
    
    parser.add_argument(
        'input_file',
        type=Path,
        help='Input Amazon order history CSV file'
    )
    
    parser.add_argument(
        'output_file', 
        type=Path,
        help='Output consolidated transactions CSV file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    parser.add_argument(
        '-r', '--returns',
        type=Path,
        help='Optional returns payment CSV file to include refund transactions'
    )
    
    return parser.parse_args()


def validate_input_file(file_path: Path) -> None:
    """Validate that input file exists and is readable."""
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Input path is not a file: {file_path}")
    
    if file_path.suffix.lower() != '.csv':
        logging.warning(f"Input file does not have .csv extension: {file_path}")


def validate_output_file(file_path: Path) -> None:
    """Validate output file path and create parent directories if needed."""
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Warn if file will be overwritten
    if file_path.exists():
        logging.warning(f"Output file will be overwritten: {file_path}")


def validate_returns_file(file_path: Path) -> None:
    """Validate that returns file exists and is readable."""
    if not file_path.exists():
        raise FileNotFoundError(f"Returns file not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Returns path is not a file: {file_path}")
    
    if file_path.suffix.lower() != '.csv':
        logging.warning(f"Returns file does not have .csv extension: {file_path}")


def main() -> int:
    """Main application entry point."""
    try:
        # Parse arguments and setup logging
        args = parse_arguments()
        setup_logging(args.verbose)
        
        logger = logging.getLogger(__name__)
        logger.info("Amazon Order History Converter starting...")
        
        # Validate input and output files
        validate_input_file(args.input_file)
        validate_output_file(args.output_file)
        
        # Validate returns file if provided
        if args.returns:
            validate_returns_file(args.returns)
        
        # Process the order data
        processor = OrderHistoryProcessor()
        processed_df = processor.process(args.input_file)
        
        # Process returns data if provided
        if args.returns:
            logger.info(f"Processing returns data from: {args.returns}")
            returns_df = processor.process_returns(args.returns)
            
            # Combine order and returns data
            combined_df = processor.combine_transactions(returns_df)
            
            # Update processed_df to the combined data
            processor.processed_df = combined_df
            processed_df = combined_df
        
        # Save final results
        processor.save_csv(args.output_file)
        
        # Report results
        transaction_type = "combined order and return transactions" if args.returns else "transactions"
        logger.info(f"Successfully processed {len(processed_df)} {transaction_type}")
        logger.info(f"Output saved to: {args.output_file}")
        
        return 0
        
    except KeyboardInterrupt:
        logging.error("Process interrupted by user")
        return 1
        
    except FileNotFoundError as e:
        logging.error(f"File error: {e}")
        return 2
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            logging.exception("Full traceback:")
        return 3


if __name__ == '__main__':
    sys.exit(main())
