# Navigation Guide

## Bottom Navigation Tabs

The T-Mobile app now has fully functional bottom navigation with the following tabs:

### 1. **Status Tab** (Home Screen)
- **Icon:** Ticket/Status icon (filled when active)
- **Color:** Magenta (#E20074) when active
- **Functionality:** Takes you to the main home screen
- **Features:**
  - Magenta Status card
  - Redeem your offers section
  - AI Recommendation card (when available)
  - FAB button for customer profile access

### 2. **Connect Tab** (Connect Screen)
- **Icon:** Location icon (filled when active)
- **Color:** Magenta (#E20074) when active
- **Functionality:** Identical page to Home screen
- **Features:**
  - Same layout and functionality as Home screen
  - All the same cards and components
  - Independent FAB button for customer profile
  - Independent AI recommendations

### 3. **Shop Tab**
- **Icon:** Shopping bag icon
- **Status:** Not yet implemented (placeholder)

### 4. **Manage Tab**
- **Icon:** Person icon
- **Status:** Not yet implemented (placeholder)

## Navigation Flow

```
┌─────────────────────────────────────┐
│         Home Screen (Status)        │
│  - Magenta Status card              │
│  - Offers section                   │
│  - AI Recommendations               │
│  - FAB → Customer Profile           │
└─────────────────────────────────────┘
            ↕ (Connect tab)
┌─────────────────────────────────────┐
│      Connect Screen (Connect)       │
│  - Identical to Home Screen         │
│  - Same features and layout         │
│  - FAB → Customer Profile           │
└─────────────────────────────────────┘
            ↓ (FAB button)
┌─────────────────────────────────────┐
│       Customer Profile Page         │
│  - Customer details                 │
│  - Account & Plan info              │
│  - Personal/Professional details    │
│  - Sales context                    │
│  - Back button → Previous screen    │
└─────────────────────────────────────┘
```

## Active Tab Indicators

- **Active tab** displays filled icon in magenta color (#E20074)
- **Inactive tabs** display outline icon in gray color (#666)
- **Active tab text** is magenta, inactive text is gray

### Home Screen
- Status tab: **Active** (magenta, filled icon)
- Connect tab: Inactive (gray, outline icon)

### Connect Screen
- Status tab: Inactive (gray, outline icon)
- Connect tab: **Active** (magenta, filled icon)

## File Structure

```
tmobile/
├── App.js                # Navigation container with 3 screens
├── HomeScreen.js         # Main home screen (Status tab)
├── ConnectScreen.js      # Connect page (identical to home)
└── CustomerProfile.js    # Customer profile detail page
```

## Implementation Details

### App.js Navigation Stack
```javascript
<Stack.Navigator>
  <Stack.Screen name="Home" component={HomeScreen} />
  <Stack.Screen name="Connect" component={ConnectScreen} />
  <Stack.Screen name="CustomerProfile" component={CustomerProfile} />
</Stack.Navigator>
```

### Bottom Navigation Buttons

**HomeScreen.js:**
- Status → Stays on Home (highlighted)
- Connect → Navigates to Connect screen
- Shop → Not yet implemented
- Manage → Not yet implemented

**ConnectScreen.js:**
- Status → Navigates back to Home screen
- Connect → Stays on Connect (highlighted)
- Shop → Not yet implemented
- Manage → Not yet implemented

## Supabase Integration

Both HomeScreen and ConnectScreen:
- Poll `active_session` table every 2 seconds
- Display AI recommendations when available
- Show/hide FAB based on session status
- Pass customer ID to profile page when available

## Future Enhancements

1. **Shop Tab:** Add shopping/products page
2. **Manage Tab:** Add account management page
3. **Tab Badge:** Show notification counts
4. **Smooth Transitions:** Add custom animations
5. **Shared State:** Use Context API to share session data between screens
6. **Persistent Bottom Nav:** Make bottom nav always visible across all screens

## Testing

1. Launch the app
2. Notice "Status" tab is highlighted (magenta)
3. Tap "Connect" tab → navigates to Connect screen
4. Notice "Connect" tab is now highlighted
5. Tap "Status" tab → navigates back to Home
6. Both screens have identical functionality
7. FAB button works on both screens
8. AI recommendations appear on both screens independently

