import streamlit as st
import json
import os
import io
from datetime import datetime
from fpdf import FPDF

st.set_page_config(page_title="AutoGarage CRM", layout="centered")

def load():
    if not os.path.exists("db.json"): return {"cars": []}
    with open("db.json", "r") as f: return json.load(f)

def save(db):
    with open("db.json", "w") as f: json.dump(db, f, indent=4)

# Функція, яка створює PDF і повертає байти
def get_pdf_bytes(car):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Historie: {car['brand']} ({car['spz']})", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, txt=f"VIN: {car.get('vin', 'N/A')}", ln=True)
    pdf.ln(5)
    for h in car['history']:
        pdf.multi_cell(0, 10, txt=h)
    return pdf.output(dest='S')

db = load()
st.title("🚗 AutoGarage CRM")

# Бокова панель
with st.sidebar:
    st.header("➕ Nové auto")
    with st.form("new_car"):
        br = st.text_input("Značka")
        nr = st.text_input("SPZ")
        if st.form_submit_button("Přidat"):
            db["cars"].append({"brand": br, "spz": nr, "vin": "", "history": []})
            save(db); st.rerun()

# Список авто
for i, car in enumerate(db["cars"]):
    with st.expander(f"{car['brand']} | {car['spz']}"):
        # Редагування
        car['brand'] = st.text_input("Značka", value=car['brand'], key=f"b{i}")
        car['spz'] = st.text_input("SPZ", value=car['spz'], key=f"s{i}")
        if st.button("Uložit", key=f"save{i}"): save(db); st.rerun()
        
        # Робота
        wrk = st.text_input("Práce", key=f"w{i}")
        if st.button("Přidat záznam", key=f"add{i}"):
            car['history'].append(f"{datetime.now().strftime('%d.%m.%Y')} | {wrk}")
            save(db); st.rerun()
            
        for h in car['history']: st.info(h)
        
        # Кнопка завантаження (Виправлено!)
        st.download_button(
            label="📥 Export PDF",
            data=get_pdf_bytes(car),
            file_name="historie.pdf",
            mime="application/pdf"
        )
