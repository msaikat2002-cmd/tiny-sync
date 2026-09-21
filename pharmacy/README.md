# MediStore - Pharmacy Billing v0.1

A lightweight, local-first pharmacy billing application for small medical shops.

## Features (v0.1)

- ✅ Medicine master (add/search medicines)
- ✅ Quick medicine search
- ✅ Quantity entry
- ✅ Price calculation (decimal-safe using integer paise)
- ✅ Billing cart
- ✅ Bill total
- ✅ Save bill with sequential bill numbers
- ✅ Basic bill history
- ✅ Simple printable bill
- ✅ Database backup
- ✅ Works completely offline after installation

## Technology Stack

**Backend:**
- Python 3 (standard library only)
- SQLite3 (included with Python)
- Built-in http.server module

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript (no frameworks)

**Zero external dependencies.**

## Installation on Termux (Android)

```bash
# Update package list
pkg update

# Install Python
pkg install python

# Navigate to project directory
cd pharmacy

# Start the server
python server.py
```

Then open your browser and go to:
```
http://127.0.0.1:8080
```

## Installation on Fedora Linux

```bash
# Ensure Python 3 is installed (usually pre-installed)
sudo dnf install python3

# Navigate to project directory
cd pharmacy

# Start the server
python3 server.py
```

Then open your browser and go to:
```
http://127.0.0.1:8080
```

## Installation on Windows

```cmd
# Ensure Python 3 is installed from python.org

# Navigate to project directory
cd pharmacy

# Start the server
python server.py
```

Then open your browser and go to:
```
http://127.0.0.1:8080
```

## Usage Guide

### Adding a Medicine

1. Click "+ Add New Medicine" button
2. Enter medicine name (required)
3. Enter price in rupees (required)
4. Optionally enter generic name and manufacturer
5. Click "Save Medicine"

### Creating a Bill

1. Type medicine name in the search box
2. Tap on the medicine from search results
3. Adjust quantity if needed (default is 1)
4. Add more medicines as needed
5. Review cart total
6. Click "Save Bill"
7. Click "Print Bill" to print

### Viewing/Reprinting Bills

- Recent bills appear in the "Recent Bills" section
- Tap any bill to view and optionally reprint

### Backing Up Database

- Click "Backup Database" button
- Backup is saved to `backups/` folder with timestamp
- Example: `backup_2026-09-21_163000.db`

## Project Structure

```
pharmacy/
│
├── server.py           # HTTP server and API endpoints
├── database.py         # SQLite database operations
├── billing.py          # Billing calculations and logic
├── config.py           # Configuration settings
├── pharmacy.db         # SQLite database (created automatically)
│
├── templates/
│   └── index.html      # Main HTML page
│
├── static/
│   ├── style.css       # Stylesheet
│   └── app.js          # Frontend JavaScript
│
├── data/               # Reserved for future use
│
├── backups/            # Database backups
│   └── backup_YYYY-MM-DD_HHMMSS.db
│
└── README.md           # This file
```

## Database Schema

### medicines table
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Medicine name |
| generic_name | TEXT | Generic name (optional) |
| manufacturer | TEXT | Manufacturer (optional) |
| price | INTEGER | Price in paise (₹1 = 100 paise) |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

### bills table
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| bill_number | TEXT | Unique bill number (e.g., BILL-000001) |
| created_at | TIMESTAMP | Creation time |
| total_amount | INTEGER | Total in paise |

### bill_items table
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| bill_id | INTEGER | Reference to bills.id |
| medicine_id | INTEGER | Reference to medicines.id (or NULL) |
| medicine_name | TEXT | Medicine name (snapshot) |
| quantity | INTEGER | Quantity |
| unit_price | INTEGER | Unit price in paise (snapshot) |
| line_total | INTEGER | Line total in paise |

**Note:** `medicine_name` and `unit_price` are stored as snapshots in `bill_items`. This ensures that if medicine prices change later, old bills remain unchanged.

## API Endpoints

### GET /api/medicines
Get all medicines.

### GET /api/medicines/search?q=query
Search medicines by name, generic name, or manufacturer.

### POST /api/medicines
Add a new medicine.
```json
{
  "name": "Paracetamol 500 mg",
  "price": 2500,
  "generic_name": "Paracetamol",
  "manufacturer": "Cipla"
}
```

### POST /api/bills
Save a new bill.
```json
{
  "items": [
    {
      "medicine_id": 1,
      "medicine_name": "Paracetamol 500 mg",
      "quantity": 2,
      "unit_price": 2500,
      "line_total": 5000
    }
  ],
  "total_amount": 5000
}
```

### GET /api/bills
Get recent bills (last 50).

### GET /api/bills/<id>
Get a specific bill with all items.

### POST /api/backup
Create a database backup.

## Money Handling

All monetary values are stored as **integer paise** to avoid floating-point precision issues.

- ₹25.50 → 2550 paise
- ₹100.00 → 10000 paise

The frontend displays rupees with decimal notation, but all backend calculations use integers.

## Security Notes

- Server binds to `127.0.0.1` only (localhost)
- Not exposed to LAN or internet by default
- No user authentication (single-user local app)
- No cloud connectivity

## Troubleshooting

### Port already in use
If you get "Address already in use" error:
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill <PID>
```

Or edit `config.py` to use a different port.

### Database not found
The database is created automatically on first run. If missing, simply restart the server.

### Browser shows blank page
Check that:
1. Server is running (look for startup message)
2. You're accessing `http://127.0.0.1:8080` (not localhost on some Android devices)
3. Check browser console for errors (F12)

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Restoring from Backup

To restore from a backup:

```bash
# Stop the server
# Copy backup to database location
cp backups/backup_2026-09-21_163000.db pharmacy.db
# Restart server
python server.py
```

## Future Versions (Planned)

- v0.2: GST support
- v0.3: Inventory management
- v0.4: Batch numbers
- v0.5: Expiry tracking
- v0.6: Purchase management
- v0.7: Supplier management
- v0.8: Reports
- v0.9: Home server sync
- v1.0: Complete pharmacy system

## License

This software is provided as-is for educational and personal use.

## Support

For issues or questions, check the source code comments. The code is designed to be readable and understandable.

---

**MediStore v0.1** - Simple, Fast, Local-First Pharmacy Billing
