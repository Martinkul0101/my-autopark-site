import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Nastavení stránky
st.set_page_config(page_title="Správa Vozového Parku", layout="wide")
DB_FILE = "garage_db.json"

# Funkce pro načítání dat
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

# --- LOGIKA APLIKACE ---
if menu == "📋 SEZNAM VOZIDEL":
    st.markdown("# 📋 Seznam vozidel")
    if not db["cars"]:
        st.info("Zatím nejsou žádná vozidla.")
    else:
        car_list = [f"{
