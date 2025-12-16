# CSV Data Transformation Tool

This repository contains a tool to transform unstructured product CSV data into a well-structured format suitable for ERP system import.

## Overview

The transformation tool processes raw, unorganized product data and outputs a clean CSV file with standardized columns and consistent formatting.

## Files

- `raw_products.csv` - Sample unstructured input data with product information
- `transform_csv.py` - Python script that performs the transformation
- `cleaned_products.csv` - Output file with structured product data

## Input Data Format

The raw CSV contains unstructured product information with varying formats:
- Product types (HPL Compact, Melamine, MDF, etc.)
- Coating specifications
- Dimensions and thicknesses
- Item numbers
- Pricing (one-sided and two-sided)
- Pallet sizes
- Special notes and requirements

## Output Format

The cleaned CSV has the following standardized columns:

| Column | Description |
|--------|-------------|
| Product Type | Type of product (HPL Compact, Melamine, MDF, etc.) |
| Coating | Coating type or finish |
| Thickness (mm) | Thickness in millimeters |
| Size (mm) | Dimensions in format WIDTHxHEIGHT |
| Item Number | Product item/SKU number, or "GENERIC" for non-coded items |
| Price One-sided (EUR) | Price for one-sided coating in Euros |
| Price Two-sided (EUR) | Price for two-sided coating in Euros |
| Pallet Size (sheets) | Number of sheets per pallet |
| Notes | Additional information, special requirements, or comments |

## Usage

Run the transformation script:

```bash
python3 transform_csv.py
```

The script will:
1. Read `raw_products.csv`
2. Parse and structure the product data
3. Generate `cleaned_products.csv` with standardized format

## Features

- **Flexible parsing** - Handles various input formats and structures
- **Data extraction** - Automatically extracts product attributes from unstructured text
- **Generic product handling** - Items without item numbers are marked as "GENERIC" and grouped by description
- **Notes preservation** - Maintains special requirements, availability notes, and additional costs
- **Price handling** - Correctly parses both one-sided and two-sided pricing
- **Validation** - Ensures product entries have minimum required information

## Requirements

- Python 3.6 or higher
- No external dependencies (uses standard library only)

## Example Transformation

**Input (raw format):**
```
Melamine - decorative woodgrain
Thickness 8mm
Dimensions 2800x1300
Item MEL-8-WG
€31.20 one-sided
€39.75 two-sided
60 sheets/pallet
Note: Premium woodgrain pattern
```

**Output (structured CSV row):**
```csv
Melamine,Woodgrain decorative,8,2800x1300,MEL-8-WG,31.20,39.75,60,Premium woodgrain pattern
```

## Notes

- The transformation script is designed to be flexible and handle various input formats
- Products without item numbers are assigned "GENERIC" and include a note in the output
- All pricing is preserved in Euros (EUR)
- Special notes such as lead times, availability, and additional costs are retained in the Notes column