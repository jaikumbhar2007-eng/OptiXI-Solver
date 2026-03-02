import pandas as pd
import random

# 1. DATABASE OF ALL 2026 CATEGORIES AND TEAMS
teams_database = {
    "International": [
        "India", "Australia", "England", "South Africa", 
        "New Zealand", "Pakistan", "West Indies", 
        "Sri Lanka", "Afghanistan", "Bangladesh"
    ],
    "IPL": [
        "MI", "CSK", "RCB", "GT", "LSG", 
        "RR", "DC", "PBKS", "KKR", "SRH"
    ]
}

# 2. HELPER FUNCTIONS FOR THE UI
def get_categories():
    """Returns the list of available tournament categories."""
    return list(teams_database.keys())

def get_teams_in_category(category):
    """Returns the list of teams belonging to a specific category."""
    return teams_database.get(category, [])

# 3. DYNAMIC MATCH DATA GENERATOR
def generate_match_data(cat_a, team_a, cat_b, team_b):
    """
    Generates a simulated 30-player pool (15 per team) 
    with realistic Data Science metrics for the solver.
    """
    players = []
    roles = ["Batter", "Bowler", "All-Rounder", "WK"]
    
    # Generate 15 players for Team A
    for i in range(1, 16):
        players.append({
            "Name": f"{team_a}_Player_{i}",
            "Team": team_a,
            "Role": random.choice(roles),
            "Credit_Cost": round(random.uniform(8.0, 10.5), 1),
            "Value_Index": round(random.uniform(25, 98), 2)  # High Value = AI Priority
        })
        
    # Generate 15 players for Team B
    for i in range(1, 16):
        players.append({
            "Name": f"{team_b}_Player_{i}",
            "Team": team_b,
            "Role": random.choice(roles),
            "Credit_Cost": round(random.uniform(8.0, 10.5), 1),
            "Value_Index": round(random.uniform(25, 98), 2)
        })
        
    # Return as a DataFrame for the Streamlit UI and PuLP Solver
    df = pd.DataFrame(players)
    
    # Sort by Value_Index so the 'Top AI Pick' metric shows the best player first
    return df.sort_values(by="Value_Index", ascending=False).reset_index(drop=True)
