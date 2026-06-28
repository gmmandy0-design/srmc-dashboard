import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import datetime
import io
import os
import json
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import folium
from folium.plugins import HeatMap

# ----------------------------------
# ✅ DATABASE SETUP
# ----------------------------------
def init_db():
    conn = sqlite3.connect('srmc_bookings.db')
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

# ----------------------------------
# ✅ PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="SRMC Dashboard", layout="wide")

# ----------------------------------
# ✅ THEME
# ----------------------------------
st.markdown("""
<style>
.stApp {background-color: #f4f8fb;}
h1,h2,h3 {color:#1f3c88;}
.stButton>button {background:#1f3c88;color:white;}
.stDownloadButton>button {background:#3cb371;color:white;}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# ✅ HEADER + LOGO
# ----------------------------------
col1, col2 = st.columns([1,4])

with col1:
    if os.path.exists("srmc_logo.png"):
        st.image("srmc_logo.png", use_container_width=True)
    else:
        st.write("🏥")

with col2:
    st.title("Schotters Road Medical Centre")
    st.markdown("### _We Listen. We Care._")
    st.caption("Growth Intelligence Dashboard")

st.markdown("---")

# ----------------------------------
# ✅ USERS
# ----------------------------------
users_db = {
    "owner1": {"password": "admin123", "role": "Owner"},
    "manager1": {"password": "manager123", "role": "Manager"},
    "staff1": {"password": "staff123", "role": "Staff"}
}

# ----------------------------------
# ✅ SESSION INIT
# ----------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ----------------------------------
# ✅ LOGIN
# ----------------------------------
st.sidebar.title("🔐 Login")

if not st.session_state.logged_in:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if username in users_db and users_db[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = users_db[username]["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ----------------------------------
# ✅ LOGOUT
# ----------------------------------
st.sidebar.write(f"👤 {st.session_state.user} ({st.session_state.role})")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# Initialize database
conn = init_db()

# ----------------------------------
# ✅ NAVIGATION TABS
# ----------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📅 Book Appointment", "👥 Bookings", "📈 Workload"])

# ----------------------------------
#  TAB 1: DASHBOARD
# ----------------------------------
with tab1:
    st.success(f"🟢 System Active | {datetime.datetime.now().strftime('%H:%M:%S')}")

    # ----------------------------------
    #  DATA GENERATION
    # ----------------------------------
    def generate_data():
        now = datetime.datetime.now()
        return pd.DataFrame({
            "Date":[now - datetime.timedelta(minutes=i*5) for i in range(30)],
            "Type":np.random.choice([
                'Family Digital Campaigns',
                'Community Engagement',
                'Allied Health (Dietitian)',
                'WorkCover / TAC'
            ],30),
            "Workload":np.random.choice(['Low','Medium','High'],30)
        })

    df = generate_data()

    # ----------------------------------
    #  CALCULATIONS
    # ----------------------------------
    conversion = {
        'Family Digital Campaigns':0.08,
        'Community Engagement':0.05,
        'Allied Health (Dietitian)':0.12,
        'WorkCover / TAC':0.15
    }

    df["Patients"] = df["Type"].map(conversion)*100
    df["Revenue"] = df["Patients"]*75
    df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M").astype(str)

    monthly = df.groupby("Month")["Patients"].sum()

    # ----------------------------------
    #  KPI
    # ----------------------------------
    st.subheader("📊 Key Metrics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Patients", int(df["Patients"].sum()))
    col2.metric("Revenue ($)", int(df["Revenue"].sum()))
    col3.metric("Top Channel", df["Type"].value_counts().idxmax())

    # ----------------------------------
    #  LIVE FEED
    # ----------------------------------
    st.subheader("🔴 Live HotDoc Feed")
    st.dataframe(df, use_container_width=True)

    # ----------------------------------
    #  GROWTH CHART
    # ----------------------------------
    st.subheader("📈 Patient Growth")

    fig1 = plt.figure(figsize=(8, 4))
    monthly.plot(marker='o', color='#1f3c88')
    plt.title("Patient Growth Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig1, use_container_width=True)
    plt.close(fig1)

    # ----------------------------------
    #  COMPETITOR BENCHMARKING
    # ----------------------------------
    st.subheader("🏥 Market Benchmark")

    competitors = pd.DataFrame({
        "Clinic":["SRMC","Doreen","South Morang","Whittlesea"],
        "Patients":[df["Patients"].sum(),
                    np.random.randint(150,300),
                    np.random.randint(180,350),
                    np.random.randint(120,250)]
    })

    total = competitors["Patients"].sum()
    competitors["Share"] = (competitors["Patients"] / total * 100).round(1)

    fig3 = plt.figure(figsize=(6, 5))
    colors = ['#1f3c88', '#3cb371', '#ff9999', '#ffcc99']
    plt.pie(competitors["Share"], labels=competitors["Clinic"], autopct='%1.1f%%', colors=colors)
    plt.title("Market Share")
    st.pyplot(fig3, use_container_width=True)
    plt.close(fig3)

# ----------------------------------
# # ----------------------------------
#  TAB 2: BOOKING FORM (PUBLIC) 
# ----------------------------------
with tab2:

    import qrcode

    #  QR + HotDoc booking link
    booking_url = "https://www.hotdoc.com.au/medical-centres/mernda-VIC-3754/schotters-road-medical-centre/doctors"

    st.subheader("📲 Quick Booking")

    qr = qrcode.make(booking_url)
    st.image(qr, caption="Scan to book instantly")

    st.link_button("✅ Book via HotDoc (Live System)", booking_url)

    st.markdown("---")

    # ✅ Booking Form
    st.subheader("📅 Book Your Appointment")
    st.write("Or request an appointment below:")

    with st.form("booking_form"):

        patient_name = st.text_input("Full Name *")
        email = st.text_input("Email *")
        phone = st.text_input("Phone Number *")

        service = st.selectbox("Service *", [
            "General Consultation",
            "Dietitian",
            "WorkCover / TAC",
            "Allied Health"
        ])

        appointment_date = st.date_input("Preferred Date *")
        appointment_time = st.time_input("Preferred Time *")

        submitted = st.form_submit_button("🔒 Request Appointment")

        if submitted:
            if patient_name and email and phone:

                c = conn.cursor()
                c.execute('''
                    INSERT INTO bookings (patient_name, email, phone, service, date, time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (patient_name, email, phone, service,
                 str(appointment_date), str(appointment_time)))

                conn.commit()

                st.success("✅ Appointment request submitted!")
                st.balloons()

            else:
                st.error("❌ Please complete all required fields")

# ----------------------------------
# ✅ TAB 3: BOOKINGS (ADMIN ONLY)
# ----------------------------------
with tab3:
    if st.session_state.role in ["Owner", "Manager"]:
        st.subheader("👥 Upcoming Bookings")
        
        c = conn.cursor()
        c.execute('SELECT * FROM bookings ORDER BY date DESC')
        bookings = c.fetchall()
        
        if bookings:
            bookings_df = pd.DataFrame(bookings, columns=['ID', 'Patient Name', 'Email', 'Phone', 'Service', 'Date', 'Time', 'Booked At'])
            st.dataframe(bookings_df[['Patient Name', 'Email', 'Phone', 'Service', 'Date', 'Time']], use_container_width=True)
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Bookings", len(bookings_df))
            col2.metric("Today's Bookings", len(bookings_df[bookings_df['Date'] == str(datetime.date.today())]))
            col3.metric("Most Popular Service", bookings_df['Service'].value_counts().idxmax())
        else:
            st.info("📭 No bookings yet")
    else:
        st.error("❌ Access restricted to Manager/Owner role")

# ----------------------------------
# ✅ TAB 4: DAILY WORKLOAD
# ----------------------------------
with tab4:
    if st.session_state.role in ["Owner", "Manager", "Staff"]:
        st.subheader("📈 Daily Workload")
        
        # Get today's bookings
        today = str(datetime.date.today())
        c = conn.cursor()
        c.execute('SELECT service, COUNT(*) FROM bookings WHERE date = ? GROUP BY service', (today,))
        workload_data = c.fetchall()
        
        if workload_data:
            workload_df = pd.DataFrame(workload_data, columns=['Service', 'Bookings'])
            
            # Workload chart
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(workload_df['Service'], workload_df['Bookings'], color='#1f3c88')
            ax.set_title("Today's Workload by Service")
            ax.set_ylabel("Number of Bookings")
            ax.set_xlabel("Service")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            
            # Workload metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Today's Total", workload_df['Bookings'].sum())
            col2.metric("Busiest Service", workload_df.loc[workload_df['Bookings'].idxmax(), 'Service'])
            col3.metric("Capacity Used", f"{(workload_df['Bookings'].sum() / 20) * 100:.0f}%")
            
            # Workload status
            total = workload_df['Bookings'].sum()
            if total < 5:
                st.success("✅ Low workload - accepting more bookings")
            elif total < 15:
                st.warning("⚠️ Medium workload - normal operations")
            else:
                st.error("🔴 High workload - consider overbooking safeguards")
        else:
            st.info("📭 No bookings for today")

# ----------------------------------
# ✅ PDF EXPORT (OWNER ONLY)
# ----------------------------------
if st.session_state.role == "Owner":
    st.subheader("📄 Export Report")
    
    def generate_pdf():
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)

        c.drawString(50,750,"SRMC Report")
        c.drawString(50,700,f"Today: {datetime.date.today()}")
        
        # Get today's bookings count
        conn_temp = sqlite3.connect('srmc_bookings.db')
        c_temp = conn_temp.cursor()
        c_temp.execute('SELECT COUNT(*) FROM bookings WHERE date = ?', (str(datetime.date.today()),))
        today_bookings = c_temp.fetchone()[0]
        
        c.drawString(50,680,f"Today's Bookings: {today_bookings}")

        c.save()
        buffer.seek(0)
        return buffer

    pdf_buffer = generate_pdf()
    st.download_button(
        label="Download Daily Report",
        data=pdf_buffer,
        file_name=f"SRMC_Report_{datetime.date.today()}.pdf",
        mime="application/pdf"
    )

conn.close()
