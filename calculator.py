import streamlit as st
import pandas as pd
import math

# --- HML CALCULATION LOGIC ---
def calculate_hml_attenuation(laeq, lcmax, h, m, l):
    b = lcmax - laeq
    if b <= 2:
        att = m - ((h - m) / 4) * (b - 2)
    else:
        att = m - ((m - l) / 8) * (b - 2)
    return round(laeq - att, 1)

def calculate_dose(laeq_at_ear, duration_hrs=7.75):
    # Standard 85dB limit for 8 hours
    dose = (duration_hrs / 8) * 10**((laeq_at_ear - 85) / 10) * 100
    return round(dose, 2)

# --- APP INTERFACE ---
st.set_page_config(page_title="HML Sound Logger", layout="wide")

st.title("🎧 Sound Exposure Tool (HML Method)")

# 1. PROTECTOR LIBRARY
st.sidebar.header("🛡️ Protector Library")
if 'protectors' not in st.session_state:
    st.session_state.protectors = {
        "Generic Plug": {"H": 25, "M": 22, "L": 20},
        "High Attenuation Muff": {"H": 32, "M": 28, "L": 22}
    }

with st.sidebar.expander("Add New Protector"):
    new_name = st.text_input("Protector Name")
    col1, col2, col3 = st.columns(3)
    nh = col1.number_input("H", value=0)
    nm = col2.number_input("M", value=0)
    nl = col3.number_input("L", value=0)
    if st.button("Save to Library"):
        st.session_state.protectors[new_name] = {"H": nh, "M": nm, "L": nl}

selected_protector = st.sidebar.selectbox("Select Protector for this Log", list(st.session_state.protectors.keys()))
p_vals = st.session_state.protectors[selected_protector]

# 2. SESSION METADATA
st.header("Step 1: Session Details")
m_col1, m_col2, m_col3, m_col4,m_col5,m_col6,m_col7,m_col8 = st.columns(8)
wk = m_col1.text_input("Wk", "3")
date = m_col2.text_input("Date", "3/23/2026")
proj = m_col3.text_input("Project", "Cybec Reh")
place = m_col4.text_input("Place", "Iwaki")
lognum = m_col5.text_input("Logger No.")
pos = m_col6.text_input("Instrument / Position")
timeStart = m_col7.text_input("Start Time")
timeEnd = m_col8.text_input("End Time")

# 3. FILE UPLOAD & PROCESSING
st.header("Step 2: Upload Logger Data")
uploaded_file = st.file_uploader("Upload 'logger data example.csv'", type=["csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    
    processed_rows = []
    for _, row in df_raw.iterrows():
        laeq = row['Laeq']
        lcmax = row['Lcmax']
        
        # Perform HML math
        effective_laeq = calculate_hml_attenuation(laeq, lcmax, p_vals['H'], p_vals['M'], p_vals['L'])
        dose = calculate_dose(effective_laeq)
        
        processed_rows.append({
            "Wk": wk,
            "Date": date,
            "Project": proj,
            "Place": place,
            "Logger": lognum,
            "Instrument / Position": pos, 
            "Start Time": timeStart,
            "End Time": timeEnd,
            "LAeq db": effective_laeq,
            "%age Dose": dose,
            "LC Max": lcmax,
            "Notes": f"Protector: {selected_protector}"
        })
    
    output_df = pd.DataFrame(processed_rows)
    
    st.subheader("Calculated Output")
    st.dataframe(output_df)
    
    # 4. EXPORT
    csv_data = output_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Formatted Log", csv_data, "sound_tech_log.csv", "text/csv")