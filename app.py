import streamlit as st
import requests
import datetime
import json



BASE_URL = "https://89mzoxcmub.execute-api.eu-west-3.amazonaws.com/prod"

st.set_page_config(page_title="AIVREST Chatbot", layout="centered")
st.title("🤖 AIVREST Coach")

# Choose endpoint
endpoint = st.sidebar.selectbox("Choose Function", [
    "Chat", "Training", "Save Program", "Get Programs",
    "Daily Program", "Chat History"
])


def display_response_as_cards(data, user_id=None):
    if not isinstance(data, list):
        data = [data]

    for item in data:
        content = item.get("content", "")
        image = item.get("image", {})
        response_type = item.get("type", "message")

        with st.container(border=True):
            if image.get("imagePath"):
                st.image(image["imagePath"], width=150)
            if content:
                st.markdown(content, unsafe_allow_html=True)
            else:
                st.info(" Pas de contenu textuel généré.")

            if response_type == "programme" and user_id:
                button_key = f"save_{hash(content)}"
                if st.button("💾 Enregistrer ce programme", key=button_key):
                    payload = {
                        "user_id": user_id,
                        "program_id": f"auto_{datetime.datetime.now().timestamp()}",
                        "title": image.get("title", "Programme Complet"),
                        "content": content,
                        "program_type": "sport",
                        "image": image.get("imagePath", ""),
                        "duration": image.get("duration", "30 min"),
                        "level": image.get("level", "débutant"),
                        "start_date": datetime.date.today().strftime("%Y-%m-%d")
                    }
                    try:
                        r = requests.post(f"{BASE_URL}/save_program", json=payload)
                        if r.status_code == 504:
                            st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
                        elif r.status_code == 200:
                            st.success(" Programme enregistré avec succès")
                        else:
                            st.error(f" Erreur API: {r.text}")
                    except Exception as e:
                        st.error(f" Connexion échouée : {e}")

# --- CHAT UI ---
if endpoint == "Chat":
    st.subheader("💬 Chat with AI Coach")

    col1, col2 = st.columns(2)
    user_id = col1.text_input("User ID", key="chat_user_id")
    chat_id = col2.text_input("Chat ID", key="chat_chat_id")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "prev_ids" not in st.session_state:
        st.session_state.prev_ids = (user_id, chat_id)
    elif st.session_state.prev_ids != (user_id, chat_id):
        st.session_state.chat_history = []
        st.session_state.prev_ids = (user_id, chat_id)

    #  Affichage de l’historique
    for msg in st.session_state.chat_history:
        role_label = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(role_label):
            st.markdown(msg.get("content", ""))
            image = msg.get("image")
            if image and image.get("imagePath"):
                st.image(image["imagePath"], width=150)

            #  Bouton enregistrer programme si assistant + type = programme
            if msg["role"] == "assistant" and msg.get("type") == "programme":
                button_key = f"save_btn_{hash(msg['content'])}"
                if st.button("💾 Enregistrer ce programme", key=button_key):
                    payload = {
                        "user_id": user_id,
                        "program_id": f"auto_{datetime.datetime.now().timestamp()}",
                        "title": msg["image"].get("title", "Programme Complet"),
                        "content": msg["content"],
                        "program_type": "sport",
                        "image": msg["image"].get("imagePath", ""),
                        "duration": msg["image"].get("duration", "30 min"),
                        "level": msg["image"].get("level", "débutant"),
                        "start_date": datetime.date.today().strftime("%Y-%m-%d")
                    }
                    try:
                        r = requests.post(f"{BASE_URL}/save_program", json=payload)
                        if r.status_code == 504:
                            st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
                        elif r.status_code == 200:
                            st.success(" Programme enregistré avec succès")
                        else:
                            st.error(f" Erreur API: {r.text}")
                    except Exception as e:
                        st.error(f" Connexion échouée : {e}")

    # --- Input
    user_message = st.chat_input("Tape ton message ici...")

    if user_message and user_id and chat_id:
        # Ajouter dans historique local
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })

        with st.spinner("Coach réfléchit..."):
            try:
                response = requests.post(f"{BASE_URL}/chat", json={
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "message": user_message
                })
                
                if response.status_code == 504:
                    st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
                elif response.status_code == 200:
                    data = response.json()
                    if not isinstance(data, list):
                        data = [data]

                    for ai_msg in data:
                        msg = {
                            "role": "assistant",
                            "content": ai_msg.get("content", ""),
                            "type": ai_msg.get("type", "message")
                        }
                        if ai_msg.get("image"):
                            msg["image"] = ai_msg["image"]

                        st.session_state.chat_history.append(msg)

                    st.rerun()

                else:
                    st.error(f" Erreur de l'API : {response.text}")
            except Exception as e:
                st.error(f" Connexion impossible : {e}")

