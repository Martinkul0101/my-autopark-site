import streamlit as st
import json
import os
from datetime import datetime

# Налаштування сторінки
st.set_page_config(page_title="AutoGarage CRM", layout="wide")

# CSS для стильного вигляду карток
st.markdown("""
    <style>
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 5px solid #FF4B4B; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# Функції бази даних
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
# Поле для пошуку
search_query = st.text_input("🔍 Пошук за номером (SPZ) або маркою", "").lower()

# Фільтрація списку авто
filtered_cars = [
    car for car in db["cars"] 
    if search_query in car['brand'].lower() or search_query in car['spz'].lower()
]

# Список авто (тепер використовуємо filtered_cars замість db["cars"])
for i, car in enumerate(filtered_cars):
    # ... далі йде весь ваш код відображення карток ...
    

# Бічна панель для додавання авто
with st.sidebar:
    st.header("➕ Додати авто")
    with st.form("new_car"):
        brand = st.text_input("Марка авто")
        spz = st.text_input("Номер (SPZ)")
        submit = st.form_submit_button("Додати в базу")
        if submit:
            db["cars"].append({"brand": brand, "spz": spz, "history": []})
            save_db(db)
            st.rerun()

# Список авто
for i, car in enumerate(db["cars"]):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    col1.subheader(f"{car['brand']} ({car['spz']})")
    
    if col2.button("🗑 Видалити", key=f"del_{i}"):
        db["cars"].pop(i)
        save_db(db)
        st.rerun()
            
    with st.expander("🛠 Деталі та історія сервісу"):
        # Редагування марки
        new_brand = st.text_input("Редагувати марку", value=car['brand'], key=f"edit_b_{i}")
        if st.button("Зберегти назву", key=f"save_n_{i}"):
            db["cars"][i]['brand'] = new_brand
            save_db(db)
            st.rerun()
            
        # Додавання роботи
        desc = st.text_input("Опис виконаних робіт", key=f"desc_{i}")
        if st.button("Додати запис", key=f"add_r_{i}"):
            date_str = datetime.now().strftime('%d.%m.%Y')
            db["cars"][i]['history'].append(f"{date_str}: {desc}")
            save_db(db)
            st.rerun()
            
        for h in car['history']: 
            st.info(h)
    st.markdown('</div>', unsafe_allow_html=True)
