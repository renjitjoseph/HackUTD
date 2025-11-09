# Quick Start Guide - Customer Profile FAB

## 🚀 Running the App

1. **Install dependencies** (if not already done):
   ```bash
   cd /Users/harsh/Documents/GitHub/HackUTD/tmobile
   npm install
   ```

2. **Start the app:**
   ```bash
   npm start
   # or
   ./start.sh
   ```

3. **Open on your device:**
   - Download Expo Go from App Store/Play Store
   - Scan the QR code
   - The app will load!

## 🎯 New Features

### Floating Action Button (FAB)
- **Look for:** A pink circular button in the bottom right corner
- **Icon:** Person/user icon
- **Position:** Above the bottom navigation, right side
- **Action:** Taps it to see the customer profile

### Customer Profile Page
- **Displays:** Complete customer information
- **Includes:** Account details, plan info, billing, loyalty points
- **Navigation:** Back arrow in top left returns to home

## 📝 Customer Data System

### Current Implementation: Random Customer Selection

The app now uses a customer data table (`customerData.js`) with 8 sample customers. Each time you open the profile page, it randomly selects one by ID.

**File: `customerData.js`**
- Contains 8 customers (IDs 1-8)
- Mix of Premium/Standard status
- Various plans and billing info

**File: `CustomerProfile.js` (lines 20-26)**

**Current Implementation:**
```javascript
useEffect(() => {
  setTimeout(() => {
    const randomCustomer = getRandomCustomer();
    setCustomerData(randomCustomer);
    setLoading(false);
  }, 300);
}, []);
```

### Integration Options

**Option 1: Fetch Specific Customer by ID**
```javascript
// In HomeScreen.js - pass detected customer ID
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
  }
  setLoading(false);
}, [route.params]);
```

**Option 2: Live API Integration**
```javascript
useEffect(() => {
  // Replace random selection with API call
  fetch('https://your-api.com/customer/current')
    .then(res => res.json())
    .then(data => {
      setCustomerData(data);
      setLoading(false);
    });
}, []);
```

**Option 3: WebSocket (Real-time)**
```javascript
useEffect(() => {
  const ws = new WebSocket('ws://your-server.com/customer-stream');
  ws.onmessage = (event) => {
    setCustomerData(JSON.parse(event.data));
    setLoading(false);
  };
  return () => ws.close();
}, []);
```

## 🎨 Customization

### Change FAB Position
Edit `HomeScreen.js` (line 338):
```javascript
fab: {
  position: 'absolute',
  right: 20,        // Change horizontal position
  bottom: 105,      // Change vertical position (raised to avoid nav bar)
  width: 60,        // Change size
  height: 60,
  borderRadius: 30,
  backgroundColor: '#E20074',  // Change color
  // ... rest of styles
}
```

### Change FAB Icon
Edit `HomeScreen.js` (line 97):
```javascript
<Ionicons name="person" size={28} color="#FFF" />
// Change to any icon from: https://icons.expo.fyi/Ionicons
```

### Add More Customer Fields
The profile now uses a compact grid layout. To add more fields, edit `CustomerProfile.js`:

**Add to existing grid:**
```javascript
<View style={styles.gridItem}>
  <Ionicons name="your-icon" size={18} color="#E20074" />
  <Text style={styles.gridLabel}>Your Label</Text>
  <Text style={styles.gridValue}>{customerData.yourField}</Text>
</View>
```

**Add to customer data table (`customerData.js`):**
```javascript
{
  id: 9,
  name: 'Your Customer',
  // ... add all required fields
  yourCustomField: 'value',
}
```

## 🔧 Troubleshooting

### FAB not appearing?
- Make sure you're on the Home screen (not Customer Profile)
- Check if it's hidden behind other elements
- Try adjusting the `bottom` value in the FAB styles

### Navigation not working?
- Ensure all navigation dependencies are installed
- Clear cache: `npx expo start --clear`
- Check for console errors in the Metro bundler

### Data not updating?
- Check your API endpoint is accessible
- Console.log the data to verify it's being received
- Ensure the data structure matches what the UI expects

## 📱 Visual Guide

```
┌─────────────────────────┐
│ Hey, Anne         🔔💬  │ ← Header
├─────────────────────────┤
│                         │
│  ┌───────────────────┐ │
│  │ Magenta Status    │ │
│  │ [Gradient Card]   │ │
│  └───────────────────┘ │
│                         │
│  ┌───────────────────┐ │
│  │ Redeem Offers     │ │
│  └───────────────────┘ │
│                         │
│                    ┌─┐ │ ← Floating Action
│                    │👤│ │   Button (FAB)
│                    └─┘ │
├─────────────────────────┤
│ 📊  📍  🛍️  👤      │ ← Bottom Nav
└─────────────────────────┘
```

## 📄 File Reference

- `App.js` - Navigation setup
- `HomeScreen.js` - Main screen + FAB (raised position)
- `CustomerProfile.js` - Profile page with compact layout
- `customerData.js` - **NEW:** Customer data table (8 customers)
- `package.json` - Dependencies

## 🎯 Next Steps

1. ✅ Test the FAB and navigation (FAB is now higher, no overlap)
2. ✅ Verify the profile page displays correctly (compact layout)
3. ✅ Test random customer selection (opens different customer each time)
4. 🔄 Replace random selection with your customer detection system
5. 🔄 Connect to live API/WebSocket for real-time data
6. 🔄 Add functionality to action buttons (Message, Call, Email)
7. 🔄 Style adjustments as needed

## 🎲 Testing Different Customers

The app includes 8 sample customers:
1. Sarah Johnson (Premium, Magenta MAX, 3 years)
2. Michael Chen (Standard, Magenta, 1 year)
3. Emily Rodriguez (Premium, Magenta MAX, 5 years)
4. David Thompson (Standard, Essentials, 6 months)
5. Jessica Williams (Premium, Magenta MAX, 2 years)
6. Robert Martinez (Standard, Magenta, 4 years)
7. Amanda Lee (Premium, Magenta MAX, 7 years)
8. Christopher Brown (Standard, Essentials, 1 year)

Each time you tap the FAB button, you'll see a different random customer!

Good luck with your integration! 🚀

