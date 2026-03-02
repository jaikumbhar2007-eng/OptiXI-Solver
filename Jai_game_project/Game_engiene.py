import pandas as pd
import random

# --- THE ACCURATE 2026 SQUAD DATABASE ---
# --- THE ULTIMATE 2026 EXPANDED DATABASE ---
TEAMS_DB = {
    "International": {
        "India": [
            {"Name": "Suryakumar Yadav", "Role": "Bat"}, {"Name": "Yashasvi Jaiswal", "Role": "Bat"},
            {"Name": "Shubman Gill", "Role": "Bat"}, {"Name": "Rishabh Pant", "Role": "WK"},
            {"Name": "Hardik Pandya", "Role": "All-Rounder"}, {"Name": "Jasprit Bumrah", "Role": "Bowl"},
            {"Name": "Arshdeep Singh", "Role": "Bowl"}, {"Name": "Axar Patel", "Role": "All-Rounder"}
        ],
        "Australia": [
            {"Name": "Travis Head", "Role": "Bat"}, {"Name": "Mitchell Marsh", "Role": "All-Rounder"},
            {"Name": "Josh Inglis", "Role": "WK"}, {"Name": "Glenn Maxwell", "Role": "All-Rounder"},
            {"Name": "Pat Cummins", "Role": "Bowl"}, {"Name": "Adam Zampa", "Role": "Bowl"}
        ],
        "South Africa": [
            {"Name": "Quinton de Kock", "Role": "WK"}, {"Name": "Heinrich Klaasen", "Role": "Bat"},
            {"Name": "David Miller", "Role": "Bat"}, {"Name": "Marco Jansen", "Role": "All-Rounder"},
            {"Name": "Kagiso Rabada", "Role": "Bowl"}, {"Name": "Anrich Nortje", "Role": "Bowl"}
        ],
        "England": [
            {"Name": "Jos Buttler", "Role": "WK"}, {"Name": "Phil Salt", "Role": "Bat"},
            {"Name": "Liam Livingstone", "Role": "All-Rounder"}, {"Name": "Sam Curran", "Role": "All-Rounder"},
            {"Name": "Jofra Archer", "Role": "Bowl"}, {"Name": "Adil Rashid", "Role": "Bowl"}
        ]
    },
    "IPL": {
        "CSK": [
            {"Name": "Ruturaj Gaikwad", "Role": "Bat"}, {"Name": "MS Dhoni", "Role": "WK"},
            {"Name": "Ravindra Jadeja", "Role": "All-Rounder"}, {"Name": "Matheesha Pathirana", "Role": "Bowl"}
        ],
        "MI": [
            {"Name": "Hardik Pandya", "Role": "All-Rounder"}, {"Name": "Rohit Sharma", "Role": "Bat"},
            {"Name": "Suryakumar Yadav", "Role": "Bat"}, {"Name": "Jasprit Bumrah", "Role": "Bowl"}
        ],
        "RCB": [
            {"Name": "Virat Kohli", "Role": "Bat"}, {"Name": "Rajat Patidar", "Role": "Bat"},
            {"Name": "Mohammed Siraj", "Role": "Bowl"}, {"Name": "Cameron Green", "Role": "All-Rounder"}
        ],
        "GT": [
            {"Name": "Shubman Gill", "Role": "Bat"}, {"Name": "Rashid Khan", "Role": "Bowl"},
            {"Name": "Sai Sudharsan", "Role": "Bat"}, {"Name": "Rahul Tewatia", "Role": "All-Rounder"}
        ],
        "LSG": [
            {"Name": "KL Rahul", "Role": "WK"}, {"Name": "Nicholas Pooran", "Role": "Bat"},
            {"Name": "Ravi Bishnoi", "Role": "Bowl"}, {"Name": "Marcus Stoinis", "Role": "All-Rounder"}
        ],
        "SRH": [
            {"Name": "Pat Cummins", "Role": "Bowl"}, {"Name": "Abhishek Sharma", "Role": "Bat"},
            {"Name": "Travis Head", "Role": "Bat"}, {"Name": "Heinrich Klaasen", "Role": "WK"}
        ],
        "KKR": [
            {"Name": "Shreyas Iyer", "Role": "Bat"}, {"Name": "Sunil Narine", "Role": "All-Rounder"},
            {"Name": "Andre Russell", "Role": "All-Rounder"}, {"Name": "Rinku Singh", "Role": "Finisher"}
        ],
        "DC": [
            {"Name": "Rishabh Pant", "Role": "WK"}, {"Name": "Kuldeep Yadav", "Role": "Bowl"},
            {"Name": "Jake Fraser-McGurk", "Role": "Bat"}, {"Name": "Axar Patel", "Role": "All-Rounder"}
        ]
    }
}
def get_categories():
    return list(TEAMS_DB.keys())

def get_teams_in_category(category):
    return list(TEAMS_DB[category].keys())

def generate_match_data(cat1, team1, cat2, team2):
    squad1 = TEAMS_DB[cat1][team1]
    squad2 = TEAMS_DB[cat2][team2]
    
    combined = []
    for team_name, squad in [(team1, squad1), (team2, squad2)]:
        for p in squad:
            # Add dynamic credit costs and form
            combined.append({
                "Name": p["Name"],
                "Team": team_name,
                "Role": p["Role"],
                "Credit_Cost": random.choice([8.5, 9.0, 9.5, 10.0, 10.5]),
                "Recent_Form": random.randint(45, 95) # Higher base form for 2026 stars
            })
    
    df = pd.DataFrame(combined)
    df['Value_Index'] = (df['Recent_Form'] / df['Credit_Cost']).round(2)
    return df.sort_values(by='Value_Index', ascending=False)