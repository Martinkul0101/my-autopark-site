import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="Správa Vozového Parku", layout="wide", page_icon="🚚")
DB_FILE = "database.json"

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

st.sidebar.markdown("## 🚚 AUTOPARK")
menu = st.sidebar.radio("NAVIGACE", ["📋 SEZNAM VOZIDEL", "➕ PŘIDAT VOZIDLO"])

if menu == "📋 SEZNAM VOZIDEL":
    st.title("📋 Seznam vozidel")
    if not db["cars"]:
        st.info("Zatím nejsou žádná vozidla.")
    else:
        selected_idx = st.selectbox("Vyberte vozidlo:", range(len(db["cars"])), 
                                     format_func=lambda i: f"{db['cars'][i]['brand_model']} ({db['cars'][i]['reg_number']})")
        car = db["cars"][selected_idx]
        st.header(f"📇 {car.get('brand_model')} - {car.get('reg_number')}")

        tab1, tab2, tab3 = st.tabs(["📊 Informace", "🔧 Přidat servis", "📜 Historie"])

        with tab1:
            col1, col2, col3 = st.columns(3)
            col1.metric("VIN", car.get("vin"))
            col2.metric("Tachometr", f"{car.get('mileage')} km")
            col3.metric("STK do", car.get("stk_date"))
            
            st.divider()
            st.subheader("📌 Naposledy použité díly")
            history = [r for r in db["repairs"] if r["vin"] == car["vin"]]
            if history:
                last = history[-1]
                st.info(f"Servis ze dne {last['date']}")
                st.write(f"**Díly:** {last['parts']}")
            else:
                st.write("Žádná historie.")

        with tab2:
            st.subheader("Nový servisní záznam")
            if history:
                if st.button("🔄 Předvyplnit z posledního servisu"):
                    st.session_state.last_parts = history[-1]['parts']
                    st.rerun()
            
            with st.form(f"repair_form_{car['vin']}"):
                col_a, col_b = st.columns(2)
                desc = col_a.text_input("Popis práce")
                parts = col_b.text_input("Díly / Oleje", value=st.session_state.get('last_parts', ""))
                cost = col_a.number_input("Cena (Kč)", min_value=0)
                new_km = col_b.number_input("Stav tachometru", value=int(car.get('mileage', 0)))
                
                if st.form_submit_button("Uložit servis"):
                    if 'last_parts' in st.session_state: del st.session_state.last_parts
                    db["repairs"].append({"vin": car["vin"], "date": str(datetime.today().date()), "description": desc, "parts": parts, "cost": cost, "mileage": new_km})
                    db["cars"][selected_idx]["mileage"] = new_km
                    save_data(db)
                    st.success("Záznam uložen!")
                    st.rerun()

        with tab3:
            st.subheader("Historie údržby")
            search = st.text_input("🔍 Hledat v dílech:")
            filtered = [r for r in history if search.lower() in r['parts'].lower() or search.lower() in r['description'].lower()]
            
            for i, record in enumerate(reversed(filtered)):
                with st.expander(f"📅 {record['date']} — {record['parts']} ({record['cost']} Kč)"):
                    st.write(f"**Popis:** {record['description']}")
                    if st.button(f"Smazat záznam", key=f"del_{record['date']}_{i}"):
                        db["repairs"].remove(record)
                        save_data(db)
                        st.rerun()

elif menu == "➕ PŘIDAT VOZIDLO":
    st.title("➕ Registrace nového vozidla")
    with st.form("new_car"):
        vin = st.text_input("VIN kód")
        model = st.text_input("Značka a model")
        if st.form_submit_button("Uložit"):
            db["cars"].append({"vin": vin, "brand_model": model, "mileage": 0, "reg_number": "", "stk_date": ""})
            save_data(db)
            st.success("Uloženo!")
            st.rerun()
