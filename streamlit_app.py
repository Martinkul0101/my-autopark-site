import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 1. Konfigurace stránky (Musí být jako první Streamlit příkaz)
st.set_page_config(page_title="Správa Vozového Parku", layout="centered", page_icon="🚚")

DB_FILE = "database.json"

# 2. Lokální databáze (Funkce pro načítání a ukládání JSON souboru)
def load_data():
    if not os.path.exists(DB_FILE):
        return {"cars": [], "repairs": [], "stock": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Kontrola přítomnosti všech klíčů v databázi
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

# Inicializace databáze do paměti aplikace
db = load_data()

# 3. Pomocná funkce pro analýzu termínů (STK, Pojištění)
def zkontrolovat_status_data(date_str):
    if not date_str or date_str == "—":
        return "—"
    try:
        t_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        days = (t_date - datetime.today().date()).days
        if days < 0:
            return f"🚨 PROŠLÉ! ({abs(days)} dní)"
        if days <= 30:
            return f"⚠️ Končí za {days} dní"
        return f"✅ V pořádku ({days} dní)"
    except Exception:
        return "—"

# 4. Boční navigační menu
st.sidebar.title("🚚 AUTOPARK")
st.sidebar.write("Lokální evidenční systém")
st.sidebar.divider()

menu = st.sidebar.radio("NAVIGACE", ["📋 Seznam vozidel", "➕ Přidat nové auto", "📦 Sklad dílů"])

# =================================================================
# OBRAZOVKA 1: 📋 SEZNAM VOZIDEL
# =================================================================
if menu == "📋 Seznam vozidel":
    st.title("📋 Seznam vozidel v autoparku")
    st.write("Kliknutím на řádek v tabulce otevřete kartu vozidla, historii oprav nebo přidejte servisní záznam.")
    
    cars_data = db["cars"]
    
    if not cars_data:
        st.info("V autoparku nejsou žádná vozidla. Přejděte na '➕ Přidat nové auto' pro registraci prvního vozidla.")
    else:
        # Výpočet statistik pro horní panely
        ct_tahac = sum(1 for c in cars_data if c.get("type") == "Tahač")
        ct_prives = sum(1 for c in cars_data if c.get("type") == "Přívěs")
        ct_osobni = sum(1 for c in cars_data if c.get("type") == "Osobní auto")
        ct_autobus = sum(1 for c in cars_data if c.get("type") == "Autobus")
        
        stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
        stat_c1.metric("🚚 Tahače", f"{ct_tahac} ks")
        stat_c2.metric("📦 Přívěsy", f"{ct_prives} ks")
        stat_c3.metric("🚗 Osobní", f"{ct_osobni} ks")
        stat_c4.metric("🚌 Autobusy", f"{ct_autobus} ks")
        st.write("---")
        
        # Sestavení tabulky pro zobrazení
        tabela_aut = []
        for c in cars_data:
            curr_km = int(c.get('mileage', 0))
            is_trailer = c.get("type") == "Přívěs"
            tabela_aut.append({
                "VIN": c.get("vin"),
                "Typ": c.get('type', 'Osobní auto'),
                "Značka a model": c.get('brand_model', 'Neznámé'),
                "SPZ": c.get('reg_number', '—'),
                "Tachometr": f"{curr_km:,} km".replace(",", " ") if not is_trailer else "—",
                "STK Status": zkontrolovat_status_data(c.get('stk_date', '')),
                "Pojištění Status": zkontrolovat_status_data(c.get('insurance_date', ''))
            })
            
        df_cars = pd.DataFrame(tabela_aut).sort_values(by="Typ")
        
        # Interaktivní dataframe s výběrem řádku
        id_vyberu = st.dataframe(
            df_cars, 
            use_container_width=True, 
            hide_index=True, 
            on_select="rerun", 
            selection_mode="single", 
            key="cars_df_selection"
        )
        
        oznacene_radky = id_vyberu.get("selection", {}).get("rows", [])
        
        # --- DETAIL VOZIDLA (PO ROZKLIKNUTÍ ŘÁDKU) ---
        if oznacene_radky:
            vybrany_index = oznacene_radky[0]
            avin = df_cars.iloc[vybrany_index]["VIN"]
            
            # Bezpečné nalezení vybraného vozu v databázi
            car = next((c for c in cars_data if c["vin"] == avin), None)
            
            if car:
                v_type = car.get('type', 'Osobní auto')
                is_trailer = v_type == "Přívěs"
                
                st.write("---")
                st.header(f"📇 [{v_type}] {car.get('brand_model', 'Neznámé')} ({car.get('reg_number', '—')})")
                
                # Hlavní metriky karty vozidla
                m1, m2, m3 = st.columns(3)
                m1.metric("Aktuální tachometr", f"{int(car.get('mileage', 0)):,} km".replace(",", " ") if not is_trailer else "— (Přívěs)")
                m2.metric("Příští TO při", f"{int(car.get('next_to_km', 0)):,} km".replace(",", " ") if not is_trailer else "—")
                m3.metric("VIN kód", car.get("vin"))
                
                st.subheader("📆 Termíny dokumentů a revizí")
                st.markdown(f"**Platnost STK do:** {car.get('stk_date', '—')} ({zkontrolovat_status_data(car.get('stk_date', ''))})")
                st.markdown(f"**Platnost pojištění do:** {car.get('insurance_date', '—')} ({zkontrolovat_status_data(car.get('insurance_date', ''))})")
                st.markdown(f"**Datum příštího TO:** {car.get('next_to_date', '—')}")
                
                # --- FORMULÁŘ PRO NOVÝ SERVISNÍ ZÁZNAM ---
                st.markdown("### 🔧 Nový servisní záznam / oprava")
                
                stock_data = db["stock"]
                sklad_dily = ["-- Ruční zadání / Bez dílu ze skladu --"] + [f"{item['name']} ({item['pid']}) - Skladem: {item['quantity']}ks" for item in stock_data if int(item.get('quantity', 0)) > 0]
                
                with st.form("new_repair_form"):
                    col_s1, col_s2 = st.columns(2)
                    r_date = col_s1.date_input("Datum servisu:", value=datetime.today().date())
                    r_km = col_s2.number_input("Nový stav tachometru (km):", min_value=0, value=int(car.get('mileage', 0)), disabled=is_trailer)
                    
                    r_desc = st.text_area("Popis provedené práce / servisu:")
                    vybrany_dil = st.selectbox("Použít díl ze skladu:", sklad_dily)
                    r_parts_manual = st.text_input("Kódy použitých dílů (pokud ručně / nejsou skladem):")
                    r_cost = st.number_input("Celková cena opravy (Kč):", min_value=0.0, step=100.0)
                    
                    repair_submitted = st.form_submit_button("Uložit servisní záznam", type="primary", use_container_width=True)
                    
                    if repair_submitted:
                        part_final = r_parts_manual if vybrany_dil.startswith("-- Ruční zadání") else vybrany_dil
                        
                        novy_servis = {
                            "vin": avin,
                            "date": str(r_date),
                            "mileage": int(r_km) if not is_trailer else 0,
                            "description": r_desc,
                            "part_codes": part_final,
                            "cost": float(r_cost)
                        }
                        
                        db["repairs"].append(novy_servis)
                        
                        # Aktualizace stavu tachometru vozidla
                        if not is_trailer:
                            for c_item in db["cars"]:
                                if c_item["vin"] == avin:
                                    c_item["mileage"] = int(r_km)
                                    
                        # Automatické odečtení dílu ze skladu
                        if not vybrany_dil.startswith("-- Ruční zadání"):
                            try:
                                start_idx = vybrany_dil.rfind("(") + 1
                                end_idx = vybrany_dil.rfind(")")
                                pid_extracted = vybrany_dil[start_idx:end_idx]
                                for item in db["stock"]:
                                    if item["pid"] == pid_extracted and item["quantity"] > 0:
                                        item["quantity"] -= 1
                            except Exception:
                                pass
                                
                        save_data(db)
                        st.success("Servisní záznam úspěšně uložen!")
                        st.rerun()

                # --- ZOBRAZENÍ HISTORIE OPRAV ---
                st.markdown("### 📜 Historie oprav tohoto vozidla")
                hist_oprav = [d for d in db["repairs"] if d.get("vin") == avin]
                
                if hist_oprav:
                    tabela_dilu = []
                    for d in hist_oprav:
                        tabela_dilu.append({
                            "Datum": d.get("date", "—"),
                            "Tachometr": f"{int(d.get('mileage', 0)):,} km".replace(",", " ") if not is_trailer else "—",
                            "Použité díly": d.get("part_codes", "—"),
                            "Popis opravy": d.get("description", "—"),
                            "Cena (Kč)": f"{d.get('cost', 0.0):,} Kč".replace(",", " ")
                        })
                    st.dataframe(pd.DataFrame(tabela_dilu), use_container_width=True, hide_index=True)
                else:
