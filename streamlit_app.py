import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Garage", layout="wide")

def load():
    if not os.path.exists("db.json"): return {"cars": []}
    with open("db.json", "r") as f: return json.load(f)

def save(db):
    with open("db.json", "w") as f: json.dump(db, f)

db = load()

st.title("🚗 AutoGarage")

with st.sidebar:
    st.header("➕ Додати авто")
    with st.form("new"):
        br = st.text_input("Марка")
        nr = st.text_input("Номер")
        if st.form_submit_button("Додати"):
            db["cars"].append({"brand": br, "spz": nr, "history": []})
            save(db)
            st.rerun()

src = st.text_input("🔍 Пошук", "")

filt = [c for c in db["cars"] if src.lower() in c['brand'].lower() or src.lower() in c['spz'].lower()]

for car in filt:
    idx = db["cars"].index(car)
    with st.container():
        st.subheader(f"{car['brand']} | {car['spz']}")
        if st.button("Видалити", key=f"del_{idx}"):
            db["cars"].pop(idx)
            save(db)
            st.rerun()
        with st.expander("Деталі"):
            wrk = st.text_input("Робота", key=f"w_{idx}")
            if st.button("Зберегти", key=f"s_{idx}"):
                db["cars"][idx]['history'].append(f"{datetime.now().strftime('%d.%m')} : {wrk}")
                save(db)
                st.rerun()
            for h in car['history']: st.info(h)
