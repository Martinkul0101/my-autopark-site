import streamlit as st
import json
import os

st.set_page_config(page_title="AutoGarage CRM")

# Спрощена функція завантаження
def load():
    if not os.path.exists("db.json"): 
        return {"cars": []}
    try:
        with open("db.json", "r") as f: 
            return json.load(f)
    except:
        return {"cars": []}

db = load()

st.title("🚗 AutoGarage CRM")

# Перевірка, чи взагалі працює відображення
st.write(f"Počet aut v databázi: {len(db['cars'])}")

# Якщо є авто, покажемо їх
for car in db["cars"]:
    st.write(f"Auto: {car.get('brand', 'Bez značky')}")
