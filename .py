# -----------------------
# Multiplayer Word Game
# -----------------------
elif page == "Play Game":
    st.subheader("🎲 Multiplayer Word Game")

    # --- Setup groups if not already ---
    if "groups" not in st.session_state:
        num_groups = st.number_input("Enter number of groups:", min_value=1, step=1, value=2)
        if st.button("Start Game"):
            st.session_state.groups = {f"Group {i+1}": 0 for i in range(num_groups)}
            st.session_state.current_group = 0
            st.session_state.current_item = ""
            st.session_state.current_level = "simple"
            st.session_state.current_type = "words"
            st.experimental_rerun()
        st.stop()

    group_names = list(st.session_state.groups.keys())
    current_group_name = group_names[st.session_state.current_group]
    st.markdown(f"### 🟢 Current Turn: {current_group_name}")

    # --- Select level and type ---
    col1, col2 = st.columns(2)
    with col1:
        level = st.radio("Level / سطح:", ("simple", "medium", "hard"), index=["simple","medium","hard"].index(st.session_state.current_level))
    with col2:
        item_type = st.radio("Type / نوع:", ("words", "sentences"), index=["words","sentences"].index(st.session_state.current_type))

    st.session_state.current_level = level
    st.session_state.current_type = item_type
    items = words_dict[level][item_type]

    if not items:
        st.warning("No items for this level/type!")
        st.stop()

    # --- Pick a word if not already ---
    if st.session_state.current_item == "":
        st.session_state.current_item = random.choice(items)

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
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("✅ Got it!"):
            # Add points based on difficulty
            if level == "simple":
                st.session_state.groups[current_group_name] += 1
            elif level == "medium":
                st.session_state.groups[current_group_name] += 2
            else:
                st.session_state.groups[current_group_name] += 3
            st.session_state.current_item = random.choice(items)
            st.experimental_rerun()

    with col2:
        if st.button("⏭ Skip"):
            st.session_state.groups[current_group_name] -= 1  # subtract 1 point
            st.session_state.current_item = random.choice(items)
            st.experimental_rerun()

    with col3:
        if st.button("➡️ Next Group"):
            st.session_state.current_group = (st.session_state.current_group + 1) % len(group_names)
            st.session_state.current_item = random.choice(items)  # first word for next group
            st.experimental_rerun()

    # --- Display scores ---
    st.markdown("### 🏆 Scores")
    for g, score in st.session_state.groups.items():
        st.write(f"{g}: {score}")
