# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python script that converts Amazon order history CSV data into a credit card transaction format. The tool groups individual order items by order ID and transaction amount to create consolidated transaction records.

## Development Commands

**Python Environment:**
- Run the main script: `python main.py`
- The project uses Python 3.9+ (specified in pyproject.toml)

**Package Management:**
- Dependencies are managed through pyproject.toml via `uv`.
- Install dependencies: `uv install .`

## Data Processing Architecture

**Input:** Amazon order history CSV where each row represents an individual ordered item
**Output:** Transaction-based CSV where each row represents a complete order/transaction

**Key Transformation Logic:**
1. Group order items by Order ID and transaction amount
2. Aggregate "Shipment Item Subtotal" values (positive = charge, negative = refund)  
3. Combine product names into semicolon-separated lists
4. Generate Amazon order URLs from Order ID
5. Sort by order date (most recent first)

**Output CSV Columns:**
- Order Date
- Order ID
- Transaction Amount (aggregated subtotals)
- Product Names (semicolon-separated)
- Order URL (amazon.com/gp/your-account/order-details?orderID={order_id})

## File Structure

- `main.py` - Main script entry point (currently minimal)
- `Retail.OrderHistory.1.csv` - Sample Amazon order history data
- `design/init-requirements.md` - Detailed project requirements
- `pyproject.toml` - Python project configuration
