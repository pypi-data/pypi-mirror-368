# Phase 6: Returns Payment Data Integration

## Overview
Integrate Amazon returns payment data to include refund transactions alongside regular order transactions in the consolidated output CSV.

## Requirements
- Using `Retail.OrdersReturned.Payments.1` CSV as input source
- Each return payment data row becomes a corresponding transaction row
- Combine returns data with existing order transaction data
- Maintain backwards compatibility with existing functionality

## Data Mapping

### Returns CSV → Output CSV Column Mapping
| Returns Column | Output Column | Notes |
|---|---|---|
| OrderID | Order ID | Direct mapping |
| Refund Completion Date | Ship Date | Use refund date as transaction date |
| AmountRefunded | Transaction Amount | **Convert to negative values** (refunds) |
| (inferred) | Order Total | **Calculate from order data** by summing Total Owed for Order ID |
| (inferred) | Product Names | **Infer from matching order data** |
| OrderID | Order URL | Generate from Order ID as usual |

## Implementation Plan

### 1. Configuration Updates (`src/config.py`)
```python
# Returns CSV column mappings
RETURNS_COLUMNS = {
    'ORDER_ID': 'OrderID',
    'REFUND_DATE': 'Refund Completion Date', 
    'AMOUNT_REFUNDED': 'AmountRefunded'
}

# Returns data types
RETURNS_DTYPES = {
    'OrderID': 'string',
    'Refund Completion Date': 'object',
    'AmountRefunded': 'object'
}
```

### 2. Data Processor Enhancements (`src/data_processor.py`)

#### New Methods:
- `load_returns_csv(file_path)` - Load returns payment CSV
- `clean_returns_data()` - Parse dates, convert amounts to numeric
- `process_returns()` - Main returns processing pipeline
- `calculate_order_totals_for_returns()` - Calculate Order Total from order data
- `infer_product_names()` - Match returns to order data for product names
- `combine_transactions()` - Merge order and returns data

#### Product Name Inference Logic:
1. For each return payment row:
   - Match by `Order ID` from returns to order data
   - Find order items where `Total Owed` ≈ `AmountRefunded` (within tolerance)
   - Use matching order item product names (truncated to 60 chars each)
   - If no match found, use `"Return - Order {OrderID}"`

### 3. Main Application Updates (`main.py`)

#### CLI Enhancements:
```python
parser.add_argument(
    '--returns',
    type=Path,
    help='Optional returns payment CSV file to include refund transactions'
)
```

#### Processing Flow:
1. Process order history as usual → order transactions
2. If `--returns` provided:
   - Process returns data → returns transactions  
   - Combine both datasets
   - Sort combined data by Ship Date

### 4. Data Processing Logic

#### Returns Processing Pipeline:
```python
def process_returns(self, returns_file: Path) -> pd.DataFrame:
    # Load and clean returns data
    returns_df = self.load_returns_csv(returns_file)
    cleaned_returns = self.clean_returns_data(returns_df)
    
    # Convert amounts to negative (refunds)
    cleaned_returns['Transaction Amount'] = -cleaned_returns['AmountRefunded'].abs()
    
    # Calculate Order Total from order data (same logic as regular transactions)
    cleaned_returns = self.calculate_order_totals_for_returns(cleaned_returns)
    
    # Infer product names from order data
    returns_with_products = self.infer_product_names(cleaned_returns)
    
    # Generate URLs and format
    final_returns = self.finalize_returns_data(returns_with_products)
    
    return final_returns
```

#### Product Name Matching Strategy:
```python
def infer_product_names(self, returns_df: pd.DataFrame) -> pd.DataFrame:
    for idx, return_row in returns_df.iterrows():
        order_id = return_row['Order ID']
        refund_amount = abs(return_row['Transaction Amount'])
        
        # Find matching order items
        matching_items = self.df[
            (self.df['Order ID'] == order_id) & 
            (abs(self.df['Total Owed'] - refund_amount) < 0.01)  # Tolerance for float comparison
        ]
        
        if not matching_items.empty:
            # Use product names from matching items
            product_names = '; '.join([name[:60] for name in matching_items['Product Name']])
            returns_df.at[idx, 'Product Names'] = product_names
        else:
            # Fallback if no match
            returns_df.at[idx, 'Product Names'] = f"Return - Order {order_id}"
    
    return returns_df

def calculate_order_totals_for_returns(self, returns_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Order Total for returns by summing Total Owed from order data."""
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
```

### 5. Output Format

#### Combined Transaction Types:
- **Order Transactions**: Positive `Transaction Amount`, calculated `Order Total`, aggregated product names
- **Return Transactions**: Negative `Transaction Amount`, calculated `Order Total` (same as original order), inferred product names

#### Example Output:
```csv
Ship Date,Order ID,Transaction Amount,Order Total,Product Names,Order URL
2025-08-05,111-1111111-1111111,61.58,61.58,Beef Chuck Roast; Organic Red Onion,https://amazon.com/gp/your-account/order-details?orderID=111-1111111-1111111
2025-08-10,111-1111111-1111111,-13.99,61.58,Beef Chuck Roast,https://amazon.com/gp/your-account/order-details?orderID=111-1111111-1111111
```

## Benefits
- **Complete Transaction History**: Shows both purchases and refunds
- **Backwards Compatible**: Existing order-only processing still works
- **Optional Feature**: Returns integration only when `--returns` provided  
- **Accurate Refund Tracking**: Negative amounts clearly indicate refunds
- **Product Context**: Inferred product names provide transaction context

## Usage Examples
```bash
# Order transactions only (existing functionality)
uv run python main.py orders.csv transactions.csv

# Orders + returns combined
uv run python main.py orders.csv transactions.csv --returns returns.csv
```

## Testing Strategy
- Unit tests for returns data loading and processing
- Integration tests combining order and returns data  
- Product name inference accuracy tests
- Edge cases: partial refunds, multiple returns per order
- Performance tests with large returns datasets
