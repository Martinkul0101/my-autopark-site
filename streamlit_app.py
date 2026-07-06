import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- НАЛАШТУВАННЯ СТОРІНКИ ---
st.set_page_config(page_title="Správa Vozového Parku", layout="wide", page_icon="🚚")
DB_FILE = "database.json"

# --- БАЗА ДАНИХ ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {"cars": [], "repairs": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"cars": [], "repairs": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

# --- БІЧНЕ МЕНЮ ---
st.sidebar.markdown("## 🚚 AUTOPARK")
menu = st.sidebar.radio("NAVIGACE", ["📋 SEZNAM VOZIDEL", "➕ PŘIDAT VOZIDLO"])
st.sidebar.divider()
st.sidebar.info("Lokální systém pro správu vozidel.")

# --- ДОПОМІЖНІ ФУНКЦІЇ ---
def get_status_emoji(days):
    if days < 0: return "🚨"
    if days <= 30: return "⚠️"
    return "✅"

# --- ЕКРАН 1: SEZNAM VOZIDEL ---
    # --- ЕКРАН 1: SEZNAM VOZIDEL ---
if menu == "📋 SEZNAM VOZIDEL":
    st.title("📋 Seznam vozidel")
    
    if not db["cars"]:
        st.info("Zatím nejsou žádná vozidla.")
    else:
        # Вибір авто
        selected_car_idx = st.selectbox("Vyberte vozidlo:", range(len(db["cars"])), 
                                        format_func=lambda x: f"{db['cars'][x]['brand_model']} ({db['cars'][x]['reg_number']})")
        
        car = db["cars"][selected_car_idx]
        st.header(f"📇 {car.get('brand_model')} - {car.get('reg_number')}")

        # СТВОРЮЄМО ВКЛАДКИ
        tab1, tab2, tab3 = st.tabs(["📊 Informace", "🔧 Přidat servis", "📜 Historie"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            col1.metric("VIN", car.get("vin"))
            col2.metric("Tachometr", f"{car.get('mileage')} km")
            col3.metric("STK do", car.get("stk_date"))

        with tab2:
            st.subheader("Nový servisní záznam")
            with st.form(f"repair_form_{car['vin']}"):
                col_a, col_b = st.columns(2)
                desc = col_a.text_input("Popis práce")
                parts = col_b.text_input("Díly / Oleje")
                cost = col_a.number_input("Cena (Kč)", min_value=0)
                new_km = col_b.number_input("Stav tachometru", value=int(car.get('mileage', 0)))
                
                if st.form_submit_button("Uložit servis"):
                    db["repairs"].append({
                        "vin": car["vin"],
                        "date": str(datetime.today().date()),
                        "description": desc,
                        "parts": parts,
                        "cost": cost,
                        "mileage": new_km
                    })
                    db["cars"][selected_car_idx]["mileage"] = new_km
                    save_data(db)
                    st.success("Záznam uložen!")
                    st.rerun()

        with tab3:
            st.subheader("Historie údržby")
            history = [r for r in db["repairs"] if r["vin"] == car["vin"]]
            
            if history:
                for i, record in enumerate(reversed(history)):
                    with st.expander(f"📅 {record['date']} — {record['description']} ({record['cost']} Kč)"):
                        st.write(f"**Díly/Olej:** {record['parts']}")
                        st.write(f"**Stav tachometru:** {record['mileage']} km")
                        
                        if st.button(f"Smazat záznam", key=f"del_{record['date']}_{i}"):
                            db["repairs"].remove(record)
                            save_data(db)
                            st.success("Smazáno!")
                            st.rerun()
            else:
                st.info("Žádná historie.")


        # Створюємо гарний дашборд
        df_cars = pd.DataFrame(db["cars"])
        
        # Вибір авто
        selected_car_idx = st.selectbox("Vyberte vozidlo pro zobrazení detailů:", range(len(df_cars)), 
                                        format_func=lambda x: f"{df_cars.iloc[x]['brand_model']} ({df_cars.iloc[x]['reg_number']})")
        
        car = db["cars"][selected_car_idx]
        
        # Відображення деталей
        col1, col2, col3 = st.columns(3)
        col1.metric("Model", car.get("brand_model"))
        col2.metric("SPZ", car.get("reg_number"))
        col3.metric("Tachometr", f"{car.get('mileage')} km")
        
        st.divider()
        st.subheader("🔧 Servisní historie")
        
        # Таблиця з ремонтами
        repairs = [r for r in db["repairs"] if r["vin"] == car["vin"]]
        if repairs:
            st.dataframe(pd.DataFrame(repairs)[["date", "description", "cost"]], use_container_width=True)
        else:
            st.write("Žádné servisní záznamy.")

# --- ЕКРАН 2: PŘIDAT VOZIDLO ---
elif menu == "➕ PŘIDAT VOZIDLO":
    st.title("➕ Registrace nového vozidla")
    
    with st.form("new_car"):
        c1, c2 = st.columns(2)
        vin = c1.text_input("VIN kód")
        model = c2.text_input("Značka a model")
        spz = c1.text_input("SPZ")
        km = c2.number_input("Počáteční stav tachometru", min_value=0)
        stk = st.date_input("Platnost STK")
        
        if st.form_submit_button("Uložit vozidlo"):
            if vin and model:
                db["cars"].append({
                    "vin": vin, "brand_model": model, "reg_number": spz, 
                    "mileage": km, "stk_date": str(stk)
                })
                save_data(db)
                st.success("Vozidlo bylo uloženo!")
                st.rerun()
            else:
                st.error("Vyplňte alespoň VIN a Model.")
