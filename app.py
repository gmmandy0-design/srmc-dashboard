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
