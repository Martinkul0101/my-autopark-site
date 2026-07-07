import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF

# Конфігурація
st.set_page_config(page_title="AutoGarage CRM", layout="centered")

def load():
    if not os.path.exists("db.json"): return {"cars": []}
    with open("db.json", "r") as f: 
        try:
            return json.load(f)
        except:
            return {"cars": []}

def save(db):
    with open("db.json", "w") as f: 
        json.dump(db, f, indent=4)

import unicodedata

def clean_text(text):
    # Видаляємо діакритичні знаки (š -> s, č -> c тощо)
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')

def get_pdf_bytes(car):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Використовуємо clean_text для заголовка
    header = clean_text(f"Historie: {car['brand']} ({car['spz']})")
    pdf.cell(0, 10, txt=header, ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, txt=f"VIN: {car.get('vin', 'N/A')}", ln=True)
    pdf.ln(5)
    
    for h in car['history']:
        # Використовуємо clean_text для кожного рядка історії
        pdf.multi_cell(0, 10, txt=clean_text(h))
    
    return pdf.output(dest='S')
    

# Бічна панель
with st.sidebar:
    st.header("➕ Nové auto")
    with st.form("new_car"):
        br = st.text_input("Značka")
        nr = st.text_input("SPZ")
        if st.form_submit_button("Přidat"):
            if br and nr:
                db["cars"].append({"brand": br, "spz": nr, "vin": "", "history": []})
                save(db)
                st.rerun()

# Список авто
for i, car in enumerate(db["cars"]):
    with st.expander(f"{car['brand']} | {car['spz']}"):
        # Редагування
        car['brand'] = st.text_input("Značka", value=car['brand'], key=f"b{i}")
        car['spz'] = st.text_input("SPZ", value=car['spz'], key=f"s{i}")
        car['vin'] = st.text_input("VIN", value=car.get('vin', ''), key=f"v{i}")
        if st.button("Uložit změny", key=f"save{i}"): save(db); st.rerun()
        
        st.write("---")
        wrk = st.text_input("Provedená práce", key=f"w{i}")
        if st.button("Přidat záznam", key=f"add{i}"):
            car['history'].append(f"{datetime.now().strftime('%d.%m.%Y')} | {wrk}")
            save(db); st.rerun()
            
        for h in car['history']: st.info(h)
        
        # Кнопка PDF з примусовим перетворенням у bytes
        pdf_bytes = get_pdf_bytes(car)
        st.download_button(
            label="📥 Export PDF",
            data=bytes(pdf_bytes),
            file_name=f"{car['spz']}_historie.pdf",
            mime="application/pdf"
        )
