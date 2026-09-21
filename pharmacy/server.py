"""
HTTP Server for Pharmacy Billing v0.1
Uses Python's built-in http.server module.
No external dependencies required.
"""

import json
import os
import shutil
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import config
from database import (
    add_medicine,
    search_medicines,
    get_all_medicines,
    get_medicine_by_id,
    get_next_bill_number,
    save_bill,
    get_all_bills,
    get_bill_by_id
)
from billing import paise_to_rupees


class PharmacyHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for pharmacy API."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=config.PROJECT_ROOT, **kwargs)
    
    def send_json_response(self, data, status=200):
        """Send a JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        # Serve static files and templates
        if path == '/' or path == '/index.html':
            self.path = '/templates/index.html'
            return super().do_GET()
        
        # API: Get all medicines
        if path == '/api/medicines':
            try:
                medicines = get_all_medicines()
                self.send_json_response({'success': True, 'data': medicines})
            except Exception as e:
                self.log_error(f"Error getting medicines: {e}")
                self.send_json_response({'success': False, 'error': str(e)}, 500)
            return
        
        # API: Search medicines
        if path == '/api/medicines/search':
            try:
                q = query.get('q', [''])[0]
                if len(q) < 1:
                    self.send_json_response({'success': True, 'data': []})
                    return
                
                medicines = search_medicines(q)
                self.send_json_response({'success': True, 'data': medicines})
            except Exception as e:
                self.log_error(f"Error searching medicines: {e}")
                self.send_json_response({'success': False, 'error': str(e)}, 500)
            return
        
        # API: Get all bills
        if path == '/api/bills':
            try:
                bills = get_all_bills(limit=50)
                self.send_json_response({'success': True, 'data': bills})
            except Exception as e:
                self.log_error(f"Error getting bills: {e}")
                self.send_json_response({'success': False, 'error': str(e)}, 500)
            return
        
        # API: Get single bill
        if path.startswith('/api/bills/'):
            try:
                bill_id = int(path.split('/')[-1])
                bill = get_bill_by_id(bill_id)
                
                if bill:
                    self.send_json_response({'success': True, 'data': bill})
                else:
                    self.send_json_response({'success': False, 'error': 'Bill not found'}, 404)
            except ValueError:
                self.send_json_response({'success': False, 'error': 'Invalid bill ID'}, 400)
            except Exception as e:
                self.log_error(f"Error getting bill: {e}")
                self.send_json_response({'success': False, 'error': str(e)}, 500)
            return
        
        # Default: serve static files
        return super().do_GET()
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
            return
        
        # API: Add medicine
        if path == '/api/medicines':
            try:
                name = data.get('name', '').strip()
                price = data.get('price')
                generic_name = data.get('generic_name')
                manufacturer = data.get('manufacturer')
                
                if not name:
                    self.send_json_response({'success': False, 'error': 'Medicine name is required'}, 400)
                    return
                
                if price is None or not isinstance(price, (int, float)) or price < 0:
                    self.send_json_response({'success': False, 'error': 'Valid price is required'}, 400)
                    return
                
                medicine_id = add_medicine(name, int(price), generic_name, manufacturer)
                
                if medicine_id:
                    self.send_json_response({
                        'success': True,
                        'data': {'id': medicine_id, 'name': name, 'price': price}
                    })
                else:
                    self.send_json_response({'success': False, 'error': 'Failed to save medicine'}, 500)
                    
            except Exception as e:
                self.log_error(f"Error adding medicine: {e}")
                self.send_json_response({'success': False, 'error': str(e)}, 500)
            return
        
        # API: Save bill
        if path == '/api/bills':
            try:
                items = data.get('items', [])
                total_amount = data.get('total_amount', 0)
                
                if not items:
                    self.send_json_response({'success': False, 'error': 'Cart is empty'}, 400)
                    return
                
                if not isinstance(total_amount, int) or total_amount < 0:
                    self.send_json_response({'success': False, 'error': 'Invalid total amount'}, 400)
                    return
                
                # Save bill transactionally (generates bill number internally)
                bill_id, bill_number = save_bill(total_amount, items)
                
                self.send_json_response({
                    'success': True,
                    'bill_id': bill_id,
                    'bill_number': bill_number
                })
                
            except Exception as e:
                self.log_error(f"Error saving bill: {e}")
                self.send_json_response({'success': False, 'error': str(e)}, 500)
            return
        
        # API: Backup database
        if path == '/api/backup':
            try:
                # Ensure backup directory exists
                os.makedirs(config.BACKUP_DIR, exist_ok=True)
                
                # Generate backup filename with timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                backup_filename = f'backup_{timestamp}.db'
                backup_path = os.path.join(config.BACKUP_DIR, backup_filename)
                
                # Copy database file
                if os.path.exists(config.DATABASE_PATH):
                    shutil.copy2(config.DATABASE_PATH, backup_path)
                    
                    self.send_json_response({
                        'success': True,
                        'backup_file': backup_filename
                    })
                else:
                    self.send_json_response({'success': False, 'error': 'Database not found'}, 404)
                    
            except Exception as e:
                self.log_error(f"Error creating backup: {e}")
                self.send_json_response({'success': False, 'error': str(e)}, 500)
            return
        
        # Default: 404
        self.send_json_response({'success': False, 'error': 'Not found'}, 404)
    
    def log_message(self, format, *args):
        """Log HTTP requests."""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")
    
    def log_error(self, format, *args):
        """Log errors."""
        print(f"[ERROR {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def run_server(host=config.HOST, port=config.PORT):
    """Start the HTTP server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, PharmacyHandler)
    
    print(f"\n{'='*50}")
    print(f"MediStore - Pharmacy Billing v0.1")
    print(f"{'='*50}")
    print(f"\nServer starting on http://{host}:{port}")
    print(f"\nOpen this URL in your browser:")
    print(f"  http://localhost:{port}")
    print(f"\nPress Ctrl+C to stop the server.\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    run_server()
