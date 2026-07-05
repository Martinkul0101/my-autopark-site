import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Autopark PRO", layout="wide")

# --- СТИЛІ ---
st.markdown("""
    <style>
    .card { background: #ffffff; padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- БАЗА (з кешуванням) ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- ФУНКЦІЇ ОНОВЛЕННЯ ---
@st.fragment
def render_repairs(vin):
    st.subheader("🔧 Historie oprav")
    with st.form("add_rep", clear_on_submit=True):
        desc = st.text_input("Práce/Díly")
        if st.form_submit_button("Přidat"):
            supabase.table("repairs").insert({"vin": vin, "description": desc, "date": str(datetime.now().date())}).execute()
            st.rerun()
    
    hist = supabase.table("repairs").select("*").eq("vin", vin).order("date", desc=True).execute().data
    for h in hist:
        st.info(f"**{h['date']}**: {h['description']}")

# --- ЛОГІКА ---
if 'view' not in st.session_state: st.session_state.view = "list"

if st.session_state.view == "list":
    st.title("🚛 Vozový park")
    cars = supabase.table("cars").select("*").execute().data
    for car in cars:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            col1.write(f"### {car.get('brand_model', 'Neznámý model')}")
            col1.caption(f"VIN: {car.get('vin')}")
            if col2.button("Detail", key=f"btn_{car['vin']}"):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view == "details":
    vin = st.session_state.car_vin
    car = supabase.table("cars").select("*").eq("vin", vin).execute().data[0]
    
    if st.button("⬅ Zpět"):
        st.session_state.view = "list"
        st.rerun()
        
    st.title(f"📄 {car['brand_model']}")
    
    c1, c2 = st.columns(2)
    with c1:
        with st.form("tech_form"):
            oil_m = st.text_input("Motorový olej", value=car.get('oil_motor', ''))
            oil_k = st.text_input("Olej KPP", value=car.get('oil_kpp', ''))
            if st.form_submit_button("Uložit údaje"):
                supabase.table("cars").update({"oil_motor": oil_m, "oil_kpp": oil_k}).eq("vin", vin).execute()
                st.success("Uloženo")
    
    with c2:
        render_repairs(vin)
