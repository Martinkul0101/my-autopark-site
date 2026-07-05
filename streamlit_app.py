import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Správa Autoparku", layout="wide", page_icon="🚗")

# Підключення до Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def zkontrolovat_datum(d_str):
    if not d_str: return "-"
    try:
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        rozdil = (dt - datetime.now()).days
        if rozdil < 0: return f"❌ {dt.strftime('%d.%m.%Y')}"
        elif rozdil <= 30: return f"⚠️ {dt.strftime('%d.%m.%Y')}"
        else: return f"✅ {dt.strftime('%d.%m.%Y')}"
    except: return "-"

def zkontrolovat_udrzbu(next_date_str, next_km, current_km, is_trailer=False):
    d_status = "-"
    if next_date_str:
        try:
            dt = datetime.strptime(next_date_str, "%Y-%m-%d")
            rozdil = (dt - datetime.now()).days
            d_status = "❌" if rozdil < 0 else ("⚠️" if rozdil <= 30 else "✅")
        except: pass
    k_status = "-"
    if not is_trailer and next_km and current_km:
        rozdil_km = next_km - current_km
        k_status = "❌" if rozdil_km < 0 else ("⚠️" if rozdil_km <= 2000 else "✅")
    
    if "❌" in d_status or "❌" in k_status: return "❌ Servis nutný"
    elif "⚠️" in d_status or "⚠️" in k_status: return "⚠️ Servis se blíží"
    return "✅ OK"

# --- НАВІГАЦІЯ ---
if 'selected_vin' not in st.session_state:
    st.session_state.selected_vin = None

menu = st.sidebar.radio("📌 Navigace", ["🚗 Seznam vozidel", "📦 Sklad náhradních dílů"])

# ==========================================
# СЕКЦІЯ 1: СПИСОК ТА ДЕТАЛІ
# ==========================================
if menu == "🚗 Seznam vozidel":
    if st.session_state.selected_vin:
        # --- ДЕТАЛІ АВТО ---
        car = supabase.table("cars").select("*").eq("vin", st.session_state.selected_vin).execute().data[0]
        
        if st.button("⬅️ Назад до списку"):
            st.session_state.selected_vin = None
            st.rerun()
            
        st.header(f"🚖 {car['brand_model']} ({car['reg_number']})")
        
        tab1, tab2, tab3 = st.tabs(["📋 Info", "🔧 Nový servis", "📖 Historie"])
        
        with tab1:
            st.write(f"**VIN:** {car['vin']}")
            st.write(f"**Aktuální KM:** {car['mileage']}")
            
        with tab2:
            st.subheader("Přidat servisní záznam")
            with st.form("servis_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                r_date = col1.date_input("Datum:", value=datetime.now())
                r_km = col2.number_input("Tachometr (km):", min_value=0, value=int(car.get('mileage', 0)))
                r_desc = st.text_area("Popis práce:")
                r_parts = st.text_input("Použité díly:")
                r_cost = st.number_input("Cena (Kč):", min_value=0.0, step=100.0)
                
                if st.form_submit_button("Zapsat do historie"):
                    supabase.table("repairs").insert({
                        "vin": car['vin'], "date": r_date.isoformat(), "km": r_km, 
                        "description": r_desc, "parts": r_parts, "cost": r_cost
                    }).execute()
                    supabase.table("cars").update({"mileage": r_km}).eq("vin", car['vin']).execute()
                    st.success("Uloženo!")
                    st.rerun()

        with tab3:
            repairs = supabase.table("repairs").select("*").eq("vin", car['vin']).order("date", desc=True).execute().data
            if repairs:
                st.dataframe(pd.DataFrame(repairs), use_container_width=True)
            else:
                st.info("Žádná historie.")

    else:
        # --- СПИСОК ---
        st.title("🚗 Systém správy autoparku")
        cars = supabase.table("cars").select("*").execute().data
        for car in cars:
            stk = zkontrolovat_datum(car.get('stk_date', ''))
            to = zkontrolovat_udrzbu(car.get('next_to_date', ''), car.get('next_to_km', 0), car.get('mileage', 0))
            badge = "🔴" if ("❌" in stk or "❌" in to) else ("🟡" if ("⚠️" in stk or "⚠️" in to) else "🟢")
            
            with st.container(border=True):
                c1, c2, c3 = st.columns([0.5, 4, 1.5])
                c1.write(badge)
                c2.write(f"**{car['brand_model']}** | SPZ: {car['reg_number']}")
                c2.caption(f"STK: {stk} | TO: {to}")
                if c3.button("Деталі", key=f"btn_{car['vin']}"):
                    st.session_state.selected_vin = car['vin']
                    st.rerun()

# ==========================================
# СЕКЦІЯ 2: СКЛАД
# ==========================================
elif menu == "📦 Sklad náhradních dílů":
    st.title("📦 Sklad náhradních dílů")
    stock = supabase.table("stock").select("*").execute().data
    if stock:
        st.dataframe(pd.DataFrame(stock), use_container_width=True)
    else:
        st.info("Sklad je prázdný.")
