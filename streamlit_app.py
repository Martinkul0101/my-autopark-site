import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Autopark Dashboard", layout="wide", page_icon="🚚")

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

# --- СТАН ---
if 'view' not in st.session_state: st.session_state.view = "list"
if 'car_vin' not in st.session_state: st.session_state.car_vin = None

# --- SIDEBAR ---
st.sidebar.title("🛠 AUTOPARK")
if st.sidebar.button("🚗 Seznam vozidel"): 
    st.session_state.view = "list"
    st.rerun()
menu = st.sidebar.radio("Navigace:", ["Hlavní strana", "Sklad náhradních dílů"])

# ==========================================
# 1. DASHBOARD
# ==========================================
if menu == "Hlavní strana" and st.session_state.view == "list":
    st.title("🚚 Dashboard vozového parku")
    cars = supabase.table("cars").select("*").execute().data
    
    # Статистика
    c1, c2, c3 = st.columns(3)
    c1.metric("Počet vozidel", len(cars))
    c2.metric("Nouzový servis", sum(1 for c in cars if get_status_icon(c.get('stk_date')) == "❌"))
    c3.metric("Upozornění", sum(1 for c in cars if get_status_icon(c.get('stk_date')) == "⚠️"))
    
    st.divider()
    
    # Додавання
    with st.expander("➕ Přidat nové vozidlo"):
        with st.form("add_car"):
            col1, col2 = st.columns(2)
            c_model = col1.text_input("Značka a model")
            c_spz = col2.text_input("SPZ")
            c_vin = col1.text_input("VIN kód")
            c_km = col2.number_input("Stav tachometru", min_value=0)
            if st.form_submit_button("Uložit"):
                supabase.table("cars").insert({"brand_model": c_model, "reg_number": c_spz, "vin": c_vin, "mileage": c_km}).execute()
                st.rerun()

    # Список карток
    for car in cars:
        stk = get_status_icon(car.get('stk_date'))
        pov = get_status_icon(car.get('pov_date'))
        
        with st.container(border=True):
            cols = st.columns([1, 4, 3])
            cols[0].write("🚛")
            cols[1].markdown(f"### {car['brand_model']} - {car['reg_number']}")
            cols[1].caption(f"VIN: {car['vin']} | KM: {car.get('mileage', 0)}")
            cols[2].write(f"**STK:** {stk} | **POV:** {pov}")
            if cols[2].button("Detail vozidla", key=car['vin']):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()

# ==========================================
# 2. ДЕТАЛІ
# ==========================================
elif st.session_state.view == "details":
    car = supabase.table("cars").select("*").eq("vin", st.session_state.car_vin).execute().data[0]
    if st.button("⬅ Zpět"):
        st.session_state.view = "list"
        st.rerun()
        
    st.title(f"📄 {car['brand_model']} ({car['reg_number']})")
    
    tab1, tab2 = st.tabs(["🔧 Servisní záznam", "📖 Historie oprav"])
    
    with tab1:
        with st.form("add_repair"):
            r_desc = st.text_input("Popis opravy")
            stock_data = supabase.table("stock").select("name").execute().data
            parts = st.multiselect("Použité díly ze skladu:", [i['name'] for i in stock_data])
            r_cost = st.number_input("Cena (Kč)", min_value=0)
            if st.form_submit_button("Uložit opravu"):
                supabase.table("repairs").insert({
                    "vin": car['vin'], "description": r_desc, 
                    "parts_used": ", ".join(parts), "cost": r_cost
                }).execute()
                st.success("Zapsáno!")

    with tab2:
        hist = supabase.table("repairs").select("*").eq("vin", car['vin']).execute().data
        if hist: st.dataframe(pd.DataFrame(hist), use_container_width=True)

# ==========================================
# 3. СКЛАД
# ==========================================
elif menu == "Sklad náhradních dílů":
    st.title("📦 Sklad náhradních dílů")
    with st.expander("Přidat díl"):
        with st.form("add_part"):
            name = st.text_input("Název dílu")
            qty = st.number_input("Množství", min_value=0)
            if st.form_submit_button("Přidat"):
                supabase.table("stock").insert({"name": name, "quantity": qty}).execute()
                st.rerun()
    st.dataframe(pd.DataFrame(supabase.table("stock").select("*").execute().data), use_container_width=True)
