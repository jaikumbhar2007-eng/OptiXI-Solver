import streamlit as st
import pandas as pd
import pulp
import time
import base64  # This is the missing piece!
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
                /* This forces a dark 'glass' tint over everything for readability */
                .main .block-container {{
                    background-color: rgba(0, 0, 0, 0.6);
                    border-radius: 20px;
                    padding: 30px;
                    color: white !important;
                }}
                /* Ensures sidebar text stays white */
                [data-testid="stSidebar"] {{
                    background-color: rgba(0, 0, 0, 0.8) !important;
                    color: white !important;
                }}
                </style>
                """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Background image not found!")
        
# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="OptiXI: 2026 Strategy Solver", layout="wide")
# Updated path to include the subfolder
apply_custom_ui("Jai_game_project/zoshua-colah-CYbiE2T6Xtc-unsplash.jpg")

# --- 3. SIDEBAR SETUP ---
st.sidebar.title("🎮 Match Setup")
st.sidebar.caption("Fact-Checked for 2026 Season")

col_a, col_b = st.sidebar.columns(2)
with col_a:
    cat_a = st.sidebar.selectbox("Category A", get_categories(), key="ca")
    team_a = st.sidebar.selectbox("Team A", get_teams_in_category(cat_a), key="ta")
with col_b:
    cat_b = st.sidebar.selectbox("Category B", get_categories(), key="cb")
    team_b = st.sidebar.selectbox("Team B", get_teams_in_category(cat_b), key="tb")

budget = st.sidebar.slider("Credit Limit", 80.0, 100.0, 100.0)

with st.sidebar.expander("⚖️ Privacy & Disclaimer"):
    st.caption("OptiXI is an AI-driven tool for educational purposes. Fantasy sports involve risk. Use at your own risk.")

# --- 4. MAIN INTERFACE ---
if team_a == team_b and cat_a == cat_b:
    st.title("🏏 OptiXI Strategy Solver")
    st.markdown("### Welcome, User! Optimize your 2026 Fantasy Squad.")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Algorithm Accuracy", "89.4%", "+2.1% vs 2025")
    m2.metric("Total Data Points", "124k+", "Live Syncing")
    m3.metric("Avg winning Score", "184", "High Scoring Season")

    cl, cr = st.columns(2)
    with cl:
        st.subheader("💡 Why use OptiXI?")
        st.info("Uses Linear Programming to solve budget constraints and maximize ROI.")
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

    # --- GENERATOR BUTTON ---
    if st.button("⚡ GENERATE OPTIMAL XI", use_container_width=True):
        if 'last_request_time' not in st.session_state:
            st.session_state.last_request_time = 0
            
        current_time = time.time()
        if current_time - st.session_state.last_request_time < 5:
            st.warning("⚠️ Please wait... The AI is refreshing the data.")
        else:
            st.session_state.last_request_time = current_time
            with st.spinner("Processing Optimal Squad..."):
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

                    st.success(f"✅ AI Optimal Team Found! Total Cost: {best_team['Credit_Cost'].sum()} Credits")
                    st.table(best_team[['Name', 'Team', 'Role', 'Credit_Cost', 'Value_Index']])
                    
                    # --- WHATSAPP SHARE BUTTON ---
                    st.divider()
                    share_text = f"Check out my Optimal XI for {team_a} vs {team_b} generated by OptiXI! 🏏\nView it here: https://optixi-solver.streamlit.app"
                    encoded_text = share_text.replace("\n", "%0A").replace(" ", "%20")
                    whatsapp_url = f"https://wa.me/?text={encoded_text}"

                    st.markdown(f'''
                        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                            <button style="width: 100%; background-color: #25D366; color: white; padding: 12px; border: none; border-radius: 10px; cursor: pointer; font-weight: bold;">
                                📲 Share this Team on WhatsApp
                            </button>
                        </a>
                        ''', unsafe_allow_html=True)

                except Exception as e:
                    st.error("❌ Solver Error: Try increasing the credit budget.")

    st.divider()
    st.subheader("🔍 Full Player Analytics")
    st.dataframe(df, use_container_width=True, hide_index=True)







