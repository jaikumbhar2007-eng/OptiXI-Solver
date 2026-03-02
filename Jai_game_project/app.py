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
                    background-color: rgba(0, 0, 0, 0.75);
                    border-radius: 20px;
                    padding: 30px;
                    color: white !important;
                }}
                [data-testid="stSidebar"] {{
                    background-color: rgba(0, 0, 0, 0.85) !important;
                }}
                h1, h2, h3, p, span, label {{ color: white !important; }}
                </style>
                """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Background image not found!")

# --- 2. DYNAMIC API FETCH ---
@st.cache_data(ttl=300) 
def fetch_live_fixtures():
    url = "https://cricket-live-score-api1.p.rapidapi.com/matches"
    headers = {
        "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"], 
        "X-RapidAPI-Host": "cricket-live-score-api1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        raw_matches = data.get('matches', []) or data.get('scorecard', [])
        live_list = []
        for m in raw_matches:
            t1, t2 = m.get('team_a', 'TBD'), m.get('team_b', 'TBD')
            live_list.append({"match": f"{t1} vs {t2}", "status": m.get('status', 'Upcoming').upper()})
        return live_list if live_list else [{"match": "IND vs ENG", "status": "UPCOMING"}]
    except Exception:
        return [{"match": "IND vs ENG", "status": "UPCOMING"}]

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="OptiXI: 2026 Strategy Solver", layout="wide")
apply_custom_ui("Jai_game_project/zoshua-colah-CYbiE2T6Xtc-unsplash.jpg")

# --- 4. SIDEBAR ---
st.sidebar.title("🎮 Match Setup")
cat_a = st.sidebar.selectbox("Category A", get_categories(), key="ca")
cat_b = st.sidebar.selectbox("Category B", get_categories(), key="cb")

if 'ta' not in st.session_state: st.session_state.ta = get_teams_in_category(cat_a)[0]
if 'tb' not in st.session_state: st.session_state.tb = get_teams_in_category(cat_b)[1]

team_a = st.sidebar.selectbox("Team A", get_teams_in_category(cat_a), key="ta_s", index=get_teams_in_category(cat_a).index(st.session_state.ta) if st.session_state.ta in get_teams_in_category(cat_a) else 0)
team_b = st.sidebar.selectbox("Team B", get_teams_in_category(cat_b), key="tb_s", index=get_teams_in_category(cat_b).index(st.session_state.tb) if st.session_state.tb in get_teams_in_category(cat_b) else 1)
budget = st.sidebar.slider("Credit Limit", 80.0, 100.0, 100.0)

# --- 5. MAIN INTERFACE ---
st.title("🏆 OptiXI Live Strategy Solver")

# Live Ticker
st.markdown("### 🏟️ Active & Upcoming Matches")
fixtures = fetch_live_fixtures()
f_cols = st.columns(min(len(fixtures), 4))
for i, f in enumerate(fixtures):
    with f_cols[i % 4]:
        label = "🔴 LIVE" if "LIVE" in f['status'] else "🗓️ UPCOMING"
        if st.button(f"{label}\n\n{f['match']}", key=f"fix_{i}", use_container_width=True):
            teams = f['match'].split(" vs ")
            st.session_state.ta, st.session_state.tb = teams[0].strip(), teams[1].strip()
            st.rerun()

st.divider()

# --- 6. PLAYER DATA TABLE (The "Missing" Part) ---
df = generate_match_data(cat_a, team_a, cat_b, team_b)

st.subheader(f"📊 Player Pool: {team_a} vs {team_b}")
# Show key metrics before solving
m1, m2, m3 = st.columns(3)
m1.metric("Available Players", len(df))
m2.metric("Highest ROI", df.iloc[0]['Name'] if not df.empty else "N/A")
m3.metric("Avg Credits", f"{df['Credit_Cost'].mean():.1f}" if not df.empty else "0")

# The Full Data Table
st.dataframe(df[['Name', 'Team', 'Role', 'Credit_Cost', 'Value_Index']], use_container_width=True)

# --- 7. SOLVER ---
if st.button("⚡ GENERATE OPTIMAL XI", use_container_width=True):
    with st.spinner("Calculating Optimal Squad..."):
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

            st.success(f"✅ AI Found the Best Squad! Total Cost: {best_team['Credit_Cost'].sum()}")
            st.table(best_team[['Name', 'Team', 'Role', 'Credit_Cost', 'Value_Index']])
            
            # WhatsApp Share
            share_text = f"My Optimal XI for {team_a} vs {team_b}! 🏏\nView: https://optixi-solver.streamlit.app"
            st.markdown(f'''<a href="https://wa.me/?text={share_text.replace(' ', '%20')}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;padding:12px;border:none;border-radius:10px;font-weight:bold;">📲 Share on WhatsApp</button></a>''', unsafe_allow_html=True)
        except Exception:
            st.error("❌ Solver Error: Increase budget.")

# --- 8. FOOTER ---
st.markdown("<br><hr><center><b>OptiXI v2.5</b> | Advanced Analysis | 2026 Season</center>", unsafe_allow_html=True)





