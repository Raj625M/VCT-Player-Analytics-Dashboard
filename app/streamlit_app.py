import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

def get_archetype(row):

    if (
        row["entry_impact"] > 0.7 and
        row["kd"] > 1.2
    ):
        return "Aggressive Duelist"

    elif (
        row["clutch_success_percent"] > 20
    ):
        return "Clutch Anchor"

    elif (
    row["impact_score"] > 1.8 and
    row["assists_per_round"] > 0.35
):
        return "Support Initiator"

    elif (
    row["kd"] > 1.25 and
    row["kills_per_round"] > 0.9
):
        return "Entry Fragger"

    else:
        return "Balanced Flex"
    

st.set_page_config(page_title="VCT Analytics Dashboard", layout = "wide")
st.title("VCT Player Analytics Dashboard")
st.write("Analyze Player Performance, Conistency, and Meta Evolution from VCT 2021 - 2026")

import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "processed",
    "final_players1.csv"
)
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:rawzu625@localhost:5432/VCT_Analytics"
)
players = pd.read_sql(
    "SELECT * FROM players_stats",
    engine
)
players["archetype"] = players.apply(
    get_archetype,
    axis=1
)
selected_year = st.sidebar.selectbox(
    "Select Year",
    sorted(players["year"].unique())
)
filtered_players = players[
    players["year"] == selected_year
]
query = f"""
SELECT player, ultimate_score
FROM players_stats
WHERE year = '{selected_year}'
"""

top_players = pd.read_sql(query, engine)

# Convert to numeric
top_players["ultimate_score"] = pd.to_numeric(
    top_players["ultimate_score"],
    errors="coerce"
)

# Remove nulls
top_players = top_players.dropna(
    subset=["ultimate_score"]
)

# Sort properly
top_players = top_players.sort_values(
    "ultimate_score",
    ascending=False
).head(10)

print(top_players.head())

st.subheader(
    f"Top 10 Players by Ultimate Score in {selected_year}"
)
top_players = top_players.dropna(subset=["player"])
top_players["player"] = top_players["player"].astype(str)
fig, ax = plt.subplots(figsize=(10, 6))

colors = plt.cm.viridis(
    top_players["ultimate_score"] /
    top_players["ultimate_score"].max()
)

ax.barh(
    top_players["player"],
    top_players["ultimate_score"],
    color=colors
)

ax.invert_yaxis()

ax.set_xlabel("Ultimate Score")
ax.set_ylabel("Player")

st.pyplot(fig)
st.markdown("---")

st.subheader("Player Archetypes")
fig, ax = plt.subplots(figsize=(10, 6))
samples = filtered_players.sample(min(2000, len(filtered_players)), random_state=42)

ax.scatter(samples["kd"], samples["entry_impact"], alpha=0.4, c=samples["ultimate_score"], cmap="viridis")
#reference lines    
ax.axvline(1, color="red", linestyle="--", label="K/D = 1", alpha=0.5)
ax.axhline(0.1, color="blue", linestyle="--", label="Entry Impact = 0.1", alpha=0.5)

#labels 
ax.text(1.8, 0.18, "Aggressive Stars", fontsize=12, color="darkred")
ax.text(0.5, 0.18, "Risk Entries", fontsize=12, color="darkblue")
ax.text(1.8, -0.18, "Safe Players", fontsize=12, color="darkgreen")
ax.text(0.5, -0.18, "Struggling Players", fontsize=12, color="darkorange")

ax.set_xlabel("K/D Ratio")
ax.set_ylabel("Entry Impact")

st.pyplot(fig)
st.markdown("---")

st.subheader("Consistency Map")
query = f"""
SELECT
    player,
    AVG(kd) as mean_kd,
    STDDEV(kd) as std_kd
FROM players_stats
WHERE year = '{selected_year}'
GROUP BY player
"""

consistency = pd.read_sql(query, engine)
# consistency = (filtered_players.groupby("Player")["KD"].agg(["mean", "std"]).reset_index())
fig, ax = plt.subplots(figsize=(10, 6))

sample = consistency.sample(min(1000, len(consistency)), random_state=42)
ax.scatter(sample["mean_kd"], sample["std_kd"], alpha=0.4, c=sample["mean_kd"], cmap="viridis")

fig, ax = plt.subplots(figsize=(10, 6))

sample = consistency.sample(min(1000, len(consistency)), random_state=42)

ax.scatter(sample["mean_kd"], sample["std_kd"], alpha=0.5, c=sample["mean_kd"], cmap="viridis")

ax.text(1.3, 0.05, "Elite Consistent")
ax.text(1.3, 0.25, "High Skill , Inconistent")
ax.text(0.6, 0.05, "Average but Stable")
ax.text(0.6, 0.25, "Struggling")    

ax.set_xlabel("Average KD")
ax.set_ylabel("KD variablility")

st.pyplot(fig)
st.markdown("---")

#META Evolution
st.subheader("Meta Evolution")
query = f"""
SELECT agents, COUNT(*) as pick_count
FROM players_stats
WHERE year = '{selected_year}'
GROUP BY agents
ORDER BY pick_count DESC
LIMIT 10
"""

agents_counts = pd.read_sql(query, engine)
# agents_counts = (filtered_players["Agents"].value_counts().head(10))

fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.plasma(range(len(agents_counts)))
ax.bar(
    agents_counts["agents"],
    agents_counts["pick_count"]
)
#ax.bar(agents_counts.index, agents_counts.values, color = colors)
ax.set_xlabel("Agents")
ax.set_ylabel("Pick Count")
st.pyplot(fig)
st.markdown("---")

players_in_year = sorted(
    filtered_players["player"]
    .dropna()
    .unique()
)

# Initialize session state
if "selected_player" not in st.session_state:
    st.session_state.selected_player = players_in_year[0]

# If current selected player does not exist in this year
if st.session_state.selected_player not in players_in_year:
    st.session_state.selected_player = players_in_year[0]

selected_player = st.selectbox(
    "Select Player",
    players_in_year,
    key="selected_player"
)

player_data = filtered_players[
    filtered_players["player"] == selected_player
].iloc[0]

st.subheader(f"{selected_player}'s Performance Overview")
col1, col2 , col3, col4 = st.columns(4)

col1.metric("KD", round(player_data["kd"].mean(), 2))
col2.metric("Impact", round(player_data['impact_score'].mean(), 2))
col3.metric("Entry Impact", round(player_data["entry_impact"].mean(), 2))
col4.metric("Clutch %", round(player_data["clutch_success_percent"].mean(), 2))
st.markdown("---")

selected_player_archetype = player_data["archetype"]

st.subheader(f"{selected_player}'s Archetype")

st.metric(
    "Primary Role",
    selected_player_archetype
)
archetype_counts = (
    filtered_players["archetype"]
    .value_counts()
)

fig = px.pie(
    values=archetype_counts.values,
    names=archetype_counts.index,
    title=f"{selected_year} Archetype Distribution"
)

st.plotly_chart(fig)
st.markdown("---")

st.subheader("Player Career Progression")
trend_player = st.selectbox(
    "Select Player for Trend Analysis",
    sorted(players["player"].dropna().unique())
)
metric_options = {
    "KD": "kd",
    "Impact Score": "impact_score",
    "Entry Impact": "entry_impact",
    "Clutch %": "clutch_success_percent",
    "Ultimate Score": "ultimate_score"
}
selected_metric_label = st.selectbox(
    "Select Metric",
    list(metric_options.keys())
)

trend_metric = metric_options[selected_metric_label]
query = f"""
SELECT
    year,
    AVG({trend_metric}) as metric_value
FROM players_stats
WHERE player = '{trend_player}'
GROUP BY year
ORDER BY year
"""
trend_df = pd.read_sql(query, engine)
trend_df["metric_value"] = pd.to_numeric(
    trend_df["metric_value"],
    errors="coerce"
)

fig = px.line(
    trend_df,
    x="year",
    y="metric_value",
    markers=True,
    title=f"{trend_player} - {trend_metric} Progression"
)

fig.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="white")
)

st.plotly_chart(
    fig,
    use_container_width=True
)
st.markdown("---")

st.subheader("Player Comparison")
players_list = sorted(
    players["player"]
    .dropna()
    .unique()
)
# Initialize session state
if "player1" not in st.session_state:
    st.session_state.player1 = players_list[0]

if "player2" not in st.session_state:
    st.session_state.player2 = players_list[1]

player1 = st.selectbox(
    "Select Player 1",
    players_list,
    key="player1"
)

player2 = st.selectbox(
    "Select Player 2",
    players_list,
    key="player2"
)
p1_check = filtered_players[
    filtered_players["player"] == player1
]

p2_check = filtered_players[
    filtered_players["player"] == player2
]
if p1_check.empty:
    st.warning(
        f"{player1} did not play in {selected_year}"
    )

if p2_check.empty:
    st.warning(
        f"{player2} did not play in {selected_year}"
    )
if p1_check.empty or p2_check.empty:
    st.stop()
if player1 == player2:
    st.warning(
        "Select two different players for comparison."
    )
    st.stop()

p1 = filtered_players[
    filtered_players["player"] == player1
]

p2 = filtered_players[
    filtered_players["player"] == player2
]

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"### {player1}")
    st.metric("KD", round(p1["kd"].iloc[0], 2))
    st.metric("Impact", round(p1['impact_score'].iloc[0], 2))
    st.metric("Entry Impact", round(p1["entry_impact"].iloc[0], 2))
    st.metric("Clutch %", round(p1["clutch_success_percent"].iloc[0], 2))
with col2:
    st.markdown(f"### {player2}")
    st.metric("KD", round(p2["kd"].iloc[0], 2))
    st.metric("Impact", round(p2['impact_score'].iloc[0], 2))
    st.metric("Entry Impact", round(p2["entry_impact"].iloc[0], 2))
    st.metric("Clutch %", round(p2["clutch_success_percent"].iloc[0], 2))   
st.markdown("---")
st.subheader("Player Radar Comparison")
radar_metrics = ["kd", "impact_score", "entry_impact", "clutch_success_percent", "ultimate_score"]
p1_values = []
p2_values = []

for metric in radar_metrics:

    # global min/max from all players
    min_val = players[metric].min()
    max_val = players[metric].max()

    # player values
    p1_val = float(p1[metric].iloc[0])
    p2_val = float(p2[metric].iloc[0])

    # normalize 0 → 1
    p1_norm = (p1_val - min_val) / (max_val - min_val)
    p2_norm = (p2_val - min_val) / (max_val - min_val)

    p1_values.append(p1_norm)
    p2_values.append(p2_norm)
fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=p1_values,
    theta=radar_metrics,
    fillcolor="rgba(0,229,255,0.08)",
    name=player1,
    line = dict(color = "#00E5FF", width = 3)))

fig.add_trace(go.Scatterpolar(
    r=p2_values,
    theta=radar_metrics,
    fillcolor="rgba(255,75,75,0.08)",
    name=player2, 
    line = dict(color = "#FF4081", width = 3)))

fig.update_layout(polar = dict(
    radialaxis = dict(
        visible = True)),
        showlegend = True,
        title = "Player Performance Radar"
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("---")

st.caption("Built with Python, Pandas, Matplotlib, PostgreSQL & Streamlit")

#UI Styling

st.markdown("""
<style>
.big-font{
            font_size : 28px !important;
            font-weight: 700 
}
.metric-container {
            background-color: #111;
            padding : 10px;
            border-radius : 10px;
}
</style>
            """, unsafe_allow_html=True)
            
