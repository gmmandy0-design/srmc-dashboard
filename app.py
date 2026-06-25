import streamlit as st
import pandas as pd
import numpy as np
import datetime
import io
from reportlab.pdfgen import canvas
from PIL import Image

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="SRMC Dashboard", layout="wide")

# -----------------------------
# BRANDING WITH LOGO
# -----------------------------
col1, col2 = st.columns([1, 4])

with col1:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=80)
    except:
        st.write("🏥")

with col2:
    st.title("Schotters Road Medical Centre")
    st.caption("We Listen. We Care.")

st.markdown("---")

# -----------------------------
# USER DATABASE
# -----------------------------
users_db = {
    "owner1": {"password": "admin123", "role": "Owner"},
    "manager1": {"password": "manager123", "role": "Manager"},
    "staff1": {"password": "staff123", "role": "Staff"}
}

# -----------------------------
# SESSION INIT
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
st.sidebar.title("🔐 Login")

if not st.session_state.logged_in:

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in users_db and users_db[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = users_db[username]["role"]
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

    st.stop()

# -----------------------------
# LOGOUT BUTTON
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.write(f"👤 {st.session_state.user} ({st.session_state.role})")

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.rerun()

# -----------------------------
# MOCK REAL-TIME DATA
# -----------------------------
def generate_data():
    now = datetime.datetime.now()

    return pd.DataFrame({
        "Date": [now - datetime.timedelta(minutes=i*5) for i in range(10)],
        "Type": np.random.choice(['Digital Ads', 'Community', 'Allied Health', 'B2B'], 10),
        "Workload": np.random.choice(['Low','Medium','High'], 10)
    })

df = generate_data()

# -----------------------------
# CALCULATIONS
# -----------------------------
conversion = {
    'Digital Ads': 0.08,
    'Community': 0.05,
    'Allied Health': 0.12,
    'B2B': 0.15
}

df["Estimated_Patients"] = df["Type"].map(conversion) * 100
df["Revenue"] = df["Estimated_Patients"] * 75

# -----------------------------
# DASHBOARD
# -----------------------------
st.subheader("🔴 Live HotDoc Booking Feed (Simulated)")
st.dataframe(df, use_container_width=True)

total_patients = int(df["Estimated_Patients"].sum())
revenue = int(df["Revenue"].sum())

col1, col2 = st.columns(2)

col1.metric("👨‍👩‍👧 Patients (Estimated)", total_patients)
col2.metric("💰 Revenue ($)", revenue)

# -----------------------------
# PDF GENERATION
# -----------------------------
def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    c.drawString(50, 750, "Schotters Road Medical Centre")
    c.drawString(50, 735, "Performance Report")

    c.drawString(50, 700, f"Estimated Patients: {total_patients}")
    c.drawString(50, 680, f"Estimated Revenue: ${revenue}")

    c.save()
    buffer.seek(0)

    return buffer

# -----------------------------
# ROLE-BASED ACCESS
# -----------------------------
if st.session_state.role == "Owner":

    st.subheader("📄 Executive Report")

    pdf = generate_pdf()

    if st.download_button(
        "⬇️ Download SRMC Report",
        data=pdf,
        file_name="SRMC_Report.pdf",
        mime="application/pdf"
    ):
        st.success("✅ Report downloaded")

else:
    st.info("📄 Report access restricted to Owner role")
