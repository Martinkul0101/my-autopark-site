import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- КОНФІГУРАЦІЯ ---
st.set_page_config(page_title="Autopark System", layout="wide", page_icon="🚚")
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

# --- НАВІГАЦІЯ (SESSION STATE) ---
if 'view' not in st.session_state: st.session_state.view = "list"
if 'car_vin' not in st.session_state: st.session_state.car_vin = None

# --- БІЧНА ПАНЕЛЬ ---
st.sidebar.title("🛠 АВТОПАРК")
if st.sidebar.button("🚗 Список авто"): 
    st.session_state.view = "list"
    st.rerun()
menu = st.sidebar.radio("Навігація:", ["Головна", "Склад запчастин"])

# ==========================================
# 1. ГОЛОВНИЙ ЕКРАН (СПИСОК)
# ==========================================
if menu == "Головна" and st.session_state.view == "list":
    st.title("🚚 Стручний перегляд парку")
    cars = supabase.table("cars").select("*").execute().data
    
    # Пошук
    car_options = {f"{c['brand_model']} ({c['reg_number']})": c['vin'] for c in cars}
    selected = st.selectbox("🔍 Швидкий пошук:", ["-- Виберіть авто --"] + list(car_options.keys()))
    
    if selected != "-- Виберіть авто --":
        st.session_state.car_vin = car_options[selected]
        st.session_state.view = "details"
        st.rerun()

    for car in cars:
        with st.container(border=True):
            cols = st.columns([1, 4, 3])
            cols[0].markdown("### 🚛")
            cols[1].markdown(f"### {car['brand_model']} - {car['reg_number']}")
            cols[1].caption(f"Пробіг: {car['mileage']} км | VIN: {car['vin']}")
            stk_icon = get_status_icon(car.get('stk_date'))
            cols[2].markdown(f"**STK:** {stk_icon}")
            if cols[2].button("Деталі", key=f"det_{car['vin']}"):
                st.session_state.car_vin = car['vin']
                st.session_state.view = "details"
                st.rerun()

# ==========================================
# 2. ЕКРАН ДЕТАЛЕЙ АВТО
# ==========================================
elif st.session_state.view == "details":
    car = supabase.table("cars").select("*").eq("vin", st.session_state.car_vin).execute().data[0]
    
    if st.button("⬅ Назад"):
        st.session_state.view = "list"
        st.rerun()
        
    st.title(f"📄 Карта: {car['brand_model']} ({car['reg_number']})")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔧 Додати сервісний запис")
        with st.form("add_servis"):
            r_desc = st.text_area("Popis práce:")
            r_parts = st.text_input("Použité náhradní díly:")
            r_cost = st.number_input("Cena (Kč):", min_value=0.0)
            if st.form_submit_button("💾 Зберегти сервіс"):
                supabase.table("repairs").insert({"vin": car['vin'], "description": r_desc, "parts": r_parts, "cost": r_cost}).execute()
                st.success("Збережено!")

    with col2:
        st.subheader("📖 Історія")
        hist = supabase.table("repairs").select("*").eq("vin", car['vin']).execute().data
        st.dataframe(pd.DataFrame(hist), hide_index=True, use_container_width=True)

# ==========================================
# 3. ЕКРАН СКЛАДУ
# ==========================================
elif menu == "Склад запчастин":
    st.title("📦 Склад запчастин")
    
    # Додавання нової запчастини
    with st.expander("➕ Додати нову запчастину на склад"):
        with st.form("new_part"):
            n_name = st.text_input("Назва запчастини")
            n_qty = st.number_input("Кількість", min_value=1)
            if st.form_submit_button("Додати"):
                supabase.table("stock").insert({"name": n_name, "quantity": n_qty}).execute()
                st.rerun()
    
    # Відображення складу
    stock = supabase.table("stock").select("*").execute().data
    st.dataframe(pd.DataFrame(stock), use_container_width=True)
