import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Налаштування сторінки
st.set_page_config(page_title="Správa Autoparku", layout="wide", page_icon="🚚")

# Підключення до Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def get_status_icon(date_str):
    if not date_str: return "⚪"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        days_left = (dt - datetime.now()).days
        return "❌" if days_left < 0 else ("⚠️" if days_left <= 30 else "✅")
    except: return "⚪"

# --- НАВІГАЦІЯ ---
if 'view' not in st.session_state: st.session_state.view = "list"
if 'car_vin' not in st.session_state: st.session_state.car_vin = None

st.sidebar.title("🛠 AUTOPARK")
if st.sidebar.button("🚗 Seznam vozidel"): 
    st.session_state.view = "list"
    st.rerun()
menu = st.sidebar.radio("Navigace:", ["Hlavní strana", "Sklad náhradních dílů"])

# ==========================================
# 1. ГОЛОВНИЙ ЕКРАН (СПИСОК + ДОДАВАННЯ)
# ==========================================
if menu == "Hlavní strana" and st.session_state.view == "list":
    st.title("🚚 Stručný přehled vozového parku")
    
    # Форма додавання нового авто
    with st.expander("➕ Přidat nové vozidlo"):
        with st.form("add_car_form"):
            c_model = st.text_input("Značka a model")
            c_spz = st.text_input("SPZ")
            c_vin = st.text_input("VIN kód")
            c_km = st.number_input("Aktuální stav tachometru", min_value=0)
            c_stk = st.date_input("Termín STK")
            
            if st.form_submit_button("Uložit vozidlo"):
                supabase.table("cars").insert({
                    "brand_model": c_model, "reg_number": c_spz, 
                    "vin": c_vin, "mileage": c_km, "stk_date": str(c_stk)
                }).execute()
                st.success("Vozidlo bylo přidáno!")
                st.rerun()

    cars = supabase.table("cars").select("*").execute().data
    
    # Пошук
    car_options = {f"{c['brand_model']} ({c['reg_number']})": c['vin'] for c in cars}
    selected = st.selectbox("🔍 Rychlé vyhledávání:", ["-- Vyberte vozidlo --"] + list(car_options.keys()))
    
    if selected != "-- Vyberte vozidlo --":
        st.session_state.car_vin = car_options[selected]
        st.session_state.view = "details"
        st.rerun()

    for car in cars:
        stk_icon = get_status_icon(car.get('stk_date'))
        with st.container(border=True):
            cols = st.columns([1, 4, 3])
            cols[0].markdown("### 🚛")
            cols[1].markdown(f"### {car['brand_model']} - {car['reg_number']}")
            cols[1].caption(f"Stav tachometru: {car.get('mileage', 0)} km | VIN: {car['vin']}")
            cols[2].write(f"**STK:** {stk_icon}")
            if cols[2].button("Detaily", key=f"det_{car['vin']}"):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()

# ==========================================
# 2. ЕКРАН ДЕТАЛЕЙ
# ==========================================
elif st.session_state.view == "details":
    car = supabase.table("cars").select("*").eq("vin", st.session_state.car_vin).execute().data[0]
    if st.button("⬅ Zpět na seznam"):
        st.session_state.view = "list"
        st.rerun()
    st.title(f"📄 Karta vozidla: {car['brand_model']}")
    # (Решта деталей залишається без змін)
    
# ==========================================
# 3. ЕКРАН СКЛАДУ
# ==========================================
elif menu == "Sklad náhradních dílů":
    # (Логіка складу залишається без змін)
    st.title("📦 Sklad náhradních dílů")
    stock = supabase.table("stock").select("*").execute().data
    st.dataframe(pd.DataFrame(stock), use_container_width=True)
