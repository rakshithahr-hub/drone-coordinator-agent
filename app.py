import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from coordinator_logic import check_assignment_conflicts, handle_urgent_reassignment

# --- STEP 1: DATABASE CONNECTION ---
def get_gsheet_client():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
    return gspread.authorize(creds)

client = get_gsheet_client()
spreadsheet = client.open("Drone_Operations")

def load_data(sheet_name):
    worksheet = spreadsheet.worksheet(sheet_name)
    return pd.DataFrame(worksheet.get_all_records())

# --- STEP 2: UI CONFIGURATION ---
st.set_page_config(page_title="Skylark Drone Ops AI", layout="wide")
st.title("🚁 Drone Operations Coordinator AI")

if 'pilots' not in st.session_state:
    st.session_state.pilots = load_data("pilot_roster")
    st.session_state.drones = load_data("drone_fleet")
    st.session_state.missions = load_data("missions")

# --- STEP 3: SIDEBAR - ROSTER MANAGEMENT ---
st.sidebar.header("📋 Quick Management")
with st.sidebar.expander("Update Pilot Status"):
    p_names = st.session_state.pilots['name'].tolist()
    selected_p = st.selectbox("Select Pilot", p_names)
    new_status = st.selectbox("New Status", ["Available", "On Leave", "Assigned", "Unavailable"])
    
    if st.button("Sync to Google Sheets"):
        sheet = spreadsheet.worksheet("pilot_roster")
        cell = sheet.find(selected_p)
        # Updating Column 6 (Status)
        sheet.update_cell(cell.row, 6, new_status)
        st.success(f"Updated {selected_p} status!")
        st.session_state.pilots = load_data("pilot_roster")

# --- STEP 4: CHAT INTERFACE & COORDINATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I can help you with drone missions. Ask me about 'conflicts' or 'urgent' reassignments."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ex: Check conflicts for assigning Arjun"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = ""
    
    if "urgent" in prompt.lower():
        mission = st.session_state.missions.iloc[0] 
        best_pilot = handle_urgent_reassignment(mission, st.session_state.pilots)
        if best_pilot is not None:
            response = f"🚨 **Urgent Reassignment:** Based on mission location ({mission['location']}), I recommend **{best_pilot['name']}**."
        else:
            response = "No available pilots found for urgent reassignment."
    
    elif "conflict" in prompt.lower() or "assign" in prompt.lower():
        # Using index 0 (Arjun) as an example for the demo
        pilot = st.session_state.pilots.iloc[0] 
        drone = st.session_state.drones.iloc[0]
        mission = st.session_state.missions.iloc[0]
        
        conflicts, warnings = check_assignment_conflicts(pilot, drone, mission)
        
        if not conflicts and not warnings:
            response = "✅ No conflicts detected for this assignment."
        else:
            response = "### ⚠️ Coordinator Alerts:\n" + "\n".join(conflicts + warnings)
    else:
        response = "Try asking about 'conflicts' or 'urgent' reassignments."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)