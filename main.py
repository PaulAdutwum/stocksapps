"""This script is bulidng a streamlit app"""

import streamlit as st
from auth import init_auth_db, login_form
from stock_analysis import render_stock_analysis

# Initialize the authentication database
init_auth_db()

# Page config
st.set_page_config(
    page_title="Stock Market Analysis Platform",
    page_icon="📈",
    layout="wide"
)

# Load custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Main application flow
if login_form():
    render_stock_analysis()

    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()