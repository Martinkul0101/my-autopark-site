import streamlit as st
import pandas as pd

# Налаштування сторінки
st.set_page_config(page_title="Тест Автопарку", layout="centered", page_icon="🚚")

# --- БІЧНЕ МЕНЮ ---
st.sidebar.title("🚚 AUTOPARK")
st.sidebar.write("Режим розробки та дизайну")
st.sidebar.divider()

# Створюємо перемикач екранів у меню
menu = st.sidebar.radio("НАВІГАЦІЯ", ["📋 Списоки техніки", "➕ Додати нове авто", "📦 Склад деталей"])

# --- ЕКРАН 1: СПИСОК ТЕХНІКИ ---
if menu == "📋 Списоки техніки":
    st.title("📋 Списоки техніки в автопарку")
    st.write("Тут буде відображатися загальна таблиця з усім транспортом.")
    
    # Робимо гарні картки статистики вгорі
    c1, c2, c3 = st.columns(3)
    c1.metric("🚚 Тягачі", "5 од.")
    c2.metric("📦 Причепи", "3 од.")
    c3.metric("🚗 Легкові", "2 од.")
    st.write("---")
    
    # Створюємо тимчасову демонстраційну таблицю, щоб оцінити зовнішній вигляд
    test_data = {
        "Держ. номер": ["AA 1111 BB", "BC 2222 CE", "AM 3333 KH"],
        "Тип": ["Тягач", "Причіп", "Легкове авто"],
        "Марка та модель": ["Volvo FH16", "Schmitz", "Skoda Octavia"],
        "Пробіг (км)": [450000, "—", 120000],
        "Статус ТО": ["✅ В порядку", "🚨 Прострочено!", "⚠️ Скоро термін"]
    }
    df = pd.DataFrame(test_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- ЕКРАН 2: ДОДАТИ АВТО ---
elif menu == "➕ Додати нове авто":
    st.title("➕ Реєстрація нового транспорту")
    st.write("Форма для внесення картки автомобіля.")
    
    # Створюємо тестові поля форми
    with st.form("test_car_form"):
        type_tech = st.selectbox("Оберіть тип техніки:", ["Тягач", "Причіп", "Легкове авто", "Автобус"])
        vin_code = st.text_input("VIN-код:")
        brand = st.text_input("Марка та модель (напр. DAF XF):")
        plate = st.text_input("Державний номер (SPZ):")
        km_start = st.number_input("Поточний пробіг (км):", min_value=0, value=0)
        
        submitted = st.form_submit_button("Зберегти автомобіль в систему", type="primary")
        if submitted:
            st.success(f"Тест: [{type_tech}] {brand} успішно пройшов валідацію форми!")

# --- ЕКРАН 3: СКЛАД ДЕТАЛЕЙ ---
elif menu == "📦 Склад деталей":
    st.title("📦 Склад запасних частин")
    st.write("Управління залишками на складі деталей.")
    
    with st.form("test_stock_form"):
        part_id = st.text_input("Артикул / OE Номер:")
        part_name = st.text_input("Назва деталі (напр. Фільтр масляний):")
        qty = st.number_input("Кількість (шт):", min_value=1, value=1)
        price = st.number_input("Ціна закупівлі (Kč):", min_value=0.0, value=0.0)
        
        stock_submitted = st.form_submit_button("Прийняти на склад", type="primary")
        if stock_submitted:
            st.success(f"Тест: Деталь {part_name} у кількості {qty} шт. готова до запису.")
