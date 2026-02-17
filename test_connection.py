import gspread
from google.oauth2.service_account import Credentials

# Set up access
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
client = gspread.authorize(creds)

# Try to open your sheet
try:
    sheet = client.open("Drone_Operations").worksheet("pilot_roster")
    print("✅ Success! Connected to:", sheet.title)
    print("First Pilot:", sheet.cell(2, 2).value) # Should print 'Arjun'
except Exception as e:
    print("❌ Connection failed:", e)