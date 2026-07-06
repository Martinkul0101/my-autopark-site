import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Nastavení stránky
st.set_page_config(page_title="Správa Vozového Parku", layout="wide")
DB_FILE = "garage_db.json"

# Funkce pro načítání a ukládání dat
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"cars": {}, "repairs": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_data()
db = st.session_state.db

# --- BOČNÍ PANEL ---
st.sidebar.markdown("<h2 style='color: #1a73e8; text-align: center;'>🚚 AUTOPARK</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("NAVIGACE", ["📋 SEZNAM VOZIDEL", "➕ PŘIDAT VOZIDLO", "📊 CELKOVÝ DENÍK SERVISU"])

# Funkce pro kontrolu termínů
def check_dates_alert(date_str):
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        days_left = (target_date - datetime.today().date()).days
        if days_left < 0: return "🚨 PROŠLÉ!", "red"
        elif days_left <= 30: return f"⚠️ Končí za {days_left} dní", "orange"
        return f"✅ V pořádku ({days_left} dní)", "green"
    except: return "—", "gray"

# --- HLAVNÍ LOGIKA ---
if menu == "📋 SEZNAM VOZIDEL":
    st.markdown("# 📋 Seznam vozidel")
    if not db["cars"]:
        st.info("Zatím nejsou žádná vozidla.")
    else:
        car_list = []
        for vin, car in db["cars"].items():
            display_str = f"{car.get('brand_model', 'Neznámé')} [{car.get('reg_number', '—')}] (VIN: {vin})"
            car_list.append(display_str)
        
        selected_car = st.selectbox("Vyberte vozidlo:", ["-- Vyberte --"] + car_list)
        
        if selected_car != "-- Vyberte --":
            active_vin = selected_car.split("VIN: ")[-1].replace(")", "")
            car_data = db["cars"][active_vin]
            st.markdown(f"### Karta vozidla: {car_data.get('brand_model')}")
            st.write(f"**VIN:** {active_vin} | **SPZ:** {car_data.get('reg_number')}")

elif menu == "➕ PŘIDAT VOZIDLO":
    st.markdown("# ➕ Registrace nového vozidla")
    with st.form("add_car"):
        col1, col2 = st.columns(2)
        vin = col1.text_input("VIN kód").strip().upper()
        brand = col2.text_input("Značka a model")
        reg = col1.text_input("SPZ")
        mileage = col2.text_input("Stav tachometru", "0")
        stk = st.date_input("Platnost STK")
        
        if st.form_submit_button("Uložit"):
            if not vin:
                st.error("VIN kód je povinný!")
            elif vin in db["cars"]:
                st.error("Vozidlo s tímto VIN již existuje!")
            else:
                db["cars"][vin] = {
                    "brand_model": brand, 
                    "reg_number": reg, 
                    "mileage": mileage, 
                    "stk_date": str(stk)
                }
                save_data(db)
                st.success("Vozidlo úspěšně uloženo!")
                st.rerun()

elif menu == "📊 CELKOVÝ DENÍK SERVISU":
    st.markdown("# 📊 Celkový deník servisu")
    if not db["repairs"]:
        st.info("Žádné záznamy.")
    else:
        df = pd.DataFrame(db["repairs"])
        st.dataframe(df, use_container_width=True)
