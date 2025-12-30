# Mock Medical E-Commerce Ecosystem

This folder contains two fully functional mock medical e-commerce websites for testing the MCP (Medical Comparison & Purchase) server.

## 📁 Structure

```
mock-ecosystem/
├── site-a/                    # Mimics Tata 1mg
│   ├── package.json
│   ├── server.js              # Express server with all APIs
│   └── views/
│       ├── index.ejs          # Homepage
│       ├── product.ejs        # Product detail page
│       ├── cart.ejs           # Shopping cart
│       ├── checkout.ejs       # Checkout page
│       ├── order.ejs          # Order confirmation
│       └── error.ejs          # Error page
│
├── site-b/                    # Mimics Apollo Pharmacy
│   ├── package.json
│   ├── server.js              # Express server with all APIs
│   └── views/
│       ├── index.ejs          # Homepage
│       ├── product.ejs        # Product detail page
│       ├── cart.ejs           # Shopping cart
│       ├── checkout.ejs       # Checkout page
│       ├── order.ejs          # Order confirmation
│       └── error.ejs          # Error page
│
└── README.md
```

## 🚀 Quick Start

### Start Site-A (Tata 1mg Mock) - Port 3001
```bash
cd site-a
npm install
npm start
```
Visit: http://localhost:3001

### Start Site-B (Apollo Mock) - Port 3002
```bash
cd site-b
npm install
npm start
```
Visit: http://localhost:3002

## 🔌 API Endpoints

Both sites expose identical API structure (for MCP server compatibility):

### Health Check
```
GET /api/health
```

### Medicines
```
GET  /api/medicines                    # List all medicines (with filters)
GET  /api/medicines/:id                # Get medicine by ID
POST /api/medicines/search             # Search by names array
GET  /api/categories                   # Get all categories
```

**Query Parameters for `/api/medicines`:**
- `category` - Filter by category
- `search` - Search in name/generic/brand
- `prescriptionRequired` - true/false
- `inStock` - true
- `sortBy` - price/rating/name/discount
- `order` - asc/desc

### Cart Operations
```
GET    /api/cart/:userId               # Get cart
POST   /api/cart/:userId/add           # Add item
PUT    /api/cart/:userId/update        # Update quantity
DELETE /api/cart/:userId/remove/:id    # Remove item
DELETE /api/cart/:userId/clear         # Clear cart
```

### Orders
```
POST /api/orders/create                # Create order
POST /api/orders/:orderId/pay          # Process payment
GET  /api/orders/:orderId              # Get order details
GET  /api/orders/user/:userId          # Get user orders
PUT  /api/orders/:orderId/status       # Update status
```

### Prescription
```
POST /api/prescription/upload          # Upload prescription
POST /api/prescription/:id/verify      # Verify prescription
```

### Delivery
```
GET /api/delivery/slots                # Get available slots
```

### Users
```
GET  /api/users/:userId                # Get user profile
POST /api/users/:userId/addresses      # Add address
```

## 📦 Sample Medicines

### Site-A (Tata 1mg):
| ID | Medicine | Price | Prescription |
|----|----------|-------|--------------|
| MED001 | Paracetamol 500mg (Crocin) | ₹25 | No |
| MED002 | Azithromycin 500mg (Azithral) | ₹85 | Yes |
| MED003 | Metformin 500mg (Glycomet) | ₹45 | Yes |
| MED004 | Omeprazole 20mg (Omez) | ₹65 | No |
| MED005 | Amoxicillin 500mg (Mox) | ₹55 | Yes |
| MED006 | Vitamin D3 60000 IU (D-Rise) | ₹120 | No |
| MED007 | Cetirizine 10mg (Cetzine) | ₹35 | No |
| MED008 | Atorvastatin 10mg (Atorva) | ₹95 | Yes |

