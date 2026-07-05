import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Налаштування сторінки
st.set_page_config(page_title="Správa Vozového Parku", layout="centered", page_icon="🚚")

# --- ПІДКЛЮЧЕННЯ SUPABASE ІЗ ЗАХИСТОМ ВІД ЗБОЇВ ---
@st.cache_resource
def get_supabase_client() -> Client:
    # Виправлено помилку в URL та налаштовано роботу через Secrets
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase_client()

# --- БІЧНЕ МЕНЮ ---
st.sidebar.title("🚚 AUTOPARK")
st.sidebar.write("Interní evidenční systém")
st.sidebar.divider()
menu = st.sidebar.radio("NAVIGACE", ["📋 SEZNAM VOZIDEL", "➕ PŘIDAT VOZIDLO", "📦 SKLAD NÁHRADNÍCH DÍLŮ"])

def zkontrolovat_datum(date_str):
    try:
        t_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        days = (t_date - datetime.today().date()).days
        if days < 0: return f"🚨 PROŠLÉ! ({abs(days)} dní)"
        if days <= 30: return f"⚠️ Končí za {days} dní"
        return f"✅ V pořádku ({days} dní)"
    except Exception:
        return "—"

def zkontrolovat_udrzbu(next_date_str, next_km, current_km, is_trailer=False):
    status_date, status_km = "", ""
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
    
    res_cars = supabase.table("cars").select("*").execute()
    cars_data = res_cars.data if res_cars.data else []
    
    if not cars_data:
        st.info("V autoparku nejsou žádná vozidla. Přejdete na '➕ PŘIDAT VOZIDLO'.")
    else:
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
        
        tabela_aut = []
        for c in cars_data:
            curr_km = int(c.get('mileage', 0))
            is_trailer = c.get("type") == "Přívěs"
            tabela_aut.append({
                "VIN": c.get("vin"),
                "Typ": c.get('type', 'Osobní auto'),
                "Značka a model": c.get('brand_model', 'Neznámé'),
                "SPZ": c.get('reg_number', '—'),
                "Tachometr (km)": "—" if is_trailer else curr_km,
                "STK Status": zkontrolovat_datum(c.get('stk_date', '')),
                "Tachograf": zkontrolovat_datum(c.get('tachograf_date', '')) if c.get('type') in ["Tahač", "Autobus"] else "—",
                "Údržba Status": zkontrolovat_udrzbu(c.get('next_to_date', ''), c.get('next_to_km', 0), curr_km, is_trailer)
            })
            
        df_cars = pd.DataFrame(tabela_aut).sort_values(by="Typ")
id_vyberu = st.dataframe(df_cars, use_container_width=True, hide_index=True, 
on_select="rerun", selection_mode="single", key="cars_df_select")
oznacene_radky = id_vyberu.get("selection", {}).get("rows", [])        
        if oznacene_radky:
            avin = df_cars.iloc[oznacene_radky]["VIN"].values[0]
            car = next(c for c in cars_data if c["vin"] == avin)
            v_type = car.get('type', 'Osobní auto')
            st.write("---")
            st.header(f"📇 [{v_type}] {car.get('brand_model', 'Neznámé')}")
            m1, m2 = st.columns(2)
            m1.metric("SPZ", car.get('reg_number', '—'))
            m2.metric("Tachometr", "— (Přívěs)" if v_type == "Přívěs" else f"{int(car.get('mileage', 0)):,} km".replace(",", " "))
            
            st.markdown("### 🔧 Nový servisní záznam")
            col_s1, col_s2 = st.columns(2)
            r_date = col_s1.date_input("Datum servisu:", value=datetime.today().date())
            r_km = col_s2.number_input("Aktuální stav tachometru (km):", min_value=0, value=int(car.get('mileage', 0)) if v_type != "Přívěs" else 0, disabled=(v_type == "Přívěs"))
            r_desc = st.text_area("Popis servisu / práce:", key="rep_desc")
            
            res_stock = supabase.table("stock").select("*").execute()
            stock_data = res_stock.data if res_stock.data else []
            sklad_dily = ["-- Ruční zadání --"] + [f"{item['name']} ({item['pid']})" for item in stock_data]
            vybrany_dil = st.selectbox("Vybrat díl ze skladu:", sklad_dily)
            r_parts = st.text_input("Kódy použitých dílů (pokud nejsou na skladě):")
            r_cost = st.number_input("Celková cena opravy (Kč):", min_value=0.0, step=100.0)
            
            if st.button("Uložit servisní záznam", type="primary", use_container_width=True):
                part_final = r_parts if vybrany_dil == "-- Ruční zadání --" else vybrany_dil
                novy_servis = {"vin": avin, "date": str(r_date), "mileage": int(r_km), "description": r_desc, "part_codes": part_final, "cost": float(r_cost)}
                supabase.table("repairs").insert(novy_servis).execute()
                if v_type != "Přívěs":
                    supabase.table("cars").update({"mileage": int(r_km)}).eq("vin", avin).execute()
                st.success("Servisní záznam uložen!")
                st.rerun()

            st.markdown("### 📜 Historie oprav")
            res_rep = supabase.table("repairs").select("*").eq("vin", avin).execute()
            hist_oprav = res_rep.data if res_rep.data else []
            if hist_oprav:
                tabela_dilu = [{"Datum": d.get("date", "—"), "Použité díly": d.get("part_codes", "—"), "Popis opravy": d.get("description", "—"), "Cena": f"{d.get('cost', 0.0)} Kč"} for d in hist_oprav]
                st.dataframe(pd.DataFrame(tabela_dilu), use_container_width=True, hide_index=True)
            else:
                st.info("Žádná historie oprav.")# =================================================================
