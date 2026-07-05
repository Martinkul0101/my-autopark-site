import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# Налаштування сторінки
st.set_page_config(page_title="Správa Vozového Parku", layout="centered", page_icon="🚚")

DB_FILE = "garage_db.json"

# --- ЗАВАНТАЖЕННЯ ДАНИХ ---
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({"cars": {}, "repairs": [], "stock": {}}, f, ensure_ascii=False, indent=4)

try:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        db = json.load(f)
except Exception:
    db = {"cars": {}, "repairs": [], "stock": {}}

# Безпечна ініціалізація ключів
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

# --- ПЕРЕВІРКА ПЛАНОВОГО ТО ---
def zkontrolovat_udrzbu(next_date_str, next_km, current_km, is_trailer=False):
    status_date = ""
    status_km = ""
    
    try:
        t_date = datetime.strptime(next_date_str, "%Y-%m-%d").date()
        days = (t_date - datetime.today().date()).days
        if days < 0: status_date = f"🚨 Prošlé datum ({abs(days)} dní)"
        elif days <= 30: status_date = f"⚠️ Termín za {days} dní"
    except Exception:
        pass

    if not is_trailer:
        try:
            diff_km = int(next_km) - int(current_km)
            if diff_km < 0: status_km = f"🚨 Přetažen kilometráž ({abs(diff_km)} km)"
            elif diff_km <= 1500: status_km = f"⚠️ Servis za {diff_km} km"
        except Exception:
            pass
        
    if "🚨" in status_date or "🚨" in status_km:
        return f"🚨 SERVIS! ({status_date if '🚨' in status_date else status_km})"
    if "⚠️" in status_date or "⚠️" in status_km:
        return f"⚠️ Blíží se ({status_date if '⚠️' in status_date else status_km})"
        
    return "✅ V pořádku"

