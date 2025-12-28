import streamlit as st
import json
import os
import random
import binascii
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
ROOMS_FILE = "rooms.json"

# =========================
# HELPER FUNCTIONS
# =========================
def load_rooms():
    if not os.path.exists(ROOMS_FILE):
        return {}
    with open(ROOMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_rooms(rooms):
    with open(ROOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(rooms, f, indent=2)

def shuffle_assign(items, players):
    """Shuffle items and assign to players (rotating)"""
    shuffled = items.copy()
    random.shuffle(shuffled)
    distributed = {}
    for i, player in enumerate(players):
        distributed[player] = shuffled[i % len(players)]
    return distributed

# =========================
# SESSION STATE
# =========================
if "room_code" not in st.session_state:
    st.session_state.room_code = ""
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

st.set_page_config(page_title="Gartic Telephone", layout="centered")
st.title("🎨📞 Gartic Telephone Game")

# =========================
# AUTO REFRESH
# =========================
st_autorefresh(interval=2000, key="room_refresh")  # refresh every 2s

# =========================
# JOIN ROOM
# =========================
if st.session_state.room_code == "":
    room_code = st.text_input("Enter Room Code")
    name = st.text_input("Enter Your Name")

    if st.button("Join Room"):
        if room_code and name:
            rooms = load_rooms()
            if room_code not in rooms:
                rooms[room_code] = {
                    "players": [],
                    "phase": "word",
                    "round": 0,
                    "chains": {},       # player -> list of steps
                    "submissions": {},
                    "current_items": {} # task for each player
                }

            if name not in rooms[room_code]["players"]:
                rooms[room_code]["players"].append(name)
                rooms[room_code]["chains"][name] = []

            save_rooms(rooms)
            st.session_state.room_code = room_code
            st.session_state.player_name = name
            st.experimental_rerun()
    st.stop()

# =========================
# LOAD ROOM
# =========================
rooms = load_rooms()
room = rooms.get(st.session_state.room_code)
if not room:
    st.error("Room not found!")
    st.stop()

players = room["players"]
player_name = st.session_state.player_name

st.subheader(f"Room: {st.session_state.room_code}")
st.write("Players:", ", ".join(players))
st.write("Round:", room["round"] + 1)
st.write("Phase:", room["phase"].capitalize())

# =========================
# WORD SUBMISSION PHASE
# =========================
if room["phase"] == "word":
    if player_name not in room["submissions"]:
        word = st.text_input("✍️ Enter a word or phrase")
        if st.button("Submit Word"):
            if word.strip():
                room["submissions"][player_name] = word.strip()
                save_rooms(rooms)
                st.experimental_rerun()
    else:
        st.info("Waiting for other players to submit words...")

    # All words submitted? Move to draw phase
    if len(room["submissions"]) == len(players):
        # Assign words to other players
        items = list(room["submissions"].items())  # [(player, word)]
        words_only = [word for _, word in items]
        distributed = shuffle_assign(words_only, players)

        room["current_items"] = distributed
        room["submissions"] = {}
        room["phase"] = "draw"
        save_rooms(rooms)
        st.experimental_rerun()

# =========================
# DRAWING PHASE
# =========================
elif room["phase"] == "draw":
    task = room["current_items"].get(player_name, None)
    if task is None:
        st.warning("Waiting for tasks to be assigned...")
        st.stop()

    if player_name not in room["submissions"]:
        st.subheader("🎨 Draw this word/phrase:")
        st.markdown(f"**{task}**")

        upload = st.file_uploader("Upload your drawing (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if st.button("Submit Drawing"):
            if upload:
                room["submissions"][player_name] = upload.getvalue().hex()
                save_rooms(rooms)
                st.experimental_rerun()
    else:
        st.info("Waiting for other players to submit drawings...")

    # All drawings submitted? Move to guess phase
    if len(room["submissions"]) == len(players):
        # Save drawings in chains
        for p, img_hex in room["submissions"].items():
            room["chains"][p].append({
                "type": "drawing",
                "value": img_hex
            })

        # Redistribute drawings for guessing
        items = list(room["submissions"].items())
        drawings_only = [img for _, img in items]
        distributed = shuffle_assign(drawings_only, players)

        room["current_items"] = distributed
        room["submissions"] = {}
        room["phase"] = "guess"
        save_rooms(rooms)
        st.experimental_rerun()

# =========================
# GUESSING PHASE
# =========================
elif room["phase"] == "guess":
    img_hex = room["current_items"].get(player_name, None)
    if img_hex is None:
        st.warning("Waiting for drawings to be assigned...")
        st.stop()

    if player_name not in room["submissions"]:
        st.subheader("🤔 Guess this drawing:")
        try:
            st.image(binascii.unhexlify(img_hex), width=400)
        except:
            st.warning("Error displaying image. Maybe file corrupted.")

        guess = st.text_input("Your guess")
        if st.button("Submit Guess"):
            if guess.strip():
                room["submissions"][player_name] = guess.strip()
                save_rooms(rooms)
                st.experimental_rerun()
    else:
        st.info("Waiting for other players to submit guesses...")

    # All guesses submitted? Save and start new round
    if len(room["submissions"]) == len(players):
        for p, guess in room["submissions"].items():
            room["chains"][p].append({
                "type": "guess",
                "value": guess
            })

        room["round"] += 1
        room["submissions"] = {}

        # Check if we should continue or show results
        # For simplicity, stop after each player has submitted one word and one guess
        # Can extend to multiple rounds
        room["phase"] = "results"
        save_rooms(rooms)
        st.experimental_rerun()

# =========================
# RESULTS
# =========================
elif room["phase"] == "results":
    st.subheader("🏁 Game Results")
    for player, chain in room["chains"].items():
        st.markdown(f"## 🔗 {player}'s Word Chain")
        for step in chain:
            if step["type"] == "drawing":
                try:
                    st.image(binascii.unhexlify(step["value"]), width=250)
                except:
                    st.warning("Could not display image")
            else:
                st.write("📝", step["value"])
        st.markdown("---")

    st.success("🎉 Game complete!")
