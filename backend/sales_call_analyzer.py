"""
Complete Sales Call Analysis System
Combines voice transcription with Gemini API for real-time strategic insights.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from voice_transcription_local import LocalVoiceTranscriber
from google import genai
from datetime import datetime
import time
import threading
import pyttsx3
from supabase import create_client, Client
import json

# Try to import facial sentiment (optional)
try:
    from facial_sentiment_headless import HeadlessFacialSentiment
    FACIAL_AVAILABLE = True
except ImportError:
    FACIAL_AVAILABLE = False
    print("⚠️  Facial sentiment not available (install: pip install fer tensorflow keras)")

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class SalesCallAnalyzer:
    """
    Real-time sales call analyzer that provides strategic insights.
    """

    def __init__(self, gemini_api_key: str, model_size: str = "base",
                 camera_index: int = 0, enable_facial: bool = True,
                 supabase_url: str = None, supabase_key: str = None,
                 customer_id: str = None):
        """
        Initialize the sales call analyzer.

        Args:
            gemini_api_key: Your Google Gemini API key
            model_size: Whisper model size (tiny, base, small, medium, large)
            camera_index: Camera device index for facial analysis (default: 0)
            enable_facial: Enable facial sentiment analysis (default: True)
            supabase_url: Supabase project URL (optional)
            supabase_key: Supabase API key (optional)
            customer_id: Customer identifier from face recognition (optional)
        """
        # Set API key in environment for genai.Client()
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        self.client = genai.Client()

        # Initialize Supabase client (optional)
        self.supabase = None
        if supabase_url and supabase_key:
            try:
                self.supabase = create_client(supabase_url, supabase_key)
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"⚠️  Supabase initialization failed: {e}")
                self.supabase = None

        # Store customer ID for linking conversations
        self.customer_id = customer_id
        if customer_id:
            print(f"👤 Customer ID set: {customer_id}")

        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 175)  # Speed (default is 200)
        self.tts_engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Create transcriber
        self.transcriber = LocalVoiceTranscriber(
            on_transcript=self._handle_new_transcript,
            model_size=model_size
        )
        
        # Storage for analysis
        self.insights = []
        self.latest_recommendation = "No recommendation yet"
        
        # Initialize facial sentiment analyzer (optional)
        self.facial_analyzer = None
        self.facial_enabled = False
        
        if enable_facial and FACIAL_AVAILABLE:
            try:
                print("\n🎥 Initializing facial sentiment analysis...")
                self.facial_analyzer = HeadlessFacialSentiment(
                    camera_index=camera_index,
                    use_mtcnn=False,  # Use fast OpenCV detector
                    sample_interval=1.0  # Sample every 1 second
                )
                if self.facial_analyzer.start_capture():
                    self.facial_enabled = True
                    print("✅ Facial sentiment enabled")
                else:
                    print("⚠️  Facial sentiment disabled (camera error)")
                    self.facial_analyzer = None
            except Exception as e:
                print(f"⚠️  Facial sentiment disabled: {e}")
                self.facial_analyzer = None
        elif enable_facial and not FACIAL_AVAILABLE:
            print("⚠️  Facial sentiment disabled (libraries not installed)")
        
        # Start keyboard listener thread
        self.listening = True
        self.keyboard_thread = threading.Thread(target=self._listen_for_enter)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        
    def _handle_new_transcript(self, new_chunk: str, full_context: str):
        """
        Called every 10 seconds with new transcript.
        Sends to Gemini for analysis in a separate thread (non-blocking).
        """
        print("\n" + "="*70)
        print("📝 NEW TRANSCRIPT CHUNK")
        print("="*70)
        print(f"Latest 10s: {new_chunk}")
        print(f"\nFull conversation ({len(full_context)} chars): ")
        if len(full_context) > 200:
            print(f"   ...{full_context[-200:]}")
        else:
            print(f"   {full_context}")
        print("="*70)
        
        # Get strategic insights from Gemini IN PARALLEL (don't block recording)
        print("\n🤖 Analyzing with Gemini AI (in background)...")
        
        # Run Gemini analysis in separate thread so recording continues
        analysis_thread = threading.Thread(
            target=self._analyze_async,
            args=(new_chunk, full_context)
        )
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def _analyze_async(self, new_chunk: str, full_context: str):
        """
        Run Gemini analysis asynchronously so it doesn't block recording.
        """
        try:
            # Get facial emotion data if available
            emotion_data = None
            if self.facial_enabled and self.facial_analyzer:
                emotion_data = self.facial_analyzer.get_emotion_summary(duration_seconds=10)
            
            insights = self._get_sales_insights(full_context, emotion_data)
            
            # Store insights with emotion data
            self.insights.append({
                'timestamp': datetime.now(),
                'transcript': new_chunk,
                'full_context': full_context,
                'emotion_data': emotion_data,
                'insights': insights
            })
            
            # Display insights (compact)
            print("\n" + "⚡"*35)
            print(insights)
            print("⚡"*35 + "\n")
            
            # Speak the status report
            self._speak_insights(insights)
            
        except Exception as e:
            print(f"❌ Error getting insights: {e}")
    
    def _speak_insights(self, insights: str):
        """
        Convert insights to speech (TTS) - ONLY the status line.
        Also extracts and saves the recommendation.
        """
        try:
            # Extract status and recommendation
            lines = insights.strip().split('\n')
            
            status_text = ""
            for line in lines:
                if line.startswith('STATUS:'):
                    status = line.replace('STATUS:', '').strip()
                    status_text = status
                elif line.startswith('SAY THIS:'):
                    recommendation = line.replace('SAY THIS:', '').strip().strip('"')
                    self.latest_recommendation = recommendation
            
            if status_text:
                print(f"🔊 Speaking: {status_text}")
                self.tts_engine.say(status_text)
                self.tts_engine.runAndWait()
                
        except Exception as e:
            print(f"⚠️  TTS error: {e}")
    
    def _listen_for_enter(self):
        """
        Listen for Enter key press to speak the latest recommendation.
        """
        import sys
        while self.listening:
            try:
                # Wait for Enter key
                input()  # This blocks until Enter is pressed
                
                # Speak the latest recommendation
                if self.latest_recommendation and self.latest_recommendation != "No recommendation yet":
                    print(f"\n💬 Speaking recommendation: {self.latest_recommendation}\n")
                    self.tts_engine.say(self.latest_recommendation)
                    self.tts_engine.runAndWait()
                else:
                    print("\n⚠️  No recommendation available yet. Wait for first analysis.\n")
                    
            except:
                break
            
    def _get_sales_insights(self, transcript: str, emotion_data: dict = None) -> str:
        """
        Get strategic insights from Gemini based on transcript and facial emotions.
        
        Args:
            transcript: The complete conversation transcript (full history)
            emotion_data: Optional dict with facial emotion analysis
            
        Returns:
            Strategic insights and recommendations
        """
        # Build emotion context if available
        emotion_context = ""
        if emotion_data:
            dominant = emotion_data['dominant_emotion']
            confidence = emotion_data['confidence'] * 100
            trajectory = emotion_data['emotion_trajectory']
            
            # Format top 3 emotions
            breakdown = emotion_data['emotion_breakdown']
            top_emotions = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
            emotion_list = "\n".join([
                f"- {emotion.capitalize()}: {score*100:.0f}%" 
                for emotion, score in top_emotions
            ])
            
            emotion_context = f"""

