import streamlit as st
import json
import os
from datetime import datetime

# Налаштування стилю
st.set_page_config(page_title="AutoGarage CRM", layout="wide")
st.markdown("""
    <style>
    .card { background-color: #f0f2f6; padding: 20px; border-radius: 15px; margin-bottom: 10px; border-left: 5px solid #FF4B4B; }
    .stButton>button { width: 100%; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# База даних (Функції)
def load_db():
    if not os.path.exists("db.json"): return {"cars": []}
    with open("db.json", "r") as f: return json.load(f)

def save_db(db):
    with open("db.json", "w") as f: json.dump(db, f)

db = load_db()

# Інтерфейс
st.title("🚗 AutoGarage Management")

# Додавання авто
with st.sidebar:
    st.header("➕ Nové auto")
    with st.form("new_car"):
        brand = st.text_input("Značka")
        spz = st.text_input("SPZ")
        if st.form_submit_button("Přidat"):
            db["cars"].append({"brand": brand, "spz": spz, "history": []})
            save_db(db); st.rerun()

# Список авто у вигляді сучасних карток
for i, car in enumerate(db["cars"]):
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        col1.subheader(f"{car['brand']} | {car['spz']}")
        
        if col2.button("🗑 Smazat", key=f"del_{i}"):
            db["cars"].pop(i)
            save_db(db)
            st.rerun()
            
        with st.expander("🛠 Detaily a servis"):
            # Редагування
            new_brand = st.text_input("Změnit značku", value=car['brand'], key=f"brand_{i}")
            if st.button("Uložit změny", key=f"save_{i}"):
                db["cars"][i]['brand'] = new_brand
                save_db(db)
                st.rerun()
            
            # Роботи
            st.write("---")
            desc = st.text_input("Nová práce", key=f"desc_{i}")
            if st.button("Přidat záznam", key=f"add_{i}"):
                db["cars"][i]['history'].append(f"{datetime.now().strftime('%d.%m.%Y')}: {desc}")
                save_db(db)
                st.rerun()
            
            for h in car['history']: 
                st.info(h)
        st.markdown('</div>', unsafe_allow_html=True)

            # Редагування
            new_brand = st.text_input("Změnit značku", value=car['brand'], key=f"brand_{i}")
            if st.button("Uložit změny", key=f"save_{i}"):
                db["cars"][i]['brand'] = new_brand
                save_db(db); st.rerun()
            
            # Роботи
            st.write("---")
            desc = st.text_input("Nová práce", key=f"desc_{i}")
            if st.button("Přidat záznam", key=f"add_{i}"):
                db["cars"][i]['history'].append(f"{datetime.now().strftime('%d.%m.%Y')}: {desc}")
                save_db(db); st.rerun()
            
            for h in car['history']: st.info(h)
        st.markdown('</div>', unsafe_allow_html=True
