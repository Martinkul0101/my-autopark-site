import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Налаштування сторінки
st.set_page_config(page_title="Správa Vozového Parku", layout="centered", page_icon="🚚")
DB_FILE = "database.json"

# --- БАЗА ДАНИХ ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {"cars": [], "repairs": [], "stock": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"cars": [], "repairs": [], "stock": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

# --- БІЧНЕ МЕНЮ ---
st.sidebar.title("🚚 AUTOPARK")
menu = st.sidebar.radio("NAVIGACE", ["📋 SEZNAM VOZIDEL", "➕ PŘIDAT VOZIDLO", "📦 SKLAD NÁHRADNÍCH DÍLŮ"])

# Функції перевірки (винесені для чистоти)
def zkontrolovat_datum(date_str):
    try:
        t_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        days = (t_date - datetime.today().date()).days
        if days < 0: return f"🚨 PROŠLÉ! ({abs(days)} dní)"
        if days <= 30: return f"⚠️ Končí za {days} dní"
        return f"✅ V pořádku ({days} dní)"
    except: return "—"

# --- ЕКРАН 1: SEZNAM VOZIDEL ---
if menu == "📋 SEZNAM VOZIDEL":
    st.title("📋 Seznam vozidel")
    if not db["cars"]:
        st.info("Žádná vozidla.")
    else:
        df_cars = pd.DataFrame(db["cars"])
        # Використовуємо selection_mode="single-row" для вибору
        event = st.dataframe(df_cars, use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun")
        
        # Обробка вибору через session_state (новий стандарт Streamlit)
        selection = event.selection.get("rows", [])
        if selection:
            idx = selection[0]
            car = db["cars"][idx]
            st.header(f"📇 {car.get('brand_model')}")
            # (Тут ваш код для форми ремонту...)

# --- ЕКРАН 3: SKLAD ---
elif menu == "📦 SKLAD NÁHRADNÍCH DÍLŮ":
    st.title("📦 Sklad náhradních dílů")
    # ... ваша форма додавання ...
    
    st.subheader("📋 Aktuální stav skladu")
    if db["stock"]:
        df_stock = pd.DataFrame(db["stock"])
        st.dataframe(df_stock, use_container_width=True)
    else:
        st.write("Sklad je prázdný.")
