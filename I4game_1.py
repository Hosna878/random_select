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
        json.dump(rooms, f, indent=2)

# =========================
# SESSION STATE
# =========================
if "room_code" not in st.session_state:
    st.session_state.room_code = ""
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

st.set_page_config(page_title="Gartic Telephone Game", layout="centered")
st.title("🎨📞 Gartic Telephone Game")

# =========================
# JOIN ROOM
# =========================
if st.session_state.room_code == "":
    room_code = st.text_input("Room Code")
    name = st.text_input("Your Name")

    if st.button("Join Room"):
        if room_code and name:
            rooms = load_rooms()
            if room_code not in rooms:
                rooms[room_code] = {
                    "players": [],
                    "phase": "word",
                    "round": 0,
                    "chains": {},   # player -> list of steps
                    "submissions": {},
                    "current_items": {}
                }

            if name not in rooms[room_code]["players"]:
                rooms[room_code]["players"].append(name)
                rooms[room_code]["chains"][name] = []

            save_rooms(rooms)
            st.session_state.room_code = room_code
            st.session_state.player_name = name
            st.rerun()
    st.stop()

# =========================
# LOAD ROOM
# =========================
rooms = load_rooms()
room = rooms[st.session_state.room_code]
players = room["players"]

st.subheader(f"Room: {st.session_state.room_code}")
st.write("Players:", ", ".join(players))
st.write("Round:", room["round"] + 1)

# =========================
# HELPER: Shuffle without self-assignment
# =========================
def shuffle_no_self_assignment(players, items):
    if len(players) < 2:
        return {players[0]: items[0]}  # only one player
    while True:
        shuffled = items[:]
        random.shuffle(shuffled)
        if all(players[i] != shuffled[i] for i in range(len(players))):
            return {players[i]: shuffled[i] for i in range(len(players))}

# =========================
# WORD PHASE
# =========================
if room["phase"] == "word":
    if st.session_state.player_name not in room["submissions"]:
        word = st.text_input("✍️ Enter a word or phrase")
        if st.button("Submit Word"):
            if word.strip():
                room["submissions"][st.session_state.player_name] = word.strip()
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others to submit words...")

    # Check if all words submitted
    if len(room["submissions"]) == len(players):
        distributed = shuffle_no_self_assignment(list(room["submissions"].keys()),
                                                 list(room["submissions"].values()))
        room["current_items"] = distributed
        room["submissions"] = {}
        room["phase"] = "draw"
        save_rooms(rooms)
        st.rerun()

# =========================
# DRAW PHASE
# =========================
elif room["phase"] == "draw":
    task = room["current_items"][st.session_state.player_name]
    if st.session_state.player_name not in room["submissions"]:
        st.subheader("🎨 Draw this word")
        st.markdown(f"**{task}**")

        upload = st.file_uploader("Upload drawing (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if st.button("Submit Drawing"):
            if upload:
                room["submissions"][st.session_state.player_name] = upload.getvalue().hex()
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others to submit drawings...")

    if len(room["submissions"]) == len(players):
        # Add drawings to chains
        for p, img in room["submissions"].items():
            room["chains"][p].append({"type": "drawing", "value": img})

        # Redistribute drawings for guessing
        distributed = shuffle_no_self_assignment(list(room["submissions"].keys()),
                                                 list(room["submissions"].values()))
        room["current_items"] = distributed
        room["submissions"] = {}
        room["phase"] = "guess"
        save_rooms(rooms)
        st.rerun()

# =========================
# GUESS PHASE
# =========================
elif room["phase"] == "guess":
    img_hex = room["current_items"][st.session_state.player_name]
    if st.session_state.player_name not in room["submissions"]:
        st.subheader("🤔 Guess this drawing")
        st.image(binascii.unhexlify(img_hex), width=400)

        guess = st.text_input("Your guess")
        if st.button("Submit Guess"):
            if guess.strip():
                room["submissions"][st.session_state.player_name] = guess.strip()
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others to submit guesses...")

    if len(room["submissions"]) == len(players):
        # Add guesses to chains
        for p, guess in room["submissions"].items():
            room["chains"][p].append({"type": "guess", "value": guess})

        room["round"] += 1
        room["submissions"] = {}

        if room["round"] >= len(players):
            room["phase"] = "results"
        else:
            # Next round: everyone submits a new word
            room["phase"] = "word"
            room["current_items"] = {}
        save_rooms(rooms)
        st.rerun()

# =========================
# RESULTS PHASE
# =========================
elif room["phase"] == "results":
    st.subheader("🏁 Final Chains")
    for player, chain in room["chains"].items():
        st.markdown(f"## 🔗 {player}'s Chain")
        for step in chain:
            if step["type"] == "drawing":
                st.image(binascii.unhexlify(step["value"]), width=250)
            else:
                st.write("📝", step["value"])
        st.markdown("---")
    st.success("🎉 Game complete!")
