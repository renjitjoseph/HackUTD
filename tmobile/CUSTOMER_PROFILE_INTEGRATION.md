# Customer Profile Integration Guide

## Overview
A floating action button (FAB) has been added to the bottom right of the home screen that navigates to a detailed customer profile page.

## What Was Added

### 1. Floating Action Button (FAB)
- **Location:** Bottom right corner, above the navigation bar
- **Icon:** Person icon in T-Mobile magenta
- **Action:** Taps navigate to the Customer Profile screen
- **Styling:** Circular button with shadow and hover effect

### 2. Customer Profile Screen
A comprehensive customer profile page displaying:
- **Header:** Magenta gradient with back button
- **Profile Section:** Customer avatar, name, and premium status badge
- **Account Info:** Account number, phone number, member duration
- **Plan Details:** Current plan (Magenta MAX), monthly bill, data usage, device
- **Billing Info:** Last payment date, next bill date
- **Loyalty Rewards:** Points available
- **Action Buttons:** Message, Call, Email (ready for functionality)

### 3. Navigation System
- Implemented React Navigation with Native Stack Navigator
- Smooth transitions between Home and Customer Profile screens
- Back button functionality on profile screen

## File Structure

```
tmobile/
├── App.js                    # Navigation container and stack setup
├── HomeScreen.js            # Main T-Mobile Life screen with FAB
├── CustomerProfile.js       # Customer profile page with mock data
├── package.json             # Updated with navigation dependencies
└── README.md                # Updated documentation
```

## Integration Points for Live Data

### Current Implementation: Random Customer Selection
The app currently picks a random customer from the data table on each profile page load:

```javascript
// In CustomerProfile.js
useEffect(() => {
  setTimeout(() => {
    const randomCustomer = getRandomCustomer();
    setCustomerData(randomCustomer);
    setLoading(false);
  }, 300);
}, []);
```

### Option 1: Fetch Specific Customer by ID
Replace random selection with a specific customer:

```javascript
// In HomeScreen.js - pass customer ID when navigating
navigation.navigate('CustomerProfile', {
  customerId: detectedCustomerId
});

// In CustomerProfile.js
import { getCustomerById } from './customerData';

useEffect(() => {
  const customerId = route.params?.customerId;
  if (customerId) {
    const customer = getCustomerById(customerId);
    setCustomerData(customer);
  } else {
    const customer = getRandomCustomer();
    setCustomerData(customer);
  }
  setLoading(false);
}, [route.params]);
```

### Option 2: Live API Integration
Replace the mock data table with API calls:

```javascript
// In CustomerProfile.js
useEffect(() => {
  fetchCustomerData();
}, []);

async function fetchCustomerData() {
  try {
    // Replace with your API endpoint
    const response = await fetch('https://your-api.com/customer/current');
    const data = await response.json();
    setCustomerData(data);
    setLoading(false);
  } catch (error) {
    console.error('Error fetching customer data:', error);
    setLoading(false);
  }
}
```

### Option 3: Context API for App-Wide Customer State
Create a customer context for app-wide state:

```javascript
// Create CustomerContext.js
import React, { createContext, useState } from 'react';

export const CustomerContext = createContext();

export const CustomerProvider = ({ children }) => {
  const [currentCustomer, setCurrentCustomer] = useState(null);
  
  return (
    <CustomerContext.Provider value={{ currentCustomer, setCurrentCustomer }}>
      {children}
    </CustomerContext.Provider>
  );
};

// Use in components
const { currentCustomer } = useContext(CustomerContext);
```

### Option 4: WebSocket for Real-Time Updates
Replace mock data with live fetching:

```javascript
// In CustomerProfile.js
const [customerData, setCustomerData] = useState(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  fetchCustomerData();
  // Or setup WebSocket connection
  const ws = new WebSocket('ws://your-server.com/customer-data');
  ws.onmessage = (event) => {
    setCustomerData(JSON.parse(event.data));
  };
  return () => ws.close();
}, []);

async function fetchCustomerData() {
  try {
    const response = await fetch('https://your-api.com/customer/current');
    const data = await response.json();
    setCustomerData(data);
    setLoading(false);
  } catch (error) {
    console.error('Error fetching customer data:', error);
  }
}
```

### Option 5: Redux/State Management
For larger apps with complex state:

```javascript
// Using Redux Toolkit
import { useSelector, useDispatch } from 'react-redux';
import { fetchCustomer } from './store/customerSlice';

const customerData = useSelector((state) => state.customer.data);
const dispatch = useDispatch();

useEffect(() => {
  dispatch(fetchCustomer());
}, []);
```

## Mock Data Structure

### Customer Data Table (`customerData.js`)

The app now includes a customer data table with 8 sample customers. Each time you open the profile page, it randomly selects one customer by ID.

**Customer Data Structure:**
```javascript
{
  id: 1,
  name: 'Sarah Johnson',
  accountNumber: '****7829',
  phoneNumber: '(555) 123-4567',
  plan: 'Magenta MAX',
  status: 'Premium',
  accountAge: '3 years',
  monthlyBill: '$85.00',
  dataUsage: '24.5 GB',
  deviceModel: 'iPhone 14 Pro',
  lastPayment: 'Nov 2, 2025',
  nextBillDate: 'Nov 15, 2025',
  loyaltyPoints: 2450,
}
```

**Available Customers:** 8 customers with IDs 1-8
- Mix of Premium and Standard status
- Various plans: Magenta MAX, Magenta, Essentials
- Different account ages, devices, and loyalty points

## Next Steps

1. **Connect to your backend:**
   - Replace mock data with API calls
   - Implement real-time updates via WebSocket
   - Add authentication if needed

2. **Add functionality to action buttons:**
   - Message: Open chat interface
   - Call: Initiate phone call
   - Email: Open email client

3. **Enhance the profile:**
   - Add more customer details as needed
   - Include purchase history
   - Show active services
   - Display recent interactions

4. **Add loading states:**
   - Show loading spinner while fetching data
   - Handle error states gracefully
   - Add pull-to-refresh functionality

## Testing the Feature

1. Start the app: `npm start`
2. Navigate to the home screen
3. Look for the magenta circular button in the bottom right
4. Tap the button to navigate to the customer profile
5. Use the back arrow to return to home

The profile currently shows mock data for "Sarah Johnson". Replace this with your live customer detection system.

