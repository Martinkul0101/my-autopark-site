import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Nastavení stránky musí být první příkaz Streamlitu
st.set_page_config(page_title="Správa Autoparku", layout="wide", page_icon="🚗")

# Připojení k databázi
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- POMOCNÉ FUNKCE ---
def zkontrolovat_datum(d_str):
    if not d_str:
        return "-"
    try:
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        rozdil = (dt - datetime.now()).days
        if rozdil < 0:
            return f"❌ Expirováno ({dt.strftime('%d.%m.%Y')})"
        elif rozdil <= 30:
            return f"⚠️ Blíží se ({dt.strftime('%d.%m.%Y')})"
        else:
            return f"✅ OK ({dt.strftime('%d.%m.%Y')})"
    except ValueError:
        return "-"

def zkontrolovat_udrzbu(next_date_str, next_km, current_km, is_trailer=False):
    d_status = "-"
    if next_date_str:
        try:
            dt = datetime.strptime(next_date_str, "%Y-%m-%d")
            rozdil = (dt - datetime.now()).days
            if rozdil < 0:
                d_status = "❌"
            elif rozdil <= 30:
                d_status = "⚠️"
            else:
                d_status = "✅"
        except ValueError:
            pass

    k_status = "-"
    if not is_trailer and next_km and current_km:
        rozdil_km = next_km - current_km
        if rozdil_km < 0:
            k_status = "❌"
        elif rozdil_km <= 2000:
            k_status = "⚠️"
        else:
            k_status = "✅"

    if "❌" in d_status or "❌" in k_status:
        return "❌ Nutný servis"
    elif "⚠️" in d_status or "⚠️" in k_status:
        return "⚠️ Servis se blíží"
    elif "✅" in d_status or "✅" in k_status:
        return "✅ OK"
    return "-"

# --- BOČNÍ MENU ---
st.sidebar.title("📌 Navigace")
menu = st.sidebar.radio("Vyberte sekci:", ["🚗 Seznam vozidel", "📦 Sklad náhradních dílů"])

