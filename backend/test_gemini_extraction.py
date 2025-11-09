"""
Test script for Gemini customer profile extraction
"""
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from google import genai

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Sample transcript
transcript = """Hi, welcome to T-Mobile. My name is Alex. Are you browsing for our new phones? Or is there something specific I can help you with today? I'm just kind of looking, I guess I'm with... I'm getting pretty sick of it. I hear that Bill Shock is the worst. It's exactly like we're in the price lock guarantee. The price you sign up with on our eligible plans is the... price you keep. But before we get into that, what's the most frustrated you have thing you have with Verizon? Is it just the price or is it coverage, data speeds? What's the main pain point? It's mostly the price. I feel like I'm paying for all these extras. I don't know. Engaged and curious. My data gets super slow at the end of the month, which is annoying. I travel a bit for work and I can't even get a little bit of up. Engaged and curious. Like the hotspot reliably. Okay, so to recap, you need a bill that's predictable and transparent. You want an unlimited data that doesn't slow down just because you're using it. And you need to remember that all of us are working for work travel. Exactly."""

# Initialize Gemini
api_key = os.getenv("GEMINI_API_KEY")
os.environ["GEMINI_API_KEY"] = api_key
client = genai.Client()

# Extraction prompt
prompt = f"""You are a customer intelligence analyst. Extract key information from this sales call transcript and structure it into a clean customer profile.

TRANSCRIPT:
{transcript}

Extract information and format as JSON with this EXACT structure:

{{
  "name": "Customer name if mentioned, or null",
  "personal_details": [
    "Single line bullet point about personal life",
    "Another personal detail",
    ...
  ],
  "professional_details": [
    "Single line bullet point about work/career",
    "Another professional detail",
    ...
  ],
  "sales_context": [
    "Current provider: [Provider name]",
    "Current pain point: [Specific issue]",
    "Another sales-relevant detail",
    ...
  ]
}}

RULES:
1. Each bullet must be ONE LINE only - concise and specific
2. Only include information EXPLICITLY mentioned in the transcript
3. If a category has no information, use an empty array []
4. Be specific - include exact details (provider names, dollar amounts, features mentioned)
5. Focus on facts, not interpretations
6. Format sales_context bullets as "Topic: Detail" for easy scanning

Return ONLY valid JSON, no markdown formatting or explanation."""

print("🤖 Calling Gemini for customer profile extraction...\n")

response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt
)

print("✅ Extraction complete!\n")
print("="*70)
print("EXTRACTED CUSTOMER PROFILE:")
print("="*70)

# Parse and pretty print
try:
    # Clean the response text (remove markdown if present)
    response_text = response.text.strip()
    if response_text.startswith("```"):
        # Remove markdown code blocks
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
        response_text = response_text.replace("```json", "").replace("```", "").strip()

    profile = json.loads(response_text)
    print(json.dumps(profile, indent=2))

    print("\n" + "="*70)
    print("FORMATTED VIEW:")
    print("="*70)

    print(f"\n👤 NAME: {profile.get('name') or 'Not mentioned'}")

    print(f"\n🏠 PERSONAL DETAILS ({len(profile.get('personal_details', []))} items):")
    for detail in profile.get('personal_details', []):
        print(f"  • {detail}")
    if not profile.get('personal_details'):
        print("  (none mentioned)")

    print(f"\n💼 PROFESSIONAL DETAILS ({len(profile.get('professional_details', []))} items):")
    for detail in profile.get('professional_details', []):
        print(f"  • {detail}")
    if not profile.get('professional_details'):
        print("  (none mentioned)")

    print(f"\n📊 SALES CONTEXT ({len(profile.get('sales_context', []))} items):")
    for detail in profile.get('sales_context', []):
        print(f"  • {detail}")
    if not profile.get('sales_context'):
        print("  (none mentioned)")

    print("\n" + "="*70)
    print("✅ This format will be stored in Supabase customers table")
    print("="*70)

except json.JSONDecodeError as e:
    print(f"❌ Failed to parse JSON: {e}")
    print(f"\nRaw response:\n{response.text}")
