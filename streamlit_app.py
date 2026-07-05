import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Autopark PRO", layout="wide", page_icon="🚛")

# --- СТИЛІЗАЦІЯ (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .car-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .metric-card { background: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# --- БАЗА ---
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

if 'view' not in st.session_state: st.session_state.view = "list"
if 'car_vin' not in st.session_state: st.session_state.car_vin = None

# --- SIDEBAR ---
st.sidebar.title("🛠 AUTOPARK")
if st.sidebar.button("🏠 Seznam vozidel"):
    st.session_state.view = "list"
    st.rerun()

# --- ПЕРЕГЛЯД ---
if st.session_state.view == "list":
    st.title("🚛 Dashboard vozového parku")
    cars = supabase.table("cars").select("*").execute().data
    
    # Створення карток
    for car in cars:
        with st.container():
            st.markdown(f'<div class="car-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            col1.markdown(f"### {car['brand_model']}  `{car['reg_number']}`")
            col1.caption(f"VIN: {car['vin']}")
            if col2.button("Detail vozidla", key=car['vin']):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view == "details":
    car = supabase.table("cars").select("*").eq("vin", st.session_state.car_vin).execute().data[0]
    
    st.title(f"{car['brand_model']}")
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("💧 Technické údaje")
        with st.form("tech_form"):
            oil_m = st.text_input("Motorový olej", value=car.get('oil_motor', ''))
            oil_k = st.text_input("Olej v KPP", value=car.get('oil_kpp', ''))
            oil_d = st.text_input("Olej v dif.", value=car.get('oil_dif', ''))
            st_date = st.date_input("Termín STK", value=pd.to_datetime(car.get('stk_date', datetime.now())))
            if st.form_submit_button("💾 Uložit data"):
                supabase.table("cars").update({"oil_motor": oil_m, "oil_kpp": oil_k, "oil_dif": oil_d, "stk_date": str(st_date)}).eq("vin", car['vin']).execute()
                st.rerun()

    with col_b:
        st.subheader("🔧 Historie údržby")
        with st.form("history_form"):
            new_record = st.text_input("Popis práce a použité díly")
            if st.form_submit_button("➕ Přidat záznam"):
                supabase.table("repairs").insert({"vin": car['vin'], "description": new_record, "date": str(datetime.now().date())}).execute()
                st.rerun()
        
        hist = supabase.table("repairs").select("*").eq("vin", car['vin']).order("date", desc=True).execute().data
        for row in hist:
            st.warning(f"**{row['date']}**: {row['description']}")
