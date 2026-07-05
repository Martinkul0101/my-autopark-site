import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Autopark PRO", layout="wide", page_icon="🚛")

# --- СТИЛІЗАЦІЯ (CSS) ---
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; color: #1f77b4; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

if 'view' not in st.session_state: st.session_state.view = "list"
if 'car_vin' not in st.session_state: st.session_state.car_vin = None

# --- SIDEBAR (Навігація) ---
st.sidebar.markdown("## 🚛 AUTOPARK PRO")
if st.sidebar.button("📋 Seznam vozidel"):
    st.session_state.view = "list"
    st.rerun()

# ==========================================
# 1. ГОЛОВНИЙ ЕКРАН (Dashboard)
# ==========================================
if st.session_state.view == "list":
    st.title("🚚 Správa vozového parku")
    
    # Статистика зверху
    cars = supabase.table("cars").select("*").execute().data
    col1, col2, col3 = st.columns(3)
    col1.metric("Počet vozidel", len(cars))
    col2.metric("Aktivní servis", "0") # Можна додати логіку
    col3.metric("Najeto celkem", sum(int(c.get('mileage', 0)) for c in cars))
    
    st.divider()

    # Сетка автомобілів
    for car in cars:
        with st.container(border=True):
            cols = st.columns([0.5, 3, 1])
            cols[0].markdown("## 🚛")
            cols[1].markdown(f"### {car['brand_model']}")
            cols[1].caption(f"SPZ: {car['reg_number']} | VIN: {car['vin']}")
            if cols[2].button("Detail vozidla", key=car['vin']):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()

# ==========================================
# 2. КАРТКА АВТО (Професійна панель)
# ==========================================
elif st.session_state.view == "details":
    car = supabase.table("cars").select("*").eq("vin", st.session_state.car_vin).execute().data[0]
    
    if st.button("⬅ Zpět na seznam"):
        st.session_state.view = "list"
        st.rerun()
    
    st.markdown(f"<p class='big-font'>{car['brand_model']} - {car['reg_number']}</p>", unsafe_allow_html=True)
    
    # Використання колонок для поділу екрану
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("💧 Technické náplně")
        with st.form("oil_form"):
            oil_m = st.text_input("Motorový olej", value=car.get('oil_motor', ''))
            oil_k = st.text_input("Olej v převodovce", value=car.get('oil_kpp', ''))
            oil_d = st.text_input("Olej v diferenciálu", value=car.get('oil_dif', ''))
            if st.form_submit_button("💾 Uložit náplně"):
                supabase.table("cars").update({"oil_motor": oil_m, "oil_kpp": oil_k, "oil_dif": oil_d}).eq("vin", car['vin']).execute()
                st.rerun()
                
    with col_right:
        st.subheader("🔧 Servisní historie")
        hist = supabase.table("repairs").select("*").eq("vin", car['vin']).execute().data
        if hist:
            df = pd.DataFrame(hist)
            st.dataframe(df[['description', 'cost']], use_container_width=True)
        else:
            st.info("Historie je prázdná.")
