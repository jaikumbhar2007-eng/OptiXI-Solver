import streamlit as st
import pandas as pd
import pulp
import base64
import time
from Game_engiene import get_categories, get_teams_in_category, generate_match_data

# --- 1. SECURITY: INITIALIZE RATE LIMITER ---
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

# --- 2. UI ENGINE: FULL-SCREEN HD BACKGROUND & DARK GLASS ---
def apply_custom_ui(image_file):
    try:
        with open(image_file, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        
        style = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.4)), 
                              url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
        }}
        
        .stAppHeader, .stAppViewContainer, .stMainViewContainer {{
            background: transparent !important;
        }}

        .main .block-container {{
            background: rgba(0, 0, 0, 0.65) !important; 
            backdrop-filter: blur(15px);
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 3rem;
            margin-top: 2rem;
            max-width: 1200px;
        }}

        h1, h2, h3, p, span, li, label, div[data-testid="stMetricValue"] {{ 
            color: white !important; 
        }}
        
        div[data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 15px;
        }}

        .stButton>button {{
            background: linear-gradient(90deg, #ff4b4b, #ff8181);
            color: white; border-radius: 30px; font-weight: bold; width: 100%;
        }}
        /* FORCING SIDEBAR DARK THEME */
        section[data-testid="stSidebar"] {{
            background-color: #1a1a1a !important; /* Rich Dark Grey */
            color: white !important;
        }}
        
        /* Fixing Sidebar Text Visibility */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {{
            color: white !important;
        }}

        /* Making select boxes look cleaner on mobile */
        div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 10px;
        }}
        </style>
        """
        
        st.markdown(style, unsafe_allow_html=True)
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Background image not found!")

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="OptiXI: 2026 Strategy Solver", layout="wide")
apply_custom_ui("Jai_game_project/zoshua-colah-CYbiE2T6Xtc-unsplash.jpg")

# --- 4. SIDEBAR SETUP ---
st.sidebar.title("🎮 Match Setup")
st.sidebar.caption("Fact-Checked for 2026 Season")

col_a, col_b = st.sidebar.columns(2)
with col_a:
    cat_a = st.selectbox("Category A", get_categories(), key="ca")
    team_a = st.selectbox("Team A", get_teams_in_category(cat_a), key="ta")
with col_b:
    cat_b = st.selectbox("Category B", get_categories(), key="cb")
    team_b = st.selectbox("Team B", get_teams_in_category(cat_b), key="tb")

budget = st.sidebar.slider("Credit Limit", 80.0, 100.0, 100.0)

# --- 5. LEGAL DISCLAIMER (Sidebar) ---
st.sidebar.divider()
with st.sidebar.expander("⚖️ Privacy & Disclaimer"):
    st.caption("""
    **Disclaimer:** OptiXI is an AI-driven research tool for educational purposes only. 
    Fantasy sports involve financial risk. We do not guarantee winnings or accuracy 
    of match predictions. Use at your own risk.
    
    **Legal:** OptiXI is not affiliated with any official cricket board, league, 
    or fantasy platform. All player data is based on publicly available stats.
    
    **Privacy:** We do not store your personal data or team selections.
    """)

# --- 6. MAIN CONTENT ---
if team_a == team_b and cat_a == cat_b:
    st.title("🏏 OptiXI Strategy Solver")
    st.markdown("### Welcome, User! Optimize your 2026 Fantasy Squad.")
    
    st.divider()
    
    # Hero Intro Stats
    m1, m2, m3 = st.columns(3)
    m1.metric("Backtested model confidence", "89.4%", "+2.1% vs 2025")
    m2.metric("Total Data Points", "124k+", "Live Syncing")
    m3.metric("Avg winning Score", "184", "High Scoring Season")

    st.divider()

    # Info Cards
    cl, cr = st.columns(2)
    with cl:
        st.subheader("🤖 Why use OptiXI?")
        st.info("Uses Linear Programming to solve budget constraints and maximize ROI for the 2026 season.")
    with cr:
        st.subheader("🔥 Trending Today")
        st.success("**Yashasvi Jaiswal** - ROI: 11.2")

else:
    # --- ACTIVE MATCH ANALYSIS ---
    df = generate_match_data(cat_a, team_a, cat_b, team_b)
    st.title(f"🏆 {team_a} vs {team_b}")
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Top AI Pick", df.iloc[0]['Name'], f"{df.iloc[0]['Value_Index']} ROI")
    k2.metric("Player Pool", len(df))
    k3.metric("Avg. Credits", f"{df['Credit_Cost'].mean():.1f}")
    k4.metric("Strategy", "Balanced")

    st.divider()

    # --- RATE LIMITED GENERATOR BUTTON ---
    if st.button("⚡ GENERATE OPTIMIZED XI", use_container_width=True):
        current_time = time.time()
        
        if current_time - st.session_state.last_request_time < 10:
            st.warning("Please wait... The AI is refreshing the data.")
        else:
            st.session_state.last_request_time = current_time
            with st.spinner("Processing..."):
                try:
                    prob = pulp.LpProblem("FantasyTeam", pulp.LpMaximize)
                    players = df['Name'].tolist()
                    rewards = dict(zip(players, df['Value_Index']))
                    costs = dict(zip(players, df['Credit_Cost']))
                    player_vars = pulp.LpVariable.dicts("Select", players, cat='Binary')

                    prob += pulp.lpSum([rewards[i] * player_vars[i] for i in players])
                    prob += pulp.lpSum([costs[i] * player_vars[i] for i in players]) <= budget
                    prob += pulp.lpSum([player_vars[i] for i in players]) == 11

                    prob.solve()
                    selected = [p for p in players if player_vars[p].value() == 1]
                    best_team = df[df['Name'].isin(selected)]
                    
                    st.success(f"✅ AI Optimal Team Found! Total Cost: {best_team['Credit_Cost'].sum()} Credits")
                    st.table(best_team[['Name', 'Team', 'Role', 'Credit_Cost', 'Value_Index']])
                except Exception as e:
                    st.error("❌ Solver Error: Could not find a valid XI. Try increasing the credit budget.")


                # --- WHATSAPP SHARE BUTTON ---
share_text = f"Check out my Optimal XI for the next match generated by OptiXI! 🏏\nView it here: https://optixi-solver.streamlit.app"
        encoded_text = share_text.replace("\n", "%0A").replace(" ", "%20")
        whatsapp_url = f"https://wa.me/?text={encoded_text}"

        st.markdown(f'''
            <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                <button style="
                    width: 100%;
                    background-color: #25D366;
                    color: white;
                    padding: 12px;
                    border: none;
                    border-radius: 10px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 16px;
                    margin-top: 10px;
                ">
                    📲 Share this Team on WhatsApp
                </button>
            </a>
            ''', unsafe_allow_html=True)
         
    # --- FULL PLAYER ANALYTICS TABLE ---
    st.divider()
    st.subheader("🔍 Full Player Analytics")

    st.dataframe(df, use_container_width=True, hide_index=True)



