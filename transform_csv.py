#!/usr/bin/env python3
"""
Transform unstructured product CSV data into a well-structured format for ERP import.
"""

import csv
import re
from typing import Dict, List, Optional


def parse_product_entry(lines: List[str]) -> Optional[Dict[str, str]]:
    """
    Parse a product entry from multiple lines of text.
    
    Returns a dictionary with standardized product attributes.
    """
    if not lines:
        return None
    
    product = {
        'Product Type': '',
        'Coating': '',
        'Thickness (mm)': '',
        'Size (mm)': '',
        'Item Number': '',
        'Price One-sided (EUR)': '',
        'Price Two-sided (EUR)': '',
        'Pallet Size (sheets)': '',
        'Notes': ''
    }
    
    notes = []
    text = '\n'.join(lines)
    
    # Extract product type
    type_match = re.search(r'Type:\s*([^\n]+)', text, re.IGNORECASE)
    if type_match:
        product['Product Type'] = type_match.group(1).strip()
    else:
        # Try to find HPL, Melamine, MDF, etc. in the text
        if 'Fire-rated compact laminate' in text or 'HPL Compact FR' in text:
            product['Product Type'] = 'HPL Compact FR'
        elif 'Exterior HPL' in text or 'Exterior compact' in text:
            product['Product Type'] = 'Exterior HPL Compact'
        elif 'HPL Compact' in text or 'HPL with' in text or 'compact laminate' in text.lower():
            product['Product Type'] = 'HPL Compact'
        elif 'Melamine' in text:
            product['Product Type'] = 'Melamine'
        elif 'MDF' in text:
            product['Product Type'] = 'MDF'
        elif 'Foil-wrapped' in text:
            product['Product Type'] = 'Foil-wrapped MDF'
    
    # Extract coating
    coating_match = re.search(r'Coating:\s*([^\n]+)', text, re.IGNORECASE)
    if coating_match:
        product['Coating'] = coating_match.group(1).strip()
    else:
        # Look for coating descriptions
        if 'raw uncoated' in text.lower() or 'uncoated' in text.lower() or 'raw material' in text.lower():
            product['Coating'] = 'Raw/Uncoated'
        elif 'antimicrobial' in text.lower():
            product['Coating'] = 'Antimicrobial coating'
        elif 'fire-rated' in text.lower() or 'fire rating' in text.lower():
            product['Coating'] = 'Fire-rated'
        elif 'textured finish' in text.lower():
            product['Coating'] = 'Textured finish'
        elif 'high-gloss' in text.lower():
            product['Coating'] = 'High-gloss finish'
        elif 'woodgrain' in text.lower():
            product['Coating'] = 'Woodgrain decorative'
        elif 'UV resistant' in text or 'UV stabilized' in text:
            product['Coating'] = 'UV resistant'
        elif 'Weather resistant' in text or 'weather' in text.lower():
            product['Coating'] = 'Weather resistant'
        elif 'foil finish' in text.lower() or 'foil-wrapped' in text.lower():
            product['Coating'] = 'Foil finish'
        elif 'white core' in text.lower():
            product['Coating'] = 'White core'
        elif 'black core' in text.lower():
            product['Coating'] = 'Black core'
        elif 'decorative' in text.lower():
            product['Coating'] = 'Decorative'
        elif 'premium' in text.lower():
            product['Coating'] = 'Premium'
        elif 'standard white' in text.lower():
            product['Coating'] = 'Standard white'
        elif 'custom' in text.lower() and product['Product Type'] == 'HPL Compact':
            product['Coating'] = 'Custom'
    
    # Extract thickness
    thickness_match = re.search(r'Thickness[:\s]+(\d+)\s*mm', text, re.IGNORECASE)
    if thickness_match:
        product['Thickness (mm)'] = thickness_match.group(1)
    else:
        # Try alternate formats
        thickness_match = re.search(r'(\d+)\s*mm\s+thick', text, re.IGNORECASE)
        if thickness_match:
            product['Thickness (mm)'] = thickness_match.group(1)
        else:
            # Try just standalone "10mm" or "Thickness options: 6mm"
            thickness_match = re.search(r'(?:^|[\s:])(\d+)\s*mm(?:\s|$|,)', text, re.IGNORECASE)
            if thickness_match:
                product['Thickness (mm)'] = thickness_match.group(1)
    
    # Extract size/dimensions
    size_patterns = [
        r'Size[s]?[:\s]+(\d{4})\s*x\s*(\d{4})\s*mm',
        r'Dimensions[:\s]+(\d{4})\s*x\s*(\d{4})',
        r'(\d{4})\s*x\s*(\d{4})\s*mm',
        r'Size[:\s]+(\d{4})\s*x\s*(\d{4})',
        r'(\d{4})x(\d{4})mm',
        r'(\d{4})x(\d{4})\s+size',
        r',\s*(\d{4})x(\d{4})',
        r'\s+in\s+(\d{4})x(\d{4})',
        r'(\d{4})x(\d{4})',  # Most general - should be last
    ]
    for pattern in size_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product['Size (mm)'] = f"{match.group(1)}x{match.group(2)}"
            break
    
    # Extract item number
    item_patterns = [
        r'Item\s*#?[:\s]+([A-Z0-9-]+)',
        r'Item\s+number[:\s]+([A-Z0-9-]+)',
        r'Item\s+code[:\s]+([A-Z0-9-]+)',
        r'Item[:\s]+([A-Z]{3,}-\d+-[A-Z0-9-]+)',
        r'^([A-Z]{3,}-\d+-[A-Z0-9-]+)$',
    ]
    for pattern in item_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            item_num = match.group(1).strip()
            # Validate it looks like an item number
            if re.match(r'^[A-Z]{3,}-\d+-[A-Z0-9-]+$', item_num, re.IGNORECASE):
                product['Item Number'] = item_num
                break
    
    # Extract prices
    # One-sided price patterns
    one_sided_patterns = [
        r'Price\s*\(One-sided\)[:\s]+€?([\d.]+)',
        r'€([\d.]+)\s*\(one-sided\)',
        r'Price[:\s]+€([\d.]+)\s*\(single sided\)',
        r'€([\d.]+)\s+one-sided(?!\s*,)',
        r'One-sided[:\s]+€([\d.]+)',
        r'one side[:\s]+€([\d.]+)',
        r'Pricing[:\s]+€([\d.]+)\s+one-sided',
        r'One-sided price[:\s]+€([\d.]+)',
    ]
    for pattern in one_sided_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product['Price One-sided (EUR)'] = match.group(1)
            break
    
    # Two-sided price patterns
    two_sided_patterns = [
        r'Two-sided price[:\s]+€([\d.]+)',
        r'Price\s*\(Two-sided\)[:\s]+€?([\d.]+)',
        r'€([\d.]+)\s*\(two-sided\)',
        r'€([\d.]+)\s*\(double sided\)',
        r'€([\d.]+)\s+two-sided',
        r'Two-sided[:\s]+€([\d.]+)',
        r'Both sides[:\s]+€([\d.]+)',
    ]
    for pattern in two_sided_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product['Price Two-sided (EUR)'] = match.group(1)
            break
    
    # Special case: combined price format "€X / €Y"
    combined_price = re.search(r'€([\d.]+)\s*(?:\((?:one-sided|single sided)\))?\s*/\s*€([\d.]+)\s*(?:\((?:two-sided|double sided)\))?', text, re.IGNORECASE)
    if combined_price:
        if not product['Price One-sided (EUR)']:
            product['Price One-sided (EUR)'] = combined_price.group(1)
        if not product['Price Two-sided (EUR)']:
            product['Price Two-sided (EUR)'] = combined_price.group(2)
    
    # Alternative format with pipes: "One-sided: €X | Two-sided: €Y"
    if not product['Price One-sided (EUR)'] or not product['Price Two-sided (EUR)']:
        pipe_match = re.search(r'One-sided[:\s]+€([\d.]+)\s*\|\s*Two-sided[:\s]+€([\d.]+)', text, re.IGNORECASE)
        if pipe_match:
            if not product['Price One-sided (EUR)']:
                product['Price One-sided (EUR)'] = pipe_match.group(1)
            if not product['Price Two-sided (EUR)']:
                product['Price Two-sided (EUR)'] = pipe_match.group(2)
    
    # Alternative format with commas: "€X one-sided, €Y two-sided"
    if not product['Price One-sided (EUR)'] or not product['Price Two-sided (EUR)']:
        comma_match = re.search(r'€([\d.]+)\s+one-sided\s*,\s*€([\d.]+)\s+two-sided', text, re.IGNORECASE)
        if comma_match:
            if not product['Price One-sided (EUR)']:
                product['Price One-sided (EUR)'] = comma_match.group(1)
            if not product['Price Two-sided (EUR)']:
                product['Price Two-sided (EUR)'] = comma_match.group(2)
    
    # For raw/generic products with only one price
    if not product['Price One-sided (EUR)'] and not product['Price Two-sided (EUR)']:
        single_price = re.search(r'€([\d.]+)\s*(?:per sheet|/sheet|each)', text, re.IGNORECASE)
        if single_price:
            product['Price One-sided (EUR)'] = single_price.group(1)
    
    # Extract pallet size
    pallet_patterns = [
        r'Pallet[:\s]+(\d+)\s*sheets',
        r'(\d+)\s*sheets\s*per\s*pallet',
        r'(\d+)\s*sheets/pallet',
        r'(\d+)\s*per\s*pallet',
        r'Pallet\s+size[:\s]+(\d+)\s*sheets',
        r'Pallet\s+configuration[:\s]+(\d+)\s*sheets',
    ]
    for pattern in pallet_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product['Pallet Size (sheets)'] = match.group(1)
            break
    
    # Extract notes
    note_patterns = [
        r'Note[:\s]+([^\n]+)',
        r'Special[:\s]+([^\n]+)',
        r'Additional[:\s]+([^\n]+)',
    ]
    for pattern in note_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            note_text = match.group(1).strip()
            if note_text and note_text not in notes:
                notes.append(note_text)
    
    # Add special indicators to notes
    if 'N/A' in text and 'one-sided' in text.lower():
        notes.append('Two-sided only')
    if 'raw only' in text.lower():
        notes.append('Raw material - no coating options')
    if 'generic' in text.lower() or 'no item number' in text.lower():
        notes.append('Generic product - no specific item code')
    
    product['Notes'] = '; '.join(notes) if notes else ''
    
    # Skip entries that don't have enough information
    if not product['Product Type'] and not product['Item Number']:
        return None
    
    # For generic products without item number, use description as identifier
    if not product['Item Number'] and product['Product Type']:
        product['Item Number'] = 'GENERIC'
    
    return product


def transform_raw_csv(input_file: str, output_file: str):
    """
    Transform the raw unstructured CSV into a clean structured format.
    """
    products = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into sections by blank lines
    sections = re.split(r'\n\s*\n', content)
    
    for section in sections:
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        
        # Skip headers and section titles
        if not lines:
            continue
            
        first_line = lines[0].lower()
        if any(skip in first_line for skip in ['product information', 'hpl compact - phenolic', 'melamine panels', 'compact laminate - exterior', 'standard mdf boards', 'specialty items']):
            continue
        
        # Each non-empty section should be a product
        product = parse_product_entry(lines)
        if product:
            products.append(product)
    
    # Write to clean CSV
    if products:
        fieldnames = [
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
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        
        print(f"Successfully transformed {len(products)} products from {input_file} to {output_file}")
    else:
        print("No products found in the input file.")


if __name__ == '__main__':
    transform_raw_csv('raw_products.csv', 'cleaned_products.csv')
