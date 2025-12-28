import streamlit as st
import json
import random
import os

# -----------------------
# File paths
# -----------------------
FARSI_FILE = "farsi_words.json"
EN_FILE = "english_words.json"

# -----------------------
# Default words/sentences
# -----------------------
default_farsi = {
    "simple": {
        "words": ["آب", "نان", "گل", "باد", "نور", "شب", "روز", "دست", "پا", "چشم", "خانه", "کوچه"],
        "sentences": [
            "هوا امروز آفتابی است", "من عاشق کتاب خواندن هستم", "دیروز به مدرسه رفتم",
            "من امروز خوشحالم", "پرنده‌ای روی درخت نشست", "من با دوچرخه می‌روم"
        ]
    },
    "medium": {
        "words": ["دوچرخه", "ماشین", "قطار", "هواپیما", "کشتی", "باغ", "گلخانه", "بازار"],
        "sentences": [
            "امروز درس ریاضی سخت بود", "دیروز به مهمانی رفتم", "برای سفر آماده می‌شوم",
            "من با دوستانم صحبت می‌کنم", "من به پارک رفتم و دویدم", "دوست من مرا دید"
        ]
    },
    "hard": {
        "words": ["آزادی", "عدالت", "ایمان", "فلسفه", "منطق", "تحلیل", "تفکر", "هویت"],
        "sentences": [
            "انسان باید با خرد زندگی کند", "جهان پر از پیچیدگی و تضاد است",
            "زندگی با تلاش و صبر معنا پیدا می‌کند", "تفکر انتقادی برای همه مهم است",
            "حقوق بشر باید رعایت شود", "تحلیل فرهنگی به ما کمک می‌کند"
        ]
    }
}

default_english = {
    "simple": {
        "words": ["water", "bread", "flower", "wind", "light", "night", "day", "hand", "foot", "eye", "house", "street"],
        "sentences": ["Today is sunny", "I love reading books", "Yesterday I went to school",
                      "I am happy today", "A bird sat on the tree", "I ride my bike"]
    },
    "medium": {
        "words": ["bicycle", "car", "train", "airplane", "ship", "garden", "greenhouse", "market"],
        "sentences": ["Math class was hard today", "Yesterday I went to a party", "I am preparing for a trip",
                      "I talk with my friends", "I went to the park and ran", "My friend saw me"]
    },
    "hard": {
        "words": ["freedom", "justice", "faith", "philosophy", "logic", "analysis", "thinking", "identity"],
        "sentences": ["Man should live with wisdom", "The world is full of complexity and conflict",
                      "Life finds meaning through effort and patience", "Critical thinking is important for all",
                      "Human rights must be respected", "Cultural analysis helps us understand better"]
    }
}

# -----------------------
# Load JSON or create
# -----------------------
def load_words(file_path, default_words):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_words, f, ensure_ascii=False, indent=4)
        return default_words.copy()

# -----------------------
# Session State
# -----------------------
if "lang" not in st.session_state:
    st.session_state.lang = "Farsi"
if "farsi_words" not in st.session_state:
    st.session_state.farsi_words = load_words(FARSI_FILE, default_farsi)
if "english_words" not in st.session_state:
    st.session_state.english_words = load_words(EN_FILE, default_english)

# -----------------------
# Page setup
# -----------------------
st.set_page_config(page_title="Random Words/Sentences App", layout="wide")
st.title("🎲 Random Words & Sentences Generator")

# -----------------------
# Language selection
# -----------------------
lang = st.sidebar.radio("🌐 Select Language / انتخاب زبان:", ["Farsi", "English"])
if lang == "Farsi":
    words_dict = st.session_state.farsi_words
else:
    words_dict = st.session_state.english_words

# -----------------------
# Sidebar navigation
# -----------------------
page = st.sidebar.radio("🔹 Select Functionality / انتخاب عملکرد:", 
                        ["Random Word/Sentence", "Add Word/Sentence", "Add List", "Random Letter/Number","Play Game"])

# -----------------------
# Random Word/Sentence
# -----------------------
if page == "Random Word/Sentence":
    st.subheader("💡 Random Word or Sentence")
    col1, col2 = st.columns(2)
    with col1:
        level = st.radio("Level / سطح:", ("simple", "medium", "hard"))
    with col2:
        item_type = st.radio("Type / نوع:", ("words", "sentences"))

    st.markdown("---")
    if st.button("🎯 Generate Random"):
        items = words_dict[level][item_type]
        if items:
            random_item = random.choice(items)
            text_color = random.choice(["#FF5733","#33FF57","#3380FF","#FF33EC","#FFC300"])
            bg_color = random.choice(["#F0F8FF","#FFFACD","#E6E6FA","#F5F5DC","#FFE4E1"])
            while text_color == bg_color:
                bg_color = random.choice(["#F0F8FF","#FFFACD","#E6E6FA","#F5F5DC","#FFE4E1"])
            st.markdown(
                f"<div style='text-align:center; font-size:28px; color:{text_color}; "
                f"background-color:{bg_color}; padding:25px; border-radius:15px; font-weight:bold;'>{random_item}</div>",
                unsafe_allow_html=True
            )
        else:
            st.warning(f"No {item_type} in this level!")

