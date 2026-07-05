import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Správa Autoparku", layout="wide", page_icon="🚚")

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

if 'view' not in st.session_state: st.session_state.view = "list"
if 'car_vin' not in st.session_state: st.session_state.car_vin = None

st.sidebar.title("🛠 AUTOPARK")
if st.sidebar.button("🚗 Seznam vozidel"): 
    st.session_state.view = "list"
    st.rerun()
menu = st.sidebar.radio("Navigace:", ["Hlavní strana", "Sklad náhradních dílů"])

# ==========================================
# 1. ГОЛОВНИЙ ЕКРАН
# ==========================================
if menu == "Hlavní strana" and st.session_state.view == "list":
    st.title("🚚 Stručný přehled vozového parku")
    
    with st.expander("➕ Přidat nové vozidlo"):
        with st.form("add_car"):
            c_model = st.text_input("Značka a model")
            c_spz = st.text_input("SPZ")
            c_vin = st.text_input("VIN kód")
            c_km = st.number_input("Stav tachometru", min_value=0)
            c_stk = st.date_input("Termín STK")
            if st.form_submit_button("Uložit"):
                supabase.table("cars").insert({
                    "brand_model": c_model, "reg_number": c_spz, 
                    "vin": c_vin, "mileage": c_km, "stk_date": str(c_stk)
                }).execute()
                st.rerun()

    cars = supabase.table("cars").select("*").execute().data
    for car in cars:
        with st.container(border=True):
            cols = st.columns([1, 4, 2])
            cols[0].write("🚛")
            cols[1].write(f"### {car['brand_model']} - {car['reg_number']}")
            if cols[2].button("Detaily", key=f"det_{car['vin']}"):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()

# ==========================================
# 2. ЕКРАН ДЕТАЛЕЙ (ВИПРАВЛЕНИЙ)
# ==========================================
elif st.session_state.view == "details":
    car = supabase.table("cars").select("*").eq("vin", st.session_state.car_vin).execute().data[0]
    
    if st.button("⬅ Zpět"):
        st.session_state.view = "list"
        st.rerun()
        
    st.title(f"📄 Karta: {car['brand_model']}")
    
    tab1, tab2 = st.tabs(["⚙️ Upravit údaje", "🔧 Servis a historie"])
    
    with tab1: # РЕДАГУВАННЯ
        with st.form("edit_car"):
            new_model = st.text_input("Značka a model", value=car['brand_model'])
            new_spz = st.text_input("SPZ", value=car['reg_number'])
            new_km = st.number_input("Stav tachometru", value=int(car['mileage']))
            if st.form_submit_button("💾 Uložit změny"):
                supabase.table("cars").update({
                    "brand_model": new_model, "reg_number": new_spz, "mileage": new_km
                }).eq("vin", car['vin']).execute()
                st.success("Aktualizováno!")
                st.rerun()

    with tab2: # СЕРВІС ТА ІСТОРІЯ
        with st.form("add_repair"):
            desc = st.text_input("Popis opravy")
            cost = st.number_input("Cena", min_value=0)
            if st.form_submit_button("➕ Přidat opravu"):
                supabase.table("repairs").insert({
                    "vin": car['vin'], "description": desc, "cost": cost
                }).execute()
                st.rerun()
        
        hist = supabase.table("repairs").select("*").eq("vin", car['vin']).execute().data
        if hist: st.dataframe(pd.DataFrame(hist))
        else: st.info("Žádná historie.")

# ==========================================
# 3. ЕКРАН СКЛАДУ
# ==========================================
elif menu == "Sklad náhradních dílů":
    st.title("📦 Sklad náhradních dílů")
    # (Логіка складу як раніше)
    stock = supabase.table("stock").select("*").execute().data
    st.dataframe(pd.DataFrame(stock), use_container_width=True)
