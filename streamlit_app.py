import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="AutoGarage CRM", layout="wide")

def load():
    if not os.path.exists("db.json"): return {"cars": []}
    with open("db.json", "r") as f: 
        try:
            return json.load(f)
        except:
            return {"cars": []}

def save(db):
    with open("db.json", "w") as f: json.dump(db, f, indent=4)

db = load()

st.title("🚗 AutoGarage CRM")

with st.sidebar:
    st.header("➕ Přidat auto")
    with st.form("new"):
        br = st.text_input("Značka")
        nr = st.text_input("SPZ")
        vin = st.text_input("VIN kód")
        if st.form_submit_button("Přidat"):
            db["cars"].append({"brand": br, "spz": nr, "vin": vin, "history": []})
            save(db)
            st.rerun()

src = st.text_input("🔍 Hledat", "")
filt = [c for c in db["cars"] if src.lower() in c['brand'].lower() or src.lower() in c['spz'].lower()]

for car in filt:
    idx = db["cars"].index(car)
    with st.container():
        st.subheader(f"{car['brand']} | {car['spz']}")
        
        with st.expander("📝 Upravit informace / Servis"):
            new_brand = st.text_input("Značka", value=car['brand'], key=f"b_{idx}")
            new_spz = st.text_input("SPZ", value=car['spz'], key=f"n_{idx}")
            new_vin = st.text_input("VIN kód", value=car.get('vin', ''), key=f"v_{idx}")
            
            if st.button("Uložit změny dat", key=f"save_data_{idx}"):
                db["cars"][idx].update({"brand": new_brand, "spz": new_spz, "vin": new_vin})
                save(db)
                st.rerun()
            
            st.write("---")
            wrk = st.text_input("Provedená práce", key=f"w_{idx}")
            parts = st.text_input("Použité náhradní díly", key=f"p_{idx}")
            km = st.number_input("Stav tachometru (km)", min_value=0, key=f"km_{idx}")
            
            if st.button("Uložit záznam", key=f"s_{idx}"):
                zaznam = f"{datetime.now().strftime('%d.%m.%Y')} | {km} km | {wrk} | Díly: {parts}"
                db["cars"][idx]['history'].append(zaznam)
                save(db)
                st.rerun()
            
            for h in car['history']: st.info(h)
            
            st.write("---")
            if st.button("🗑 Smazat celé auto", key=f"del_{idx}"):
                db["cars"].pop(idx)
                save(db)
                st.rerun()
                
