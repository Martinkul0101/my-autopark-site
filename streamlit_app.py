import streamlit as st
import json
import os
from datetime import datetime

# Налаштування сторінки
st.set_page_config(page_title="Управління Автопарком", layout="wide")

DB_FILE = "garage_db.json"

# Функції для роботи з файлом бази даних
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # АВТОКОРЕКЦІЯ: Перевіряємо старі записи, щоб уникнути KeyError
        if "cars" in data:
            for vin, car in data["cars"].items():
                if "model" in car and "brand_model" not in car:
                    car["brand_model"] = car["model"]
                if "reg_number" not in car:
                    car["reg_number"] = "НЕВКАЗАНО"
        return data
    return {"cars": {}, "repairs": []}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

# --- СТИЛЬНЕ БІЧНЕ МЕНЮ ---
st.sidebar.markdown("<h2 style='color: #1a73e8; text-align: center;'>🚚 АВТОПАРК</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: gray;'>Внутрішня система обліку</p>", unsafe_allow_html=True)
st.sidebar.divider()

menu = st.sidebar.radio(
    "НАВІГАЦІЯ",
    ["📋 СПИСОК ТРАНСПОРТУ", "➕ ДОДАТИ ТЗ В АВТОПАРК", "📊 ЗАГАЛЬНИЙ ЖУРНАЛ ТО"]
)

st.sidebar.divider()
st.sidebar.info("Дані автоматично зберігаються в файл garage_db.json.")

# --- РОЗДІЛ 1: СПИСОК ТРАНСПОРТУ ТА ДЕТАЛЬНІ КАРТКИ ---
if menu == "📋 СПИСОК ТРАНСПОРТУ":
    st.markdown("# 📋 Список транспортних засобів")
    st.write("Оберіть автомобіль зі списку нижче, щоб відкрити його картку, змінити пробіг або додати ремонт.")
    st.divider()

    if not db["cars"]:
        st.info("В автопарку ще немає зареєстрованих автомобілів. Перейдіть у вкладку 'Додати ТЗ в автопарк'.")
    else:
        # Безпечне створення списку автомобілів
        car_list = [f"{car.get('brand_model', 'Невідоме авто')} [{car.get('reg_number', '—')}] (VIN: {vin})" for vin, car in db["cars"].items()]
        selected_car = st.selectbox("🔍 Швидкий пошук та вибір автомобіля для редагування:", ["-- Оберіть авто для перегляду детальної інформації --"] + car_list)
        
        st.divider()
        
        if selected_car != "-- Оберіть авто для перегляду детальної інформації --":
            active_vin = selected_car.split("VIN: ")[-1].replace(")", "")
            car_data = db["cars"][active_vin]
            
            # --- ПЕРСОНАЛЬНА КАРТКА АВТОМОБІЛЯ ---
            st.markdown(f"## 📇 Картка автомобіля: {car_data.get('brand_model', 'Невідоме авто')}")
            
            col_edit, col_repair = st.columns(2)
            
            with col_edit:
                st.markdown("#### ⚙️ Змінити поточні дані ТЗ")
                with st.form(key=f"edit_form_{active_vin}"):
                    new_brand_model = st.text_input("Марка та модель", value=car_data.get('brand_model', ''))
                    new_reg = st.text_input("Реєстраційний номер", value=car_data.get('reg_number', '')).upper()
                    new_mileage = st.text_input("Поточний кілометраж (км)", value=car_data.get('mileage', '0'))
                    
                    if st.form_submit_button("Зберегти зміни", type="primary"):
                        db["cars"][active_vin]["brand_model"] = new_brand_model
                        db["cars"][active_vin]["reg_number"] = new_reg
                        db["cars"][active_vin]["mileage"] = new_mileage
                        save_data(db)
                        st.success("Дані автомобіля успішно оновлено!")
                        st.rerun()
                        
            with col_repair:
                st.markdown("#### 🔧 Додати новий ремонт для цього авто")
                with st.form(key=f"repair_form_{active_vin}"):
                    rep_desc = st.text_area("Що було зроблено (опис робіт)", placeholder="Наприклад: Заміна масла двигуна, паливного фільтра...")
                    rep_cost = st.number_input("Вартість ремонту/запчастин (грн)", min_value=0.0, step=500.0)
                    auto_update_mileage = st.text_input("Пробіг на момент цього ТО (км)", value=car_data.get('mileage', '0'))
                    
                    if st.form_submit_button("Записати ремонт в історію"):
                        if rep_desc:
                            db["cars"][active_vin]["mileage"] = auto_update_mileage
                            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                            db["repairs"].append({
                                "vin": active_vin,
                                "date": date_str,
                                "description": rep_desc,
                                "cost": rep_cost,
                                "mileage": auto_update_mileage
                            })
                            save_data(db)
                            st.success("Новий ремонт успішно додано в базу!")
                            st.rerun()
                        else:
                            st.error("Будь ласка, введіть опис робіт перед збереженням.")
            
            st.divider()
            # --- ПЕРСОНАЛЬНА ІСТОРІЯ РЕМОНТІВ ---
            st.markdown(f"#### 📜 Історія ремонтів для {car_data.get('brand_model', '')} ({car_data.get('reg_number', '')})")
            
            personal_repairs = [r for r in db["repairs"] if r["vin"] == active_vin]
            
            if not personal_repairs:
                st.info("По цьому автомобілю ще немає жодного запису про ремонти.")
            else:
                personal_table = []
                for idx, r in enumerate(personal_repairs):
                    personal_table.append({
                        "№": idx + 1,
                        "Дата": r["date"],
                        "Виконані роботи / Запчастини": r["description"],
                        "Пробіг на момент ТО (км)": r["mileage"],
                        "Вартість": f"{r['cost']} грн"
                    })
                st.dataframe(personal_table, use_container_width=True, hide_index=True)
                
        else:
            st.markdown("### Короткий огляд автопарку:")
            for vin, car in db["cars"].items():
                with st.container(border=True):
                    c1, c2, c3 = st.columns()
                    with c1:
                        st.markdown("<h2 style='text-align: center; margin:0;'>🚛</h2>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**{car.get('brand_model', 'Невідоме авто')}** — `{car.get('reg_number', '—')}`")
                        st.caption(f"VIN: {vin}")
                    with c3:
                        st.markdown(f"📈 `{car.get('mileage', '0')} км` пробігу")

