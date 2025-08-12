I want to make a Python script that converts exported Amazon order history data (in CSV format where each line is a separate ordered item) into a CSV of credit card transactions similar to the Amazon Transactions page (where all items in a transaction are on a single line).

Transactions are grouped from order history data by order ID then transaction amount.

The output CSV should have the followings columns (in order of left to right):
- order date
- order ID
- transaction amount: this is a grouped version of "Shipment Item Subtotal" column in order history. A positive value is a charge, negative is a refund.
- product names: a semicolon separated list of product names that were grouped together by order ID then transaction amount.
- order URL: amazon.com URL to order, derived from order ID.

The output CSV should be sorted most recent order date first.



