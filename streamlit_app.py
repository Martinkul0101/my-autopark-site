import streamlit as st
import json
import os
from datetime import datetime

# Nastavení stránky
st.set_page_config(page_title="Správa Vozového Parku", layout="wide")

DB_FILE = "garage_db.json"

# Funkce pro načítání dat z JSON souboru
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # AUTOKOREKCE: Kontrola a doplnění chybějících polí pro STK a Pojištění
        if "cars" in data:
            for vin, car in data["cars"].items():
                if "model" in car and "brand_model" not in car:
                    car["brand_model"] = car["model"]
                if "reg_number" not in car:
                    car["reg_number"] = "NEUVEDENO"
                if "stk_date" not in car:
                    car["stk_date"] = str(datetime.today().date())
                if "insurance_date" not in car:
                    car["insurance_date"] = str(datetime.today().date())
                    
        if "repairs" in data:
            for r in data["repairs"]:
                if "part_codes" not in r:
                    r["part_codes"] = "—"
        return data
    return {"cars": {}, "repairs": []}

# Funkce pro ukládání dat
def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

# --- BOČNÍ PANEL (SIDEBAR) ---
st.sidebar.markdown("<h2 style='color: #1a73e8; text-align: center;'>🚚 AUTOPARK</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: gray;'>Interní evidenční systém</p>", unsafe_allow_html=True)
st.sidebar.divider()

menu = st.sidebar.radio(
    "NAVIGACE",
    ["📋 SEZNAM VOZIDEL", "➕ PŘIDAT VOZIDLO", "📊 CELKOVÝ DENÍK SERVISU"]
)

st.sidebar.divider()
st.sidebar.info("Data se automaticky ukládají do souboru garage_db.json.")

# --- POMOCNÁ FUNKCE PRO KONTROLU TERMÍNŮ (STK / POJIŠTĚNÍ) ---
def check_dates_alert(date_str):
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        days_left = (target_date - today).days
        
        if days_left < 0:
            return "🚨 PROŠLÉ!", "red"
        elif days_left <= 30:
            return f"⚠️ Končí za {days_left} dní", "orange"
        else:
            return f"✅ V pořádku ({days_left} dní)", "green"
    except:
        return "—", "gray"