# -----------------------
# Add Word/Sentence
# -----------------------
elif page == "Add Word/Sentence":
    st.subheader("✏️ Add a new Word or Sentence")
    col1, col2 = st.columns([2,1])
    with col1:
        new_item = st.text_input("Enter Word or Sentence / وارد کردن کلمه یا جمله:")
    with col2:
        add_level = st.selectbox("Level / سطح:", ("simple", "medium", "hard"))
        add_type = st.selectbox("Type / نوع:", ("words", "sentences"))

    if st.button("➕ Add"):
        if new_item.strip():
            if new_item.strip() not in words_dict[add_level][add_type]:
                words_dict[add_level][add_type].append(new_item.strip())
                file_path = FARSI_FILE if lang=="Farsi" else EN_FILE
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(words_dict, f, ensure_ascii=False, indent=4)
                st.success(f"{add_type[:-1].capitalize()} '{new_item}' added!")
            else:
                st.info("Item already exists.")
        else:
            st.error("Please enter a valid item.")

# -----------------------
# Add List
# -----------------------
elif page == "Add List":
    st.subheader("📋 Add a List of Words/Sentences")
    col1, col2 = st.columns([2,1])
    with col1:
        input_text = st.text_area("Enter list (comma or newline separated):")
    with col2:
        bulk_level = st.selectbox("Level / سطح:", ("simple", "medium", "hard"))
        bulk_type = st.selectbox("Type / نوع:", ("words", "sentences"))

    if st.button("📥 Add List"):
        if input_text.strip():
            items_input = [w.strip() for w in input_text.replace("\n", ",").split(",") if w.strip()]
            added_items = []
            existing_set = set(words_dict[bulk_level][bulk_type])
            for item in items_input:
                if item not in existing_set:
                    words_dict[bulk_level][bulk_type].append(item)
                    added_items.append(item)
                    existing_set.add(item)
            file_path = FARSI_FILE if lang=="Farsi" else EN_FILE
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(words_dict, f, ensure_ascii=False, indent=4)
            if added_items:
                st.success(f"New {bulk_type} added: {', '.join(added_items)}")
            else:
                st.info("No new items to add.")
        else:
            st.error("Please enter at least one item.")

