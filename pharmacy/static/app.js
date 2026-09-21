/**
 * Pharmacy Billing v0.1 - Frontend JavaScript
 * Vanilla JS, no frameworks
 */

// Global cart state
let cart = [];
let currentBillId = null;

// Utility: Convert paise to rupees string
function paiseToRupees(paise) {
    return '₹' + (paise / 100).toFixed(2);
}

// Utility: Convert rupees to paise (integer)
function rupeesToPaise(rupees) {
    return Math.round(parseFloat(rupees) * 100);
}

// Toggle Add Medicine form visibility
function toggleAddMedicine() {
    const form = document.getElementById('addMedicineForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

// Save new medicine
async function saveNewMedicine() {
    const name = document.getElementById('newMedName').value.trim();
    const priceStr = document.getElementById('newMedPrice').value;
    const genericName = document.getElementById('newMedGeneric').value.trim();
    const manufacturer = document.getElementById('newMedManufacturer').value.trim();

    if (!name) {
        alert('Please enter a medicine name.');
        return;
    }

    if (!priceStr || parseFloat(priceStr) < 0) {
        alert('Please enter a valid price.');
        return;
    }

    const pricePaise = rupeesToPaise(priceStr);

    try {
        const response = await fetch('/api/medicines', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                price: pricePaise,
                generic_name: genericName || null,
                manufacturer: manufacturer || null
            })
        });

        const result = await response.json();

        if (result.success) {
            alert('Medicine saved successfully!');
            // Clear form
            document.getElementById('newMedName').value = '';
            document.getElementById('newMedPrice').value = '';
            document.getElementById('newMedGeneric').value = '';
            document.getElementById('newMedManufacturer').value = '';
            // Hide form
            toggleAddMedicine();
            // Refresh search results if there's a query
            const searchQuery = document.getElementById('medicineSearch').value;
            if (searchQuery) {
                searchMedicines();
            }
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        console.error('Error saving medicine:', error);
        alert('Unable to save medicine. Please try again.');
    }
}

// Search medicines
async function searchMedicines() {
    const query = document.getElementById('medicineSearch').value.trim();
    const resultsDiv = document.getElementById('searchResults');

    if (query.length < 1) {
        resultsDiv.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`/api/medicines/search?q=${encodeURIComponent(query)}`);
        const result = await response.json();

        if (result.success && result.data.length > 0) {
            resultsDiv.innerHTML = result.data.map(med => `
                <div class="search-result-item" onclick="addToCart(${med.id}, '${escapeHtml(med.name)}', ${med.price})">
                    <div class="med-name">${escapeHtml(med.name)}</div>
                    <div class="med-details">
                        ${med.generic_name ? escapeHtml(med.generic_name) + ' | ' : ''}
                        ${med.manufacturer ? escapeHtml(med.manufacturer) : 'Generic'}
                    </div>
                    <div class="med-price">${paiseToRupees(med.price)}</div>
                </div>
            `).join('');
        } else if (result.success) {
            resultsDiv.innerHTML = '<div class="no-results">No medicines found. Try adding a new one.</div>';
        } else {
            resultsDiv.innerHTML = '<div class="no-results">Error searching medicines.</div>';
        }
    } catch (error) {
        console.error('Error searching medicines:', error);
        resultsDiv.innerHTML = '<div class="no-results">Error connecting to server.</div>';
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add medicine to cart
function addToCart(medicineId, medicineName, unitPricePaise) {
    // Check if medicine already in cart
    const existingItem = cart.find(item => item.medicine_id === medicineId);
    
    if (existingItem) {
        existingItem.quantity += 1;
        existingItem.line_total = existingItem.quantity * existingItem.unit_price;
    } else {
        cart.push({
            medicine_id: medicineId,
            medicine_name: medicineName,
            quantity: 1,
            unit_price: unitPricePaise,
            line_total: unitPricePaise
        });
    }

    // Clear search
    document.getElementById('medicineSearch').value = '';
    document.getElementById('searchResults').innerHTML = '';
    
    renderCart();
}

// Update cart item quantity
function updateQuantity(index, newQuantity) {
    const qty = parseInt(newQuantity) || 0;
    
    if (qty <= 0) {
        removeFromCart(index);
        return;
    }
    
    cart[index].quantity = qty;
    cart[index].line_total = cart[index].quantity * cart[index].unit_price;
    renderCart();
}

// Remove item from cart
function removeFromCart(index) {
    cart.splice(index, 1);
    renderCart();
}

// Clear entire cart
function clearCart() {
    if (cart.length === 0) return;
    
    if (confirm('Are you sure you want to clear the cart?')) {
        cart = [];
        currentBillId = null;
        renderCart();
        document.getElementById('printBillBtn').disabled = true;
    }
}

// Render cart UI
function renderCart() {
    const cartItemsEl = document.getElementById('cartItems');
    const emptyMessageEl = document.getElementById('emptyCartMessage');
    const cartTotalEl = document.getElementById('cartTotal');
    const cartTableEl = document.getElementById('cartTable');

    if (cart.length === 0) {
        cartItemsEl.innerHTML = '';
        emptyMessageEl.style.display = 'block';
        cartTableEl.style.display = 'none';
        cartTotalEl.querySelector('span:last-child').textContent = paiseToRupees(0);
        return;
    }

    emptyMessageEl.style.display = 'none';
    cartTableEl.style.display = 'table';

    cartItemsEl.innerHTML = cart.map((item, index) => `
        <tr>
            <td>${escapeHtml(item.medicine_name)}</td>
            <td>
                <input 
                    type="number" 
                    class="qty-input" 
                    value="${item.quantity}" 
                    min="1"
                    inputmode="numeric"
                    onchange="updateQuantity(${index}, this.value)"
                >
            </td>
            <td>${paiseToRupees(item.unit_price)}</td>
            <td>${paiseToRupees(item.line_total)}</td>
            <td>
                <button class="btn btn-danger remove-btn" onclick="removeFromCart(${index})">Remove</button>
            </td>
        </tr>
    `).join('');

    // Calculate and display total
    const totalPaise = cart.reduce((sum, item) => sum + item.line_total, 0);
    cartTotalEl.querySelector('span:last-child').textContent = paiseToRupees(totalPaise);
}

// Save bill
async function saveBill() {
    if (cart.length === 0) {
        alert('Cart is empty. Add medicines before saving bill.');
        return;
    }

    const totalPaise = cart.reduce((sum, item) => sum + item.line_total, 0);

    try {
        const response = await fetch('/api/bills', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                items: cart,
                total_amount: totalPaise
            })
        });

        const result = await response.json();

        if (result.success) {
            currentBillId = result.bill_id;
            alert(`Bill saved successfully!\nBill Number: ${result.bill_number}`);
            
            // Enable print button
            document.getElementById('printBillBtn').disabled = false;
            
            // Refresh bills list
            loadRecentBills();
            
            // Don't clear cart - allow printing first
        } else {
            alert('Error saving bill: ' + result.error);
        }
    } catch (error) {
        console.error('Error saving bill:', error);
        alert('Unable to save bill. Please try again.');
    }
}

