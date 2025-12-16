#!/usr/bin/env python3
"""
Tests for the CSV transformation tool
"""

import csv
import os
import sys


def test_transformation():
    """Test that the transformation produces valid output"""
    
    # Check files exist
    assert os.path.exists('raw_products.csv'), "Raw CSV file not found"
    assert os.path.exists('cleaned_products.csv'), "Cleaned CSV file not found"
    
    # Read cleaned CSV
    with open('cleaned_products.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = list(reader)
    
    # Basic validation
    assert len(products) > 0, "No products found in cleaned CSV"
    
    # Check all required columns exist
    required_columns = [
        'Product Type',
        'Coating',
        'Thickness (mm)',
        'Size (mm)',
        'Item Number',
        'Price One-sided (EUR)',
        'Price Two-sided (EUR)',
        'Pallet Size (sheets)',
        'Notes'
    ]
    
    for col in required_columns:
        assert col in products[0], f"Missing required column: {col}"
    
    # Validate data quality
    for i, product in enumerate(products):
        # Every product must have a type
        assert product['Product Type'], f"Product {i+1} missing Product Type"
        
        # Every product must have an item number (or GENERIC)
        assert product['Item Number'], f"Product {i+1} missing Item Number"
        
        # Every product must have pallet size
        assert product['Pallet Size (sheets)'], f"Product {i+1} missing Pallet Size"
        
        # If thickness exists, it should be numeric
        if product['Thickness (mm)']:
            try:
                int(product['Thickness (mm)'])
            except ValueError:
                assert False, f"Product {i+1} has invalid thickness: {product['Thickness (mm)']}"
        
        # If price exists, it should be numeric
        for price_col in ['Price One-sided (EUR)', 'Price Two-sided (EUR)']:
            if product[price_col]:
                try:
                    float(product[price_col])
                except ValueError:
                    assert False, f"Product {i+1} has invalid {price_col}: {product[price_col]}"
    
    print(f"✓ All tests passed!")
    print(f"  - {len(products)} products validated")
    print(f"  - All required columns present")
    print(f"  - Data quality checks passed")
    return True


if __name__ == '__main__':
    try:
        test_transformation()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)
