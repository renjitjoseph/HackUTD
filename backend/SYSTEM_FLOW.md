# Sales Call System - Data Flow

## Overview
This system uses **two separate processes** that communicate via Supabase:

1. **main.py** - Face Recognition System
2. **sales_call_analyzer.py** - Sales Call Analyzer

## How They Connect

```
┌─────────────────────┐
│     main.py         │
│  Face Recognition   │
└──────────┬──────────┘
           │
           │ 1. Detects face
           │ 2. Locks customer (2s stable)
           │ 3. Writes to Supabase
           ↓
    ┌─────────────────────────┐
    │   Supabase Database     │
    │   active_session table  │
    │                         │
    │   current_customer_id   │
    └──────────┬──────────────┘
               ↑
               │ Polls every 2s
               │
   ┌───────────┴──────────────┐
   │  sales_call_analyzer.py  │
   │   Sales Call Analysis    │
   └──────────┬───────────────┘
              │
              │ On call end:
              │ 1. Calls Gemini to extract profile
              │ 2. Separates personal/professional/sales
              │ 3. Saves to customers table
              ↓
       ┌─────────────────┐
       │  Supabase DB    │
       │  customers      │
       └─────────────────┘
```

## Key Points

### Face Detection (main.py)
- Detects faces using OpenCV + DeepFace
- Requires **2 seconds of stable detection** to lock a customer
- Updates `active_session.current_customer_id` in Supabase
- Customer stays locked even if they move out of frame (10s timeout)

### Sales Call Analysis (sales_call_analyzer.py)
- Polls `active_session` table **every 2 seconds**
- Syncs `customer_id` from main.py
- Transcribes audio + provides AI insights
- **On call end:** If `customer_id` exists, calls Gemini to extract profile

### Profile Extraction (Gemini Prompt)
Located in `sales_call_analyzer.py` → `extract_customer_profile()` (line 893)

**Prompt separates information into:**
- `name` - Customer name if mentioned
- `personal_details[]` - Personal life details
- `professional_details[]` - Work/career details  
- `sales_context[]` - Current provider, pain points, sales info

**Then saves to `customers` table via:**
- `save_customer_profile()` (line 963)
- Merges with existing profile if customer already exists
- New info appears first (sorted by recency)

## Why Wasn't It Saving Before?

**Problem:** The two systems were running independently but NOT communicating.

- `main.py` detected the face ✅
- But `sales_call_analyzer.py` never knew about it ❌
- When call ended, `customer_id` was `None` ❌
- Line 1074 check failed: `if self.customer_id:` ❌
- Profile extraction was skipped entirely ❌

**Solution:** sales_call_analyzer.py now polls Supabase to get the customer_id from main.py.

## How to Run

```bash
cd backend
python launch_system.py
```

Or run individually:
```bash
# Terminal 1
cd backend
python main.py

# Terminal 2
cd backend
python sales_call_analyzer.py
```

## How to End a Call

### Option 1: Graceful End (Recommended) ✅
In the **Sales Analyzer terminal**, type:
```
q
```
Then press **ENTER**.

This will:
- ✅ Stop the call recording cleanly
- ✅ Trigger the `stop()` method
- ✅ Extract customer profile with Gemini
- ✅ Save everything to Supabase

### Option 2: Force Stop ⚠️
Press **Ctrl+C** (in launch_system or sales_call_analyzer terminal).

⚠️ **Warning:** This may not always trigger profile extraction cleanly. Use 'q' instead!

## Keyboard Controls

While the call is active in **sales_call_analyzer.py**:

| Key | Action |
|-----|--------|
| **ENTER** | Speak the latest recommendation out loud |
| **q + ENTER** | End call gracefully and save customer profile |

## Debug Tips

### Check if customer_id is syncing:
Look for this in sales_call_analyzer output:
```
👤 Customer detected by main.py: Person_ABC123
```

### Check if profile is being saved:
After pressing **'q' + ENTER** to end the call, you should see:
```
🛑 'q' pressed - Ending call gracefully...

✅ Customer detected during call: Person_ABC123
💾 Saving conversation for customer: Person_ABC123
🧠 Extracting customer profile with Gemini...
📋 Extracted Profile:
   Name: John Doe
   Personal: 2 details
   Professional: 3 details
   Sales Context: 4 details
💾 Saving customer profile...
✅ Customer profile updated
```

### If you see this warning:
```
⚠️  WARNING: No customer_id detected during this call!
   Make sure main.py is running and has locked a customer.
```

**Causes:**
1. main.py is not running
2. No face was detected/locked for 2+ seconds
3. Supabase connection issue

## Database Schema

### active_session table
```sql
- id (int)
- status ('active' | 'idle')
- current_customer_id (text) -- Written by main.py, read by sales_call_analyzer
- confidence_level ('detecting' | 'stable')
```

### customers table
```sql
- customer_id (text, primary key)
- name (text)
- personal_details (text[])
- professional_details (text[])
- sales_context (text[])
```

### conversations table
```sql
- id (auto)
- customer_id (text, foreign key)
- timestamp (timestamp)
- full_transcript (text)
- insights (jsonb)
```

