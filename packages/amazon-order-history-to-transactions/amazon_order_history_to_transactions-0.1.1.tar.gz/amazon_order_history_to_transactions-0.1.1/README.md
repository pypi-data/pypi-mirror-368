Convert exported Amazon order and return history into something close to credit card transactions.

## Why
To better track my finances, I wanted to identify which Amazon orders / products each of my credit card transactions corresponded to so I could categorize the transactions and figure out where my spending is going.

Amazon has a [transactions page](https://www.amazon.com/cpe/yourpayments/transactions), but it does not allow navigating directly to specific time periods, instead requiring you to hit the 'Next' page button as many times as needed to go back in time. Worse, you cannot link to transactions pages as they do not modify the URL, so if you lose your place (or Amazon gives the dreaded "you have no transactions" error) and you have to start all over again.

There are other tools like the Chrome extension [Amazon Order History Reporter (Azad)](https://github.com/philipmulcahy/azad) which can export your order history by scraping Amazon pages, but I found them all to output lots of missing data to the point of being nearly unusable. To be fair, Amazon order history and transacions pages are an ever moving target. 

Working directly with official Amazon exported data like this script does is much easier and in principle fully complete. Plus it comes in a convenient CSV format that you may find useful for your own quick lookups and analysis.

I personally use this tool to track my spending with [Lunch Money](https://lunchmoney.app/), categorizing Amazon transactions based on what I bought. In the near future I plan to create a tool that makes use of the exported data from this tool to directly update corresponding transactions in Lunch Money since it has an open API.

## Quick Start

1. Export your Amazon order history (may take an hour or longer): https://www.amazon.com/hz/privacy-central/data-requests/preview.html
1. While you wait, install this script using `pipx install .`, `uv tool install .`, or a similar Python app manager.
1. Once export is complete, download the resulting ZIP file and extract the `Retail.OrderHistory.1.csv` and `Retail.OrdersReturned.Payments.1.csv` files, ideally to the same location as the script to avoid specifiying paths.
1. [Run the script](#usage), pointing it to your files and desired output filename.
1. Done! The [output transactions CSV](#output) file will not perfectly match you credit card transactions since Amazon sometimes charges one transaction per shipment and other times charges the whole order as one transaction. Hence the reason both transaction amounts (cost of a shipment or refund) and overall order totals are given.

## Usage

Order transactions only:

```
amazon-order-history-to-transactions Retail.OrderHistory.1.csv transactions.csv
```

Orders + returns combined:

```
amazon-order-history-to-transactions Retail.OrderHistory.1.csv transactions.csv --returns Retail.OrdersReturned.Payments.1.csv
```

## Output

The script produces a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| **Ship Date** | Date when the order shipped (YYYY-MM-DD format). For returns, this is the refund completion date. |
| **Order ID** | Amazon order identifier that links to the original order |
| **Transaction Amount** | Total amount charged/refunded for a single shipment/return. Positive values are charges, negative values are refunds. |
| **Order Total** | Total cost of the entire order (sum of all items for that Order ID). Useful when the whole order was charged to your card as one transaction, rather than one transaction per shipment. |
| **Product Names** | Semicolon-separated list of product names. Each product name is truncated to 60 characters max for readability. |
| **Order URL** | Direct link to Amazon order details page |

### Transaction Grouping

The script groups individual order items into transactions based on:
- **Order ID** + **Shipment Item Subtotal** (to handle partial charges/refunds)
- Items with the same Order ID and subtotal amount are combined into a single transaction row
- Product names from grouped items are concatenated with semicolons

### Example Output

```csv
Ship Date,Order ID,Transaction Amount,Order Total,Product Names,Order URL
2025-08-10,111-1111111-1111111,-13.99,61.58,Watermelon,https://amazon.com/gp/your-account/order-details?orderID=111-1111111-1111111
2025-08-05,111-1111111-1111111,61.58,61.58,Watermelon; Organic Red Onion,https://amazon.com/gp/your-account/order-details?orderID=111-1111111-1111111
2025-08-04,222-2222222-2222222,25.99,25.99,Wireless Headphones,https://amazon.com/gp/your-account/order-details?orderID=222-2222222-2222222
```

**Note:** Returns appear as separate rows with negative Transaction Amount values, but maintain the same Order Total as the original order for context.

## Develop

To make development easier, I prefer to install via pipx with the `--editable`
flag so that all updates to the code automatically reflect in the installed
tool:

```
pipx install --editable .
```

### Publishing to PyPI

The package is configured for PyPI publication. To publish a new version:

1. **Update version** in `pyproject.toml`
2. **Build the package:**
   ```bash
   uv run python -m build
   ```
3. **Validate the build:**
   ```bash
   uv run python -m twine check dist/*
   ```
4. **Upload to PyPI:**
   ```bash
   # Test upload (recommended first)
   uv run python -m twine upload --repository testpypi dist/*
   
   # Production upload
   uv run python -m twine upload dist/*
   ```

**Prerequisites:**
- PyPI account with API token configured
- Install dev dependencies: `uv sync --group dev`