# =================================================================
# ЕКРАН 1: 📋 SEZNAM VOZIDEL
# =================================================================
if menu == "📋 SEZNAM VOZIDEL":
    st.title("📋 Seznam vozidel v autoparku")
    
    if not db["cars"]:
        st.info("V autoparku nejsou žádná vozidla. Přejdete na '➕ PŘIDAT VOZIDLO'.")
    else:
        # Швидкі метрики за категоріями техніки вгорі екрана
        ct_tahac = sum(1 for c in db["cars"].values() if c.get("type") == "Tahač")
        ct_prives = sum(1 for c in db["cars"].values() if c.get("type") == "Přívěs")
        ct_osobni = sum(1 for c in db["cars"].values() if c.get("type") == "Osobní auto")
        ct_autobus = sum(1 for c in db["cars"].values() if c.get("type") == "Autobus")
        
        stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
        stat_c1.metric("🚛 Tahače", f"{ct_tahac} ks")
        stat_c2.metric("📦 Přívěsy", f"{ct_prives} ks")
        stat_c3.metric("🚗 Osobní", f"{ct_osobni} ks")
        stat_c4.metric("🚌 Autobusy", f"{ct_autobus} ks")
        
        st.write("---")
        st.write("💡 **Kliknutím na řádek v tabulce** vyberete techniku pro správu nebo TO.")
        
        # Підготовка даних для таблиці
        tabela_aut = []
        for v, c in db["cars"].items():
            curr_km = int(c.get('mileage', 0))
            is_trailer = c.get("type") == "Přívěs"
            
            tabela_aut.append({
                "VIN": v,
                "Typ": c.get('type', 'Osobní auto'),
                "Značka a model": c.get('brand_model', 'Neznámé'),
                "SPZ": c.get('reg_number', '—'),
                "Tachometr (km)": "—" if is_trailer else curr_km,
                "STK Status": zkontrolovat_datum(c.get('stk_date', '')),
                "Tachograf": zkontrolovat_datum(c.get('tachograf_date', '')) if c.get('type') in ["Tahač", "Autobus"] else "—",
                "Údržba Status": zkontrolovat_udrzbu(c.get('next_to_date', ''), c.get('next_to_km', 0), curr_km, is_trailer)
            })
        
        df_cars = pd.DataFrame(tabela_aut)
        df_cars = df_cars.sort_values(by="Typ")
        
        id_vyberu = st.dataframe(
            df_cars,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single",
            key="cars_df_selection"
        )
        
        oznacene_radky = id_vyberu.get("selection", {}).get("rows", [])
        
        if oznacene_radky:
            index_auta = oznacene_radky[0]
            avin = df_cars.iloc[index_auta]["VIN"]
            car = db["cars"][avin]
            v_type = car.get('type', 'Osobní auto')
            
            st.write("---")
            st.header(f"📇 [{v_type}] {car.get('brand_model', 'Neznámé')}")
            
            # Візуальні картки
            m1, m2, m3 = st.columns(3)
            m1.metric("SPZ", car.get('reg_number', '—'))
            m2.metric("Tachometr", "— (Přívěs)" if v_type == "Přívěs" else f"{int(car.get('mileage', 0)):,} km".replace(",", " "))
            m3.metric("VIN kód", avin[:8] + "...")
            
            if v_type in ["Tahač", "Autobus"]:
                st.warning(f"⏱️ **Platnost cejchování tachografu:** {zkontrolovat_datum(car.get('tachograf_date', ''))}")
            
            # Генерація карти авто для скачування
            hist_oprav = [r for r in db["repairs"] if r["vin"] == avin]
            report_text = f"KARTA TECHNIKY [{v_type}]\n"
            report_text += f"Vygenerováno: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            report_text += f"==================================================\n\n"
            report_text += f"- Model: {car.get('brand_model', 'Neznámé')}\n"
            report_text += f"- SPZ: {car.get('reg_number', '—')}\n"
            report_text += f"- VIN: {avin}\n"
            if v_type != "Přívěs":
                report_text += f"- Tachometr: {car.get('mileage', 0)} km\n"
            report_text += f"- STK do: {car.get('stk_date', '—')}\n\n"
            report_text += f"SERVISNÍ HISTORIE:\n"
            for idx, r in enumerate(hist_oprav, 1):
                report_text += f"\n[{r.get('date', '—')}] Tachometr: {r.get('mileage', '—')} km | Cena: {r.get('cost', 0.0)} Kč\n   Práce: {r.get('description', '—')}\n   Materiál/Díly: {r.get('part_codes', '—')}\n"
            
            st.download_button(label="📥 Stáhnout kartu techniky (.txt)", data=report_text, file_name=f"karta_{car.get('reg_number','tech')}.txt", mime="text/plain", use_container_width=True)
            
            st.write("")
            t1, t2, t3, t4 = st.tabs(["🔧 Servisní záznam / TO", "📦 Použité náhradní díly", "📜 Historie oprav", "⚙️ Upravit údaje"])
            
            # Вкладка 1: Додавання сервісного запису
            with t1:
                col_s1, col_s2 = st.columns(2)
                r_date = col_s1.date_input("Datum servisu:", value=datetime.today().date())
                r_km = col_s2.number_input("Aktuální stav tachometru (km):", min_value=0, value=int(car.get('mileage', 0)) if v_type != "Přívěs" else 0, disabled=(v_type == "Přívěs"))
                
                r_desc = st.text_area("Popis servisu / práce:", key="rep_desc")
                
                st.markdown("##### 🛢️ Specifikace motorového oleje (volitelné)")
                col_oil1, col_oil2 = st.columns(2)
                oil_type = col_oil1.text_input("Typ/Viskozita oleje (např. 5W-30 Total):", key="oil_type_input").strip()
                oil_qty = col_oil2.number_input("Množství oleje (v litrech):", min_value=0.0, max_value=50.0, value=0.0, step=0.5, key="oil_qty_input")
                
                st.markdown("##### 📦 Náhradní díly")
                sklad_dily = ["-- Vlastní kód / Bez odepsání --"] + [f"{item['name']} ({pid}) [Skladem: {item.get('quantity', 0)}ks]" for pid, item in db["stock"].items()]
                vybrany_dil = st.selectbox("Vybrat díl ze skladu:", sklad_dily)
                r_parts = st.text_input("Kódy použitých dílů (ručně, pokud nejsou na skladě):")
                r_cost = st.number_input("Celková cena opravy (Kč):", min_value=0.0, step=100.0)
                
                if st.button("Uložit servisní záznam", type="primary", use_container_width=True):
                    novy_servis = {
                        "vin": avin,
                        "date": str(r_date),
                        "mileage": r_km,
                        "description": r_desc,
                        "oil_type": oil_type,
                        "oil_quantity": oil_qty,
                        "part_codes": r_parts if vybrany_dil == "-- Vlastní kód / Bez odepsání --" else vybrany_dil,
                        "cost": r_cost
                    }
                    db["repairs"].append(novy_servis)
                    if v_type != "Přívěs":
                        db["cars"][avin]["mileage"] = r_km
                    ulozit_data()
                    st.success("Servisní záznam úspěšně uložen!")
                    st.rerun()

            # Вкладка 2: Використані запчастини
            with t2:
                st.subheader("Přehled použitých dílů pro toto vozidlo")
                dily_v_a = [r for r in db["repairs"] if r["vin"] == avin and r.get("part_codes")]
                if dily_v_a:
                    for d in dily_v_a:
