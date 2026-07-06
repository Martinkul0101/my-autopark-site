import streamlit as st
import json
import os
from datetime import datetime

# Налаштування сторінки
st.set_page_config(page_title="AutoGarage CRM", layout="wide")

# CSS для стильного вигляду
st.markdown("""
    <style>
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 5px solid #FF4B4B; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# База даних (використовуємо файл db.json)
def load_db():
    if not os.path.exists("db.json"): 
        return {"cars": []}
    with open("db.json", "r") as f: 
        return json.load(f)

def save_db(db):
    with open("db.json", "w") as f: 
        json.dump(db, f)

db = load_db()

st.title("🚗 AutoGarage Management")

# Бічна панель для додавання авто
with st.sidebar:
    st.header("➕ Додати авто")
    with st.form("new_car"):
        brand = st.text_input("Марка авто")
        spz = st.text_input("Номер (SPZ)")
        submit = st.form_submit_button("Додати в базу")
        if submit:
            db["cars"].append({"brand": brand, "spz": spz, "history": []})
            save