CUSTOMER FACIAL EXPRESSIONS (last 10 seconds):
Dominant Emotion: {dominant.capitalize()} ({confidence:.0f}% confidence)
Emotion Trajectory: {trajectory.capitalize()}
Breakdown:
{emotion_list}
"""
        
        prompt = f"""You are a sales coach. Analyze this conversation{' and the customer\'s facial expressions' if emotion_data else ''} and give a quick status update.

CONVERSATION TRANSCRIPT:
{transcript}{emotion_context}

Respond in this EXACT format (keep it SHORT):

STATUS: [Pick ONE: Ready to Buy | Highly Interested | Engaged & Curious | Feeling Neutral | Showing Hesitation | Has Objections | Feeling Confused | Losing Interest | Not a Fit]

REASON: [One short sentence why{' - consider BOTH words AND facial expressions' if emotion_data else ''}]

SAY THIS: "[Exact phrase to say next - max 20 words]"

SCORE: [1-10]

Keep it brief and actionable."""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
        
    def start(self):
        """Start the sales call analysis."""
        print("\n" + "🚀"*35)
        print("SALES CALL ANALYZER STARTED")
        print("🚀"*35)
        print("\nListening to sales call...")
        print("⚡ Real-time transcription + AI insights every 10 seconds")
        print("📚 Maintains FULL conversation history for context")
        print("🔄 Parallel processing - NO GAPS in recording!")
        print("🔊 TTS enabled - Status reports spoken out loud!")
        if self.facial_enabled:
            print("🎥 Facial sentiment analysis ACTIVE")
        print("⌨️  Press ENTER anytime to hear latest recommendation!")
        print("Press Ctrl+C to stop\n")
        
        self.transcriber.start()
        
    def stop(self):
        """Stop the analysis."""
        self.listening = False
        self.transcriber.stop()

        # Stop facial capture if enabled
        if self.facial_analyzer:
            self.facial_analyzer.stop()

        # Save conversation to Supabase if available
        if self.supabase and len(self.insights) > 0:
            self.save_conversation_to_supabase()

        # Show summary
        print("\n" + "📊"*35)
        print("CALL SUMMARY")
        print("📊"*35)
        print(f"Total insights generated: {len(self.insights)}")
        print(f"Call duration: ~{len(self.insights) * 10} seconds")
        if self.facial_enabled:
            print(f"Facial analysis: Enabled")
        print("📊"*35 + "\n")
        
    def get_full_analysis(self) -> str:
        """
        Get a complete analysis of the entire call.
        """
        if not self.insights:
            return "No insights available yet."
            
        # Compile all transcripts
        full_transcript = " ".join([i['transcript'] for i in self.insights])
        
        # Get comprehensive analysis
        prompt = f"""You are an expert sales strategist. Provide a comprehensive POST-CALL analysis with SPECIFIC, ACTIONABLE recommendations.

