import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="AutoGarage CRM", layout="wide")

st.markdown("""
    <style>
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 5px solid #FF4B4B; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

def load_db():
    if not os.path.exists("db.json"): return {"cars": []}
    with open("db.json", "r") as f: return json.load(f)

def save_db(db):
    with open("db.json", "w") as f: json.dump(db, f)

db = load_db()

st.title("🚗 AutoGarage Management")

# 1. БІЧНА ПАНЕЛЬ (Має бути ДО циклу)
with st.sidebar:
    st.header("➕ Додати авто")
    with st.form("new_car"):
        brand = st.text_input("Марка авто")
        spz = st.text_input("Номер (SPZ)")
        if st.form_submit_button("Додати"):
            db["cars"].append({"brand": brand, "spz": spz, "history": []})
            save_db(db)
            st.rerun()

# 2. ПОШУК
search_query = st.text_input("🔍 Пошук (введіть номер або марку)", "").lower()
filtered_cars = [c for c in db["cars"] if search_query in c['brand'].lower() or search_query in c['spz'].lower()]

# 3. ЦИКЛ ВІДОБРАЖЕННЯ
for car in filtered_cars:
    i = db["cars"].index(car) 
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    col1.subheader(f"{car['brand']} ({car['spz']})")
    
    if col2.button("🗑 Видалити", key=f"del_{i}"):
        db["cars"].pop(i)
        save_db(db)
        st.rerun()
            
    with st.expander("🛠 Деталі та історія"):
        new_brand = st.text_input("Редагувати марку", value=car['brand'], key=f"edit_b_{i}")
        if st.button("Зберегти", key=f"save_{i}"):
            db["cars"][i]['brand'] = new_brand
            save_db(db)
            st.rerun()
            
        desc = st.text_input("Робота", key=f"desc_{i}")
        if st.button("Додати запис", key=f"add_{i}"):
            db["cars"][i]['history'].append(f"{datetime.now().strftime('%d.%m.%Y')}: {desc}")
            save_db(db)
            st.rerun()
        for h in car['history']: 
            st.info(h)
    st.markdown('</div>', unsafe_allow_html=True)
