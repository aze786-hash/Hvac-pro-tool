import streamlit as st
import re

# --- FUNCTIONS ---
def get_unit_specs(model):
    model = model.upper().replace("-", "").strip()
    # Looking for capacity numbers in model strings
    match = re.search(r'(018|024|030|036|042|048|060|090|120|18|24|30|36|42|48|60|90|120)', model)
    
    gas = "Check Plate (R22/R410A)"
    if any(x in model for x in ["Z", "410", "P"]): gas = "R-410A"
    elif any(x in model for x in ["G", "N", "22"]): gas = "R-22"
    
    if match:
        code = int(match.group())
        btu = code * 1000 if code > 15 else code * 10000 
        return round(btu/12000, 1), gas
    return None, gas

# --- APP INTERFACE ---
st.set_page_config(page_title="Kuwait HVAC Pro", page_icon="❄️")
st.title("❄️ Kuwait HVAC Tech Tool")

# This creates the tabs correctly
tab1, tab2, tab3 = st.tabs(["🔍 Model Lookup", "⚡ LRA to Tons", "🛠️ Troubleshoot"])

with tab1:
    st.header("Search by Model")
    user_input = st.text_input("Enter Compressor or Unit Model", placeholder="e.g. ZR94, YCJ36, APMR-5020")
    if user_input:
        tons, info = get_unit_specs(user_input)
        if tons:
            st.success(f"Estimated Capacity: {tons} Tons")
            st.info(f"Probable Gas: {info}")
            st.metric("Running Amps (Normal)", f"{round(tons * 6, 1)} A")
        else:
            st.error("Model not recognized. Try entering the LRA instead.")

with tab2:
    st.header("Tonnage from LRA")
    lra_val = st.number_input("Enter LRA from Nameplate", min_value=0.0, step=1.0)
    phase = st.radio("Power System", ["3-Phase (380V/415V)", "1-Phase (220V)"])
    if lra_val > 0:
        # Field divisors for Kuwait climate
        divisor = 11.5 if "3-Phase" in phase else 36
        tons_lra = round(lra_val / divisor, 1)
        st.metric("Calculated Tonnage", f"{tons_lra} TR")
        st.warning(f"Max Safe Amps (50°C Ambient): {round((lra_val/6)*1.2, 1)} A")

with tab3:
    st.header("Pressure Diagnostic")
    st.write("Calculates normal pressures based on Kuwait outdoor temperature.")
    gas_type = st.selectbox("Select Refrigerant", ["R-410A", "R-22"])
    ambient_temp = st.slider("Outdoor Temp (°C)", 30, 55, 45)
    
    col_p1, col_p2 = st.columns(2)
    suction_p = col_p1.number_input("Suction (PSI)", min_value=0.0)
    discharge_p = col_p2.number_input("Discharge (PSI)", min_value=0.0)

    if suction_p > 0:
        if gas_type == "R-410A":
            target_low = 115 + (ambient_temp - 35) * 2
        else:
            target_low = 65 + (ambient_temp - 35) * 1.5
            
        st.subheader("Result:")
        if suction_p < (target_low - 15):
            st.error(f"🚩 LOW GAS: Suction should be near {round(target_low)} PSI at {ambient_temp}°C")
        elif suction_p > (target_low + 20) and discharge_p > 0 and discharge_p < 250:
            st.warning("🚩 WEAK COMPRESSOR: High suction / Low discharge.")
        else:
            st.success("✅ SYSTEM BALANCED: Pressures look normal for this temperature.")

st.divider()
st.caption("Developed for AC Technicians in Kuwait.")
