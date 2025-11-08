from calendar_service import CalendarService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Environment variables:")
print(f"GOOGLE_CLIENT_ID: {os.getenv('GOOGLE_CLIENT_ID')}")
print(f"GOOGLE_CLIENT_SECRET: {os.getenv('GOOGLE_CLIENT_SECRET') and '***'}")
print(f"GOOGLE_REDIRECT_URI: {os.getenv('GOOGLE_REDIRECT_URI')}")

# Initialize calendar service
service = CalendarService()

# Try to get authorization URL
try:
    auth_url = service.oauth_flow
    print("\nOAuth Flow configuration:")
    print(f"Client config: {service.client_config}")
except Exception as e:
    print(f"\nError: {str(e)}")