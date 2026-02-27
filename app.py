import streamlit as st
import re
import pytesseract
from PIL import Image

def get_unit_specs(model):
    model = model.upper().replace("-", "").replace(" ", "").strip()
    
    gas = "Check Nameplate"
    if any(x in model for x in ["Z", "410", "P"]): gas = "R-410A"
    elif any(x in model for x in ["G", "N", "22"]): gas = "R-22"

    # BRISTOL Logic
    if model.startswith("H"):
        bristol_match = re.search(r'H.{2,3}(\d{2,3})', model)
        if bristol_match:
            val = int(bristol_match.group(1))
            if 12 <= val <= 300: return round((val * 1000) / 12000, 1), gas

    # COPELAND / DANFOSS Logic
    comp_match = re.search(r'[A-Z]{2,4}(\d{2,3})', model)
    if comp_match:
        val = int(comp_match.group(1))
        if 12 <= val <= 300: return round((val * 1000) / 12000, 1), gas

    # STANDARD UNIT Logic
    unit_match = re.search(r'(018|024|030|036|042|048|054|060|072|090|120|18|24|30|36|42|48|54|60|72|90|120)', model)
    if unit_match:
        code = int(unit_match.group(1))
        return round((code * 1000) / 12000, 1), gas
        
    return None, gas

# --- APP INTERFACE ---
st.set_page_config(page_title="Kuwait HVAC Pro", page_icon="❄️")
st.title("❄️ Kuwait HVAC Tech Tool")

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Lookup", "⚡ LRA", "🛠️ Pressure", "📸 Scanner"])

with tab1:
    st.header("Search by Model")
    user_input = st.text_input("Enter Compressor or Unit Model")
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
    phase = st.radio("Power System", ["3-Phase (380V)", "1-Phase (220V)"])
    if lra_val > 0:
        divisor = 11.5 if "3-Phase" in phase else 36
        tons_lra = round(lra_val / divisor, 1)
        st.metric("Calculated Tonnage", f"{tons_lra} TR")
        st.warning(f"Max Safe Amps (50°C Ambient): {round((lra_val/6)*1.2, 1)} A")

with tab3:
    st.header("Pressure Diagnostic")
    gas_type = st.selectbox("Select Refrigerant", ["R-410A", "R-22"])
    ambient_temp = st.slider("Outdoor Temp (°C)", 30, 55, 45)
    col_p1, col_p2 = st.columns(2)
    suction_p = col_p1.number_input("Suction (PSI)", min_value=0.0)
    discharge_p = col_p2.number_input("Discharge (PSI)", min_value=0.0)

    if suction_p > 0:
        target_low = 115 + (ambient_temp - 35) * 2 if gas_type == "R-410A" else 65 + (ambient_temp - 35) * 1.5
        st.subheader("Result:")
        if suction_p < (target_low - 15):
            st.error(f"🚩 LOW GAS: Suction should be near {round(target_low)} PSI at {ambient_temp}°C")
        elif suction_p > (target_low + 20) and discharge_p > 0 and discharge_p < 250:
            st.warning("🚩 WEAK COMPRESSOR: High suction / Low discharge.")
        else:
            st.success("✅ SYSTEM BALANCED: Pressures look normal for this temperature.")

with tab4:
    st.header("📸 Nameplate Scanner")
    st.write("Take a clear photo of the nameplate to scan for model numbers.")
    
    picture = st.camera_input("Take a photo")
    uploaded_file = st.file_uploader("Or upload from gallery", type=['jpg', 'jpeg', 'png'])

    if picture or uploaded_file:
        img_file = picture if picture else uploaded_file
        st.image(img_file)
        
        with st.spinner("Scanning for text..."):
            try:
                img = Image.open(img_file)
                # This is where the magic happens!
                extracted_text = pytesseract.image_to_string(img)
                
                st.write("**Scanned Text:**")
                st.code(extracted_text) # Shows the raw text it found
                
                # Check if the app can automatically find the tonnage in the scanned text
                tons, info = get_unit_specs(extracted_text)
                if tons:
                    st.success(f"🎉 Auto-Detected Capacity: {tons} Tons")
            except Exception as e:
                st.error("Scanner is still installing on the server. Please wait 2 minutes and refresh the app.")

st.divider()
st.caption("Developed for AC Technicians in Kuwait.by azeez kazema")
