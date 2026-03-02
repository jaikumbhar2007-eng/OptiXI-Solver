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
                /* Force background image and dark overlay */
                .stApp {{
                    background-image: url("data:image/jpg;base64,{data}");
                    background-size: cover;
                    background-attachment: fixed;
                }}
                /* Glassmorphism: Fixes readability in Light/Dark browser themes */
                .main .block-container {{
                    background-color: rgba(0, 0, 0, 0.75);
                    border-radius: 20px;
                    padding: 30px;
                    color: white !important;
                }}
                [data-testid="stSidebar"] {{
                    background-color: rgba(0, 0, 0, 0.85) !important;
                }}
                /* Ensure all text stays white */
                h1, h2, h3, p, span, label {{
                    color: white !important;
                }}
                </style>
                """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Background image not found!")

# --- 2. DYNAMIC API FETCH (2026 Season) ---
@st.cache_data(ttl=300) 
def fetch_live_fixtures():
    # Uses the RAPIDAPI_KEY from your Streamlit Secrets
    url = "https://cricket-live-score-api1.p.rapidapi.com/matches"
    headers = {
        "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"], 
        "X-RapidAPI-Host": "cricket-live-score-api1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        live_list = []
        # Checks both potential keys in the API response for live/upcoming games
        raw_matches = data.get('matches', []) or data.get('scorecard', [])
        
        for m in raw_matches:
            t1 = m.get('team_a') or m.get('team_one') or "TBD"
            t2 = m.get('team_b') or m.get('team_two') or "TBD"
            status = m.get('status', 'Upcoming').upper()
            
            live_list.append({
                "match": f"{t1} vs {t2}",
                "status": status,
                "time": m.get('start_time', 'Scheduled')
            })
        
        # Fallback: If API returns empty, show the big IND vs ENG Semi-final
        if not live_list:
            return [{"match": "IND vs ENG", "status": "UPCOMING", "time": "Mar 5 (Semi-Final)"}]
            
        return live_list
    except Exception:
        # Emergency fallback for offline mode
        return [{"match": "IND vs ENG", "status": "UPCOMING", "time": "Mar 5"}]

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="OptiXI: 2026 Strategy Solver", layout="wide")
# Ensure the path matches your GitHub folder structure
apply_custom_ui("Jai_game_project/zoshua-colah-CYbiE2T6Xtc-unsplash.jpg")

# --- 4. SIDEBAR & SESSION STATE ---
st.sidebar.title("🎮 Match Setup")
cat_a = st.sidebar.selectbox("Category A", get_categories(), key="ca")
cat_b = st.sidebar.selectbox("Category B", get_categories(), key="cb")

# Manage dynamic selection via session state
if 'ta' not in st.session_state: st.session_state.ta = get_teams_in_category(cat_a)[0]
if 'tb' not in st.session_state: st.session_state.tb = get_teams_in_category(cat_b)[1]

team_a = st.sidebar.selectbox("Team A", get_teams_in_category(cat_a), key="ta_select", 
                             index=get_teams_in_category(cat_a).index(st.session_state.ta) if st.session_state.ta in get_teams_in_category(cat_a) else 0)
team_b = st.sidebar.selectbox("Team B", get_teams_in_category(cat_b), key="tb_select", 
                             index=get_teams_in_category(cat_b).index(st.session_state.tb) if st.session_state.tb in get_teams_in_category(cat_b) else 1)

budget = st.sidebar.slider("Credit Limit", 80.0, 100.0, 100.0)

# --- 5. MAIN INTERFACE ---
st.title("🏆 OptiXI Live Strategy Solver")

with st.expander("🔬 How it Works"):
    st.write("OptiXI uses **Linear Programming** to solve for the mathematically highest ROI squad.")

# Live Match Ticker (Automatic Updates)
st.markdown("### 🏟️ Active & Upcoming Matches")
fixtures = fetch_live_fixtures()
f_cols = st.columns(min(len(fixtures), 4)) 

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
    with st.spinner("Analyzing Match Data..."):
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

            st.success(f"✅ AI Found the Best Squad! Cost: {best_team['Credit_Cost'].sum()}")
            st.table(best_team[['Name', 'Team', 'Role', 'Credit_Cost', 'Value_Index']])
            
            # WhatsApp Share Button
            share_text = f"Check out my Optimal XI for {team_a} vs {team_b}! 🏏\nView it here: https://optixi-solver.streamlit.app"
            encoded_text = share_text.replace("\n", "%0A").replace(" ", "%20")
            st.markdown(f'''<a href="https://wa.me/?text={encoded_text}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;padding:12px;border:none;border-radius:10px;cursor:pointer;font-weight:bold;">📲 Share on WhatsApp</button></a>''', unsafe_allow_html=True)
        except Exception:
            st.error("❌ Solver Error: Try increasing the budget slider.")

# --- 7. PROFESSIONAL FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 14px;">
        <p><b>OptiXI Strategy Solver v2.5</b></p>
        <p>Advanced Mathematical Analysis | 2026 Season</p>
        <p style="font-style: italic;">Disclaimer: This is an analytical research tool. We do not promote gambling.</p>
    </div>
    """, 
    unsafe_allow_html=True
)