### Site-B (Apollo):
| ID | Medicine | Price | Prescription |
|----|----------|-------|--------------|
| APL001 | Paracetamol 500mg (Dolo) | ₹22 | No |
| APL002 | Azithromycin 500mg (Zithromax) | ₹95 | Yes |
| APL003 | Metformin 500mg (Glucophage) | ₹38 | Yes |
| APL004 | Pantoprazole 40mg (Pan-D) | ₹75 | No |
| APL005 | Amoxicillin 500mg (Amoxil) | ₹48 | Yes |
| APL006 | Vitamin D3 60000 IU (Calcirol) | ₹105 | No |
| APL007 | Levocetirizine 5mg (Xyzal) | ₹42 | No |
| APL008 | Rosuvastatin 10mg (Crestor) | ₹110 | Yes |
| APL009 | Ibuprofen 400mg (Brufen) | ₹28 | No |
| APL010 | Montelukast 10mg (Montair) | ₹135 | Yes |

## 🔄 MCP Server Integration

### Search for medicines across sites:
```javascript
// Search by medicine name
const searchMedicines = async (names) => {
  const [tata1mgResults, apolloResults] = await Promise.all([
    fetch('http://localhost:3001/api/medicines/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ names })
    }),
    fetch('http://localhost:3002/api/medicines/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ names })
    })
  ]);
  
  return {
    tata1mg: await tata1mgResults.json(),
    apollo: await apolloResults.json()
  };
};
```

### Compare prices:
```javascript
// Compare prices for same medicine
const comparePrices = async (medicineName) => {
  const results = await searchMedicines([medicineName]);
  
  return {
    tata1mg: results.tata1mg.data[0]?.matches[0],
    apollo: results.apollo.data[0]?.matches[0],
    cheapest: // determine cheapest
  };
};
```

### Add to cart and checkout:
```javascript
// Full purchase flow
const purchaseMedicine = async (siteUrl, userId, medicineId) => {
  // Add to cart
  await fetch(`${siteUrl}/api/cart/${userId}/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ medicineId, quantity: 1 })
  });
  
  // Create order
  const order = await fetch(`${siteUrl}/api/orders/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      userId,
      addressId: 'addr1',
      paymentMethod: 'UPI'
    })
  });
  
  // Process payment
  await fetch(`${siteUrl}/api/orders/${order.orderId}/pay`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ paymentMethod: 'UPI' })
  });
  
  return order;
};
```

## 🎨 Features

### Site-A (Tata 1mg Mock):
- 🎨 Coral/Pink theme (#ff6f61)
- 📦 1-2 days standard delivery
- 💰 Free delivery above ₹500
- 📋 Prescription verification

### Site-B (Apollo Mock):
- 🎨 Indigo/Blue theme (#1a237e)
- 🚀 24 hours express delivery
- 💰 Free delivery above ₹400
- 🏥 Store locator API
- 📋 Prescription verification

## 📝 Test User

Both sites have a pre-configured test user:

```json
{
  "userId": "user123",
  "name": "Test User",
  "email": "test@example.com",
  "phone": "9876543210"
}
```

## ⚠️ Important Notes

1. **This is for testing only** - Not connected to real pharmacies
2. **No real payments** - All transactions are simulated
3. **Mock data** - Medicine info is for demonstration
4. **In-memory storage** - Data resets on server restart

## 🧪 Testing with cURL

```bash
# Get all medicines
curl http://localhost:3001/api/medicines

# Search medicines
curl -X POST http://localhost:3001/api/medicines/search \
  -H "Content-Type: application/json" \
  -d '{"names": ["paracetamol", "azithromycin"]}'

# Add to cart
curl -X POST http://localhost:3001/api/cart/user123/add \
  -H "Content-Type: application/json" \
  -d '{"medicineId": "MED001", "quantity": 2}'

# Get cart
curl http://localhost:3001/api/cart/user123

# Create order
curl -X POST http://localhost:3001/api/orders/create \
  -H "Content-Type: application/json" \
  -d '{"userId": "user123", "addressId": "addr1", "paymentMethod": "COD"}'
```

---

Built for the MCP Server Prescription Management System 🏥
