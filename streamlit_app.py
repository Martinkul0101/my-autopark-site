import streamlit as st
import json
import os

# --- НАЛАШТУВАННЯ ---
st.set_page_config(page_title="AutoCRM Pro", layout="wide", page_icon="🔧")

# CSS для "професійного" вигляду
st.markdown("""
    <style>
    .client-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 10px; }
    .car-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- БД ---
def load_db():
    if not os.path.exists("database.json"):
        return {"clients": [], "cars": [], "repairs": []}
    with open("database.json", "r") as f:
        data = json.load(f)
        return data

db = load_db()

# --- МЕНЮ ---
st.title("🔧 AutoCRM Professional")
tabs = st.tabs(["👥 Klienti", "🚗 Vozový park", "➕ Nový záznam"])

# 1. ВКЛАДКА КЛІЄНТІВ
with tabs[0]:
    st.header("Správa klientů")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("client_form"):
            name = st.text_input("Jméno klienta")
            phone = st.text_input("Telefon")
            if st.form_submit_button("Přidat klienta"):
                db["clients"].append({"id": len(db["clients"]), "name": name, "phone": phone})
                with open("database.json", "w") as f: json.dump(db, f)
                st.rerun()
    with col2:
        for c in db["clients"]:
            st.markdown(f"<div class='client-card'>👤 <b>{c['name']}</b> | 📞 {c['phone']}</div>", unsafe_allow_html=True)

# 2. ВКЛАДКА АВТО
with tabs[1]:
    st.header("Seznam vozidel")
    for car in db["cars"]:
        st.markdown(f"<div class='car-card'>🚗 <b>{car['brand_model']}</b> ({car['reg_number']})</div>", unsafe_allow_html=True)

# 3. ВКЛАДКА ДОДАВАННЯ
with tabs[2]:
    st.header("Přidat nové auto")
    # Тут буде форма додавання авто...
