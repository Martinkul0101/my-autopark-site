import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Správa Autoparku", layout="wide", page_icon="🚗")

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

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
                d_status = "❌ Expirováno (Datum)"
            elif rozdil <= 30:
                d_status = "⚠️ Blíží se (Datum)"
            else:
                d_status = "✅ OK (Datum)"
        except ValueError:
            pass

    k_status = "-"
    if not is_trailer and next_km and current_km:
        rozdil_km = next_km - current_km
        if rozdil_km < 0:
            k_status = "❌ Expirováno (Km)"
        elif rozdil_km <= 2000:
            k_status = "⚠️ Blíží se (Km)"
        else:
            k_status = "✅ OK (Km)"

    if "❌" in d_status or "❌" in k_status:
        return "❌ Nutný servis"
    elif "⚠️" in d_status or "⚠️" in k_status:
        return "⚠️ Servis se blíží"
    elif "✅" in d_status or "✅" in k_status: # Виправлено друкарську помилку
        return "✅ OK"
    return "-"

st.title("🚗 Systém správy autoparku")

try:
    response = supabase.table("cars").select("*").execute()
    cars_data = response.data
except Exception as e:
    st.error(f"Chyba při načítání dat: {e}")
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
    
    if "Vybrat" not in df_cars.columns:
        df_cars.insert(0, "Vybrat", False)
    
    id_vyberu = st.data_editor(
        df_cars, 
        use_container_width=True, 
        hide_index=True,
        disabled=["VIN", "Značka a model", "SPZ", "Typ", "Tachometr (km)", "STK Status", "Tachograf", "Údržba Status"]
    )
    
    vybrane_indexy = id_vyberu[id_vyberu["Vybrat"] == True].index.tolist()
    
    # Захист від вибору кількох автомобілів одночасно
    if len(vybrane_indexy) > 1:
        st.warning("⚠️ Prosím, vyberte pouze jedno vozidlo pro přidání servisního záznamu.")
    elif len(vybrane_indexy) == 1:
        izvoleny_index = vybrane_indexy[0]
        avin = df_cars.iloc[izvoleny_index]["VIN"]
        
        car = next((c for c in cars_data if c["vin"] == avin), None)
        
        if car:
            v_type = car.get('type', 'Osobní auto')
            
            st.write("---")
            st.header(f"🚖 [{v_type}] {car.get('brand_model', 'Neznámé')}")
            m1, m2 = st.columns(2)
            m1.metric("SPZ", car.get('reg_number', '-'))
            m2.metric("Tachometr", f"- (Přívěs)" if v_type == "Přívěs" else f"{car.get('mileage', 0)} km")

            st.markdown("### 🔧 Nový servisní záznam")
            col_s1, col_s2 = st.columns(2)
            r_date = col_s1.date_input("Datum servisu:", value=datetime.now())
            r_km = col_s2.number_input("Aktuální stav tachometru (km):", min_value=0, value=int(car.get('mileage', 0)))
            r_desc = st.text_area("Popis servisu / práce:", value="")

            try:
                res_stock = supabase.table("stock").select("*").execute()
                stock_data = res_stock.data
            except Exception:
                stock_data = []

            # Показуємо лише ті деталі, які є в наявності (> 0)
            sklad_dily = ["-- Ruční zadání --"] + [f"{item['name']} (Sklad: {item['quantity']} ks)" for item in stock_data if item.get('quantity', 0) > 0]
            vybrany_dil = st.selectbox("Vybrat použitý díl ze skladu:", sklad_dily)
            r_parts = st.text_input("Kódy použitých dílů (pokud není na skladě):")
            r_cost = st.number_input("Celková cena opravy (Kč):", min_value=0.0, value=0.0, step=100.0)

            if st.button("Uložit servisní záznam", type="primary"):
                part_final = r_parts if vybrany_dil == "-- Ruční zadání --" else vybrany_dil
                
                # Використовуємо .isoformat() для безпечного формату дати в БД
                novy_servis = {
                    "vin": avin, 
                    "date": r_date.isoformat(), 
                    "km": r_km, 
                    "description": r_desc, 
                    "parts": part_final, 
                    "cost": r_cost
                }
                
                try:
                    # 1. Uložení servisního záznamu
                    supabase.table("repairs").insert(novy_servis).execute()
                    
                    # 2. Aktualizace tachometru v tabulce cars (mimo přívěsy)
                    if v_type != "Přívěs":
                        supabase.table("cars").update({"mileage": r_km}).eq("vin", avin).execute()
                    
                    # 3. Odečtení použitého dílu ze skladu
                    if vybrany_dil != "-- Ruční zadání --":
                        # Знайдемо оригінальний запис деталі, щоб отримати її поточну кількість та ідентифікатор
                        selected_stock = next((item for item in stock_data if f"{item['name']} (Sklad: {item['quantity']} ks)" == vybrany_dil), None)
                        
                        if selected_stock and selected_stock.get('quantity', 0) > 0:
                            new_quantity = selected_stock['quantity'] - 1
                            # Визначаємо ключ для оновлення (бажано 'id', якщо його немає, використовуємо 'name')
                            filter_col = "id" if "id" in selected_stock else "name"
                            supabase.table("stock").update({"quantity": new_quantity}).eq(filter_col, selected_stock[filter_col]).execute()

                    st.success("Servisní záznam uložen a data aktualizována!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Chyba při ukládání: {e}")
