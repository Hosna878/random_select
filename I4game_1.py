import streamlit as st
import random
import json
import os
import binascii

# =========================
# CONFIG
# =========================
ROOMS_FILE = "rooms.json"

# =========================
# STORAGE
# =========================
def load_rooms():
    if not os.path.exists(ROOMS_FILE):
        return {}
    with open(ROOMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_rooms(rooms):
    with open(ROOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(rooms, f, ensure_ascii=False, indent=2)

# =========================
# SESSION IDENTITY
# =========================
if "room_code" not in st.session_state:
    st.session_state.room_code = ""
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

st.set_page_config(page_title="Gartic-Style Game", layout="centered")
st.title("🎨📢 Multiplayer Drawing & Guess Game")

# =========================
# JOIN ROOM
# =========================
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
                    "draw_queue": [],
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

# =========================
# LOAD ROOM
# =========================
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
        prompt = st.text_input("✍️ Enter a word or phrase")

        if st.button("Submit Prompt"):
            if prompt.strip():
                room["prompts"][st.session_state.player_name] = prompt.strip()
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Prompt submitted. Waiting for others...")

    if len(room["prompts"]) == len(room["players"]):
        prompts = list(room["prompts"].values())
        random.shuffle(prompts)

        room["draw_queue"] = []
        for i, prompt in enumerate(prompts):
            drawer = room["players"][i % len(room["players"])]
            room["draw_queue"].append({
                "pr
