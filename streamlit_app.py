# --- PŘIDAT VOZIDLO (dokončení) ---
elif menu == "➕ PŘIDAT VOZIDLO":
    st.markdown("# ➕ Registrace nového vozidla")
    st.divider()
    
    with st.form("add_car_form"):
        col1, col2 = st.columns(2)
        with col1:
            car_vin = st.text_input("VIN kód (unikátní identifikátor)").strip().upper()
            car_brand_model = st.text_input("Značka a model")
        with col2:
            car_reg = st.text_input("Registrační značka (SPZ)").upper()
            car_mileage = st.text_input("Aktuální stav tachometru (km)", value="0")
            
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            car_stk = st.date_input("Platnost STK")
        with col_date2:
            car_ins = st.date_input("Platnost pojištění")
            
        submitted = st.form_submit_button("Uložit vozidlo do databáze", type="primary")
        
        if submitted:
            if not car_vin:
                st.error("VIN kód je povinný!")
            elif car_vin in db["cars"]:
                st.error("Vozidlo s tímto VIN již v databázi existuje.")
            else:
                db["cars"][car_vin] = {
                    "brand_model": car_brand_model,
                    "reg_number": car_reg,
                    "mileage": car_mileage,
                    "stk_date": str(car_stk),
                    "insurance_date": str(car_ins)
                }
                save_data(db)
                st.success(f"Vozidlo {car_brand_model} bylo úspěšně přidáno!")
                st.balloons()

# --- CELKOVÝ DENÍK SERVISU ---
elif menu == "📊 CELKOVÝ DENÍK SERVISU":
    st.markdown("# 📊 Celkový přehled servisních záznamů")
    if not db["repairs"]:
        st.info("Zatím nebyly zapsány žádné servisní úkony.")
    else:
        # Převedení na DataFrame pro přehlednou tabulku
        all_repairs = []
        for r in db["repairs"]:
            # Najdeme název vozidla podle VIN
            car_name = db["cars"].get(r["vin"], {}).get("brand_model", "Neznámé")
            all_repairs.append({
                "Datum": r["date"],
                "Vozidlo": car_name,
                "Popis": r["description"],
                "Díly": r["part_codes"],
                "Cena (Kč)": r["cost"]
            })
        import pandas as pd
        df = pd.DataFrame(all_repairs)
        st.dataframe(df, use_container_width=True)
        
