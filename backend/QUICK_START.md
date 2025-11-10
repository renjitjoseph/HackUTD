# Quick Start Guide - Sales Call System

## Running the System (Single Terminal)

### Step 1: Start Everything
```bash
cd backend
python launch_system.py
```

### Step 2: What You'll See

**Your terminal will show:**
```
======================================================================
🚀 UNIFIED SALES CALL SYSTEM LAUNCHER
======================================================================

This will start:
  1. Face Recognition System (main.py)
     → Detects & locks customer faces
     → Updates active_session table in Supabase

  2. Sales Call Analyzer (sales_call_analyzer.py)
     → Reads customer_id from active_session
     → Transcribes call & provides AI insights
     → Saves conversation & customer profile

🔄 The systems communicate via Supabase active_session table

Press Ctrl+C to stop both processes
======================================================================

🎥 Starting Face Recognition System (main.py)...
    This will take over the terminal for keyboard input.
    Face Recognition will run in the background.

📞 Starting Sales Call Analyzer (sales_call_analyzer.py)...

✅ Both systems started successfully!

======================================================================
SYSTEM STATUS:
  ✅ Face Recognition: RUNNING
  ✅ Sales Analyzer: RUNNING
======================================================================

⌨️  HOW TO END CALL:
  • Type 'q' + ENTER in THIS terminal
    → This ends call gracefully and saves customer profile
  • To force stop everything: Press Ctrl+C

💡 TIP: Face Recognition runs in background with camera window
💡 TIP: Customer must be locked for 2+ seconds to save profile
💡 TIP: You can type 'q' anytime to end the call

📞 Sales Call Analyzer is now active...
    (You should see its output above)
    Type 'q' + ENTER when ready to end the call

🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
SALES CALL ANALYZER STARTED
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

Listening to sales call...
⚡ Real-time transcription + AI insights every 10 seconds
📚 Maintains FULL conversation history for context
🔄 Parallel processing - NO GAPS in recording!
🔊 TTS enabled - Status reports spoken out loud!
👁️  Face detection managed by main.py
🔄 Syncing customer_id from active_session table

⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️
KEYBOARD CONTROLS:
  • Press ENTER → Hear latest recommendation
  • Type 'q' + ENTER → End call gracefully
⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️⌨️
```

**Separate window will open:**
- OpenCV camera window showing Face Recognition
- Green box around detected face
- Customer ID displayed above face

### Step 3: During the Call

**Watch for these messages in the terminal:**

```
👤 Customer detected by main.py: Person_ABC123
```
✅ This means face is detected and customer_id is synced!

```
📝 NEW TRANSCRIPT CHUNK
Latest 10s: [Your speech here]
```
✅ Transcription is working!

```
⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
📊 GEMINI INSIGHTS:
STATUS: Engaged & Curious
REASON: Customer asking questions about features
SAY THIS: "Let me show you how this solves that exact problem..."
SCORE: 7
⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡
```
✅ AI insights are being generated!

### Step 4: End the Call

**In the SAME terminal, type:**
```
q
```
**Press ENTER**

**You'll see:**
```
🛑 'q' pressed - Ending call gracefully...

✅ Customer detected during call: Person_ABC123
💾 Saving conversation for customer: Person_ABC123
🧠 Extracting customer profile with Gemini...
📋 Extracted Profile:
   Name: John Smith
   Personal: 2 details
   Professional: 3 details
   Sales Context: 4 details
💾 Saving customer profile...
✅ Customer profile updated (merged with existing data)

✅ Sales Analyzer stopped
🛑 Stopping Face Recognition...
✅ Face Recognition stopped

======================================================================
✅ ALL SYSTEMS STOPPED
======================================================================
```

## Troubleshooting

### Problem: No customer_id syncing
**Look for:** `👤 Customer detected by main.py: Person_ABC123`

**If missing:**
1. Check if Face Recognition camera window is open
2. Make sure your face is visible to camera
3. Wait 2 seconds for face to be "locked"
4. Check Supabase connection

### Problem: Profile not saving
**Look for:** `🧠 Extracting customer profile with Gemini...`

**If missing:**
1. Make sure you pressed 'q' (not Ctrl+C)
2. Check that customer_id was detected (see above)
3. Verify Gemini API key is set in .env
4. Check Supabase credentials

### Problem: Can't type in terminal
**Solution:** 
- The sales_call_analyzer should control the terminal automatically
- If it's frozen, press Ctrl+C and restart

## Visual Flow

```
┌─────────────────────────────────────────────┐
│         ONE TERMINAL WINDOW                 │
│                                             │
│  launch_system.py (launcher)                │
│      ↓                                      │
│  main.py (background) + camera window       │
│      ↓                                      │
│  sales_call_analyzer.py (foreground)        │
│      ↓                                      │
│  [You type 'q' here]                        │
│      ↓                                      │
│  Profile extracted & saved ✅                │
└─────────────────────────────────────────────┘
```

## Key Points

✅ **Everything happens in ONE terminal**
✅ **Type 'q' + ENTER in that terminal to end call**
✅ **Face Recognition camera window opens separately**
✅ **Customer must be locked for 2+ seconds**
✅ **Profile is automatically extracted when you press 'q'**

## Alternative: Run in Separate Terminals

If you prefer more control:

**Terminal 1:**
```bash
cd backend
python main.py
```

**Terminal 2:**
```bash
cd backend
python sales_call_analyzer.py
```

Then press **'q' + ENTER** in Terminal 2 to end the call.

