import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Správa Vozového Parku", layout="centered", page_icon="🚚")

DB_FILE = "garage_db.json"

# --- ЗАВАНТАЖЕННЯ ДАНИХ ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"cars": {}, "repairs": [], "stock": {}}, f)

try:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
except Exception:
    db = {"cars": {}, "repairs": [], "stock": {}}

if "cars" not in db: db["cars"] = {}
if "repairs" not in db: db["repairs"] = []
if "stock" not in db: db["stock"] = {}

# --- СТАНДАРТНА ФУНКЦІЯ ЗБЕРЕЖЕННЯ ---
def ulozit_data():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# --- БІЧНЕ МЕНЮ ---
st.sidebar.title("🚚 AUTOPARK")
st.sidebar.write("Interní evidenční systém")
st.sidebar.divider()
menu = st.sidebar.radio("NAVIGACE", ["📋 SEZNAM VOZIDEL", "➕ PŘIDAT VOZIDLO", "📦 SKLAD NÁHRADNÍCH DÍLŮ"])

# --- ПЕРЕВІРКА ДАТ ---
def zkontrolovat_datum(date_str):
    try:
        t_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        days = (t_date - datetime.today().date()).days
        if days < 0: return f"🚨 PROŠLÉ! ({abs(days)} dní)"
        if days <= 30: return f"⚠️ Končí za {days} dní"
        return f"✅ V pořádku ({days} dní)"
    except Exception:
        return "—"

# =================================================================
# ЕКРАН 1: 📋 SEZNAM VOZIDEL
# =================================================================
if menu == "📋 SEZNAM VOZIDEL":
    st.title("📋 Seznam vozidel v autoparku")
    
    if not db["cars"]:
        st.info("V autoparku nejsou žádná vozidla. Přejdete na '➕ PŘIDAT VOZIDLO'.")
    else:
        seznam_aut = ["-- Vyberte auto --"] + [f"{c['brand_model']} [{c['reg_number']}] (VIN: {v})" for v, c in db["cars"].items()]
        vybrane_auto = st.selectbox("🔍 Rychlý výběr vozidla:", seznam_aut)
        
        if vybrane_auto != "-- Vyberte auto --":
            avin = vybrane_auto.split("VIN: ")[-1].replace(")", "").strip()
            car = db["cars"][avin]
            
            st.header(f"📇 {car.get('brand_model', 'Neznámé auto')}")
            st.write(f"**VIN:** {avin} | **SPZ:** {car.get('reg_number', '—')} | **Tachometr:** {car.get('mileage', '0')} km")
            st.write(f"**STK:** {zkontrolovat_datum(car.get('stk_date', ''))}")
            st.write(f"**Pojištění:** {zkontrolovat_datum(car.get('insurance_date', ''))}")
            
            st.write("---")
            t1, t2 = st.tabs(["⚙️ Upravit údaje", "🔧 Přidat servisní záznam"])
            
            with t1:
                e_model = st.text_input("Značka a model:", value=car.get('brand_model', ''))
                e_spz = st.text_input("Registrační značka (SPZ):", value=car.get('reg_number', '')).upper()
                e_km = st.text_input("Stav tachometru (km):", value=car.get('mileage', '0'))
                
                try:
                    c_stk = datetime.strptime(car.get("stk_date", str(datetime.today().date())), "%Y-%m-%d").date()
                    c_ins = datetime.strptime(car.get("insurance_date", str(datetime.today().date())), "%Y-%m-%d").date()
                except Exception:
                    c_stk = datetime.today().date()
                    c_ins = datetime.today().date()
                    
                e_stk = st.date_input("Konec platnosti STK:", value=c_stk)
                e_ins = st.date_input("Konec platnosti pojištění:", value=c_ins)
                
                if st.button("💾 Uložit změny"):
                    db["cars"][avin]["brand_model"] = e_model
                    db["cars"][avin]["reg_number"] = e_spz
                    db["cars"][avin]["mileage"] = e_km
                    db["cars"][avin]["stk_date"] = str(e_stk)
                    db["cars"][avin]["insurance_date"] = str(e_ins)
                    ulozit_data()
                    st.success("Aktualizováno!")
                    st.rerun()
                    
            with t2:
                r_desc = st.text_area("Popis servisu / práce:")
                
                sklad_dily = ["-- Vlastní kód / Bez odepsání ze skladu --"] + [f"{item['name']} ({pid}) [Skladem: {item['quantity']}ks]" for pid, item in db["stock"].items() if item.get('quantity', 0) > 0]
                r_sklad = st.selectbox("Použít náhradní díl ze skladu:", sklad_dily)
                
                r_custom = st.text_input("Vlastní kód dílu (pokud není na skladě):")
                r_km = st.text_input("Stav tachometru při opravě (km):", value=car.get('mileage', '0'))
                r_cost = st.number_input("Cena celkem (Kč):", min_value=0.0, step=100.0)
                
                if st.button("🛠️ Zapsat servis do historie"):
                    if not r_desc:
                        st.error("Zadejte popis prací.")
                    else:
                        kod_dilu = "—"
                        if r_sklad != "-- Vlastní kód / Bez odepsání ze skladu --":
                            chosen_id = r_sklad.split(" (")[-1].split(")")[0].strip()
                            kod_dilu = chosen_id
                            if chosen_id in db["stock"] and db["stock"][chosen_id]["quantity"] > 0:
                                db["stock"][chosen_id]["quantity"] -= 1
                        elif r_custom:
                            kod_dilu = r_custom.upper().strip()
                            
                        db["cars"][avin]["mileage"] = r_km
                        d_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                        db["repairs"].append({"vin": avin, "date": d_str, "description": r_desc, "part_codes": kod_dilu, "cost": r_cost, "mileage": r_km})
                        ulozit_data()
                        st.success("Servis úspěšně zapsán!")
                        st.rerun()
                        
            st.write("---")
            st.subheader("📜 Historie oprav a dílů")
            hist_oprav = [r for r in db["repairs"] if r["vin"] == avin]
            if not hist_oprav:
                st.info("Pro toto vozidlo nejsou žádné záznamy.")
            else:
                rep_records = []
                for r in hist_oprav:
                    rep_records.append({"Datum": r.get("date", "—"), "Popis práce": r.get("description", "—"), "Kód dílu": r.get("part_codes", "—"), "Tachometr": f"{r.get('mileage', '0')} km", "Cena": f"{r.get('cost', 0.0):,.2f} Kč"})
                st.dataframe(pd.DataFrame(rep_records), use_container_width=True, hide_index=True)

