import streamlit as st
import json
import os
from datetime import datetime  # <--- ЦЕЙ РЯДОК МАЄ БУТИ ДОДАНИЙ

# --- НАЛАШТУВАННЯ ---
st.set_page_config(page_title="AutoCRM Pro", layout="wide", page_icon="🔧")

# --- ФУНКЦІЇ БАЗИ ДАНИХ ---
def load_db():
    if not os.path.exists("database.json"):
        initial_data = {"clients": [], "cars": []}
        with open("database.json", "w") as f: json.dump(initial_data, f)
        return initial_data
    with open("database.json", "r") as f:
        data = json.load(f)
        if "clients" not in data: data["clients"] = []
        if "cars" not in data: data["cars"] = []
        return data

def save_db(db):
    with open("database.json", "w") as f: json.dump(db, f, indent=4)

db = load_db()

# --- ІНТЕРФЕЙС ---
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
                save_db(db); st.rerun()
    with col2:
        for c in db["clients"]:
            with st.expander(f"👤 {c['name']} (📞 {c['phone']})"):
                cars = [car for car in db["cars"] if car.get("owner_id") == c["id"]]
                if cars:
                    for car in cars: st.write(f"🚗 {car['brand_model']} ({car['reg_number']})")
                else: st.warning("Žádná vozidla.")

# 2. ВКЛАДКА АВТО
# 2. ВКЛАДКА АВТО (ОНОВЛЕНА)
with tabs[1]:
    st.header("Vozový park")
    
    # Виводимо список авто у вигляді кнопок для вибору
    for i, car in enumerate(db["cars"]):
        with st.expander(f"🚗 {car['brand_model']} | {car['reg_number']}"):
            st.write(f"**VIN:** {car.get('vin', 'Nezadáno')}")
            
            # --- РЕДАГУВАННЯ ІНФО ---
            if st.checkbox(f"Upravit informace o {car['reg_number']}", key=f"edit_{i}"):
                with st.form(f"edit_form_{i}"):
                    new_model = st.text_input("Značka a model", value=car['brand_model'])
                    new_vin = st.text_input("VIN", value=car.get('vin', ''))
                    if st.form_submit_button("Uložit změny"):
                        db["cars"][i].update({"brand_model": new_model, "vin": new_vin})
                        save_db(db); st.rerun()

            # --- ІСТОРІЯ РОБІТ ---
            st.subheader("🛠 Historie servisů")
            repairs = [r for r in db.get("repairs", []) if r.get("car_index") == i]
            for r in repairs:
                st.info(f"📅 {r['date']}: {r['desc']} (Cena: {r['cost']} Kč)")

            # --- ДОДАВАННЯ НОВОГО ЗАПИСУ ---
            with st.expander("➕ Přidat záznam o servisu"):
                with st.form(f"repair_form_{i}"):
                    desc = st.text_input("Popis práce")
                    parts = st.text_area("Použité díly / Oleje")
                    cost = st.number_input("Cena (Kč)", min_value=0)
                    if st.form_submit_button("Uložit záznam"):
                        db.setdefault("repairs", []).append({
                            "car_index": i, "date": str(datetime.today().date()),
                            "desc": desc, "parts": parts, "cost": cost
                        })
                        save_db(db); st.rerun()

# 3. ВКЛАДКА ДОДАВАННЯ
with tabs[2]:
    st.header("Přidat nové auto")
    with st.form("car_form"):
        model = st.text_input("Značka a model")
        spz = st.text_input("SPZ")
        client_options = {c['name']: c['id'] for c in db["clients"]}
        selected_client = st.selectbox("Vyberte majitele", list(client_options.keys()))
        if st.form_submit_button("Uložit vozidlo"):
            db["cars"].append({"brand_model": model, "reg_number": spz, "owner_id": client_options[selected_client]})
            save_db(db); st.success("Vozidlo přidáno!"); st.rerun()
