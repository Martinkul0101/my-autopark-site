import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Налаштування сторінки
st.set_page_config(page_title="Autopark PRO", layout="wide", page_icon="🚛")

# Стилі
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #1f77b4; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Підключення
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

if 'view' not in st.session_state: st.session_state.view = "list"
if 'car_vin' not in st.session_state: st.session_state.car_vin = None

# --- SIDEBAR ---
st.sidebar.markdown("## 🚛 AUTOPARK PRO")
if st.sidebar.button("📋 Seznam vozidel"):
    st.session_state.view = "list"
    st.rerun()

# ==========================================
# 1. ГОЛОВНИЙ ЕКРАН
# ==========================================
if st.session_state.view == "list":
    st.title("🚚 Správa vozového parku")
    cars = supabase.table("cars").select("*").execute().data
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Počet vozidel", len(cars))
    col2.metric("Najeto celkem (km)", sum(int(c.get('mileage', 0)) for c in cars))
    
    st.divider()
    
    with st.expander("➕ Přidat nové vozidlo"):
        with st.form("add_car"):
            c1, c2 = st.columns(2)
            c_model = c1.text_input("Značka a model")
            c_spz = c2.text_input("SPZ")
            c_vin = c1.text_input("VIN kód")
            if st.form_submit_button("Uložit vozidlo"):
                supabase.table("cars").insert({"brand_model": c_model, "reg_number": c_spz, "vin": c_vin}).execute()
                st.rerun()

    for car in