# ==========================================
# SEKCÍ 1: SEZNAM VOZIDEL
# ==========================================
if menu == "🚗 Seznam vozidel":
    st.title("🚗 Systém správy autoparku")

    try:
        response = supabase.table("cars").select("*").execute()
        cars_data = response.data
    except Exception as e:
        st.error(f"Chyba při načítání dat z tabulky 'cars': {e}")
        cars_data = []

    if not cars_data:
        st.info("V databázi nejsou žádná vozidla.")
    else:
        tabela_aut = []
        for c in cars_data:
            is_trailer = c.get('type') == 'Přívěs'
            curr_km = c.get('mileage', 0)
            
            tabela_aut.append({
                "VIN": c.get('vin', '-'),
                "Značka a model": c.get('brand_model', 'Neznámé'),
                "SPZ": c.get('reg_number', '-'),
                "Typ": c.get('type', 'Osobní'),
                "Tachometr (km)": "-" if is_trailer else curr_km,
                "STK Status": zkontrolovat_datum(c.get('stk_date', '')),
                "Tachograf": zkontrolovat_datum(c.get('tachograf_date', '')),
                "Údržba Status": zkontrolovat_udrzbu(c.get('next_to_date', ''), c.get('next_to_km', 0), curr_km, is_trailer)
            })

        df_cars = pd.DataFrame(tabela_aut).sort_values(by="Typ")
        
        # Přidání sloupce pro výběr
        if "Vybrat" not in df_cars.columns:
            df_cars.insert(0, "Vybrat", False)
        
        id_vyberu = st.data_editor(
            df_cars, 
            use_container_width=True, 
            hide_index=True,
            disabled=[
                "VIN", "Značka a model", "SPZ", "Typ", 
                "Tachometr (km)", "STK Status", "Tachograf", "Údržba Status"
            ]
        )
        
        vybrane_indexy = id_vyberu[id_vyberu["Vybrat"] == True].index.tolist()
        
        if len(vybrane_indexy) > 1:
            st.warning("⚠️ Prosím, vyberte pouze jedno vozidlo ze seznamu.")
        elif len(vybrane_indexy) == 1:
            izvoleny_index = vybrane_indexy[0]
            avin = df_cars.iloc[izvoleny_index]["VIN"]
            
            car = next((c for c in cars_data if c["vin"] == avin), None)
            
            if car:
                v_type = car.get('type', 'Osobní auto')
                brand_model = car.get('brand_model', 'Neznámé')
                
                st.write("---")
                st.header(f"🚖 [{v_type}] {brand_model} (SPZ: {car.get('reg_number', '-')})")
                
                # --- SYSTÉM ZÁLOŽEK ---
                tab1, tab2, tab3 = st.tabs(["📋 Specifikace & Díly", "🔧 Nový servis", "📖 Historie oprav"])
                
                # ZÁLOŽKA 1: Specifikace
                with tab1:
                    st.subheader("Technická data a doporučené díly")
                    if "CR-V" in brand_model or "Honda" in brand_model:
                        col_sp1, col_sp2, col_sp3 = st.columns(3)
                        col_sp1.info("**Motor:** 2.2 Diesel (103 kW)\n\n**Olej:** 0W-30 / 5W-30\n\n**Objem oleje:** ~5.9 l")
                        col_sp2.warning("**Filtry (Kódy):**\n\nOlejový: *HO-123*\n\nVzduchový: *HA-456*\n\nPalivový: *HF-789*")
                        col_sp3.success("**Pneumatiky:**\n\nRozměr: 225/60 R18\n\nTlak: 2.1 bar")
                    elif v_type == "Přívěs":
                        st.info("Specifikace pro přívěs: Nápravy, tlak pneu, typ brzdového obložení...")
                    else:
                        st.info("Zde se zobrazí technická data pro tento konkrétní model (bude napojeno na databázi).")

                # ZÁLOŽKA 2: Nový servis
                with tab2:
                    col_s1, col_s2 = st.columns(2)
                    r_date = col_s1.date_input("Datum servisu:", value=datetime.now())
                    r_km = col_s2.number_input("Aktuální stav tachometru (km):", min_value=0, value=int(car.get('mileage', 0)))
                    r_desc = st.text_area("Popis servisu / práce:", value="")

                    try:
                        res_stock = supabase.table("stock").select("*").execute()
                        stock_data = res_stock.data
                    except Exception:
                        stock_data = []

                    sklad_dily = ["-- Ruční zadání --"] + [f"{item['name']} (Sklad: {item['quantity']} ks)" for item in stock_data if item.get('quantity', 0) > 0]
                    vybrany_dil = st.selectbox("Vybrat použitý díl ze skladu:", sklad_dily)
                    r_parts = st.text_input("Kódy použitých dílů (pokud není na skladě):")
                    r_cost = st.number_input("Celková cena opravy (Kč):", min_value=0.0, value=0.0, step=100.0)

                    if st.button("Uložit servisní záznam", type="primary"):
                        part_final = r_parts if vybrany_dil == "-- Ruční zadání --" else vybrany_dil
                        novy_servis = {
                            "vin": avin, 
                            "date": r_date.isoformat(), 
                            "km": r_km, 
                            "description": r_desc, 
                            "parts": part_final, 
                            "cost": r_cost
                        }
                        
                        try:
                            supabase.table("repairs").insert(novy_servis).execute()
                            
                            if v_type != "Přívěs":
                                supabase.table("cars").update({"mileage": r_km}).eq("vin", avin).execute()
                            
                            if vybrany_dil != "-- Ruční zadání --":
                                selected_stock = next((item for item in stock_data if f"{item['name']} (Sklad: {item['quantity']} ks)" == vybrany_dil), None)
                                if selected_stock and selected_stock.get('quantity', 0) > 0:
                                    filter_col = "id" if "id" in selected_stock else "name"
                                    supabase.table("stock").update({"quantity": selected_stock['quantity'] - 1}).eq(filter_col, selected_stock[filter_col]).execute()

                            st.success("Záznam byl úspěšně uložen!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Chyba při ukládání záznamu: {e}")

                # ZÁLOŽKA 3: Historie oprav
                with tab3:
                    st.subheader("Historie údržby")
                    try:
                        res_repairs = supabase.table("repairs").select("*").eq("vin", avin).order("date", desc=True).execute()
                        historie_data = res_repairs.data
                        
                        if not historie_data:
                            st.info("Pro toto vozidlo zatím nejsou evidovány žádné servisní záznamy.")
                        else:
                            df_hist = pd.DataFrame(historie_data)
                            df_hist = df_hist.rename(columns={
                                "date": "Datum", 
                                "km": "Tachometr", 
                                "description": "Popis práce", 
                                "parts": "Použité díly", 
                                "cost": "Cena (Kč)"
                            })
                            cols_to_show = ["Datum", "Tachometr", "Popis práce", "Použité díly", "Cena (Kč)"]
                            
                            st.dataframe(
                                df_hist[cols_to_show], 
                                use_container_width=True, 
                                hide_index=True
                            )
                            
                    except Exception as e:
                        st.error(f"Chyba při načítání historie: {e}")

# ==========================================
# SEKCÍ 2: SKLAD NÁHRADNÍCH DÍLŮ
# ==========================================
elif menu == "📦 Sklad náhradních dílů":
    st.title("📦 Sklad náhradních dílů")
    
    try:
        res_stock = supabase.table("stock").select("*").order("name").execute()
        stock_data = res_stock.data
    except Exception as e:
        st.error(f"Chyba při načítání skladu: {e}")
        stock_data = []

    if not stock_data:
        st.info("Sklad je momentálně prázdný.")
    else:
        df_stock = pd.DataFrame(stock_data)
        display_cols = {'name': 'Název dílu', 'quantity': 'Počet kusů skladem'}
        
        # Виправлений і розбитий на рядки код для таблиці складу
        st.dataframe(
            df_stock.rename(columns=display_cols)[['Název dílu', 'Počet kusů skladem']], 
            use_container_width=True, 
            hide_index=True
        )

    st.write("---")
    st.markdown("### ➕ Přidat nový díl")
    col_n1, col_n2 = st.columns(2)
    new_part_name = col_n1.text_input("Název dílu:")
    new_part_qty = col_n2.number_input("Množství (ks):", min_value=1, value=1, step=1)
    
    if st.button("Uložit do skladu", type="primary"):
        if new_part_name.strip() != "":
            try:
                existujici = next((item for item in stock_data if item['name'].lower() == new_part_name.lower()), None)
                if existujici:
                    filter_col = "id" if "id" in existujici else "name"
                    supabase.table("stock").update({"quantity": existujici['quantity'] + new_part_qty}).eq(filter_col, existujici[filter_col]).execute()
                else:
                    supabase.table("stock").insert({"name": new_part_name, "quantity": new_part_qty}).execute()
                
                st.success("Sklad byl úspěšně aktualizován.")
                st.rerun()
            except Exception as e:
                st.error(f"Chyba při aktualizaci skladu: {e}")
        else:
            st.warning("⚠️ Zadejte prosím platný název dílu.")
