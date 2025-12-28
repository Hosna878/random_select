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
# STORAGE HELPERS
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
# SESSION INIT
# =========================
if "room_code" not in st.session_state:
    st.session_state.room_code = ""
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

st.set_page_config(page_title="Gartic Style Game", layout="centered")
st.title("🎨📢 Multiplayer Drawing & Guess Game")

# =========================
# JOIN ROOM
# =========================
if st.session_state.room_code == "":
    room_code = st.text_input("Room Code")
    player_name = st.text_input("Your Name")

    if st.button("Join Room"):
        if room_code.strip() and player_name.strip():
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

# =========================
# PROMPT PHASE
# =========================
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
        for i, p in enumerate(prompts):
            drawer = room["players"][i % len(room["players"])]
            room["draw_queue"].append({
                "prompt": p,
                "drawer": drawer
            })

        room["phase"] = "draw"
        save_rooms(rooms)
        st.rerun()

# =========================
# DRAW PHASE (UPLOAD IMAGE)
# =========================
elif room["phase"] == "draw":
    task = None
    for item in room["draw_queue"]:
        if item["drawer"] == st.session_state.player_name and "drawing" not in item:
            task = item
            break

    if task:
        st.subheader("🎨 Draw This")
        st.markdown(f"**{task['prompt']}**")

        upload = st.file_uploader(
            "Upload your drawing (PNG/JPG)",
            type=["png", "jpg", "jpeg"]
        )

        if st.button("Submit Drawing"):
            if upload:
                task["drawing"] = upload.getvalue().hex()
                save_rooms(rooms)
                st.rerun()
    else:
        st.info("Waiting for other players to finish drawing...")

    if all("drawing" in d for d in room["draw_queue"]):
        room["guess_queue"] = room["draw_queue"].copy()
        random.shuffle(room["guess_queue"])
        room["phase"] = "guess"
        save_rooms(rooms)
        st.rerun()

# =========================
# GUESS PHASE
# =========================
elif room["phase"] == "guess":
    guess_item = None
    for item in room["guess_queue"]:
        if "guess" not in item:
            guess_item = item
            break

    if guess_item:
        st.subheader("🤔 Guess the Drawing")
        image_bytes = binascii.unhexlify(guess_item["drawing"])
        st.image(image_bytes, width=400)

        guess = st.text_input("Your guess")

        if st.button("Submit Guess"):
            if guess.strip():
                guess_item["guess"] = guess.strip()
                room["results"].append(guess_item)
                save_rooms(rooms)
                st.rerun()
    else:
        st.info("Waiting for others to guess...")

    if len(room["results"]) == len(room["guess_queue"]):
        room["phase"] = "results"
        save_rooms(rooms)
        st.rerun()

# =========================
# RESULTS
# =========================
elif room["phase"] == "results":
    st.subheader("🏁 Game Results")

    for i, r in enumerate(room["results"], 1):
        st.markdown(f"### Round {i}")
        st.write("📝 Prompt:", r["prompt"])
        st.image(binascii.unhexlify(r["drawing"]), width=300)
        st.write("💬 Guess:", r["guess"])
        st.markdown("---")

    st.success("🎉 Game finished!")
