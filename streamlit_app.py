import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF

# Конфігурація сторінки
st.set_page_config(page_title="AutoGarage CRM", layout="centered")

# --- Функції роботи з даними та PDF ---
def load():
    if not os.path.exists("db.json"): 
        return {"cars": []}
    with open("db.json", "r") as f: 
        return json.load(f)

def save(db):
    with open("db.json", "w") as f: 
        json.dump(db, f, indent=4)

import io # Переконайтеся, що цей імпорт є зверху

def create_pdf(car):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Historie servisu: {car['brand']} ({car['spz']})", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, txt=f"VIN: {car.get('vin', 'N/A')}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    for h in car['history']:
        pdf.multi_cell(0, 10, txt=h)
    
    # ПОВЕРТАЄМО САМЕ БАЙТИ
    return pdf.output(dest='S') 

# --- Основна частина ---
db = load()

st.title("🚗 AutoGarage CRM")

# Бокова панель: Додавання авто
with st.sidebar:
    st.header("➕ Nové auto")
    with st.form("new_car_form"):
        br = st.text_input("Značka")
        nr = st.text_input("SPZ")
        vin = st.text_input("VIN")
        if st.form_submit_button("Přidat"):
            if br and nr:
                db["cars"].append({"brand": br, "spz": nr, "vin": vin, "history": []})
                save(db)
                st.rerun()

# Пошук
src = st.text_input("🔍 Hledat podle značky nebo SPZ", "")
filt = [c for c in db["cars"] if src.lower() in c['brand'].lower() or src.lower() in c['spz'].lower()]

# Відображення списку авто
for car in filt:
    idx = db["cars"].index(car)
    with st.expander(f"{car['brand']} | {car['spz']}"):
        new_brand = st.text_input("Značka", value=car['brand'], key=f"b_{idx}")
        new_spz = st.text_input("SPZ", value=car['spz'], key=f"n_{idx}")
        new_vin = st.text_input("VIN", value=car.get('vin', ''), key=f"v_{idx}")
        
        if st.button("Uložit změny", key=f"save_{idx}"):
            db["cars"][idx].update({"brand": new_brand, "spz": new_spz, "vin": new_vin})
            save(db)
            st.rerun()
            
        st.write("---")
        wrk = st.text_input("Provedená práce", key=f"w_{idx}")
        parts = st.text_input("Náhradní díly", key=f"p_{idx}")
        km = st.number_input("Tachometr (km)", min_value=0, key=f"km_{idx}")
        
        if st.button("Přidat záznam", key=f"s_{idx}"):
            zaznam = f"{datetime.now().strftime('%d.%m.%Y')} | {km} km | {wrk} | Díly: {parts}"
            db["cars"][idx]['history'].append(zaznam)
            save(db)
            st.rerun()
            
        for h in car['history']:
            st.info(h)
            
        col1, col2 = st.columns(2)
        with col1:
            pdf_data = create_pdf(car)
            st.download_button("📥 PDF", pdf_data, f"{car['spz']}_historie.pdf", "application/pdf")
        with col2:
            if st.button("🗑 Smazat auto", key=f"del_{idx}"):
                db["cars"].pop(idx)
                save(db)
                st.rerun()