FULL CALL TRANSCRIPT:
{full_transcript}

Provide a detailed report:

📞 EXECUTIVE SUMMARY
- Call duration and outcome
- Overall effectiveness (1-10)
- Key result: [Deal advanced / Stalled / Lost]

🎯 WHAT HAPPENED
- Main topics discussed
- Customer's stated needs
- Sales rep's approach

👤 CUSTOMER PROFILE
Pain Points Discovered:
- [Specific pain point 1 with $ impact if mentioned]
- [Specific pain point 2 with $ impact if mentioned]
- [Specific pain point 3 with $ impact if mentioned]

Authority Level: [Decision maker / Influencer / End user]
Budget Signals: [Specific mentions about budget/money]
Timeline: [When they need solution by]
Competition: [Other solutions mentioned]

📊 SENTIMENT ANALYSIS
Overall: [Very Positive / Positive / Neutral / Negative / Very Negative]
- Beginning: [How they started]
- Middle: [How engagement evolved]  
- End: [How they finished]
Engagement Level: [High / Medium / Low] - [Why]

✅ WHAT WENT WELL
- [Specific thing rep did well]
- [Specific technique that worked]
- [Specific moment that built trust]

❌ MISSED OPPORTUNITIES
- [Specific question that should have been asked]
- [Specific pain point that wasn't explored]
- [Specific objection that wasn't addressed]

💡 WHAT TO DO DIFFERENTLY NEXT TIME
- [Specific improvement 1]
- [Specific improvement 2]
- [Specific improvement 3]

📋 IMMEDIATE NEXT STEPS (Next 24 hours)
1. [Specific action with exact deliverable]
2. [Specific action with exact deliverable]
3. [Specific action with exact deliverable]

📅 FOLLOW-UP STRATEGY (This Week)
- [Specific action item 1]
- [Specific action item 2]
- [Specific action item 3]

🎯 DEAL ASSESSMENT
Probability to Close: [X%]
Reasoning:
- [Factor increasing probability]
- [Factor decreasing probability]

Biggest Risk: [Specific risk]
How to Mitigate: [Specific action]

Biggest Opportunity: [Specific opportunity]
How to Capitalize: [Specific action]

🔑 KEY TALKING POINTS FOR NEXT CALL
- [Specific point 1]
- [Specific point 2]
- [Specific point 3]

Be ULTRA-SPECIFIC. Use exact quotes from the call. Give concrete actions, not generic advice."""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    def extract_customer_profile(self, transcript: str) -> dict:
        """
        Extract structured customer profile from transcript using Gemini.

        Args:
            transcript: Full conversation transcript

        Returns:
            Dictionary with name, personal_details, professional_details, sales_context
        """
        try:
            prompt = f"""You are a customer intelligence analyst. Extract key information from this sales call transcript and structure it into a clean customer profile.

TRANSCRIPT:
{transcript}

Extract information and format as JSON with this EXACT structure:

{{
  "name": "Customer name if mentioned, or null",
  "personal_details": [
    "Single line bullet point about personal life",
    "Another personal detail"
  ],
  "professional_details": [
    "Single line bullet point about work/career",
    "Another professional detail"
  ],
  "sales_context": [
    "Current provider: [Provider name]",
    "Pain point: [Specific issue]",
    "Another sales-relevant detail"
  ]
}}

RULES:
1. Each bullet must be ONE LINE only - concise and specific
2. Only include information EXPLICITLY mentioned in the transcript
3. If a category has no information, use an empty array []
4. Be specific - include exact details (provider names, dollar amounts, features mentioned)
5. Focus on facts, not interpretations
6. Format sales_context bullets as "Topic: Detail" for easy scanning
7. Return ONLY valid JSON, no markdown formatting or explanation.

JSON OUTPUT:"""

            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )

            # Clean the response (remove markdown if present)
            response_text = response.text.strip()
            if response_text.startswith("```"):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
                response_text = response_text.replace("```json", "").replace("```", "").strip()

            profile = json.loads(response_text)
            return profile

        except Exception as e:
            print(f"❌ Error extracting customer profile: {e}")
            return {
                "name": None,
                "personal_details": [],
                "professional_details": [],
                "sales_context": []
            }

    def save_customer_profile(self, profile: dict):
        """
        Save or update customer profile in Supabase with merge logic.
        New information is appended and reordered by recency (newest first).

        Args:
            profile: Extracted profile dictionary
        """
        if not self.supabase or not self.customer_id:
            print("⚠️  Cannot save customer profile (missing Supabase or customer_id)")
            return

        try:
            # Check if customer already exists
            existing = self.supabase.table('customers').select('*').eq('customer_id', self.customer_id).execute()

            if existing.data and len(existing.data) > 0:
                # MERGE with existing profile
                existing_profile = existing.data[0]

                # Merge arrays: new items first (recency), then deduplicate
                def merge_bullets(new_bullets, old_bullets):
                    # Start with new bullets
                    merged = list(new_bullets)
                    # Add old bullets that aren't duplicates
                    for old_bullet in old_bullets:
                        if old_bullet not in merged:
                            merged.append(old_bullet)
                    return merged

                merged_profile = {
                    "customer_id": self.customer_id,
                    "name": profile.get('name') or existing_profile.get('name'),
                    "personal_details": merge_bullets(
                        profile.get('personal_details', []),
                        existing_profile.get('personal_details', [])
                    ),
                    "professional_details": merge_bullets(
                        profile.get('professional_details', []),
                        existing_profile.get('professional_details', [])
                    ),
                    "sales_context": merge_bullets(
                        profile.get('sales_context', []),
                        existing_profile.get('sales_context', [])
                    )
                }

                # Update existing record
                self.supabase.table('customers').update(merged_profile).eq('customer_id', self.customer_id).execute()
                print(f"✅ Customer profile updated (merged with existing data)")

            else:
                # CREATE new profile
                new_profile = {
                    "customer_id": self.customer_id,
                    "name": profile.get('name'),
                    "personal_details": profile.get('personal_details', []),
                    "professional_details": profile.get('professional_details', []),
                    "sales_context": profile.get('sales_context', [])
                }

                self.supabase.table('customers').insert(new_profile).execute()
                print(f"✅ New customer profile created")

        except Exception as e:
            print(f"❌ Error saving customer profile: {e}")

    def save_conversation_to_supabase(self):
        """
        Save the complete conversation transcript and insights to Supabase.
        Also extracts and saves/updates customer profile.
        """
        if not self.supabase:
            print("⚠️  Supabase not configured, skipping save")
            return

        try:
            # Compile full transcript
            full_transcript = " ".join([i['transcript'] for i in self.insights])

            # Prepare conversation data
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": len(self.insights) * 10,
                "full_transcript": full_transcript,
                "insights_count": len(self.insights),
                "facial_analysis_enabled": self.facial_enabled,
                "customer_id": self.customer_id,  # Link to face recognition
                "insights": [
                    {
                        "timestamp": insight['timestamp'].isoformat(),
                        "transcript": insight['transcript'],
                        "emotion_data": insight.get('emotion_data'),
                        "insights": insight['insights']
                    }
                    for insight in self.insights
                ]
            }

            # Insert into Supabase
            print("\n💾 Saving conversation to Supabase...")
            result = self.supabase.table('conversations').insert(conversation_data).execute()
            print(f"✅ Conversation saved to Supabase (ID: {result.data[0]['id']})")

            # Extract and save customer profile
            if self.customer_id:
                print("\n🧠 Extracting customer profile with Gemini...")
                profile = self.extract_customer_profile(full_transcript)

                if profile:
                    print(f"\n📋 Extracted Profile:")
                    print(f"   Name: {profile.get('name') or 'Not mentioned'}")
                    print(f"   Personal: {len(profile.get('personal_details', []))} details")
                    print(f"   Professional: {len(profile.get('professional_details', []))} details")
                    print(f"   Sales Context: {len(profile.get('sales_context', []))} details")

                    print("\n💾 Saving customer profile...")
                    self.save_customer_profile(profile)

        except Exception as e:
            print(f"❌ Error saving to Supabase: {e}")


def main():
    """
    Main function to run the sales call analyzer.
    """
    # Get API key from .env file or environment
    api_key = os.getenv("GEMINI_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not api_key:
        print("⚠️  GEMINI_API_KEY not found")
        print("\nTo set it up:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Create a .env file in the project root:")
        print("   cp env_template.txt .env")
        print("3. Edit .env and add your key:")
        print("   GEMINI_API_KEY=your-api-key-here")
        print("\nOr enter it now (or press Enter to skip Gemini integration):")
        api_key = input("API Key: ").strip()

        if not api_key:
            print("\n⚠️  Running in TRANSCRIPTION-ONLY mode (no AI insights)")
            print("Transcripts will be shown but not analyzed.\n")

            # Run without Gemini
            transcriber = LocalVoiceTranscriber(model_size="base")
            try:
                transcriber.start()
                print("🎤 Recording for 60 seconds...")
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n\nStopped by user")
            finally:
                transcriber.stop()
            return

    # Create analyzer with Gemini integration
    analyzer = SalesCallAnalyzer(
        gemini_api_key=api_key,
        model_size="base",  # Change to "tiny" for faster, "small" for more accurate
        camera_index=0,  # Change camera index if needed
        enable_facial=True,  # Set to False to disable facial sentiment
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    try:
        # Start analysis
        analyzer.start()
        
        # Run for 60 seconds (or until interrupted)
        print("📞 Simulating 60-second sales call...")
        print("   (In production, this would run for the entire call)\n")
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
        
    finally:
        # Stop recording
        analyzer.stop()
        
        # Just save the transcript and insights - NO post-call analysis
        if len(analyzer.insights) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"call_insights_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write("SALES CALL REAL-TIME INSIGHTS\n")
                f.write("="*70 + "\n\n")
                
                # Write each insight
                for i, insight in enumerate(analyzer.insights, 1):
                    f.write(f"CHUNK {i} - {insight['timestamp']}\n")
                    f.write("-"*70 + "\n")
                    f.write(f"Transcript: {insight['transcript']}\n\n")
                    
                    # Write emotion data if available
                    if insight.get('emotion_data'):
                        emotion = insight['emotion_data']
                        f.write(f"Facial Emotion: {emotion['dominant_emotion'].capitalize()} "
                               f"({emotion['confidence']*100:.0f}%)\n")
                        f.write(f"Trajectory: {emotion['emotion_trajectory'].capitalize()}\n\n")
                    
                    f.write(f"Insights:\n{insight['insights']}\n\n")
                    f.write("="*70 + "\n\n")
                
            print(f"\n💾 Call insights saved to: {filename}")


if __name__ == "__main__":
    main()