# ЕКРАН 2: ➕ PŘIDAT VOZIDLO
# =================================================================
elif menu == "➕ PŘIDAT VOZIDLO":
    st.title("➕ Přidat nové vozidlo")
    with st.form("add_car_form"):
        f_type = st.selectbox("Typ techniky:", ["Osobní auto", "Tahač", "Přívěs", "Autobus"])
        f_vin = st.text_input("VIN kód (unikátní):").strip().upper()
        f_brand = st.text_input("Značka a model:")
        f_spz = st.text_input("SPZ:")
        f_km = st.number_input("Aktuální stav tachometru (km):", min_value=0, value=0)
        f_stk = st.date_input("Platnost STK do:")
        f_tach = st.date_input("Platnost tachografu (jen Tahač/Autobus):", value=datetime.today().date())
        f_next_date = st.date_input("Datum příštího TO:")
        f_next_km = st.number_input("Stav km pro příští TO:", min_value=0, value=0)
        submitted = st.form_submit_button("Uložit vozidlo", type="primary")
        
        if submitted:
            if not f_vin:
                st.error("VIN kód je povinný!")
            else:
                novy_auto = {
                    "vin": f_vin, "type": f_type, "brand_model": f_brand, 
                    "reg_number": f_spz, "mileage": int(f_km), "stk_date": str(f_stk),
                    "tachograf_date": str(f_tach) if f_type in ["Tahač", "Autobus"] else None,
                    "next_to_date": str(f_next_date), "next_to_km": int(f_next_km)
                }
                try:
                    supabase.table("cars").insert(novy_auto).execute()
                    st.success("Vozidlo úspěšně uloženo!")
                except Exception as e:
                    st.error(f"Chyba při ukládání: {e}")

# =================================================================
# ЕКРАН 3: 📦 SKLAD NÁHRADNÍCH DÍLŮ
# =================================================================
elif menu == "📦 SKLAD NÁHRADNÍCH DÍLŮ":
    st.title("📦 Sklad náhradních dílů")
    
    st.subheader("➕ Naskladnit novou položku")
    with st.form("add_stock_form"):
        f_pid = st.text_input("Kód dílu (např. SKU, OE číslo):").strip().upper()
        f_name = st.text_input("Název dílu:")
        f_qty = st.number_input("Množství (ks):", min_value=1, value=1)
        f_price = st.number_input("Nákupní cena za ks (Kč):", min_value=0.0, value=0.0, step=10.0)
        stock_submitted = st.form_submit_button("Uložit položku", type="primary")
        
        if stock_submitted:
            if not f_pid or not f_name:
                st.error("Kód a název dílu jsou povinné!")
            else:
                novy_dil = {
                    "pid": f_pid, "name": f_name, 
                    "quantity": int(f_qty), "price": float(f_price)
                }
                try:
                    supabase.table("stock").insert(novy_dil).execute()
                    st.success("Položka úspěšně naskladněna!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Chyba při ukládání na sklad: {e}")
                    
    st.write("---")
    st.subheader("📋 Aktuální stav skladu")
    res_stock = supabase.table("stock").select("*").execute()
    stock_data = res_stock.data if res_stock.data else []
    
    if stock_data:
        tabela_skladu = [{
            "Kód dílu": item.get("pid"), "Název dílu": item.get("name"),
            "Množství (ks)": item.get("quantity"), "Nákupní cena (Kč)": f"{item.get('price', 0.0)} Kč"
        } for item in stock_data]
        st.dataframe(pd.DataFrame(tabela_skladu), use_container_width=True, hide_index=True)
    else:
        st.info("Sklad je prázdný.")