# --- SEZNAM VOZIDEL A DETAILNÍ KARTY ---
if menu == "📋 SEZNAM VOZIDEL":
    st.markdown("# 📋 Seznam vozidel v autoparku")
    st.write("Vyberte vozidlo ze seznamu níže pro zobrazení karty, úpravu STK, pojištění, kilometrů nebo servisu.")
    st.divider()

    if not db["cars"]:
        st.info("V autoparku zatím nejsou žádná registrovaná vozidla. Přejdete na záložku 'Přidat vozidlo'.")
    else:
        car_list = [f"{car.get('brand_model', 'Neznámé auto')} [{car.get('reg_number', '—')}] (VIN: {vin})" for vin, car in db["cars"].items()]
        selected_car = st.selectbox("🔍 Rychlé vyhledávání a výběr vozidla k úpravě:", ["-- Vyberte vozidlo pro zobrazení detailů --"] + car_list)
        
        st.divider()
        
        if selected_car != "-- Vyberte vozidlo pro zobrazení detailů --":
            active_vin = selected_car.split("VIN: ")[-1].replace(")", "")
            car_data = db["cars"][active_vin]
            
            try:
                current_stk = datetime.strptime(car_data.get("stk_date", str(datetime.today().date())), "%Y-%m-%d").date()
                current_ins = datetime.strptime(car_data.get("insurance_date", str(datetime.today().date())), "%Y-%m-%d").date()
            except:
                current_stk = datetime.today().date()
                current_ins = datetime.today().date()
            
            st.markdown(f"## 📇 Karta vozidla: {car_data.get('brand_model', 'Neznámé auto')}")
            
            stk_status, stk_color = check_dates_alert(car_data.get("stk_date", ""))
            ins_status, ins_color = check_dates_alert(car_data.get("insurance_date", ""))
            
            st.markdown(f"**Platnost STK:** <span style='color:{stk_color}; font-weight:bold;'>{stk_status}</span> | **Platnost pojištění:** <span style='color:{ins_color}; font-weight:bold;'>{ins_status}</span>", unsafe_allow_html=True)
            st.write("")

            col_edit, col_repair = st.columns(2)
            
            with col_edit:
                st.markdown("#### ⚙️ Upravit údaje vozidla a termíny")
                with st.form(key=f"edit_form_{active_vin}"):
                    new_brand_model = st.text_input("Značka a model", value=car_data.get('brand_model', ''))
                    new_reg = st.text_input("Registrační značka (SPZ)", value=car_data.get('reg_number', '')).upper()
                    new_mileage = st.text_input("Aktuální stav tachometru (km)", value=car_data.get('mileage', '0'))
                    
                    st.markdown("**Termíny dokumentů:**")
                    new_stk = st.date_input("Konec platnosti STK", value=current_stk)
                    new_ins = st.date_input("Konec platnosti pojištění", value=current_ins)
                    
                    if st.form_submit_button("Uložit změny", type="primary"):
                        db["cars"][active_vin]["brand_model"] = new_brand_model
                        db["cars"][active_vin]["reg_number"] = new_reg
                        db["cars"][active_vin]["mileage"] = new_mileage
                        db["cars"][active_vin]["stk_date"] = str(new_stk)
                        db["cars"][active_vin]["insurance_date"] = str(new_ins)
                        save_data(db)
                        st.success("Údaje o vozidle a termíny úspěšně aktualizovány!")
                        st.rerun()
                        
            with col_repair:
                st.markdown("#### 🔧 Přidat nový servisní záznam a použité díly")
                with st.form(key=f"repair_form_{active_vin}"):
                    rep_desc = st.text_area("Popis provedených prací / servisu", placeholder="Např.: Výměna motorového oleje, filtrů...")
                    rep_codes = st.text_input("Použité náhradní díly (Kódy dílů / Obj. čísla)", placeholder="Např.: OIL-5W30, FL-992")
                    
                    c_col1, c_col2 = st.columns(2)
                    with c_col1:
                        auto_update_mileage = st.text_input("Stav tachometru (km)", value=car_data.get('mileage', '0'))
                    with c_col2:
                        rep_cost = st.number_input("Cena celkem (Kč, volitelné)", min_value=0.0, step=500.0)
                    
                    if st.form_submit_button("Zapsat servis do historie"):
                        if rep_desc:
                            db["cars"][active_vin]["mileage"] = auto_update_mileage
                            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                            db["repairs"].append({
                                "vin": active_vin,
                                "date": date_str,
                                "description": rep_desc,
                                "part_codes": rep_codes if rep_codes else "—",
                                "cost": rep_cost,
                                "mileage": auto_update_mileage
                            })
                            save_data(db)
                            st.success("Nový servisní záznam byl uložen!")
                            st.rerun()
                        else:
                            st.error("Před uložením prosím zadejte popis prací.")
            
            st.divider()
            st.markdown(f"#### 📜 Historie oprav a dílů pro {car_data.get('brand_model', '')} ({car_data.get('reg_number', '')})")
            
            personal_repairs = [r for r in db["repairs"] if r["vin"] == active_vin]
            
            if not personal_repairs:
                st.info("Pro toto vozidlo zatím neexistují žádné servisní záznamy.")
            else:
                personal_table = []
                for idx, r in enumerate(personal_repairs):
                    personal_table.append({
                        "Číslo": idx + 1,
                        "Datum": r["date"],
                        "Provedené práce / Servis": r["description"],
                        "Kódy použitých dílů": r.get("part_codes", "—"),
                        "Stav tachometru (km)": r["mileage"],
                        "Cena": f"{r['cost']} Kč"
                    })
                st.dataframe(personal_table, use_container_width=True, hide_index=True)
                
        else:
            st.markdown("### Stručný přehled vozového parku:")
            for vin, car in db["cars"].items():
                stk_status, stk_color = check_dates_alert(car.get("stk_date", ""))
                ins_status, ins_color = check_dates_alert(car.get("insurance_date", ""))
                
                with st.container(border=True):
                    st.markdown(f"### 🚛 {car.get('brand_model', 'Neznámé auto')} — `{car.get('reg_number', '—')}`")
                    st.markdown(f"**VIN:** `{vin}` | 📈 **Tachometr:** `{car.get('mileage', '0')} km`")
                    st.markdown(f"**STK:** <span style='color:{stk_color}; font-weight:bold;'>{stk_status}</span> | **Pojištění:** <span style='color:{ins_color}; font-weight:bold;'>{ins_status}</span>", unsafe_allow_html=True)

# --- PŘIDAT VOZIDLO (КОЛОНКИ ПОВНІСТЮ ВИДАЛЕНО ДЛЯ СТАБІЛЬНОСТІ) ---
elif menu == "➕ PŘIDAT VOZIDLO":
    st.markdown("# ➕ Registrace nového vozidla")
    st.divider()
    
    car_brand_model = st.text_input("Značka a model", placeholder="Např.: Scania R450")
    car_reg = st.text_input("Registrační značka (SPZ)", placeholder="Např.: 1AB2345").upper()
    car_vin = st.text_input("VIN kód (17 znaků)").upper()
