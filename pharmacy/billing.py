"""
Billing logic module for Pharmacy Billing v0.1
Handles price calculations and cart operations.
All monetary values are handled as integer paise (₹1.00 = 100 paise).
"""


def rupees_to_paise(rupees):
    """
    Convert rupees (float or string) to integer paise.
    Example: 25.50 → 2550
    """
    if isinstance(rupees, str):
        rupees = float(rupees.replace(',', ''))
    
    # Round to 2 decimal places and convert to paise
    return int(round(float(rupees) * 100))


def paise_to_rupees(paise):
    """
    Convert integer paise to rupees string.
    Example: 2550 → "25.50"
    """
    return f"{paise / 100:.2f}"


def calculate_line_total(quantity, unit_price_paise):
    """
    Calculate line total for a cart item.
    
    Args:
        quantity: Integer quantity
        unit_price_paise: Integer unit price in paise
    
    Returns:
        Integer line total in paise
    """
    return quantity * unit_price_paise


def calculate_bill_total(items):
    """
    Calculate total bill amount from cart items.
    
    Args:
        items: List of dicts with 'line_total' key (in paise)
    
    Returns:
        Integer total in paise
    """
    return sum(item['line_total'] for item in items)


def validate_cart_item(medicine_name, quantity, unit_price_paise):
    """
    Validate a cart item before adding.
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not medicine_name or not medicine_name.strip():
        return False, "Please enter a medicine name."
    
    if not isinstance(quantity, int) or quantity <= 0:
        return False, "Quantity must be greater than zero."
    
    if not isinstance(unit_price_paise, int) or unit_price_paise < 0:
        return False, "Price must be a valid non-negative number."
    
    return True, None


def prepare_bill_item(medicine_id, medicine_name, quantity, unit_price_paise):
    """
    Prepare a bill item dict for saving.
    
    Returns:
        Dict with all required fields for bill_items table
    """
    line_total = calculate_line_total(quantity, unit_price_paise)
    
    return {
        'medicine_id': medicine_id,
        'medicine_name': medicine_name.strip(),
        'quantity': quantity,
        'unit_price': unit_price_paise,
        'line_total': line_total
    }
