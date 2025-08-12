"""Configuration constants for Amazon order history processing."""

# Input CSV column mappings
INPUT_COLUMNS = {
    'WEBSITE': 'Website',
    'ORDER_ID': 'Order ID',
    'ORDER_DATE': 'Order Date',
    'SHIP_DATE': 'Ship Date',
    'CURRENCY': 'Currency',
    'UNIT_PRICE': 'Unit Price',
    'TOTAL_OWED': 'Total Owed',
    'SHIPMENT_SUBTOTAL': 'Shipment Item Subtotal',
    'SHIPMENT_SUBTOTAL_TAX': 'Shipment Item Subtotal Tax',
    'PRODUCT_NAME': 'Product Name',
    'QUANTITY': 'Quantity',
    'ORDER_STATUS': 'Order Status'
}

# Output CSV column names
OUTPUT_COLUMNS = [
    'Ship Date',
    'Order ID', 
    'Transaction Amount',
    'Order Total',
    'Product Names',
    'Order URL',
]

# Amazon URL template
AMAZON_ORDER_URL_TEMPLATE = 'https://amazon.com/gp/your-account/order-details?orderID={}'

# Data type specifications for pandas - use object for mixed/problematic columns
PANDAS_DTYPES = {
    'Website': 'string',
    'Order ID': 'string', 
    'Currency': 'string',
    'Unit Price': 'object',  # Handle 'Not Available' values
    'Total Owed': 'object',  # Handle 'Not Available' values
    'Shipment Item Subtotal': 'object',  # Handle 'Not Available' values
    'Shipment Item Subtotal Tax': 'object',  # Handle 'Not Available' values
    'Product Name': 'string',
    'Quantity': 'object',  # Handle 'Not Available' values
    'Order Status': 'string'
}

# Date parsing parameters
DATE_PARSER_KWARGS = {
    'format': 'ISO8601',
    'utc': True
}

# Returns CSV column mappings
RETURNS_COLUMNS = {
    'ORDER_ID': 'OrderID',
    'REFUND_DATE': 'RefundCompletionDate',
    'AMOUNT_REFUNDED': 'AmountRefunded'
}

# Returns data types
RETURNS_DTYPES = {
    'OrderID': 'string',
    'RefundCompletionDate': 'object',
    'AmountRefunded': 'object'
}
