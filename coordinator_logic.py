import pandas as pd

def check_assignment_conflicts(pilot, drone, mission):
    conflicts = []
    warnings = []

    # 1. Skill & Certification Mismatch
    required_skills = str(mission['required_skills']).split(', ')
    pilot_skills = str(pilot['skills']).split(', ')
    if not any(skill in pilot_skills for skill in required_skills):
        conflicts.append(f"❌ SKILL MISMATCH: {pilot['name']} lacks skills for {mission['project_id']}.")

    # 2. Weather Risk Alerts
    mission_weather = mission['weather_forecast']
    if mission_weather == "Rainy" and drone['weather_rating'] != "IP43":
        conflicts.append(f"⚠️ WEATHER RISK: Drone {drone['drone_id']} is not waterproof (IP43).")

    # 3. Budget Overrun Warnings
    duration = (pd.to_datetime(mission['end_date']) - pd.to_datetime(mission['start_date'])).days
    total_cost = duration * pilot['daily_rate_inr']
    if total_cost > mission['mission_budget']:
        warnings.append(f"💰 BUDGET ALERT: Project cost ({total_cost} INR) exceeds budget ({mission['mission_budget']} INR).")

    # 4. Location Mismatch
    if pilot['location'] != mission['location']:
        warnings.append(f"📍 LOGISTICS: Pilot is in {pilot['location']}, but mission is in {mission['location']}.")
    
    if drone['location'] != mission['location']:
        warnings.append(f"📍 LOGISTICS: Drone is in {drone['location']}, but mission is in {mission['location']}.")

    return conflicts, warnings

def handle_urgent_reassignment(mission, all_pilots):
    available = all_pilots[all_pilots['status'] == 'Available']
    local_pilots = available[available['location'] == mission['location']]
    
    if not local_pilots.empty:
        return local_pilots.iloc[0]
    return available.iloc[0] if not available.empty else None