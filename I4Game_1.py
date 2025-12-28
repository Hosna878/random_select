import streamlit as st
import json
import random
import os
import time

# -----------------------
# Files
# -----------------------
FARSI_FILE = "farsi_words.json"
EN_FILE = "english_words.json"

# -----------------------
# Points
# -----------------------
POINTS = {"simple": 1, "medium": 2, "hard": 3}

# -----------------------
# Defaults (short for clarity)
# -----------------------
default_farsi = {
    "simple": {"words": ["آب","نان","گل"], "sentences": ["من خوشحالم"]},
    "medium": {"words": ["دوچرخه","ماشین"], "sentences": ["دیروز به مهمانی رفتم"]},
    "hard": {"words": ["آزادی","فلسفه"], "sentences": ["تفکر انتقادی مهم است"]}
}

default_english = {
    "simple": {"words": ["water","house"], "sentences": ["I am happy"]},
    "medium": {"words": ["bicycle","market"], "sentences": ["Yesterday I went out"]},
    "hard": {"words": ["freedom","identity"], "sentences": ["Life needs patience"]}
}

# -----------------------
# Load
# -----------------------
def load_data(path, defaults):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(defaults,f,ensure_ascii=False,indent=4)
    return defaults.copy()

# -----------------------
# Session State Init
# -----------------------
if "groups" not in st.session_state:
    st.session_state.groups = []
    st.session_state.scores = {}
    st.session_state.turn = 0
    st.session_state.current_item = None
    st.session_state.start_time = None

if "farsi" not in st.session_state:
    st.session_state.farsi = load_data(FARSI_FILE, default_farsi)

if "english" not in st.session_state:
    st.session_state.english = load_data(EN_FILE, default_english)

# -----------------------
# Setup
# -----------------------
st.set_page_config("Group Word Game", layout="wide")
st.title("🎲 Group Guessing Game")

# -----------------------
# Game Setup
# -----------------------
st.sidebar.header("⚙️ Game Setup")

lang = st.sidebar.radio("Language:", ["Farsi","English"])
data = st.session_state.farsi if lang=="Farsi" else st.session_state.english

num_groups = st.sidebar.number_input("How many groups?", 2, 10, 2)
round_time = st.sidebar.slider("Time per turn (seconds)", 10, 120, 30)

if st.sidebar.button("🎮 Start Game"):
    st.session_state.groups = [f"Group {i+1}" for i in range(num_groups)]
    st.session_state.scores = {g: 0 for g in st.session_state.groups}
    st.session_state.turn = 0
    st.session_state.current_item = None
    st.session_state.start_time = time.time()
    st.rerun()

# -----------------------
# Game Running
# -----------------------
if st.session_state.groups:

    current_group = st.session_state.groups[st.session_state.turn % len(st.session_state.groups)]

    st.markdown(f"""
    <div style="text-align:center;font-size:26px;
    background:#222;color:#00ffcc;padding:12px;border-radius:12px;">
    🎯 Turn: {current_group}
    </div>
    """, unsafe_allow_html=True)

    # Scores
    cols = st.columns(len(st.session_state.groups))
    for i,g in enumerate(st.session_state.groups):
        cols[i].metric(g, st.session_state.scores[g])

    st.markdown("---")

    # Selection
    level = st.radio("Difficulty:", ["simple","medium","hard"], horizontal=True)
    item_type = st.radio("Type:", ["words","sentences","letter","number","card"], horizontal=True)

    if st.button("🎲 Generate Item"):
        st.session_state.start_time = time.time()

        if item_type in ["words","sentences"]:
            st.session_state.current_item = random.choice(data[level][item_type])

        elif item_type == "letter":
            st.session_state.current_item = random.choice(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if lang=="English"
                else "ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
            )

        elif item_type == "number":
            st.session_state.current_item = random.randint(0,100)

        else:
            suits = {"پیک":"black","گشنیز":"black","دل":"red","خشت":"red"}
            rank = random.choice(["آس","۲","۳","۴","۵","۶","۷","۸","۹","۱۰","سرباز","بی بی","شاه"])
            suit = random.choice(list(suits))
            color = suits[suit]
            st.session_state.current_item = f"<span style='color:{color}'>{rank} {suit}</span>"

    # Show Item
    if st.session_state.current_item:
        st.markdown(
            f"<div style='text-align:center;font-size:32px;padding:20px;"
            f"background:#f4f4f4;border-radius:15px;'>"
            f"{st.session_state.current_item}</div>",
            unsafe_allow_html=True
        )

        # Timer
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = max(0, round_time - elapsed)

        st.progress(remaining / round_time)
        st.markdown(f"⏱️ Time left: **{remaining}s**")

        # Buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ OK (Correct Guess)"):
                st.session_state.scores[current_group] += POINTS.get(level,1)
                st.session_state.turn += 1
                st.session_state.current_item = None
                st.rerun()

        with col2:
            if st.button("⏭️ Skip"):
                st.session_state.turn += 1
                st.session_state.current_item = None
                st.rerun()

        # Time up
        if remaining == 0:
            st.warning("⏰ Time's up!")
            st.session_state.turn += 1
            st.session_state.current_item = None
            st.rerun()
