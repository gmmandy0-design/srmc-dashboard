import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import datetime
import io
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import folium
from folium.plugins import HeatMap

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

# ----------------------------------
# ✅ LIVE STATUS
# ----------------------------------
st.success(f"🟢 System Active | {datetime.datetime.now().strftime('%H:%M:%S')}")

# ----------------------------------
# ✅ DATA GENERATION
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
# ✅ CALCULATIONS
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
# ✅ KPI
# ----------------------------------
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Patients", int(df["Patients"].sum()))
col2.metric("Revenue ($)", int(df["Revenue"].sum()))
col3.metric("Top Channel", df["Type"].value_counts().idxmax())

# ----------------------------------
# ✅ LIVE FEED
# ----------------------------------
st.subheader("🔴 Live HotDoc Feed")
st.dataframe(df, use_container_width=True)

# ----------------------------------
# ✅ GROWTH CHART
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
# ✅ KPI TRACKING
# ----------------------------------
st.subheader("🎯 KPI Performance")

fig2 = plt.figure(figsize=(8, 4))
plt.plot(monthly.index, monthly.values, marker='o', label="Actual", color='#1f3c88')
plt.plot(monthly.index, monthly.values*1.1, marker='s', label="Target", color='#3cb371')
plt.legend()
plt.title("Actual vs Target")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig2, use_container_width=True)
plt.close(fig2)

# ----------------------------------
# ✅ GEO MAP
# ----------------------------------
st.subheader("📍 Catchment Heatmap")

coords = {
    'Mernda':(-37.5986,145.0957),
    'Doreen':(-37.606,145.134),
    'South Morang':(-37.652,145.089),
    'Whittlesea':(-37.512,145.115)
}

df["Region"] = np.random.choice(list(coords.keys()),len(df))

heat = [[coords[r][0], coords[r][1], w] for r, w in zip(df["Region"], df["Patients"])]

m = folium.Map(location=[-37.6,145.1], zoom_start=12)
HeatMap(heat).add_to(m)

# Display the map
map_html = m._repr_html_()
components.html(map_html, height=400)

# ----------------------------------
# ✅ AI INSIGHTS
# ----------------------------------
st.subheader("🤖 AI Recommendations")

top = df["Type"].value_counts().idxmax()

if "Digital" in top:
    st.success("Scale digital campaigns for young families")
elif "Allied" in top:
    st.info("Expand dietitian services")
else:
    st.warning("Increase community engagement")

# ----------------------------------
# ✅ ALERTS
# ----------------------------------
if df["Workload"].value_counts().idxmax() == "High":
    st.error("⚠️ High workload detected")

# ----------------------------------
# ✅ COMPETITOR BENCHMARKING
# ----------------------------------
st.subheader("🏥 Market Benchmark")

competitors = pd.DataFrame({
    "Clinic":["SRMC","Doreen","South Morang","Whittlesea"],
    "Patients":[df["Patients"].sum(),
                np.random.randint(150,300),
                np.random.randint(180,350),
                np.random.randint(120,250)]
})

# Market share
total = competitors["Patients"].sum()
competitors["Share"] = (competitors["Patients"] / total * 100).round(1)

# Pie chart
fig3 = plt.figure(figsize=(6, 5))
colors = ['#1f3c88', '#3cb371', '#ff9999', '#ffcc99']
plt.pie(competitors["Share"], labels=competitors["Clinic"], autopct='%1.1f%%', colors=colors)
plt.title("Market Share")
st.pyplot(fig3, use_container_width=True)
plt.close(fig3)

# Bar chart
fig4 = plt.figure(figsize=(8, 4))
plt.bar(competitors["Clinic"], competitors["Patients"], color='#1f3c88')
plt.title("Patient Comparison")
plt.ylabel("Patient Count")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig4, use_container_width=True)
plt.close(fig4)

# ----------------------------------
# ✅ POSITION
# ----------------------------------
rank = competitors["Patients"].rank(ascending=False).iloc[0]

if rank == 1:
    st.success("✅ Market Leader")
elif rank == 2:
    st.warning("⚠️ Competitive Position")
else:
    st.error("🚨 Growth Opportunity")

# ----------------------------------
# ✅ PDF EXPORT
# ----------------------------------
def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    c.drawString(50,750,"SRMC Report")
    c.drawString(50,700,f"Patients: {int(df['Patients'].sum())}")
    c.drawString(50,680,f"Revenue: ${int(df['Revenue'].sum())}")

    c.save()
    buffer.seek(0)
    return buffer

if st.session_state.role == "Owner":
    st.subheader("📄 Export Report")
    pdf_buffer = generate_pdf()
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name="SRMC_Report.pdf",
        mime="application/pdf"
    )