# ----------------- TRAINING INTERFACE -----------------
 
elif endpoint == "Training":
    st.subheader("🏋️ Suivi d'entraînement personnalisé")

    col1, col2 = st.columns(2)
    user_id = col1.text_input("User ID", key="training_user_id")
    chat_id = col2.text_input("Chat ID", key="training_chat_id")

    
    user_message = st.chat_input("Pose ta question ou parle à ton coach...")

    if "training_history" not in st.session_state:
        st.session_state.training_history = []

    if "prev_training_ids" not in st.session_state:
        st.session_state.prev_training_ids = (user_id, chat_id)
    elif st.session_state.prev_training_ids != (user_id, chat_id):
        st.session_state.training_history = []
        st.session_state.prev_training_ids = (user_id, chat_id)

    #  Affichage de l'historique et bouton Enregistrer
    for msg in st.session_state.training_history:
        role = msg.get("role", "assistant")
        label = "user" if role == "user" else "assistant"

        with st.chat_message(label):
            st.markdown(msg.get("content", ""))
            image = msg.get("image") or {}
            if image.get("imagePath"):
                st.image(image["imagePath"], width=150)

            #  Enregistrer si assistant + type=programme
            if role == "assistant" and msg.get("type") == "programme":
                button_key = f"save_btn_{hash(msg['content'])}"
                if st.button("💾 Enregistrer ce programme", key=button_key):
                    payload = {
                        "user_id": user_id,
                        "program_id": f"auto_{datetime.datetime.now().timestamp()}",
                        "title": image.get("title", "Programme personnalisé"),
                        "content": msg["content"],
                        "program_type": "sport",
                        "image": image.get("imagePath", ""),
                        "duration": image.get("duration", "4 semaines"),
                        "level": image.get("level", "débutant"),
                        "start_date": datetime.date.today().strftime("%Y-%m-%d")
                    }
                    try:
                        r = requests.post(f"{BASE_URL}/save_program", json=payload)
                        if r.status_code == 504:
                            st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
                        elif r.status_code == 200:
                            st.success(" Programme enregistré avec succès.")
                        else:
                            st.error(f" Erreur API : {r.text}")
                    except Exception as e:
                        st.error(f" Erreur de connexion : {e}")

    # 🚀 Envoi du message utilisateur
    if user_message and user_id and chat_id:
        st.session_state.training_history.append({"role": "user", "content": user_message})
        try:
            with st.spinner("⏳ Envoi au coach..."):
                res = requests.post(
                    f"{BASE_URL}/training",
                    json={"user_id": user_id, "chat_id": chat_id, "message": user_message}
                )
                if res.status_code == 504:
                    st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
                elif res.status_code == 200:
                    data = res.json()
                    for item in data:
                        st.session_state.training_history.append({
                            "role": "assistant",
                            "content": item.get("content", ""),
                            "type": item.get("type"),
                            "image": item.get("image")
                        })
                    st.rerun()
                else:
                    st.error(f" Erreur backend : {res.text}")
        except Exception as e:
            st.error(f" Connexion impossible : {e}")


# ----------------- SAVE PROGRAM -----------------
elif endpoint == "Save Program":
    st.subheader("💾 Save Program")
    
    user_id = st.text_input("User ID", key="save_user")
    program_id = st.text_input("Program ID")
    title = st.text_input("Title")
    content = st.text_area("Program Content", height=300)
    program_type = st.selectbox("Program Type", ["sport", "alimentation"])
    
    col1, col2 = st.columns(2)
    image = col1.text_input("Image URL", "")
    duration = col2.text_input("Duration", "30 min")
    level = col1.selectbox("Level", ["débutant", "intermédiaire", "avancé"])
    start_date = col2.date_input("Start Date", value=datetime.date.today()).strftime("%Y-%m-%d")

    if st.button("Save Program"):
        payload = {
            "user_id": user_id,
            "program_id": program_id,
            "title": title,
            "content": content,
            "program_type": program_type,
            "image": image,
            "duration": duration,
            "level": level,
            "start_date": start_date
        }
        response = requests.post(f"{BASE_URL}/save_program", json=payload)
        if response.status_code == 504:
            st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
        elif response.status_code == 200:
            st.success(" Program saved successfully!")
        else:
            st.error(f" Error saving program: {response.text}")


