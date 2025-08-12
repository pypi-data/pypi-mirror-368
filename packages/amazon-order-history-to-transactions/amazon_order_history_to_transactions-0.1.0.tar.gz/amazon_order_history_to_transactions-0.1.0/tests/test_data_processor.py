"""Tests for the OrderHistoryProcessor class."""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from io import StringIO

from src.data_processor import OrderHistoryProcessor
from src.config import INPUT_COLUMNS, OUTPUT_COLUMNS


@pytest.fixture
def sample_csv_data():
    """Sample Amazon order history CSV data for testing."""
    return """Website,Order ID,Order Date,Purchase Order Number,Currency,Unit Price,Unit Price Tax,Shipping Charge,Total Discounts,Total Owed,Shipment Item Subtotal,Shipment Item Subtotal Tax,ASIN,Product Condition,Quantity,Payment Instrument Type,Order Status,Shipment Status,Ship Date,Shipping Option,Shipping Address,Billing Address,Carrier Name & Tracking Number,Product Name,Gift Message,Gift Sender Name,Gift Recipient Contact Details,Item Serial Number
Amazon.com,111-1111111-1111111,2025-08-04T20:39:52Z,Not Applicable,USD,13.99,0,0,0,13.99,61.54,0.04,B01LXS7YAM,New,1,Visa - 111,Closed,Shipped,2025-08-05T03:08:19.087Z,scheduled-houdini,Test Address,Test Address,CARRIER123,Beef Chuck Roast,Not Available,Not Available,Not Available,Not Available
Amazon.com,111-1111111-1111111,2025-08-04T20:39:52Z,Not Applicable,USD,0.99,0,0,0,0.99,61.54,0.04,B000P6J1FE,New,1,Visa - 111,Closed,Shipped,2025-08-05T03:08:19.087Z,scheduled-houdini,Test Address,Test Address,CARRIER123,Organic Red Onion,Not Available,Not Available,Not Available,Not Available
Amazon.com,222-2222222-2222222,2025-08-03T15:30:00Z,Not Applicable,USD,25.99,0,0,0,25.99,25.99,0,B123456789,New,1,Visa - 111,Closed,Shipped,2025-08-04T10:00:00Z,standard,Test Address,Test Address,CARRIER456,Wireless Headphones,Not Available,Not Available,Not Available,Not Available"""


@pytest.fixture
def processor():
    """Create a new OrderHistoryProcessor instance for each test."""
    return OrderHistoryProcessor()


@pytest.fixture  
def sample_csv_file(sample_csv_data):
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv_data)
        f.flush()
        yield Path(f.name)
    Path(f.name).unlink()  # Clean up


