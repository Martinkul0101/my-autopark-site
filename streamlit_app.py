import streamlit as st
import json
import os

# --- НАЛАШТУВАННЯ ---
st.set_page_config(page_title="AutoCRM Pro", layout="wide", page_icon="🔧")

# --- БД З АВТО-ВИПРАВЛЕННЯМ ---
def load_db():
    if not os.path.exists("database.json"):
        initial_data = {"clients": [], "cars": [], "repairs": []}
        with open("database.json", "w") as f:
            json.dump(initial_data, f)
        return initial_data
    
    with open("database.json", "r") as f:
        data = json.load(f)
        # Гарантуємо наявність ключів
        if "clients" not in data: data["clients"] = []
        if "cars" not in data: data["cars"] = []
        if "repairs" not in data: data["repairs"] = []
        return data

db = load_db()

def save_db(db):
    with open("database.json", "w") as f:
        json.dump(db, f, indent=4)

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
                new_id = len(db["clients"]) + 1
                db["clients"].append({"id": new_id, "name": name, "phone": phone})
                save_db(db)
                st.rerun()
    with col2:
        st.write("### Seznam registrovaných klientů")
        if not db["clients"]:
            st.info("Zatím žádní klienti.")
        for c in db["clients"]:
            st.success(f"👤 {c['name']} | 📞 {c['phone']}")

# 2. ВКЛАДКА АВТО
with tabs[1]:
    st.header("Vozový park")
    if not db["cars"]:
        st.info("Seznam vozidel je prázdný.")
    for car in db["cars"]:
        st.write(f"🚗 {car['brand_model']} ({car['reg_number']})")

# 3. ВКЛАДКА ДОДАВАННЯ
with tabs[2]:
    st.header("Přidat nové auto")
    with st.form("car_form"):
        model = st.text_input("Značka a model")
        spz = st.text_input("SPZ")
        # Вибір клієнта
        client_names = {c['name']: c['id'] for c in db["clients"]}
        selected_client = st.selectbox("Vyberte majitele", list(client_names.keys()))
        
        if st.form_submit_button("Uložit vozidlo"):
            db["cars"].append({
                "brand_model": model, 
                "reg_number": spz, 
                "owner_id": client_names[selected_client]
            })
            save_db(db)
            st.success("Vozidlo přidáno!")
            st.rerun()
