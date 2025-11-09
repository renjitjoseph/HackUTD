# T-Mobile Life App Clone

A React Native Expo app that replicates the T-Mobile Life app interface.

## Features

- **Home Screen:**
  - Header with personalized greeting "Hey, Anne"
  - Magenta Status card with gradient banner and decorative circles
  - Redeem your offers section with T-Mobile card and add button
  - Bottom navigation bar (Status, Connect, Shop, Manage)
  - **Floating Action Button (FAB)** in bottom right for quick customer profile access

- **Customer Profile Page:**
  - Customer information display with avatar
  - Account details (account number, phone, member duration)
  - Plan details (Magenta MAX, billing, data usage, device)
  - Billing information (last payment, next bill date)
  - Loyalty rewards points
  - Quick action buttons (Message, Call, Email)
  - Beautiful T-Mobile branded interface

## Quick Start

**Option 1: Use the start script**
```bash
./start.sh
```

**Option 2: Manual start**
```bash
npm start
# or to clear cache
npx expo start --clear
```

## Setup

1. **Install dependencies** (only needed once):
```bash
npm install
```

2. **Start the development server:**
```bash
npm start
```

3. **Run on your device:**
   - **Mobile (Recommended):** Download Expo Go from App Store/Play Store, then scan the QR code
   - **iOS Simulator:** Press `i` in the terminal
   - **Android Emulator:** Press `a` in the terminal  
   - **Web Browser:** Press `w` in the terminal

## Technologies Used

- React Native 0.72.6
- Expo SDK 49
- React Navigation 6 (Native Stack Navigator)
- expo-linear-gradient for the magenta gradient banner
- @expo/vector-icons (Ionicons & MaterialCommunityIcons)
- expo-font for icon rendering
- react-native-safe-area-context for proper spacing
- react-native-screens for native navigation performance

## Design Features

The app replicates the T-Mobile Life interface with:
- Clean white cards with subtle shadows
- T-Mobile's signature magenta gradient (#E20074, #D4006E)
- Modern spacing and typography
- Icon-based navigation
- Responsive layout
- Floating Action Button (FAB) for customer profile access
- Smooth screen transitions with React Navigation
- Professional customer profile view with organized sections

## Architecture

### Navigation Structure
```
App (NavigationContainer)
├── Home Screen
│   ├── Header
│   ├── Magenta Status Card
│   ├── Offers Section
│   ├── Bottom Navigation
│   └── FAB (navigates to Customer Profile)
└── Customer Profile Screen
    ├── Header with back button
    ├── Customer avatar and status
    ├── Account information card
    ├── Plan details card
    ├── Billing information card
    ├── Loyalty rewards card
    └── Action buttons
```

### Customer Profile Data
The customer profile currently displays mock data. You can integrate live data by:
1. Creating an API endpoint or WebSocket connection
2. Updating the `customerData` object in `CustomerProfile.js`
3. Using React state management (Context, Redux, etc.) to pass data between screens

Example integration point in `CustomerProfile.js`:
```javascript
// Replace this mock data with your live data source
const customerData = {
  name: 'Sarah Johnson',
  accountNumber: '****7829',
  // ... etc
};
```