// Print bill
async function printBill() {
    if (!currentBillId) {
        alert('No bill to print. Save the bill first.');
        return;
    }

    try {
        const response = await fetch(`/api/bills/${currentBillId}`);
        const result = await response.json();

        if (result.success) {
            const bill = result.data;
            generatePrintableBill(bill);
            window.print();
        } else {
            alert('Error loading bill: ' + result.error);
        }
    } catch (error) {
        console.error('Error loading bill:', error);
        alert('Unable to load bill for printing.');
    }
}

// Generate printable bill HTML
function generatePrintableBill(bill) {
    const printArea = document.getElementById('printArea');
    
    const itemsHtml = bill.items.map(item => `
        <tr>
            <td>${escapeHtml(item.medicine_name)}</td>
            <td>${item.quantity}</td>
            <td>${paiseToRupees(item.unit_price)}</td>
            <td>${paiseToRupees(item.line_total)}</td>
        </tr>
    `).join('');

    const dateObj = new Date(bill.created_at);
    const dateStr = dateObj.toLocaleDateString('en-IN');
    const timeStr = dateObj.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

    printArea.innerHTML = `
        <div class="print-bill-header">
            <h1>MediStore</h1>
            <p>Pharmacy Billing System</p>
        </div>
        
        <div class="print-bill-info">
            <div>
                <strong>Bill Number:</strong> ${bill.bill_number}<br>
                <strong>Date:</strong> ${dateStr}<br>
                <strong>Time:</strong> ${timeStr}
            </div>
        </div>
        
        <table class="print-bill-table">
            <thead>
                <tr>
                    <th>Medicine</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                ${itemsHtml}
            </tbody>
        </table>
        
        <div class="print-bill-total">
            Grand Total: ${paiseToRupees(bill.total_amount)}
        </div>
        
        <div class="print-bill-footer">
            <p>Thank you for your purchase!</p>
            <p>Generated by MediStore v0.1</p>
        </div>
    `;
}

// Load recent bills
async function loadRecentBills() {
    try {
        const response = await fetch('/api/bills');
        const result = await response.json();

        if (result.success) {
            const billsListEl = document.getElementById('billsList');
            
            if (result.data.length === 0) {
                billsListEl.innerHTML = '<div class="no-results">No bills yet.</div>';
                return;
            }

            billsListEl.innerHTML = result.data.map(bill => {
                const dateObj = new Date(bill.created_at);
                const dateStr = dateObj.toLocaleDateString('en-IN', { 
                    day: '2-digit', 
                    month: 'short', 
                    year: 'numeric' 
                });
                
                return `
                    <div class="bill-item" onclick="viewBill(${bill.id})">
                        <div>
                            <div class="bill-number">${bill.bill_number}</div>
                            <div class="bill-date">${dateStr}</div>
                        </div>
                        <div class="bill-amount">${paiseToRupees(bill.total_amount)}</div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Error loading bills:', error);
    }
}

// View a specific bill (for reprinting)
async function viewBill(billId) {
    try {
        const response = await fetch(`/api/bills/${billId}`);
        const result = await response.json();

        if (result.success) {
            const bill = result.data;
            currentBillId = bill.id;
            generatePrintableBill(bill);
            
            // Ask if user wants to print
            if (confirm(`Viewing ${bill.bill_number}. Want to print?`)) {
                window.print();
            }
        } else {
            alert('Error loading bill: ' + result.error);
        }
    } catch (error) {
        console.error('Error loading bill:', error);
        alert('Unable to load bill.');
    }
}

// Backup database
async function backupDatabase() {
    const messageEl = document.getElementById('backupMessage');
    messageEl.className = 'message';
    messageEl.textContent = 'Creating backup...';

    try {
        const response = await fetch('/api/backup', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            messageEl.className = 'message success';
            messageEl.textContent = `Backup created: ${result.backup_file}`;
        } else {
            messageEl.className = 'message error';
            messageEl.textContent = 'Error creating backup: ' + result.error;
        }
    } catch (error) {
        console.error('Error creating backup:', error);
        messageEl.className = 'message error';
        messageEl.textContent = 'Unable to create backup.';
    }
}

// Initialize app on page load
document.addEventListener('DOMContentLoaded', function() {
    loadRecentBills();
    renderCart();
});
