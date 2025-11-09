"""
Test customer profile extraction on existing conversation
"""
import os
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client
from sales_call_analyzer import SalesCallAnalyzer

# Load environment
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get credentials
api_key = os.getenv("GEMINI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase = create_client(supabase_url, supabase_key)

# Get existing conversation
print("📥 Fetching existing conversation from Supabase...")
result = supabase.table('conversations').select('*').eq('customer_id', 'Person_TEST123').execute()

if not result.data:
    print("❌ No conversation found for Person_TEST123")
    exit(1)

conversation = result.data[0]
print(f"✅ Found conversation (ID: {conversation['id']})")
print(f"   Duration: {conversation['duration_seconds']}s")
print(f"   Transcript length: {len(conversation['full_transcript'])} chars\n")

# Create analyzer instance
analyzer = SalesCallAnalyzer(
    gemini_api_key=api_key,
    supabase_url=supabase_url,
    supabase_key=supabase_key,
    customer_id='Person_TEST123'
)

# Extract profile
print("🧠 Extracting customer profile with Gemini...\n")
profile = analyzer.extract_customer_profile(conversation['full_transcript'])

print("="*70)
print("EXTRACTED PROFILE")
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

# Save to Supabase
print("\n💾 Saving customer profile to Supabase...")
analyzer.save_customer_profile(profile)

# Verify it was saved
print("\n🔍 Verifying saved profile...")
customer_result = supabase.table('customers').select('*').eq('customer_id', 'Person_TEST123').execute()

if customer_result.data:
    saved_profile = customer_result.data[0]
    print("✅ Profile saved successfully!")
    print(f"   Customer ID: {saved_profile['customer_id']}")
    print(f"   Name: {saved_profile.get('name') or 'Not set'}")
    print(f"   Personal: {len(saved_profile.get('personal_details', []))} items")
    print(f"   Professional: {len(saved_profile.get('professional_details', []))} items")
    print(f"   Sales Context: {len(saved_profile.get('sales_context', []))} items")
else:
    print("❌ Profile not found in database")