# -----------------------
# Random Letter/Number/Card
# -----------------------
elif page == "Random Letter/Number":
    st.subheader("🎲 Random Generator: Letter, Number, or Card")
    option_type = st.radio("Type / نوع:", ["Letter", "Number", "Card"])
    col1, col2 = st.columns(2)

    # Settings for Letter or Number
    with col1:
        if option_type == "Letter":
            lang_choice = st.radio("Language / زبان:", ["Farsi", "English"])
        elif option_type == "Number":
            min_val = st.number_input("Min / حداقل:", value=0)
            max_val = st.number_input("Max / حداکثر:", value=100)
        elif option_type == "Card":
            card_lang = st.radio("Card Language / زبان کارت:", ["English", "Farsi"])

    if st.button("🎯 Generate"):
        text_color = random.choice(["#FF5733","#33FF57","#3380FF","#FF33EC","#FFC300"])
        bg_color = random.choice(["#F0F8FF","#FFFACD","#E6E6FA","#F5F5DC","#FFE4E1"])
        while text_color == bg_color:
            bg_color = random.choice(["#F0F8FF","#FFFACD","#E6E6FA","#F5F5DC","#FFE4E1"])

        if option_type == "Letter":
            if lang_choice=="English":
                random_item = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
            else:
                farsi_letters = list("ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی")
                random_item = random.choice(farsi_letters)
        
        elif option_type == "Number":
            random_item = random.randint(int(min_val), int(max_val))

        elif option_type == "Card":
            suits_en = ["Spades", "Hearts", "Diamonds", "Clubs"]
            ranks_en = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

            suits_fa = ["پیک", "دل", "خشت", "گشنیز"]
            ranks_fa = ["آس", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹", "۱۰", "سرباز", "بی بی", "شاه"]

            if card_lang == "English":
                suit = random.choice(suits_en)
                rank = random.choice(ranks_en)
                random_item = f"{rank} of {suit}"
            else:
                suit = random.choice(suits_fa)
                rank = random.choice(ranks_fa)
                random_item = f"{rank} {suit}"

        st.markdown(
            f"<div style='text-align:center; font-size:28px; color:{text_color}; "
            f"background-color:{bg_color}; padding:25px; border-radius:15px; font-weight:bold;'>{random_item}</div>",
            unsafe_allow_html=True
        )
        
        
# -----------------------
# Multiplayer Word Game
# -----------------------
elif page == "Play Game":
    st.subheader("🎲 Multiplayer Word Game")

    # --- Setup groups ---
    if "groups" not in st.session_state:
        num_groups = st.number_input("Enter number of groups:", min_value=1, step=1, value=2)
        if st.button("Start Game"):
            st.session_state.groups = {f"Group {i+1}": 0 for i in range(num_groups)}
            st.session_state.current_group = 0
            st.session_state.current_item = ""
            st.session_state.current_level = "simple"
            st.session_state.current_type = "words"
            st.session_state.started = True
            st.session_state.round_played = {f"Group {i+1}": False for i in range(num_groups)}
            st.session_state.used_items = []  # Track used items to avoid repetition
        st.stop()

    group_names = list(st.session_state.groups.keys())
    current_group_name = group_names[st.session_state.current_group]
    st.markdown(f"### 🟢 Current Turn: {current_group_name} | Score: {st.session_state.groups[current_group_name]}")

    # --- Select level and type ---
    col1, col2 = st.columns(2)
    with col1:
        level = st.radio("Level / سطح:", ("simple", "medium", "hard"),
                         index=["simple","medium","hard"].index(st.session_state.current_level))
    with col2:
        item_type = st.radio("Type / نوع:", ("words", "sentences"),
                             index=["words","sentences"].index(st.session_state.current_type))

    st.session_state.current_level = level
    st.session_state.current_type = item_type
    items = words_dict[level][item_type]

    if not items:
        st.warning("No items for this level/type!")
        st.stop()

    # --- Pick a new word avoiding repeats ---
    remaining_items = [item for item in items if item not in st.session_state.used_items]
    if not remaining_items:  # Reset if all used
        st.session_state.used_items = []
        remaining_items = items.copy()

    if st.session_state.current_item == "" or st.session_state.current_item not in remaining_items:
        st.session_state.current_item = random.choice(remaining_items)
        st.session_state.used_items.append(st.session_state.current_item)

    # --- Display current word ---
    text_color = random.choice(["#FF5733","#33FF57","#3380FF","#FF33EC","#FFC300"])
    bg_color = random.choice(["#F0F8FF","#FFFACD","#E6E6FA","#F5F5DC","#FFE4E1"])
    while text_color == bg_color:
        bg_color = random.choice(["#F0F8FF","#FFFACD","#E6E6FA","#F5F5DC","#FFE4E1"])
    st.markdown(
        f"<div style='text-align:center; font-size:32px; color:{text_color}; "
        f"background-color:{bg_color}; padding:25px; border-radius:15px; font-weight:bold;'>{st.session_state.current_item}</div>",
        unsafe_allow_html=True
    )

    # --- Action buttons ---
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    with col1:
        if st.button("✅ Got it!"):
            if level == "simple":
                st.session_state.groups[current_group_name] += 1
            elif level == "medium":
                st.session_state.groups[current_group_name] += 2
            else:
                st.session_state.groups[current_group_name] += 3
            # Pick a new unused word
            remaining_items = [item for item in items if item not in st.session_state.used_items]
            if not remaining_items:
                st.session_state.used_items = []
                remaining_items = items.copy()
            st.session_state.current_item = random.choice(remaining_items)
            st.session_state.used_items.append(st.session_state.current_item)
            st.session_state.round_played[current_group_name] = True

    with col2:
        if st.button("⏭ Skip"):
            st.session_state.groups[current_group_name] -= 1
            remaining_items = [item for item in items if item not in st.session_state.used_items]
            if not remaining_items:
                st.session_state.used_items = []
                remaining_items = items.copy()
            st.session_state.current_item = random.choice(remaining_items)
            st.session_state.used_items.append(st.session_state.current_item)
            st.session_state.round_played[current_group_name] = True

    with col3:
        if st.button("➡ Next Group"):
            st.session_state.current_group = (st.session_state.current_group + 1) % len(group_names)
            remaining_items = [item for item in items if item not in st.session_state.used_items]
            if not remaining_items:
                st.session_state.used_items = []
                remaining_items = items.copy()
            st.session_state.current_item = random.choice(remaining_items)
            st.session_state.used_items.append(st.session_state.current_item)

    # --- Finish Game button ---
    if all(st.session_state.round_played.values()):
        if st.button("🏁 Finish Game"):
            st.success("🎉 Game Over! Final Scores:")
            for g, s in st.session_state.groups.items():
                st.write(f"{g}: {s}")
            # Reset game
            for key in ["groups","current_group","current_item","current_level","current_type","started","round_played","used_items"]:
                del st.session_state[key]
    else:
        st.button("🏁 Finish Game (disabled, all groups must play this round)", disabled=True)


