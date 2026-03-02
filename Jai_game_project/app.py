import streamlit as st
import pandas as pd
import pulp
import base64
import requests
from Game_engiene import get_categories, get_teams_in_category, generate_match_data

# --- 1. UI HELPERS ---
def apply_custom_ui(image_file):
    try:
        with open(image_file, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <style>
                .stApp {{
                    background-image: url("data:image/jpg;base64,{data}");
                    background-size: cover;
                    background-attachment: fixed;
                }}
                .main .block-container {{
                    background-color: rgba(0, 0, 0, 0.7);
                    border-radius: 20px;
                    padding: 30px;
                    color: white !important;
                }}
                </style>
                """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Background image not found!")

# --- 2. THE FULLY DYNAMIC API FETCH ---
@st.cache_data(ttl=300) 
def fetch_live_fixtures():
    # This uses the key you saved in Streamlit Secrets
    url = "https://cricket-live-score-api1.p.rapidapi.com/matches"
    headers = {
        "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"], 
        "X-RapidAPI-Host": "cricket-live-score-api1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        live_list = []
        # We look for matches in the 'scorecard' or 'matches' list from your API
        match_data = data.get('scorecard', []) or data.get('matches', [])
        
        for match in match_data:
            t1 = match.get('team_a') or match.get('team_one') or "Team A"
            t2 = match.get('team_b') or match.get('team_two') or "Team B"
            status = match.get('status', 'UPCOMING').upper()
            
            live_list.append({
                "match": f"{t1} vs {t2}",
                "status": status,
                "time": match.get('start_time', 'Scheduled')
            })
        
        return live_list if live_list else [{"match": "No Matches Found", "status": "EMPTY", "time": ""}]
    except Exception:
        # Fallback to help you test if API is down
        return [{"match": "IND vs ENG", "status": "UPCOMING", "time": "Mar 5"}]

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="OptiXI: 2026 Strategy Solver", layout="wide")
apply_custom_ui("Jai_game_project/zoshua-colah-CYbiE2T6Xtc-unsplash.jpg")

# --- 4. SIDEBAR & STATE ---
st.sidebar.title("🎮 Match Setup")
cat_a = st.sidebar.selectbox("Category A", get_categories(), key="ca")
cat_b = st.sidebar.selectbox("Category B", get_categories(), key="cb")

if 'ta' not in st.session_state: st.session_state.ta = get_teams_in_category(cat_a)[0]
if 'tb' not in st.session_state: st.session_state.tb = get_teams_in_category(cat_b)[1]

# Dynamic Selectors linked to Session State
team_a = st.sidebar.selectbox("Team A", get_teams_in_category(cat_a), key="ta_select", 
                             index=get_teams_in_category(cat_a).index(st.session_state.ta) if st.session_state.ta in get_teams_in_category(cat_a) else 0)
team_b = st.sidebar.selectbox("Team B", get_teams_in_category(cat_b), key="tb_select", 
                             index=get_teams_in_category(cat_b).index(st.session_state.tb) if st.session_state.tb in get_teams_in_category(cat_b) else 1)

budget = st.sidebar.slider("Credit Limit", 80.0, 100.0, 100.0)

# --- 5. MAIN INTERFACE ---
st.title("🏆 OptiXI Live Strategy Solver")

# Live Match Ticker (Scrolling or Grid)
st.markdown("### 🏟️ Active & Upcoming Matches")
fixtures = fetch_live_fixtures()
# Use a container for scrolling if there are many matches
with st.container():
    f_cols = st.columns(min(len(fixtures), 4)) # Show up to 4 columns
    for i, f in enumerate(fixtures):
        with f_cols[i % 4]:
            label = "🔴 LIVE" if "LIVE" in f['status'] else "🗓️ UPCOMING"
            if st.button(f"{label}\n\n{f['match']}", key=f"fix_{i}", use_container_width=True):
                teams = f['match'].split(" vs ")
                if len(teams) == 2:
                    st.session_state.ta, st.session_state.tb = teams[0].strip(), teams[1].strip()
                    st.rerun()

st.divider()

# --- 6. SOLVER ENGINE ---
df = generate_match_data(cat_a, team_a, cat_b, team_b)

if st.button("⚡ GENERATE OPTIMAL XI", use_container_width=True):
    with st.spinner("Analyzing..."):
        try:
            prob = pulp.LpProblem("FantasyTeam", pulp.LpMaximize)
            players = df['Name'].tolist()
            rewards = dict(zip(players, df['Value_Index']))
            costs = dict(zip(players, df['Credit_Cost']))
            player_vars = pulp.LpVariable.dicts("Select", players, cat='Binary')

            prob += pulp.lpSum([rewards[i] * player_vars[i] for i in players])
            prob += pulp.lpSum([costs[i] * player_vars[i] for i in players]) <= budget
            prob += pulp.lpSum([player_vars[i] for i in players]) == 11

            prob.solve(pulp.PULP_CBC_CMD(msg=0))
            selected = [p for p in players if player_vars[p].value() == 1]
            best_team = df[df['Name'].isin(selected)]

            st.success(f"✅ AI Optimal Team Found! Cost: {best_team['Credit_Cost'].sum()}")
            st.table(best_team[['Name', 'Team', 'Role', 'Credit_Cost', 'Value_Index']])
            
            # WhatsApp Share
            share_text = f"Check out my Optimal XI for {team_a} vs {team_b}! 🏏\nView it here: https://optixi-solver.streamlit.app"
            encoded_text = share_text.replace("\n", "%0A").replace(" ", "%20")
            st.markdown(f'''<a href="https://wa.me/?text={encoded_text}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;padding:12px;border:none;border-radius:10px;cursor:pointer;font-weight:bold;">📲 Share on WhatsApp</button></a>''', unsafe_allow_html=True)
        except Exception:
            st.error("❌ Solver Error: Try increasing the budget.")

# --- 7. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("<div style='text-align: center; color: #888; font-size: 14px;'><p><b>OptiXI Strategy Solver v2.5</b></p><p>Advanced Mathematical Analysis | 2026 Season</p></div>", unsafe_allow_html=True)





