import streamlit as st
import random
import json
import os
from filelock import FileLock
from streamlit_drawable_canvas import st_canvas

# -------------------------
# Config
# -------------------------
ROOMS_FILE = "rooms.json"
LOCK_FILE = "rooms.lock"

# -------------------------
# Safe Storage
# -------------------------
def load_rooms():
    with FileLock(LOCK_FILE):
        if not os.path.exists(ROOMS_FILE):
            return {}
        with open(ROOMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def save_rooms(rooms):
    with FileLock(LOCK_FILE):
        with open(ROOMS_FILE, "w", encoding="utf-8") as f:
            json.dump(rooms, f, ensure_ascii=False, indent=2)

# -------------------------
# Session identity (per phone)
# -------------------------
if "room_code" not in st.session_state:
    st.session_state.room_code = ""
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

st.set_page_config(page_title="Gartic-Style Game", layout="centered")
st.title("🎨📢 Gartic-Style Drawing & Guess Game")

# -------------------------
# Join Room
# -------------------------
if st.session_state.room_code == "":
    room_code = st.text_input("Room Code")
    player_name = st.text_input("Your Name")

    if st.button("Join Room"):
        if room_code and player_name:
            rooms = load_rooms()

            if room_code not in rooms:
                rooms[room_code] = {
                    "players": [],
                    "phase": "prompt",
                    "prompts": {},
                    "drawing_queue": [],
                    "guess_queue": [],
                    "results": []
                }

            if player_name not in rooms[room_code]["players"]:
                rooms[room_code]["players"].append(player_name)

            save_rooms(rooms)

            st.session_state.room_code = room_code
            st.session_state.player_name = player_name
            st.rerun()
    st.stop()

# -------------------------
# Load Room
# -------------------------
rooms = load_rooms()
room = rooms.get(st.session_state.room_code)

if not room:
    st.error("Room not found.")
    st.stop()

st.subheader(f"Room: {st.session_state.room_code}")
st.write("Players:", ", ".join(room["players"]))

# ======================================================
# PROMPT PHASE
# ======================================================
if room["phase"] == "prompt":
    if st.session_state.player_name not in room["prompts"]:
        prompt = st.text_input("✍️ Enter your word / phrase")

        if st.button("Submit Prompt"):
            if prompt.strip():
                room["prompts"][st.session_state.player_name] = prompt.strip()
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Prompt submitted. Waiting for others...")

    # Host auto-advance
    if len(room["prompts"]) == len(room["players"]):
        st.info("All prompts submitted. Drawing phase starting...")
        prompts = list(room["prompts"].values())
        random.shuffle(prompts)

        room["drawing_queue"] = []
        for i, prompt in enumerate(prompts):
            drawer = room["players"][i % len(room["players"])]
            room["drawing_queue"].append({
                "prompt": prompt,
                "drawer": drawer
            })

        room["phase"] = "draw"
        save_rooms(rooms)
        st.rerun()

# ======================================================
# DRAW PHASE
# ======================================================
elif room["phase"] == "draw":
    my_task = None
    for item in room["drawing_queue"]:
        if item["drawer"] == st.session_state.player_name and "drawing" not in item:
            my_task = item
            break

    if my_task:
        st.subheader("🎨 Draw This")
        st.markdown(f"**{my_task['prompt']}**")

        canvas = st_canvas(
            height=300,
            width=400,
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            drawing_mode="freedraw",
            key="canvas"
        )

        if st.button("Submit Drawing"):
            if canvas.image_data is not None:
                my_task["drawing"] = canvas.image_data.tolist()
                save_rooms(rooms)
                st.rerun()
    else:
        st.info("Waiting for others to finish drawing...")

    if all("drawing" in d for d in room["drawing_queue"]):
        drawings = room["drawing_queue"].copy()
        random.shuffle(drawings)

        room["guess_queue"] = drawings
        room["phase"] = "guess"
        save_rooms(rooms)
        st.rerun()

# ======================================================
# GUESS PHASE
# ======================================================
elif room["phase"] == "guess":
    my_guess = None
    for item in room["guess_queue"]:
        if "guess" not in item:
            my_guess = item
            break

    if my_guess:
        st.subheader("🤔 Guess the Drawing")
        st.image(my_guess["drawing"], width=400)
        guess = st.text_input("Your guess")

        if st.button("Submit Guess"):
            if guess.strip():
                my_guess["guess"] = guess.strip()
                room["results"].append(my_guess)
                save_rooms(rooms)
                st.rerun()
    else:
        st.info("Waiting for others to guess...")

    if len(room["results"]) == len(room["guess_queue"]):
        room["phase"] = "results"
        save_rooms(rooms)
        st.rerun()

# ======================================================
# RESULTS
# ======================================================
elif room["phase"] == "results":
    st.subheader("🏁 Final Results")

    for i, r in enumerate(room["results"], 1):
        st.markdown(f"### Round {i}")
        st.write("📝 Prompt:", r["prompt"])
        st.image(r["drawing"], width=300)
        st.write("💬 Guess:", r["guess"])
        st.markdown("---")

    st.success("Game finished 🎉")
