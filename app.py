import streamlit as st
import pandas as pd
import numpy as np
import datetime
import io
import os
import sqlite3
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import qrcode
import folium
from folium.plugins import HeatMap
from streamlit.components.v1 import html

# ----------------------------------
# ✅ DATABASE
# ----------------------------------
def init_db():
    conn = sqlite3.connect('srmc_bookings.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY,
                  patient_name TEXT,
                  email TEXT,
                  phone TEXT,
                  service TEXT,
                  date TEXT,
                  time TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn

conn = init_db()

# ----------------------------------
# ✅ PAGE
# ----------------------------------
st.set_page_config(page_title="SRMC Dashboard", layout="wide")

# ----------------------------------
# ✅ HEADER
# ----------------------------------
col1, col2 = st.columns([1, 4])

with col1:
    if os.path.exists("srmc_logo.png"):
        st.image("srmc_logo.png", width=120)
    else:
        st.write("🏥")

with col2:
    st.title("Schotters Road Medical Centre")
    st.caption("We Listen. We Care.")

st.markdown("---")

# ----------------------------------
# ✅ USERS
# ----------------------------------
users = {
    "owner1": {"password": "admin123", "role": "Owner"},
    "manager1": {"password": "manager123", "role": "Manager"},
    "staff1": {"password": "staff123", "role": "Staff"}
}

# ----------------------------------
# ✅ LOGIN
# ----------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.sidebar.title("Login")

if not st.session_state.logged_in:
    u = st.sidebar.text_input("Username")
    p = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if u in users and users[u]["password"] == p:
            st.session_state.logged_in = True
            st.session_state.role = users[u]["role"]
            st.session_state.user = u
            st.rerun()

    st.stop()

# ----------------------------------
# ✅ LOGOUT
# ----------------------------------
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

st.sidebar.write(f"{st.session_state.user} ({st.session_state.role})")

# ----------------------------------
# ✅ TABS
# ----------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Book", "Bookings", "Workload"])

# ----------------------------------
# ✅ TAB 1: DASHBOARD
# ----------------------------------
with tab1:
    st.success(f"System Active | {datetime.datetime.now().strftime('%H:%M:%S')}")

    df = pd.DataFrame({
        "Type": np.random.choice(["Digital", "Community", "Allied", "WorkCover"], 30),
        "Patients": np.random.randint(10, 50, 30)
    })

    st.subheader("📊 KPIs")

    col1, col2 = st.columns(2)
    col1.metric("Total Patients", int(df["Patients"].sum()))
    col2.metric("Top Channel", df["Type"].value_counts().idxmax())

    st.bar_chart(df.groupby("Type")["Patients"].sum())

    # KPI Chart
    st.subheader("📈 Patient Growth")
    fig, ax = plt.subplots()
    df.groupby("Type")["Patients"].sum().plot(kind="bar", ax=ax)
    st.pyplot(fig)

    # Heatmap
    st.subheader("📍 Catchment Heatmap")

    coords = [
        [-37.5986, 145.0957],
        [-37.606, 145.134],
        [-37.652, 145.089],
        [-37.512, 145.115]
    ]

    heat_data = [[lat, lon, np.random.randint(1, 10)] for lat, lon in coords]
    m = folium.Map(location=[-37.6, 145.1], zoom_start=11)
    HeatMap(heat_data).add_to(m)

    html(m._repr_html_(), height=400)

# ----------------------------------
# ✅ TAB 2: BOOKING
# ----------------------------------
with tab2:
    booking_url = "https://www.hotdoc.com.au/medical-centres/mernda-VIC-3754/schotters-road-medical-centre/doctors"

    st.subheader("📲 Quick Booking")

    qr = qrcode.make(booking_url)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    st.image(buf.getvalue())

    st.link_button("Book via HotDoc", booking_url)

    st.markdown("---")

    with st.form("booking_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")

        service = st.selectbox("Service", ["GP", "Dietitian", "Allied"])
        date = st.date_input("Date")
        time = st.time_input("Time")

        if st.form_submit_button("Submit"):
            if name:
                conn.execute(
                    "INSERT INTO bookings (patient_name,email,phone,service,date,time) VALUES (?,?,?,?,?,?)",
                    (name, email, phone, service, str(date), str(time))
                )
                conn.commit()
                st.success(f"✅ Booking saved for {name}")

# ----------------------------------
# ✅ TAB 3: BOOKINGS
# ----------------------------------
with tab3:
    if st.session_state.role != "Staff":
        df = pd.read_sql("SELECT * FROM bookings", conn)

        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No bookings yet")

# ----------------------------------
# ✅ TAB 4: WORKLOAD
# ----------------------------------
with tab4:
    df = pd.read_sql("SELECT service, COUNT(*) as count FROM bookings GROUP BY service", conn)

    if not df.empty:
        st.bar_chart(df.set_index("service"))

        total = df["count"].sum()

        if total in range(0, 5):
            st.success("✅ Low workload")
        elif total in range(5, 15):
            st.warning("⚠️ Medium workload")
        else:
            st.error("🔴 High workload")

    else:
        st.info("No workload data")

# ----------------------------------
# ✅ PDF EXPORT (IMPROVED)
# ----------------------------------
if st.session_state.role == "Owner":

    def generate_pdf():
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "SRMC Daily Report")

        today = datetime.date.today()
        c.setFont("Helvetica", 10)
        c.drawString(50, 730, f"Date: {today}")

        df = pd.read_sql("SELECT * FROM bookings", conn)

        total_bookings = len(df)

        c.setFont("Helvetica", 12)
        c.drawString(50, 700, f"Total Bookings: {total_bookings}")

        if not df.empty:
            top_service = df["service"].value_counts().idxmax()
            c.drawString(50, 680, f"Top Service: {top_service}")

        c.setFont("Helvetica-Oblique", 8)
        c.drawString(50, 650, "Generated by SRMC Dashboard")

        c.save()
        buffer.seek(0)
        return buffer

    st.subheader("📄 Export Report")

    st.download_button(
        label="Download SRMC Report",
        data=generate_pdf(),
        file_name=f"SRMC_Report_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )
