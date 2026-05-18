import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
    "players.csv"
)
players = pd.read_csv(data_path)
st.sidebar.header("Dashboard Filters")
selected_year = st.sidebar.selectbox("Select Year", sorted(players["year"].unique()))
filtered_players = players[players["year"] == selected_year]


top_players = filtered_players.sort_values("ultimate_score", ascending=False).head(10)
st.subheader(f"Top 10 Players by K/D Ratio in {selected_year}")

fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.viridis(top_players["ultimate_score"] / top_players["ultimate_score"].max())

ax.barh(top_players["Player"], top_players["ultimate_score"], color=colors)

ax.invert_yaxis()

ax.set_xlabel("Ultimate Score")
ax.set_ylabel("Player")

st.pyplot(fig)

st.subheader("Player Archetypes")
fig, ax = plt.subplots(figsize=(10, 6))
samples = filtered_players.sample(min(2000, len(filtered_players)), random_state=42)

ax.scatter(samples["KD"], samples["entry impact"], alpha=0.4, c=samples["ultimate_score"], cmap="viridis")
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

selected_player = st.sidebar.selectbox("Select Player", sorted(filtered_players["Player"].unique()))
player_data = filtered_players[filtered_players["Player"] == selected_player].iloc[0]

st.subheader(f"{selected_player}'s Performance Overview")
col1, col2 , col3, col4 = st.columns(4)

col1.metric("KD", round(player_data["KD"].mean(), 2))
col2.metric("Impact", round(player_data['impact_score'].mean(), 2))
col3.metric("Entry Impact", round(player_data["entry impact"].mean(), 2))
col4.metric("Clutch %", round(player_data["Clutch Success %"].mean(), 2))

st.subheader("Consistency Map")
consistency = (filtered_players.groupby("Player")["KD"].agg(["mean", "std"]).reset_index())
fig, ax = plt.subplots(figsize=(10, 6))

sample = consistency.sample(min(1000, len(consistency)), random_state=42)
ax.scatter(sample["mean"], sample["std"], alpha=0.4, c=sample["mean"], cmap="viridis")

fig, ax = plt.subplots(figsize=(10, 6))

sample = consistency.sample(min(1000, len(consistency)), random_state=42)

ax.scatter(sample["mean"], sample["std"], alpha=0.5, c=sample["mean"], cmap="viridis")

ax.text(1.3, 0.05, "Elite Consistent")
ax.text(1.3, 0.25, "High Skill , Inconistent")
ax.text(0.6, 0.05, "Average but Stable")
ax.text(0.6, 0.25, "Struggling")    

ax.set_xlabel("Average KD")
ax.set_ylabel("KD variablility")

st.pyplot(fig)

#META Evolution
st.subheader("Meta Evolution")
agents_counts = (filtered_players["Agents"].value_counts().head(10))

fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.plasma(range(len(agents_counts)))

ax.bar(agents_counts.index, agents_counts.values, color = colors)
ax.invert_yaxis()
ax.set_xlabel("Pick Count")
st.pyplot(fig)

st.markdown("---")
st.caption("Built with Python, Pandas, Matplotlib & Streamlit")

#UI Styling

st.markdown("""
<style>
.big-font{
            font_size : 28px !important;
            font-weight: :700 
}
.metric-container {
            background-color: #111;
            padding : 10px;
            border-raidus : 10px;
}
</style>
            """, unsafe_allow_html=True)
            