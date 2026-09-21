"""
Database module for Pharmacy Billing v0.1
Handles SQLite database initialization and operations.
All monetary values are stored as integer paise (₹1.00 = 100 paise).
"""

import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH


def get_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    """Initialize the database with required tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create medicines table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            generic_name TEXT,
            manufacturer TEXT,
            price INTEGER NOT NULL,  -- Stored in paise
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create bills table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_number TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount INTEGER NOT NULL  -- Stored in paise
        )
    ''')
    
    # Create bill_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            medicine_id INTEGER,
            medicine_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price INTEGER NOT NULL,  -- Stored in paise
            line_total INTEGER NOT NULL,  -- Stored in paise
            FOREIGN KEY (bill_id) REFERENCES bills(id)
        )
    ''')
    
    # Create index for faster searches
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_medicines_name 
        ON medicines(name)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_bills_bill_number 
        ON bills(bill_number)
    ''')
    
    conn.commit()
    conn.close()


def add_medicine(name, price, generic_name=None, manufacturer=None):
    """
    Add a new medicine to the database.
    Price should be in paise (integer).
    Returns the medicine ID on success, None on failure.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO medicines (name, generic_name, manufacturer, price)
            VALUES (?, ?, ?, ?)
        ''', (name, generic_name, manufacturer, price))
        
        conn.commit()
        medicine_id = cursor.lastrowid
        return medicine_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def search_medicines(query):
    """
    Search medicines by name, generic_name, or manufacturer.
    Returns list of matching medicines.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    search_pattern = f'%{query}%'
    cursor.execute('''
        SELECT id, name, generic_name, manufacturer, price
        FROM medicines
        WHERE name LIKE ? OR generic_name LIKE ? OR manufacturer LIKE ?
        ORDER BY name
        LIMIT 20
    ''', (search_pattern, search_pattern, search_pattern))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_all_medicines():
    """Get all medicines from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, generic_name, manufacturer, price
        FROM medicines
        ORDER BY name
    ''')
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_medicine_by_id(medicine_id):
    """Get a single medicine by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, generic_name, manufacturer, price
        FROM medicines
        WHERE id = ?
    ''', (medicine_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def get_next_bill_number(conn):
    """
    Generate the next sequential bill number.
    Requires an open connection to ensure atomicity.
    """
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT MAX(CAST(SUBSTR(bill_number, 4) AS INTEGER)) as max_num
        FROM bills
        WHERE bill_number LIKE 'BILL-%'
    ''')
    
    row = cursor.fetchone()
    max_num = row['max_num'] if row and row['max_num'] else 0
    next_num = max_num + 1
    
    # Format as BILL-000001, BILL-000002, etc.
    return f'BILL-{next_num:06d}'


def save_bill(total_amount, items):
    """
    Save a bill with all its items transactionally.
    
    Args:
        total_amount: Integer total in paise
        items: List of dicts with keys:
            - medicine_id (int or None)
            - medicine_name (str)
            - quantity (int)
            - unit_price (int, in paise)
            - line_total (int, in paise)
    
    Returns:
        Tuple (bill_id, bill_number) on success
        
    Raises:
        Exception on failure
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        cursor.execute('BEGIN TRANSACTION')
        
        # Generate bill number within transaction
        bill_number = get_next_bill_number(conn)
        
        # Insert bill
        cursor.execute('''
            INSERT INTO bills (bill_number, total_amount)
            VALUES (?, ?)
        ''', (bill_number, total_amount))
        
        bill_id = cursor.lastrowid
        
        # Insert all bill items
        for item in items:
            cursor.execute('''
                INSERT INTO bill_items (bill_id, medicine_id, medicine_name, quantity, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                bill_id,
                item.get('medicine_id'),
                item['medicine_name'],
                item['quantity'],
                item['unit_price'],
                item['line_total']
            ))
        
        # Commit transaction
        conn.commit()
        return bill_id, bill_number
        
    except Exception as e:
        # Rollback on any error
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_all_bills(limit=50):
    """Get recent bills."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, bill_number, created_at, total_amount
        FROM bills
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_bill_by_id(bill_id):
    """Get a bill with all its items."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get bill header
    cursor.execute('''
        SELECT id, bill_number, created_at, total_amount
        FROM bills
        WHERE id = ?
    ''', (bill_id,))
    
    bill_row = cursor.fetchone()
    if not bill_row:
        conn.close()
        return None
    
    bill = dict(bill_row)
    
    # Get bill items
    cursor.execute('''
        SELECT id, medicine_id, medicine_name, quantity, unit_price, line_total
        FROM bill_items
        WHERE bill_id = ?
    ''', (bill_id,))
    
    bill['items'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return bill


# Initialize database when module is imported
init_database()
