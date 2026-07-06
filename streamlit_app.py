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
                # Визначаємо авто та історію
        car = db["cars"][selected_idx]
        st.header(f"📇 {car.get('brand_model')} - {car.get('reg_number')}")
        history = [r for r in db["repairs"] if r["vin"] == car["vin"]]

                # Визначаємо історію
        history = [r for r in db["repairs"] if r["vin"] == car["vin"]]

        # 4 вкладки: Informace, Servis, Údržba, Historie
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Informace", "🔧 Servis", "🛢️ Údržba", "📜 Historie"])

        with tab1:
            st.subheader("🛠 Technické údaje")
            col1, col2 = st.columns(2)
            col1.write(f"**VIN:** {car.get('vin')}")
            col1.write(f"**Motorový olej:** {car.get('oil_motor', '—')}")
            col2.write(f"**Příští údržba:** {car.get('next_to_km', '—')} km")
            col2.write(f"**STK do:** {car.get('stk_date')}")

            with st.expander("✏️ Upravit informace"):
                with st.form(f"edit_all_{car['vin']}"):
                    new_model = st.text_input("Značka a model", value=car.get('brand_model', ''))
                    new_next_km = st.number_input("Příští údržba (km)", value=int(car.get('next_to_km', 0)))
                    if st.form_submit_button("Uložit změny"):
                        db["cars"][selected_idx].update({"brand_model": new_model, "next_to_km": new_next_km})
                        save_data(db); st.rerun()

         with tab2:
                with tab2:
            st.subheader("Nový servisní záznam")
            
            # Логіка для автозаповнення (працює окремо від форми)
            if history:
                if st.button("🔄 Předvyplnit z posledního servisu", key=f"fill_{car['vin']}"):
                    st.session_state.last_parts = history[-1]['parts']
                    st.rerun()
            
            # Сама форма (тепер з унікальним ключем)
            with st.form(key=f"repair_form_unique_{car['vin']}"):
                col_a, col_b = st.columns(2)
                
                # Поля форми
                desc = col_a.text_input("Popis práce")
                parts = col_b.text_input("Díly / Oleje", value=st.session_state.get('last_parts', ""))
                cost = col_a.number_input("Cena (Kč)", min_value=0)
                new_km = col_b.number_input("Stav tachometru", value=int(car.get('mileage', 0)))
                
                # Кнопка збереження
                if st.form_submit_button("Uložit servis"):
                    # Зберігаємо дані
                    db["repairs"].append({
                        "vin": car["vin"], 
                        "date": str(datetime.today().date()), 
                        "description": desc, 
                        "parts": parts, 
                        "cost": cost, 
                        "mileage": new_km
                    })
                    db["cars"][selected_idx]["mileage"] = new_km
                    save_data(db)
                    
                    # Очищаємо сесію після збереження
                    if 'last_parts' in st.session_state:
                        del st.session_state.last_parts
                    
                    st.success("Záznam uložen!")
                    st.rerun()

        with tab3:
            st.subheader("📋 Kódy filtrů a náplní")
            with st.form(f"maint_form_{car['vin']}"):
                air_f = st.text_input("Vzduchový filtr", value=car.get('air_filter', ''))
                oil_f = st.text_input("Olejový filtr", value=car.get('oil_filter', ''))
                fuel_f = st.text_input("Palivový filtr", value=car.get('fuel_filter', ''))
                oil_spec = st.text_input("Specifikace oleje", value=car.get('oil_spec', ''))
                if st.form_submit_button("Uložit"):
                    db["cars"][selected_idx].update({"air_filter": air_f, "oil_filter": oil_f, "fuel_filter": fuel_f, "oil_spec": oil_spec})
                    save_data(db); st.rerun()

        with tab4:
            st.subheader("Historie údržby")
            search = st.text_input("🔍 Hledat v dílech:")
            filtered = [r for r in history if search.lower() in r['parts'].lower()]
            for i, record in enumerate(reversed(filtered)):
                with st.expander(f"📅 {record['date']} — {record['parts']}"):
                    if st.button(f"Smazat záznam", key=f"del_{car['vin']}_{record['date']}_{i}"):
                        db["repairs"].remove(record); save_data(db); st.rerun()


            # --- КНОПКА ВИДАЛЕННЯ ---
            if st.button("🗑️ Smazat celé vozidlo"):
                db["cars"].pop(selected_idx)
                db["repairs"] = [r for r in db["repairs"] if r["vin"] != car["vin"]]
                save_data(db)
                st.rerun()
                
                
        with tab2:
            st.subheader("Nový servisní záznam")
            if history:
                if st.button("🔄 Předvyplnit z posledního servisu"):
                    st.session_state.last_parts = history[-1]['parts']
                    st.rerun()
            
            with st.form(key=f"unique_repair_form_{car['vin']}"):
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
            search = st.text_input("🔍 Hledat v dílech:", key=f"search_{car['vin']}")
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
        col1, col2 = st.columns(2)
        vin = col1.text_input("VIN kód")
        model = col2.text_input("Značka a model")
        spz = col1.text_input("Registrační značka (SPZ)")
        km = col2.number_input("Počáteční stav tachometru (km)", min_value=0)
        stk = col1.date_input("Platnost STK do:")
        insurance = col2.date_input("Platnost pojištění do:")
        
        if st.form_submit_button("Uložit vozidlo", type="primary"):
            if vin and model:
                db["cars"].append({
                    "vin": vin, 
                    "brand_model": model, 
                    "reg_number": spz, 
                    "mileage": km, 
                    "stk_date": str(stk),
                    "insurance_date": str(insurance)
                })
                save_data(db)
                st.success(f"Vozidlo {model} bylo úspěšně uloženo!")
                st.rerun()
            else:
                st.error("VIN kód a Model jsou povinné údaje.")
                
