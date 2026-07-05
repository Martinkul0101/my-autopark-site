import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Налаштування сторінки
st.set_page_config(page_title="Autopark Servisní Kniha", layout="wide", page_icon="🚛")

# Підключення
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

if 'view' not in st.session_state: st.session_state.view = "list"
if 'car_vin' not in st.session_state: st.session_state.car_vin = None

# --- ГОЛОВНА ---
if st.session_state.view == "list":
    st.title("🚛 Přehled vozidel")
    cars = supabase.table("cars").select("*").execute().data
    
    with st.expander("➕ Přidat nové auto"):
        with st.form("add_car"):
            col1, col2 = st.columns(2)
            c_model = col1.text_input("Značka a model")
            c_spz = col2.text_input("SPZ")
            c_vin = col1.text_input("VIN kód")
            if st.form_submit_button("Uložit"):
                supabase.table("cars").insert({"brand_model": c_model, "reg_number": c_spz, "vin": c_vin}).execute()
                st.rerun()

    for car in cars:
        with st.container(border=True):
            cols = st.columns([4, 1])
            cols[0].markdown(f"### {car['brand_model']} ({car['reg_number']})")
            cols[0].caption(f"VIN: {car['vin']}")
            if cols[1].button("Otevřít knihu", key=car['vin']):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()

# --- СЕРВІСНА КНИГА ---
elif st.session_state.view == "details":
    car = supabase.table("cars").select("*").eq("vin", st.session_state.car_vin).execute().data[0]
    
    if st.button("⬅ Zpět"):
        st.session_state.view = "list"
        st.rerun()
        
    st.title(f"📄 {car['brand_model']} - Servisní kniha")
    
    # 1. ТЕХНІЧНИЙ ПАСПОРТ
    with st.container(border=True):
        st.subheader("📋 Technický pasport")
        col1, col2, col3 = st.columns(3)
        with st.form("tech_data"):
            c1, c2, c3, c4 = st.columns(4)
            vin = c1.text_input("VIN kód", value=car.get('vin', ''))
            oil_m = c2.text_input("Motorový olej", value=car.get('oil_motor', ''))
            oil_k = c3.text_input("Olej v KPP", value=car.get('oil_kpp', ''))
            oil_d = c4.text_input("Olej v dif.", value=car.get('oil_dif', ''))
            
            c_stk = col1.date_input("Poslední STK", value=pd.to_datetime(car.get('stk_date', datetime.now())))
            c_to = col2.date_input("Poslední ТО", value=pd.to_datetime(car.get('to_date', datetime.now())))
            
            if st.form_submit_button("💾 Uložit pasport"):
                supabase.table("cars").update({
                    "oil_motor": oil_m, "oil_kpp": oil_k, "oil_dif": oil_d,
                    "stk_date": str(c_stk), "to_date": str(c_to)
                }).eq("vin", car['vin']).execute()
                st.rerun()

    # 2. ІСТОРІЯ ТА ЗАПЧАСТИНИ
    st.subheader("🔧 Servisní historie a díly")
    with st.form("add_work"):
        desc = st.text_input("Co bylo provedeno a jaké díly/oleje použity?")
        if st.form_submit_button("➕ Přidat záznam"):
            supabase.table("repairs").insert({
                "vin": car['vin'], "description": desc, "date": str(datetime.now().date())
            }).execute()
            st.rerun()
            
    hist = supabase.table("repairs").select("*").eq("vin", car['vin']).order("date", desc=True).execute().data
    if hist:
        st.table(pd.DataFrame(hist)[['date', 'description']])
