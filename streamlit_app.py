import streamlit as st
import json
import os
from datetime import datetime

# --- ФУНКЦІЇ БАЗИ ДАНИХ ---
DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"clients": [], "cars": [], "repairs": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

db = load_db()

# --- НАВІГАЦІЯ ---
st.sidebar.title("🚚 AUTOPARK CRM")
menu = st.sidebar.radio("NAVIGACE", ["📋 Seznam vozidel", "👥 Klienti", "➕ Přidat záznam"])

# --- ЛОГІКА КЛІЄНТІВ ---
if menu == "👥 Klienti":
    st.header("👥 Správa klientů")
    with st.form("add_client"):
        name = st.text_input("Jméno a příjmení")
        phone = st.text_input("Telefon")
        if st.form_submit_button("Přidat klienta"):
            db["clients"].append({"id": len(db["clients"])+1, "name": name, "phone": phone})
            save_data(db)
            st.rerun()
    
    st.write("### Seznam klientů")
    for client in db["clients"]:
        st.write(f"👤 **{client['name']}** | 📞 {client['phone']}")

# --- ЛОГІКА АВТОМОБІЛІВ ---
# --- ЛОГІКА ДОДАВАННЯ ---
elif menu == "➕ Přidat záznam":
    st.header("➕ Přidat nové vozidlo")
    
    if not db["clients"]:
        st.warning("Nejdříve musíte přidat alespoň jednoho klienta v sekci 'Klienti'.")
    else:
        with st.form("new_car"):
            model = st.text_input("Značka a model")
            vin = st.text_input("VIN")
            spz = st.text_input("SPZ")
            
            # Створюємо словник клієнтів
            client_options = {c['name']: c['id'] for c in db.get("clients", [])}
            owner_name = st.selectbox("Vyberte majitele", list(client_options.keys()))
            
            # ТУТ БУЛА ВІДСУТНЯ КНОПКА
            submit = st.form_submit_button("Uložit vozidlo")
            
            if submit:
                db["cars"].append({
                    "brand_model": model, 
                    "vin": vin, 
                    "reg_number": spz, 
                    "owner_id": client_options[owner_name], 
                    "mileage": 0
                })
                save_data(db)
                st.success("Vozidlo úspěšně přidáno!")

# --- ЛОГІКА ДОДАВАННЯ ---
elif menu == "➕ Přidat záznam":
    st.header("➕ Přidat nové vozidlo")
    with st.form("new_car"):
        model = st.text_input("Značka a model")
        vin = st.text_input("VIN")
        spz = st.text_input("SPZ")
        client_options = {c['name']: c['id'] for c in db["clients"]}
        owner_name = st.selectbox("Vyberte majitele", list(client_options.keys()))
        
        if st.form_submit_button("Uložit vozidlo"):
            db["cars"].append({
                "brand_model": model, "vin": vin, "reg_number": spz, 
                "owner_id": client_options[owner_name], "mileage": 0
            })
            save_data(db)
            st.success("Vozidlo přidáno!")
