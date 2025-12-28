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
                    "chains": {},       # player -> list of chains
                    "submissions": {},  # current round submissions
                    "current_items": {},# items to draw/guess this round
                    "pool": []          # all items for future rounds
                }

            if name not in rooms[room_code]["players"]:
                rooms[room_code]["players"].append(name)

            # Initialize chains for new player
            if name not in rooms[room_code]["chains"]:
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
        if all(players[i] != shuffled[i]["owner"] for i in range(len(players))):
            return {players[i]: shuffled[i] for i in range(len(players))}

# =========================
# WORD PHASE
# =========================
if room["phase"] == "word":
    if st.session_state.player_name not in room["submissions"]:
        word = st.text_input("✍️ Enter a word or phrase")
        if st.button("Submit Word"):
            if word.strip():
                room["submissions"][st.session_state.player_name] = {
                    "type": "word",
                    "value": word.strip(),
                    "owner": st.session_state.player_name,
                    "history": [word.strip()]  # history starts with original word
                }
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others to submit words...")

    if len(room["submissions"]) == len(players):
        # Add new words to pool
        room["pool"].extend(room["submissions"].values())

        # Shuffle pool and distribute for drawing
        distributed = shuffle_no_self_assignment(players, room["pool"])
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
        st.subheader("🎨 Draw this")
        st.markdown(f"**{task['history'][-1]}**")  # show last state (word or guess)

        upload = st.file_uploader("Upload drawing (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if st.button("Submit Drawing"):
            if upload:
                room["submissions"][st.session_state.player_name] = {
                    "type": "drawing",
                    "value": upload.getvalue().hex(),
                    "owner": task["owner"],
                    "history": task["history"] + ["drawing"]
                }
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others to submit drawings...")

    if len(room["submissions"]) == len(players):
        # Add drawings to chains and pool
        for p, item in room["submissions"].items():
            room["chains"][item["owner"]].append(item)
            room["pool"].append(item)

        # Shuffle pool for guessing
        distributed = shuffle_no_self_assignment(players, room["pool"])
        room["current_items"] = distributed
        room["submissions"] = {}
        room["phase"] = "guess"
        save_rooms(rooms)
        st.rerun()

# =========================
# GUESS PHASE
# =========================
elif room["phase"] == "guess":
    task = room["current_items"][st.session_state.player_name]
    img_hex = task["value"]
    if st.session_state.player_name not in room["submissions"]:
        st.subheader("🤔 Guess this drawing")
        st.image(binascii.unhexlify(img_hex), width=400)

        guess = st.text_input("Your guess")
        if st.button("Submit Guess"):
            if guess.strip():
                room["submissions"][st.session_state.player_name] = {
                    "type": "guess",
                    "value": guess.strip(),
                    "owner": task["owner"],
                    "history": task["history"] + [guess.strip()]
                }
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others to submit guesses...")

    if len(room["submissions"]) == len(players):
        # Add guesses to chains and pool
        for p, item in room["submissions"].items():
            room["chains"][item["owner"]].append(item)
            room["pool"].append(item)

        room["round"] += 1
        room["submissions"] = {}
        room["phase"] = "word"
        save_rooms(rooms)
        st.rerun()

# =========================
# RESULTS PHASE
# =========================
elif room["phase"] == "results":
    st.subheader("🏁 Full Word Chains")
    for player, chain in room["chains"].items():
        st.markdown(f"## 🔗 {player}'s Chain")
        for step in chain:
            if step["type"] == "drawing":
                st.image(binascii.unhexlify(step["value"]), width=250)
            else:
