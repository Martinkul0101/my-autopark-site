import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Správa Autoparku", layout="wide", page_icon="🚚")

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ФУНКЦІЇ ---
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

# ==========================================
# 1. ГОЛОВНИЙ ЕКРАН
# ==========================================
if st.session_state.view == "list":
    st.title("🚚 Dashboard vozového parku")
    cars = supabase.table("cars").select("*").execute().data
    
    with st.expander("➕ Přidat nové vozidlo"):
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
            cols = st.columns([1, 4, 2])
            cols[0].write("🚛")
            cols[1].markdown(f"### {car['brand_model']} - {car['reg_number']}")
            if cols[2].button("Detail", key=car['vin']):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()

# ==========================================
# 2. ДЕТАЛІ АВТО (З ТЕХ. РІДИНАМИ)
# ==========================================
elif st.session_state.view == "details":
    car = supabase.table("cars").select("*").eq("vin", st.session_state.car_vin).execute().data[0]
    if st.button("⬅ Zpět"):
        st.session_state.view = "list"
        st.rerun()
        
    st.title(f"📄 {car['brand_model']} ({car['reg_number']})")
    
    # Використовуємо вкладки для організації
    tab1, tab2 = st.tabs(["💧 Technické náplně", "🔧 Servisní historie"])
    
    with tab1: # Розділ мастил
        st.subheader("💧 Specifikace náplní")
        with st.form("update_fluids"):
            m_motor = st.text_input("Motorový olej (např. 5W-30)", value=car.get('oil_motor', ''))
            m_kpp = st.text_input("Olej v převodovce (KPP)", value=car.get('oil_kpp', ''))
            m_dif = st.text_input("Olej v diferenciálu", value=car.get('oil_dif', ''))
            
            if st.form_submit_button("💾 Uložit specifikace"):
                supabase.table("cars").update({
                    "oil_motor": m_motor, "oil_kpp": m_kpp, "oil_dif": m_dif
                }).eq("vin", car['vin']).execute()
                st.success("Uloženo!")
                st.rerun()
                
    with tab2: # Історія ремонтів
        st.subheader("🔧 Servisní záznamy")
        # Тут можна додати форму додавання ремонту як раніше...
        hist = supabase.table("repairs").select("*").eq("vin", car['vin']).execute().data
        if hist: st.dataframe(pd.DataFrame(hist), use_container_width=True)
