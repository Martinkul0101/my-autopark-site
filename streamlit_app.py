import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Správa Autoparku", layout="wide", page_icon="🚗")

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- POMOCNÉ FUNKCE ---
def zkontrolovat_datum(d_str):
    if not d_str: return "-"
    try:
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        rozdil = (dt - datetime.now()).days
        if rozdil < 0: return f"❌ Expirováno ({dt.strftime('%d.%m.%Y')})"
        elif rozdil <= 30: return f"⚠️ Blíží se ({dt.strftime('%d.%m.%Y')})"
        else: return f"✅ OK ({dt.strftime('%d.%m.%Y')})"
    except ValueError: return "-"

def zkontrolovat_udrzbu(next_date_str, next_km, current_km, is_trailer=False):
    d_status = "-"
    if next_date_str:
        try:
            dt = datetime.strptime(next_date_str, "%Y-%m-%d")
            rozdil = (dt - datetime.now()).days
            if rozdil < 0: d_status = "❌"
            elif rozdil <= 30: d_status = "⚠️"
            else: d_status = "✅"
        except ValueError: pass

    k_status = "-"
    if not is_trailer and next_km and current_km:
        rozdil_km = next_km - current_km
        if rozdil_km < 0: k_status = "❌"
        elif rozdil_km <= 2000: k_status = "⚠️"
        else: k_status = "✅"

    if "❌" in d_status or "❌" in k_status: return "❌ Nutný servis"
    elif "⚠️" in d_status or "⚠️" in k_status: return "⚠️ Servis se blíží"
    elif "✅" in d_status or "✅" in k_status: return "✅ OK"
    return "-"

# --- BOČNÍ MENU ---
st.sidebar.title("📌 Navigace")
menu = st.sidebar.radio("Vyberte sekci:", ["🚗 Seznam vozidel", "📦 Sklad náhradních dílů"])

# ==========================================
# SEKCÍ 1: SEZNAM VOZIDEL
# ==========================================
if menu == "🚗 Seznam vozidel":
    st.title("🚗 Systém správy autoparku")

    try:
        response = supabase.table("cars").select("*").execute()
        cars_data = response.data
    except Exception as e:
        st.error(f"Chyba při načítání dat: {e}")
        cars_data = []

    if not cars_data:
        st.info("V databázi nejsou žádná vozidla.")
    else:
        tabela_aut = []
        for c in cars_data:
            is_trailer = c.get('type') == 'Přívěs'
            curr_km = c.get('mileage', 0)
            
            tabela_aut.append({
                "VIN": c.get('vin', '-'),
                "Značka a model": c.get('brand_model', 'Neznámé'),
                "SPZ": c.get('reg_number', '-'),
                "Typ": c.get('type', 'Osobní'),
                "Tachometr (km)": "-" if is_trailer else curr_km,
                "STK Status": zkontrolovat_datum(c.get('stk_date', '')),
                "Tachograf": zkontrolovat_datum(c.get('tachograf_date', '')),
                "Údržba Status": zkontrolovat_udrzbu(c.get('next_to_date', ''), c.get('next_to_km', 0), curr_km, is_trailer)
            })

        df