# ----------------- GET PROGRAMS -----------------
elif endpoint == "Get Programs":
    st.subheader("📋 Saved Programs")
    
    user_id = st.text_input("User ID", key="all_user")

    if st.button("Get Programs"):
        try:
            response = requests.get(f"{BASE_URL}/get_all_programs", params={"user_id": user_id})
            if response.status_code == 504:
                st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
            elif response.status_code == 200:
                programs = response.json()
                for program in programs:
                    with st.expander(f"{program['title']} ({program['type']})"):
                        st.markdown(f"**ID:** {program['program_id']}")
                        st.markdown(f"**Duration:** {program.get('duration', 'N/A')}")
                        st.markdown(f"**Level:** {program.get('level', 'N/A')}")
                        st.markdown(f"**Start Date:** {program.get('start_date', 'N/A')}")
                        if program.get('image'):
                            st.image(program['image'], width=200)
                        st.markdown(program['content'])
            else:
                st.error(response.text)
        except Exception as e:
            st.error(f"Error: {e}")

# ----------------- DAILY PROGRAM -----------------
elif endpoint == "Daily Program":
    st.subheader("📆 Daily Program")
    
    col1, col2 = st.columns(2)
    user_id = col1.text_input("User ID", key="daily_user")
    program_id = col2.text_input("Program ID", key="daily_program_id")
    selected_date = st.date_input("Select Date", value=datetime.date.today()).strftime("%Y-%m-%d")

    if st.button("Get Daily Program"):
        with st.spinner("Generating daily program..."):
            try:
                response = requests.post(f"{BASE_URL}/get_day_program", json={
                    "user_id": user_id,
                    "program_id": program_id,
                    "selected_date": selected_date
                })
                
                if response.status_code == 504:
                    st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
                elif response.status_code == 200:
                    data = response.json()
                    st.success(f" Program for day {data['day_index']}")
                    
                    try:
                        program_data = json.loads(data["ai_response"])
                        
                        if "nutrition" in program_data:
                            st.subheader("🍽 Nutrition Plan")
                            for meal in program_data["nutrition"]:
                                with st.expander(f"{meal['meal_type']}: {meal['title']}"):
                                    st.markdown(f"**Calories:** {meal['kcal']}")
                                    st.markdown(f"**Macros:** Proteins: {meal['macros']['proteins']}g, Carbs: {meal['macros']['carbs']}g, Fats: {meal['macros']['fats']}g")
                                    st.markdown(f"**Description:** {meal['description']}")
                        
                        if "sport" in program_data:
                            st.subheader("🏃‍♂️ Training Plan")
                            for exercise in program_data["sport"]:
                                with st.expander(f"{exercise['zone']}: {exercise['title']}"):
                                    st.markdown(f"**Duration:** {exercise['duration']}")
                                    st.markdown(f"**Description:** {exercise['description']}")
                    
                    except json.JSONDecodeError:
                        st.warning(" Could not parse program details")
                        st.code(data["ai_response"])
                else:
                    st.error(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

# ----------------- CHAT HISTORY -----------------
elif endpoint == "Chat History":
    st.subheader("📜 Historique des Conversations")

    user_id = st.text_input("User ID", key="chat_user_id_history")

    if user_id:
        try:
            #  Récupère toutes les conversations de l'utilisateur
            response = requests.get(f"{BASE_URL}/get_all_chats", params={"user_id": user_id})
            if response.status_code == 504:
                st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
            elif response.status_code == 200:
                chats = response.json()
                if not chats:
                    st.info("Aucune conversation trouvée.")
                else:
                    chat_titles = [f"{chat['title']} ({chat['chat_id']})" for chat in chats]
                    selected = st.selectbox("🗂 Choisissez une conversation", chat_titles)

                    selected_chat_id = selected.split("(")[-1].replace(")", "").strip()

                    if st.button("📂 Afficher les messages"):
                        try:
                            msg_response = requests.get(f"{BASE_URL}/get_chat_messages", params={
                                "user_id": user_id,
                                "chat_id": selected_chat_id
                            })

                            if msg_response.status_code == 504:
                                st.warning(" Le coach met trop de temps à répondre. Veuillez réessayer plus tard.")
                            elif msg_response.status_code == 200:
                                messages = msg_response.json()

                                for msg in messages:
                                    role_raw = msg.get("role", "")
                                    content_raw = msg.get("content", "")

                                    if not isinstance(content_raw, str) or not content_raw.strip():
                                        continue  # Ignore messages vides

                                    role = str(role_raw).strip().lower()
                                    content = content_raw.strip()
                                    
                                    role_streamlit = "user" if role == "user" else "assistant"
                                    

                                    with st.chat_message(role_streamlit):
                                        st.markdown(f" {content}")

                                        if msg.get("type") == "programme":
                                            image = msg.get("image", {})
                                            if isinstance(image, dict) and image.get("imagePath"):
                                                st.image(image["imagePath"], width=150)

                            else:
                                st.error(f"Erreur API : {msg_response.text}")
                        except Exception as e:
                            st.error(f"Erreur de récupération : {e}")
            else:
                st.error(f"Erreur : {response.text}")
        except Exception as e:
            st.error(f"Erreur : {e}")

