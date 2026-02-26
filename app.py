with tab3:
    st.header("⚡ Troubleshooting & Gas Charge")
    gas_type = st.selectbox("Select Gas", ["R-410A", "R-22"])
    ambient_temp = st.slider("Outdoor Temp (°C)", 30, 55, 45)
    
    col_p1, col_p2 = st.columns(2)
    suction_p = col_p1.number_input("Suction Pressure (PSI)", min_value=0.0)
    discharge_p = col_p2.number_input("Discharge Pressure (PSI)", min_value=0.0)

    if suction_p > 0:
        st.subheader("Diagnostic Result:")
        
        # Logic for R410A in Kuwait Heat
        if gas_type == "R-410A":
            target_low = 115 + (ambient_temp - 35) * 2
            target_high = 350 + (ambient_temp - 35) * 5
        # Logic for R22
        else:
            target_low = 65 + (ambient_temp - 35) * 1.5
            target_high = 250 + (ambient_temp - 35) * 4

        if suction_p < (target_low - 15):
            st.error(f"🚩 LOW GAS: Suction should be near {round(target_low)} PSI at {ambient_temp}°C")
        elif suction_p > (target_low + 20) and discharge_p < (target_high - 30):
            st.warning("🚩 WEAK COMPRESSOR: High suction and low discharge suggest internal valve leak.")
        else:
            st.success("✅ PRESSURES NORMAL: System appears to be balanced for this ambient temp.")