# --- РОЗДІЛ 2: ДОДАТИ ТЗ ---
elif menu == "➕ ДОДАТИ ТЗ В АВТОПАРК":
    st.markdown("# ➕ Реєстрація нового транспорту")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        car_brand_model = st.text_input("Марка та модель", placeholder="Наприклад: Scania R450")
        car_reg = st.text_input("Реєстраційний номер (Держ. номер)", placeholder="Наприклад: AA1234BB").upper()
    with col2:
        car_vin = st.text_input("VIN-код (17 знаків)").upper()
        car_mileage = st.text_input("Початковий пробіг (км)", placeholder="Наприклад: 120000")
        
    if st.button("Зареєструвати транспортний засіб", type="primary"):
        if car_brand_model and car_reg and car_vin and car_mileage:
            db["cars"][car_vin] = {
                "brand_model": car_brand_model,
                "reg_number": car_reg,
                "mileage": car_mileage
            }
            save_data(db)
            st.success(f"Транспорт {car_brand_model} успішно додано!")
            st.rerun()
        else:
            st.error("Заповніть усі поля!")

# --- РОЗДІЛ 3: ЗАГАЛЬНИЙ ЖУРНАЛ ---
elif menu == "📊 ЗАГАЛЬНИЙ ЖУРНАЛ ТО":
    st.markdown("# 📊 Загальний журнал обслуговування автопарку")
    st.divider()
    
    if not db["repairs"]:
        st.info("Журнал обслуговування порожній.")
    else:
        table_data = []
        for r in db["repairs"]:
            car = db["cars"].get(r["vin"], {"brand_model": "Видалене ТЗ", "reg_number": "—"})
            table_data.append({
                "Дата": r["date"],
                "Автомобіль": car.get("brand_model", "Видалене ТЗ"),
                "Держ. номер": car.get("reg_number", "—"),
                "VIN-код": r["vin"],
                "Виконані роботи": r["description"],
                "Пробіг (км)": r["mileage"],
                "Витрати": f"{r['cost']} грн"
            })
        st.dataframe(table_data, use_container_width=True)
