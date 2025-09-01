from supabase import create_client
import datetime

SUPABASE_URL = "https://rdvwutmjprwxsmqojyfr.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJkdnd1dG1qcHJ3eHNtcW9qeWZyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU3NzgxMzgsImV4cCI6MjA3MTM1NDEzOH0.cKao31BA_cch-fMQMFe7smyrwIkZ4WES8HkCREixPnc"

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

data = {
    "name": "Test User",
    "email": "testuser@example.com",
    "subject": "Test Subject",
    "message": "This is a test message.",
    # "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()  # Optional
}

try:
    response = supabase.table("contact_messages").insert(data).execute()
    # Instead of response.error, check status_code or print full response
    if hasattr(response, "status_code") and response.status_code >= 400:
        print(f"Insert failed with status code: {response.status_code}")
        print(f"Response content: {response.data}")
    else:
        print(f"Insert succeeded: {response.data}")
except Exception as e:
    print(f"Exception during insert: {e}")
