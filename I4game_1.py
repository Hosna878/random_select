import streamlit as st
import json
import os
import random
import binascii

# =========================
# CONFIG
# =========================
ROOMS_FILE = "rooms.json"

# =========================
# STORAGE FUNCTIONS
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
                    "chains": {},  # player -> list of steps
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
# END GAME BUTTON (first player only)
# =========================
if st.session_state.player_name == players[0]:
    if st.button("🛑 End Game"):
        room["phase"] = "results"
        save_rooms(rooms)
        st.rerun()

# =========================
# WORD PHASE
# =========================
if room["phase"] == "word":
    if st.session_state.player_name not in room["submissions"]:
        word = st.text_input("✍️ Enter a word or phrase")
        if st.button("Submit Word"):
            if word.strip():
                room["submissions"][st.session_state.player_name] = word.strip()
                # Immediately add the first word to chain
                room["chains"][st.session_state.player_name].append({"type": "word", "value": word.strip()})
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others...")

    # All players submitted → move to drawing
    if len(room["submissions"]) == len(players):
        # Shuffle and assign words to other players
        items = list(room["submissions"].items())
        random.shuffle(items)
        distributed = {}
        for i, (player, word) in enumerate(items):
            distributed[player] = items[(i + 1) % len(items)][1]

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
        st.subheader("🎨 Draw This")
        st.markdown(f"**{task}**")

        upload = st.file_uploader("Upload drawing (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if st.button("Submit Drawing"):
            if upload:
                # Save image as hex string
                room["submissions"][st.session_state.player_name] = binascii.hexlify(upload.getvalue()).decode()
                # Add to chain
                room["chains"][st.session_state.player_name].append({
                    "type": "drawing",
                    "value": binascii.hexlify(upload.getvalue()).decode()
                })
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others...")

    # All drawings submitted → move to guess
    if len(room["submissions"]) == len(players):
        # Shuffle drawings and assign to others
        items = list(room["submissions"].items())
        random.shuffle(items)
        distributed = {}
        for i, (player, drawing_hex) in enumerate(items):
            distributed[player] = items[(i + 1) % len(items)][1]

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
        st.subheader("🤔 Guess This Drawing")
        st.image(binascii.unhexlify(img_hex), width=400)

        guess = st.text_input("Your guess")
        if st.button("Submit Guess"):
            if guess.strip():
                room["submissions"][st.session_state.player_name] = guess.strip()
                # Add guess to chain
                room["chains"][st.session_state.player_name].append({
                    "type": "guess",
                    "value": guess.strip()
                })
                save_rooms(rooms)
                st.rerun()
    else:
        st.success("Waiting for others...")

    # All guesses submitted → next round (word → draw → guess)
    if len(room["submissions"]) == len(players):
        # Assign guesses as next "words" for drawing round
        items = list(room["submissions"].items())
        random.shuffle(items)
        distributed = {}
        for i, (player, guess) in enumerate(items):
            distributed[player] = items[(i + 1) % len(items)][1]

        room["current_items"] = distributed
        room["submissions"] = {}
        room["phase"] = "draw"
        room["round"] += 1
        save_rooms(rooms)
        st.rerun()

# =========================
# RESULTS PHASE
# =========================
elif room["phase"] == "results":
    st.subheader("🏁 Final Chains")
    for player, chain in room["chains"].items():
        st.markdown(f"## 🔗 {player}'s Word Chain")
        for step in chain:
            if step["type"] == "drawing":
                st.image(binascii.unhexlify(step["value"]), width=250)
            else:
                st.write("📝", step["value"])
        st.markdown("---")
    st.success("🎉 Game complete!")
