import streamlit as st
import random
import json
import os

# -------------------------
# Game Storage (simulate server)
# -------------------------
ROOMS_FILE = "rooms.json"
if not os.path.exists(ROOMS_FILE):
    with open(ROOMS_FILE, "w") as f:
        json.dump({}, f)

def load_rooms():
    with open(ROOMS_FILE, "r") as f:
        return json.load(f)

def save_rooms(rooms):
    with open(ROOMS_FILE, "w") as f:
        json.dump(rooms, f)

rooms = load_rooms()

# -------------------------
# Join/Create Room
# -------------------------
st.title("🎨📢 Multiplayer Drawing & Guess Game")

room_code = st.text_input("Enter Room Code:")
player_name = st.text_input("Enter Your Name:")

if st.button("Join Room"):
    if room_code and player_name:
        if room_code not in rooms:
            rooms[room_code] = {"players": [], "phase": "join", "turn_index":0, "prompts": {}, "drawings": [], "guesses":[]}
        if player_name not in rooms[room_code]["players"]:
            rooms[room_code]["players"].append(player_name)
        save_rooms(rooms)
        st.success(f"{player_name} joined room {room_code}!")

# -------------------------
# Load Room State
# -------------------------
if room_code in rooms:
    room = rooms[room_code]
    st.write("Players in room:", room["players"])
    
    # ---------------------
    # Prompt Phase
    # ---------------------
    if room["phase"] == "join":
        if player_name in room["players"]:
            prompt = st.text_input("Enter your prompt:")
            if st.button("Submit Prompt"):
                room["prompts"][player_name] = prompt
                save_rooms(rooms)
                st.success("Prompt submitted!")
        # Host button to start game
        if st.button("Start Drawing Phase (Host)"):
            if len(room["prompts"]) == len(room["players"]):
                room["phase"] = "draw"
                room["turn_index"] = 0
                # Shuffle prompts for drawing assignment
                items = list(room["prompts"].items())
                random.shuffle(items)
                room["drawing_queue"] = [{"prompt": p, "drawer": room["players"][i % len(room["players"])]} for i, (player, p) in enumerate(items)]
                save_rooms(rooms)
                st.experimental_rerun()
            else:
                st.warning("All players must submit prompts first.")
    
    # ---------------------
    # Drawing Phase
    # ---------------------
    elif room["phase"] == "draw":
        my_turn_item = None
        for item in room["drawing_queue"]:
            if item["drawer"] == player_name and "drawing" not in item:
                my_turn_item = item
                break
        if my_turn_item:
            st.write("Your prompt to draw:", my_turn_item["prompt"])
            from streamlit_drawable_canvas import st_canvas
            canvas_result = st_canvas(
                fill_color="rgba(0, 0, 0, 0.3)",
                stroke_width=3,
                stroke_color="#000000",
                background_color="#fff",
                height=300,
                width=400,
                drawing_mode="freedraw",
                key=f"canvas_{player_name}",
            )
            if st.button("Submit Drawing"):
                my_turn_item["drawing"] = canvas_result.image_data.tolist()  # convert numpy to list
                save_rooms(rooms)
                st.success("Drawing submitted!")
        else:
            st.write("Waiting for your turn or all drawings submitted...")

# -------------------------
# Further phases (guessing, next cycles) can follow the same logic
# -------------------------
