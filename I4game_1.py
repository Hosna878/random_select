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

st.set_page_config(page_title="Gartic Telephone", layout="centered")
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
                    "host": name,
                    "phase": "word",
                    "round": 0,
                    "chains": {},  # original_word -> list of steps
                    "current_items": {},  # player -> latest item to process
                    "submissions": {}
                }
            if name not in rooms[room_code]["players"]:
                rooms[room_code]["players"].append(name)
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
host = room["host"]

st.subheader(f"Room: {st.session_state.room_code}")
st.write("Players:", ", ".join(players))
st.write("Round:", room["round"] + 1)

# =========================
# END GAME BUTTON (for host)
# =========================
if st.session_state.player_name == host:
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
                # Create a new chain for this word
                room["chains"][f"{st.session_state.player_name}_{room['round']}"] = [
                    {"type": "word", "player": st.session_state.player_name, "value": word.strip()}
                ]
                room["submissions"][st.session_state.player_name] = word.strip()
                save_rooms(rooms)
                st.rerun()
    else:
        st.info("Waiting for others...")

    # Check if all players submitted words
    if len(room["submissions"]) == len(players):
        submissions_items = list(room["submissions"].items())
        random.shuffle(submissions_items)
        distributed = {}
        for i, (player, word) in enumerate(submissions_items):
            for j in range(len(submissions_items)):
                if submissions_items[j][0] != player:
                    distributed[player] = submissions_items[j][1]
                    submissions_items.pop(j)
                    break
        room["current_items"] = distributed
        room["submissions"] = {}
        room["phase"] = "draw"
        save_rooms(rooms)
        st.rerun()

# =========================
# DRAW PHASE
# =========================
elif room["phase"] == "draw":
    task = room["current_items"].get(st.session_state.player_name)
    if task and st.session_state.player_name not in room["submissions"]:
        st.subheader("🎨 Draw This")
        st.markdown(f"**{task}**")
        upload = st.file_uploader("Upload drawing (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if st.button("Submit Drawing"):
            if upload:
                room["submissions"][st.session_state.player_name] = binascii.hexlify(upload.getvalue()).decode()
                save_rooms(rooms)
                st.rerun()
    else:
        st.info("Waiting for others...")

    # Check if all players submitted drawings
    if len(room["submissions"]) == len(players):
        # Append drawings to chains
        for player, img_hex in room["submissions"].items():
            for chain_name, chain in room["chains"].items():
                last_step = chain[-1]
                if last_step["value"] == room["current_items"].get(player):
                    chain.append({"type": "drawing", "player": player, "value": img_hex})
        # Prepare guesses
        items = list(room["submissions"].items())
        random.shuffle(items)
        distributed = {}
        for i, (player, img_hex) in enumerate(items):
            for j in range(len(items)):
                if items[j][0] != player:
                    distributed[player] = items[j][1]
                    items.pop(j)
                    break
        room["current_items"] = distributed
        room["submissions"] = {}
        room["phase"] = "guess"
        save_rooms(rooms)
        st.rerun()

# =========================
# GUESS PHASE
# =========================
elif room["phase"] == "guess":
    task = room["current_items"].get(st.session_state.player_name)
    if task and st.session_state.player_name not in room["submissions"]:
        st.subheader("🤔 Guess This Drawing")
        st.image(binascii.unhexlify(task), width=400)
        guess = st.text_input("Your guess")
        if st.button("Submit Guess"):
            if guess.strip():
                room["submissions"][st.session_state.player_name] = guess.strip()
                save_rooms(rooms)
                st.rerun()
    else:
        st.info("Waiting for others...")

    # Check if all players submitted guesses
    if len(room["submissions"]) == len(players):
        # Append guesses to chains
        for player, guess in room["submissions"].items():
            for chain_name, chain in room["chains"].items():
                last_step = chain[-1]
                if last_step["type"] == "drawing" and last_step["value"] == room["current_items"].get(player):
                    chain.append({"type": "guess", "player": player, "value": guess})

        # Prepare next round: cycle between draw and guess until host ends
        items = {}
        for chain_name, chain in room["chains"].items():
            last_step = chain[-1]
            if last_step["type"] == "guess":
                for player in players:
                    if player != last_step["player"]:
                        items[player] = last_step["value"]
                        break
        room["current_items"] = items
        room["submissions"] = {}
        room["phase"] = "draw"
        room["round"] += 1
        save_rooms(rooms)
        st.rerun()

# =========================
# RESULTS
# =========================
elif room["phase"] == "results":
    st.subheader("🏁 Final Chains")
    for chain_name, chain in room["chains"].items():
        st.markdown(f"## 🔗 {chain_name}")
        for step in chain:
            if step["type"] == "drawing":
                st.image(binascii.unhexlify(step["value"]), width=250)
            else:
                st.write(f"📝 {step['player']}: {step['value']}")
        st.markdown("---")
    st.success("🎉 Game complete!")
