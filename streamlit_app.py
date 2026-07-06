 import streamlit as st
import json
import os
from datetime import datetime

# --- НАЛАШТУВАННЯ ---
st.set_page_config(page_title="AutoCRM Pro", layout="wide", page_icon="🔧")

# --- БАЗА ДАНИХ ---
def load_db():
    if not os.path.exists("database.json"):
        return {"clients": [], "cars": [], "repairs": []}
    with open("database.json", "r") as f:
        data = json.load(f)
        data.setdefault("clients", []); data.setdefault("cars", []); data.setdefault("repairs", [])
        return data

def save_db(db):
    with open("database.json", "w") as f: json.dump(db, f, indent=4)

db = load_db()

# --- МЕНЮ ---
st.title("🔧 AutoCRM Professional")
tabs = st.tabs(["👥 Klienti", "🚗 Vozový park", "➕ Nový záznam"])

# 1. ВКЛАДКА КЛІЄНТІВ
with tabs[0]:
    st.header("Správa klientů")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("client_form"):
            name = st.text_input("Jméno klienta")
            phone = st.text_input("Telefon")
            if st.form_submit_button("Přidat klienta"):
                db["clients"].append({"id": len(db["clients"])+1, "name": name, "phone": phone})
                save_db(db); st.rerun()
    with col2:
        for c in db["clients"]:
            with st.expander(f"👤 {c['name']}"):
                cars = [ (i, car) for i, car in enumerate(db["cars"]) if car.get("owner_id") == c["id"]]
                for i, car in cars:
                    st.write(f"🚗 {car['brand_model']} ({car['reg_number']})")

# 2. ВКЛАДКА АВТО
with tabs[1]:
    st.header("Vozový park")
    for i, car in enumerate(db["cars"]):
        with st.expander(f"🚗 {car['brand_model']} | {car['reg_number']}"):
            st.subheader("🛠 Historie servisů")
            repairs = [r for r in db.get("repairs", []) if r.get("car_index") == i]
            for r in repairs:
                st.info(f"📅 {r['date']}: {r['desc']} ({r['cost']} Kč)")
            
            with st.form(f"repair_form_{i}"):
                desc = st.text_input("Popis práce")
                cost = st.number_input("Cena", min_value=0)
                if st.form_submit_button("Přidat záznam"):
                    db.setdefault("repairs", []).append({"car_index": i, "date": str(datetime.today().date()), "desc": desc, "cost": cost})
                    save_db(db); st.rerun()

# 3. ВКЛАДКА ДОДАВАННЯ
with tabs[2]:
    st.header("Přidat nové auto")
    with st.form("car_form"):
        model = st.text_input("Značka a model")
        spz = st.text_input("SPZ")
        client_options = {c['name']: c['id'] for c in db["clients"]}
        selected = st.selectbox("Majitel", list(client_options.keys()))
        if st.form_submit_button("Uložit"):
            db["cars"].append({"brand_model": model, "reg_number": spz, "owner_id": client_options[selected]})
            save_db(db); st.rerun()
                   
                    db["repairs"].append({
                        "vin": car["vin"], 
                        "date": str(datetime.today().date()), 
                        "description": full_description, 
                        "parts": parts, 
                        "cost": cost, 
                        "mileage": new_km
                    })
                    db["cars"][selected_idx]["mileage"] = new_km
                    save_data(db)
                    st.success("Servis byl úspěšně uložen!")
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
                
