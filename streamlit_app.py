import streamlit as st
import pandas as pd
import json

# --- СТИЛІЗАЦІЯ ---
def apply_custom_css():
    st.markdown("""
        <style>
        .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
        .stDataFrame { border: 1px solid #ddd; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

# ... (ваш код завантаження даних) ...

if menu == "📋 SEZNAM VOZIDEL":
    st.title("📋 Přehled vozového parku")
    
    # 1. Інформативні метрики (виглядає як професійний дашборд)
    c1, c2, c3 = st.columns(3)
    c1.metric("Celkem vozidel", len(db["cars"]))
    c2.metric("V servisu", sum(1 for c in db["cars"] if c.get("status") == "Servis"))
    c3.metric("Najeto celkem", "124 500 km") 
    
    st.markdown("---")
    
    # 2. Краща таблиця
    if db["cars"]:
        df = pd.DataFrame(db["cars"])
        # Вибираємо тільки потрібні колонки для відображення
        display_df = df[["brand_model", "reg_number", "mileage"]]
        
        # Перейменовуємо для краси
        display_df.columns = ["Model", "SPZ", "Najeto (km)"]
        
        st.dataframe(
            display_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Najeto (km)": st.column_config.NumberColumn(format="%d km")
            }
        )

# 3. Використання Expander для чистоти інтерфейсу
with st.expander("ℹ️ Jak pracovat s daty"):
    st.write("Vyberte vozidlo z tabulky kliknutím na řádek. Po výběru se níže zobrazí detailní karta s historií oprav.")
