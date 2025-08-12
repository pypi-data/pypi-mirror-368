"""Core data processing module using pandas for Amazon order history conversion."""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional

from .config import (
    INPUT_COLUMNS, 
    OUTPUT_COLUMNS, 
    AMAZON_ORDER_URL_TEMPLATE,
    PANDAS_DTYPES,
    DATE_PARSER_KWARGS,
    RETURNS_COLUMNS,
    RETURNS_DTYPES
)


class OrderHistoryProcessor:
    """Processes Amazon order history CSV data into consolidated transactions."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.df: Optional[pd.DataFrame] = None
        self.processed_df: Optional[pd.DataFrame] = None
    
    def load_csv(self, file_path: str | Path) -> pd.DataFrame:
        """Load Amazon order history CSV with proper encoding and data types."""
        try:
            self.logger.info(f"Loading CSV from {file_path}")
            
            # Load CSV with pandas, handling encoding automatically
            self.df = pd.read_csv(
                file_path,
                dtype=PANDAS_DTYPES,
                encoding='utf-8-sig',  # Handle BOM if present
                low_memory=False
            )
            
            self.logger.info(f"Loaded {len(self.df)} rows from CSV")
            return self.df
            
        except Exception as e:
            self.logger.error(f"Failed to load CSV: {e}")
            raise
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and prepare data for processing."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        self.logger.info("Cleaning data...")
        
        # Parse ship dates, handling 'Not Available' values
        self.df[INPUT_COLUMNS['SHIP_DATE']] = pd.to_datetime(
            self.df[INPUT_COLUMNS['SHIP_DATE']], 
            errors='coerce',  # Convert invalid dates to NaT
            **DATE_PARSER_KWARGS
        )
        
        # Convert 'Not Available' and similar strings to NaN for numeric columns
        numeric_columns = [INPUT_COLUMNS['TOTAL_OWED'], INPUT_COLUMNS['SHIPMENT_SUBTOTAL'], INPUT_COLUMNS['SHIPMENT_SUBTOTAL_TAX'], 'Unit Price', 'Quantity']
        for col in numeric_columns:
            if col in self.df.columns:
                # Replace non-numeric strings with NaN, then convert to numeric
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Remove any rows with missing critical data
        required_columns = [
            INPUT_COLUMNS['ORDER_ID'],
            INPUT_COLUMNS['SHIP_DATE'],
            INPUT_COLUMNS['TOTAL_OWED'],
            INPUT_COLUMNS['SHIPMENT_SUBTOTAL'],
            INPUT_COLUMNS['PRODUCT_NAME']
        ]
        
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=required_columns)
        dropped_count = initial_count - len(self.df)
        
        if dropped_count > 0:
            self.logger.warning(f"Dropped {dropped_count} rows with missing critical data")
        
        return self.df
    
    def group_transactions(self) -> pd.DataFrame:
        """Group items by Order ID and Shipment Item Subtotal."""
        if self.df is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        self.logger.info("Grouping transactions...")
        
        # Group by Order ID and Shipment Item Subtotal to handle partial refunds/charges
        grouped = self.df.groupby([
            INPUT_COLUMNS['ORDER_ID'],
            INPUT_COLUMNS['SHIPMENT_SUBTOTAL']
        ]).agg({
            INPUT_COLUMNS['SHIP_DATE']: 'first',  # Take first occurrence ship date
            INPUT_COLUMNS['PRODUCT_NAME']: lambda x: '; '.join(x.astype(str)),  # Concatenate product names
            INPUT_COLUMNS['TOTAL_OWED']: 'sum'  # Sum all Total Owed amounts in the group
        }).reset_index()
        
        # Rename the aggregated Total Owed to Transaction Amount
        grouped = grouped.rename(columns={
            INPUT_COLUMNS['TOTAL_OWED']: 'Transaction Amount'
        })
        
        self.logger.info(f"Grouped into {len(grouped)} transactions")
        return grouped
    
    def generate_order_urls(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate Amazon order URLs using vectorized operations."""
        df = df.copy()
        df['Order URL'] = AMAZON_ORDER_URL_TEMPLATE.format(
            df[INPUT_COLUMNS['ORDER_ID']].iloc[0] if len(df) > 0 else ''
        )
        
        # Use vectorized string operation for all rows
        df['Order URL'] = df[INPUT_COLUMNS['ORDER_ID']].apply(
            lambda x: AMAZON_ORDER_URL_TEMPLATE.format(x)
        )
        
        return df
    
    def sort_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort transactions by date (most recent first)."""
        return df.sort_values(
            INPUT_COLUMNS['SHIP_DATE'], 
            ascending=False
        ).reset_index(drop=True)
    
    def process(self, input_file: str | Path) -> pd.DataFrame:
        """Complete processing pipeline."""
        self.logger.info("Starting order history processing...")
        
        # Load and clean data
        self.load_csv(input_file)
        self.clean_data()
        
        # Process transactions
        grouped_df = self.group_transactions()
        
        # Generate URLs
        url_df = self.generate_order_urls(grouped_df)
        
        # Calculate Order Total for each Order ID (sum of all Total Owed for that order)
        order_totals = self.df.groupby(INPUT_COLUMNS['ORDER_ID'])[INPUT_COLUMNS['TOTAL_OWED']].sum().reset_index()
        order_totals = order_totals.rename(columns={INPUT_COLUMNS['TOTAL_OWED']: 'Order Total'})
        
        # Merge Order Total back into the grouped data
        url_df = url_df.merge(order_totals, left_on=INPUT_COLUMNS['ORDER_ID'], right_on=INPUT_COLUMNS['ORDER_ID'], how='left')
        
        # Sort by date
        final_df = self.sort_by_date(url_df)
        
        # Rename columns for output
        output_df = final_df.rename(columns={
            INPUT_COLUMNS['SHIP_DATE']: 'Ship Date',
            INPUT_COLUMNS['ORDER_ID']: 'Order ID',
            INPUT_COLUMNS['PRODUCT_NAME']: 'Product Names'
            # 'Transaction Amount' already has the correct name
        })
        
        # Format Ship Date to YYYY-MM-DD format (drop time)
        output_df['Ship Date'] = output_df['Ship Date'].dt.strftime('%Y-%m-%d')
        
        # Format Transaction Amount to two decimal places
        output_df['Transaction Amount'] = output_df['Transaction Amount'].round(2).map('{:.2f}'.format)
        
        # Format Order Total to two decimal places
        output_df['Order Total'] = output_df['Order Total'].round(2).map('{:.2f}'.format)
        
        # Select only output columns
        self.processed_df = output_df[OUTPUT_COLUMNS]
        
        self.logger.info(f"Processing complete. Generated {len(self.processed_df)} transactions")
        return self.processed_df
    
    def save_csv(self, output_file: str | Path) -> None:
        """Save processed data to CSV."""
        if self.processed_df is None:
            raise ValueError("No processed data available. Call process() first.")
        
        self.logger.info(f"Saving results to {output_file}")
        
        self.processed_df.to_csv(
            output_file,
            index=False,
            encoding='utf-8'
        )
        
        self.logger.info("Save complete")
    
    # Returns Processing Methods
    
    def load_returns_csv(self, file_path: str | Path) -> pd.DataFrame:
        """Load returns payment CSV with proper encoding and data types."""
        try:
            self.logger.info(f"Loading returns CSV from {file_path}")
            
            returns_df = pd.read_csv(
                file_path,
                dtype=RETURNS_DTYPES,
                encoding='utf-8-sig',
                low_memory=False
            )
            
            self.logger.info(f"Loaded {len(returns_df)} returns from CSV")
            return returns_df
            
        except Exception as e:
            self.logger.error(f"Failed to load returns CSV: {e}")
            raise
    
    def clean_returns_data(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare returns data for processing."""
        self.logger.info("Cleaning returns data...")
        
        # Parse refund completion dates
        returns_df[RETURNS_COLUMNS['REFUND_DATE']] = pd.to_datetime(
            returns_df[RETURNS_COLUMNS['REFUND_DATE']],
            errors='coerce',
            **DATE_PARSER_KWARGS
        )
        
        # Convert amount refunded to numeric
        returns_df[RETURNS_COLUMNS['AMOUNT_REFUNDED']] = pd.to_numeric(
            returns_df[RETURNS_COLUMNS['AMOUNT_REFUNDED']], 
            errors='coerce'
        )
        
        # Remove rows with missing critical data
        required_columns = [
            RETURNS_COLUMNS['ORDER_ID'],
            RETURNS_COLUMNS['REFUND_DATE'],
            RETURNS_COLUMNS['AMOUNT_REFUNDED']
        ]
        
        initial_count = len(returns_df)
        returns_df = returns_df.dropna(subset=required_columns)
        dropped_count = initial_count - len(returns_df)
        
        if dropped_count > 0:
            self.logger.warning(f"Dropped {dropped_count} returns with missing critical data")
        
        return returns_df
    
    def calculate_order_totals_for_returns(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Order Total for returns by summing Total Owed from order data."""
        if self.df is None:
            raise ValueError("No order data loaded. Call load_csv() first.")
        
        # Use the existing order totals calculation (same as regular transactions)
        order_totals = self.df.groupby(INPUT_COLUMNS['ORDER_ID'])[INPUT_COLUMNS['TOTAL_OWED']].sum().reset_index()
        order_totals = order_totals.rename(columns={INPUT_COLUMNS['TOTAL_OWED']: 'Order Total'})
        
        # Merge Order Total into returns data
        returns_with_totals = returns_df.merge(
            order_totals,
            left_on='Order ID',
            right_on=INPUT_COLUMNS['ORDER_ID'],
            how='left'
        )
        
        return returns_with_totals
    
    def infer_product_names_for_returns(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """Infer product names for returns by matching to order data."""
        if self.df is None:
            raise ValueError("No order data loaded. Call load_csv() first.")
        
        self.logger.info("Inferring product names for returns...")
        
        for idx, return_row in returns_df.iterrows():
            order_id = return_row['Order ID']
            refund_amount = abs(return_row['Transaction Amount'])
            
            # Find matching order items by Order ID and amount
            matching_items = self.df[
                (self.df[INPUT_COLUMNS['ORDER_ID']] == order_id) &
                (abs(self.df[INPUT_COLUMNS['TOTAL_OWED']] - refund_amount) < 0.01)
            ]
            
            if not matching_items.empty:
                # Use product names from matching items (truncate each to 60 chars)
                product_names = '; '.join([str(name)[:60] for name in matching_items[INPUT_COLUMNS['PRODUCT_NAME']]])
                returns_df.at[idx, 'Product Names'] = product_names
            else:
                # Fallback if no match
                returns_df.at[idx, 'Product Names'] = f"Return - Order {order_id}"
        
        return returns_df
    
    def process_returns(self, returns_file: str | Path) -> pd.DataFrame:
        """Complete returns processing pipeline."""
        if self.df is None:
            raise ValueError("No order data loaded. Call process() first to load order data.")
        
        self.logger.info("Starting returns processing...")
        
        # Load and clean returns data
        returns_df = self.load_returns_csv(returns_file)
        cleaned_returns = self.clean_returns_data(returns_df)
        
        # Convert amounts to negative (refunds) - do this before renaming
        cleaned_returns['Transaction Amount'] = -cleaned_returns[RETURNS_COLUMNS['AMOUNT_REFUNDED']].abs()
        
        # Rename columns for consistency
        cleaned_returns = cleaned_returns.rename(columns={
            RETURNS_COLUMNS['ORDER_ID']: 'Order ID',
            RETURNS_COLUMNS['REFUND_DATE']: 'Ship Date'
        })
        
        # Calculate Order Total from order data
        returns_with_totals = self.calculate_order_totals_for_returns(cleaned_returns)
        
        # Infer product names from order data
        returns_with_products = self.infer_product_names_for_returns(returns_with_totals)
        
        # Generate order URLs
        returns_with_urls = self.generate_order_urls(returns_with_products)
        
        # Format dates and amounts
        returns_with_urls['Ship Date'] = returns_with_urls['Ship Date'].dt.strftime('%Y-%m-%d')
        returns_with_urls['Transaction Amount'] = returns_with_urls['Transaction Amount'].round(2).map('{:.2f}'.format)
        returns_with_urls['Order Total'] = returns_with_urls['Order Total'].round(2).map('{:.2f}'.format)
        
        # Select only output columns
        final_returns = returns_with_urls[OUTPUT_COLUMNS]
        
        self.logger.info(f"Returns processing complete. Generated {len(final_returns)} return transactions")
        return final_returns
    
    def combine_transactions(self, returns_df: pd.DataFrame) -> pd.DataFrame:
        """Combine order transactions and returns transactions."""
        if self.processed_df is None:
            raise ValueError("No processed order data available. Call process() first.")
        
        self.logger.info("Combining order and returns transactions...")
        
        # Combine both DataFrames
        combined_df = pd.concat([self.processed_df, returns_df], ignore_index=True)
        
        # Sort by Ship Date (most recent first)
        combined_df['Ship Date'] = pd.to_datetime(combined_df['Ship Date'])
        combined_df = combined_df.sort_values('Ship Date', ascending=False).reset_index(drop=True)
        
        # Convert Ship Date back to string format
        combined_df['Ship Date'] = combined_df['Ship Date'].dt.strftime('%Y-%m-%d')
        
        self.logger.info(f"Combined {len(self.processed_df)} orders with {len(returns_df)} returns = {len(combined_df)} total transactions")
        
        return combined_df