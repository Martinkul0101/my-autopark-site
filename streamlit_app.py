import streamlit as st
import json
import os
from datetime import datetime

# --- НАЛАШТУВАННЯ ---
st.set_page_config(page_title="AutoCRM Pro", layout="wide", page_icon="🔧")

# --- БАЗА ДАНИХ ---
def load_db():
    if not os.path.exists("database.json"):
        return {"clients": [], "cars": [], "repairs": []}
    with open("database.json", "r") as f:
        data = json.load(f)
        data.setdefault("clients", []); data.setdefault("cars", []); data.setdefault("repairs", [])
        return data

def save_db(db):
    with open("database.json", "w") as f: json.dump(db, f, indent=4)

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
                db["clients"].append({"id": len(db["clients"])+1, "name": name, "phone": phone})
                save_db(db); st.rerun()
    with col2:
        for c in db["clients"]:
            with st.expander(f"👤 {c['name']}"):
                cars = [ (i, car) for i, car in enumerate(db["cars"]) if car.get("owner_id") == c["id"]]
                for i, car in cars:
                    st.write(f"🚗 {car['brand_model']} ({car['reg_number']})")

# 2. ВКЛАДКА АВТО
with tabs[1]:
    st.header("Vozový park")
    for i, car in enumerate(db["cars"]):
        with st.expander(f"🚗 {car['brand_model']} | {car['reg_number']}"):
            st.subheader("🛠 Historie servisů")
            repairs = [r for r in db.get("repairs", []) if r.get("car_index") == i]
            for r in repairs:
                st.info(f"📅 {r['date']}: {r['desc']} ({r['cost']} Kč)")
            
            with st.form(f"repair_form_{i}"):
                desc = st.text_input("Popis práce")
                cost = st.number_input("Cena", min_value=0)
                if st.form_submit_button("Přidat záznam"):
                    db.setdefault("repairs", []).append({"car_index": i, "date": str(datetime.today().date()), "desc": desc, "cost": cost})
                    save_db(db); st.rerun()

# 3. ВКЛАДКА ДОДАВАННЯ
with tabs[2]:
    st.header("Přidat nové auto")
    with st.form("car_form"):
        model = st.text_input("Značka a model")
        spz = st.text_input("SPZ")
        client_options = {c['name']: c['id'] for c in db["clients"]}
        selected = st.selectbox("Majitel", list(client_options.keys()))
        if st.form_submit_button("Uložit"):
            db["cars"].append({"brand_model": model, "reg_number": spz, "owner_id": client_options[selected]})
            save_db(db); st.rerun()
