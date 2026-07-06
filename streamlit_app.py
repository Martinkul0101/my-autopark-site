import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="Správa Vozového Parku", layout="centered", page_icon="🚚")

DB_FILE = "database.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"cars": [], "repairs": [], "stock": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "cars" not in data: data["cars"] = []
            if "repairs" not in data: data["repairs"] = []
            if "stock" not in data: data["stock"] = []
            return data
    except Exception:
        return {"cars": [], "repairs": [], "stock": []}

def save_data(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Chyba při ukládání dat: {e}")

db = load_data()

def zkontrolovat_status_data(date_str):
    if not date_str or date_str == "—":
        return "—"
    try:
        t_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        days = (t_date - datetime.today().date()).days
        if days < 0: return f"🚨 PROŠLÉ! ({abs(days)} dní)"
        if days <= 30: return f"⚠️ Končí za {days} dní"
        return f"✅ V pořádku ({days} dní)"
    except Exception: return "—"

st.sidebar.title("🚚 AUTOPARK")
st.sidebar.write("Lokální evidenční systém")
st.sidebar.divider()

menu = st.sidebar.radio("NAVIGACE", ["📋 Seznam vozidel", "➕ Přidat nové auto", "📦 Sklad dílů"])