class TestOrderHistoryProcessor:
    """Test cases for OrderHistoryProcessor."""
    
    def test_load_csv(self, processor, sample_csv_file):
        """Test CSV loading functionality."""
        df = processor.load_csv(sample_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'Order ID' in df.columns
        assert 'Product Name' in df.columns
        assert 'Shipment Item Subtotal' in df.columns
    
    def test_load_csv_nonexistent_file(self, processor):
        """Test loading a non-existent file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            processor.load_csv('nonexistent.csv')
    
    def test_clean_data(self, processor, sample_csv_file):
        """Test data cleaning functionality."""
        processor.load_csv(sample_csv_file)
        cleaned_df = processor.clean_data()
        
        # Check that ship dates were parsed
        assert pd.api.types.is_datetime64_any_dtype(cleaned_df['Ship Date'])
        
        # Check that no critical data is missing
        required_columns = [
            INPUT_COLUMNS['ORDER_ID'],
            INPUT_COLUMNS['SHIP_DATE'], 
            INPUT_COLUMNS['SHIPMENT_SUBTOTAL'],
            INPUT_COLUMNS['PRODUCT_NAME']
        ]
        
        for col in required_columns:
            assert not cleaned_df[col].isna().any()
    
    def test_group_transactions(self, processor, sample_csv_file):
        """Test transaction grouping functionality."""
        processor.load_csv(sample_csv_file)
        processor.clean_data()
        grouped_df = processor.group_transactions()
        
        # Should have 2 groups (one order with same subtotal, one separate order)
        assert len(grouped_df) == 2
        
        # Check that product names are concatenated
        first_group = grouped_df.iloc[0]
        if first_group['Order ID'] == '111-1111111-1111111':
            assert '; ' in first_group['Product Name']
            assert 'Beef Chuck Roast' in first_group['Product Name']
            assert 'Organic Red Onion' in first_group['Product Name']
    
    def test_generate_order_urls(self, processor):
        """Test order URL generation."""
        # Create simple test DataFrame
        test_df = pd.DataFrame({
            INPUT_COLUMNS['ORDER_ID']: ['111-1111111-1111111', '222-2222222-2222222'],
            INPUT_COLUMNS['SHIP_DATE']: pd.to_datetime(['2025-08-04', '2025-08-03']),
            INPUT_COLUMNS['SHIPMENT_SUBTOTAL']: [61.54, 25.99],
            INPUT_COLUMNS['PRODUCT_NAME']: ['Product 1', 'Product 2']
        })
        
        result_df = processor.generate_order_urls(test_df)
        
        assert 'Order URL' in result_df.columns
        assert 'amazon.com/gp/your-account/order-details?orderID=111-1111111-1111111' in result_df['Order URL'].iloc[0]
        assert 'amazon.com/gp/your-account/order-details?orderID=222-2222222-2222222' in result_df['Order URL'].iloc[1]
    
    def test_sort_by_date(self, processor):
        """Test date sorting functionality."""
        # Create test DataFrame with unsorted dates
        test_df = pd.DataFrame({
            INPUT_COLUMNS['SHIP_DATE']: pd.to_datetime(['2025-08-03', '2025-08-05', '2025-08-04']),
            INPUT_COLUMNS['ORDER_ID']: ['333', '111', '222'],
            INPUT_COLUMNS['SHIPMENT_SUBTOTAL']: [10.0, 20.0, 30.0],
            INPUT_COLUMNS['PRODUCT_NAME']: ['C', 'A', 'B']
        })
        
        sorted_df = processor.sort_by_date(test_df)
        
        # Should be sorted with most recent first
        expected_order = ['111', '222', '333']  # 08-05, 08-04, 08-03
        actual_order = sorted_df[INPUT_COLUMNS['ORDER_ID']].tolist()
        assert actual_order == expected_order
    
    def test_process_end_to_end(self, processor, sample_csv_file):
        """Test complete processing pipeline."""
        result_df = processor.process(sample_csv_file)
        
        # Check output structure
        assert isinstance(result_df, pd.DataFrame)
        assert list(result_df.columns) == OUTPUT_COLUMNS
        
        # Should have 2 transactions (grouped)
        assert len(result_df) == 2
        
        # Check that data is sorted by date (most recent first)  
        dates = pd.to_datetime(result_df['Ship Date'])
        assert dates.iloc[0] >= dates.iloc[1]
        
        # Check that URLs are generated
        assert all(result_df['Order URL'].str.contains('amazon.com'))
        assert all(result_df['Order URL'].str.contains('orderID='))
    
    def test_save_csv(self, processor, sample_csv_file):
        """Test CSV saving functionality."""
        processor.process(sample_csv_file)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            processor.save_csv(output_path)
            
            # Verify file was created and has content
            assert output_path.exists()
            
            # Load and verify structure
            saved_df = pd.read_csv(output_path)
            assert list(saved_df.columns) == OUTPUT_COLUMNS
            assert len(saved_df) == 2
            
        finally:
            output_path.unlink()  # Clean up
    
    def test_save_csv_before_processing_raises_error(self, processor):
        """Test that saving before processing raises appropriate error."""
        with tempfile.NamedTemporaryFile(suffix='.csv') as f:
            with pytest.raises(ValueError, match="No processed data available"):
                processor.save_csv(f.name)