# =================================================================
# ЕКРАН 2: ➕ PŘIDAT VOZIDLO
# =================================================================
elif menu == "➕ PŘIDAT VOZIDLO":
    st.title("➕ Přidat nové vozidlo")
    a_vin = st.text_input("VIN kód vozidla (Unikátní klíč):").upper().strip()
    a_model = st.text_input("Značka a model (Např. Scania R450):")
    a_spz = st.text_input("Registrační značka (SPZ):").upper()
    a_km = st.text_input("Stav tachometru (km):", value="0")
    
    if st.button("✅ Registrovat vozidlo do systému"):
        if not a_vin:
            st.error("Vyplňte VIN kód.")
        elif a_vin in db["cars"]:
            st.error("Tento VIN kód již v systému existuje!")
        else:
            db["cars"][a_vin] = {"brand_model": a_model, "reg_number": a_spz if a_spz else "NEUVEDENO", "mileage": a_km, "stk_date": str(datetime.today().date()), "insurance_date": str(datetime.today().date())}
            ulozit_data()
            st.success("Vozidlo úspěšně registrováno!")
            st.rerun()

# =================================================================
# ЕКРАН 3: 📦 SKLAD NÁHRADNÍCH DÍLŮ
# =================================================================
elif menu == "📦 SKLAD NÁHRADNÍCH DÍLŮ":
    st.title("📦 Sklad náhradních dílů")
    
    p_items = len(db["stock"])
    p_value = sum(item.get("quantity", 0) * item.get("price", 0.0) for item in db["stock"].values())
    
    c1, c2 = st.columns(2)
    c1.metric("Počet položek na skladě", p_items)
    c2.metric("Celková hodnota skladu", f"{p_value:,.2f} Kč")
    
    st.write("---")
    st.subheader("📥 Naskladnit novou položku")
    s_id = st.text_input("Kód dílu / Obj. číslo (např. OIL-5W30):").upper().strip()
    s_name = st.text_input("Název náhradního dílu:")
    s_qty = st.number_input("Množství (ks):", min_value=1, step=1)
    s_price = st.number_input("Nákupní cena za jednotku (Kč):", min_value=0.0, step=10.0)
    
    if st.button("📥 Přidat položku na sklad"):
        if not s_id or not s_name:
            st.error("Vyplňte kód a název dílu.")
        else:
            if s_id in db["stock"]:
                db["stock"][s_id]["quantity"] += s_qty
                db["stock"][s_id]["price"] = s_price
            else:
                db["stock"][s_id] = {"name": s_name, "quantity": s_qty, "price": s_price}
            ulozit_data()
            st.success("Zboží bylo naskladněno!")
            st.rerun()
            
    st.write("---")
    st.subheader("📊 Aktuální skladové zásoby")
    if not db["stock"]:
        st.info("Sklad je prázdný.")
    else:
        st_list = []
        for pid, item in db["stock"].items():
            st_list.append({"Kód dílu": pid, "Název dílu": item.get("name", "—"), "Množství (ks)": item.get("quantity", 0), "Cena/ks": f"{item.get('price', 0.0):,.2f} Kč", "Celkem": f"{(item.get('quantity', 0) * item.get('price', 0.0)):,.2f} Kč"})
        st.dataframe(pd.DataFrame(st_list), use_container_width=True, hide_index=True)
    