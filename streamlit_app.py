import streamlit as st
import json
import os
import unicodedata
from datetime import datetime
from fpdf import FPDF

# Налаштування сторінки
st.set_page_config(page_title="AutoGarage CRM", layout="centered")

# --- Функції бази даних ---
def load():
    if not os.path.exists("db.json"): 
        return {"cars": []}
    with open("db.json", "r") as f: 
        try:
            return json.load(f)
        except:
            return {"cars": []}

def save(db):
    with open("db.json", "w") as f: 
        json.dump(db, f, indent=4)

# --- Функції PDF та тексту ---
def clean_text(text):
    """Очищує текст від спецсимволів, щоб FPDF не видавав помилку"""
    return ''.join(c for c in unicodedata.normalize('NFD', str(text))
                   if unicodedata.category(c) != 'Mn')

def get_pdf_bytes(car):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=clean_text(f"Historie: {car['brand']} ({car['spz']})"), ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, txt=clean_text(f"VIN: {car.get('vin', 'N/A')}"), ln=True)
    pdf.ln(5)
    for h in car['history']:
        # Всі дужки закрито тут:
        pdf.multi_cell(0, 10, txt=clean_text(h))
    return pdf.output(dest='S')

# --- Основна логіка ---
db = load()

st.title("🚗 AutoGarage CRM")

# Бокова панель
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
