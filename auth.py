""" This script is building a streamlit app """

import streamlit as st 
import hashlib
import sqlite3
import re

def init_auth_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def authenticate(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()

    if result and result[0] == hash_password(password):
        return True
    return False

def create_account(email, password):
    if not is_valid_email(email):
        return False, "Invalid email format"

    if len(password) < 6:
        return False, "Password must be at least 6 characters"

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)',
                 (email, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Account created successfully"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Email already exists"

def login_form():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("""
        <h2 style='text-align: center; color: #1E88E5;'>Stock Market Analysis Platform</h2>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "Create Account"])

        with tab1:
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login"):
                if authenticate(login_email, login_password):
                    st.session_state.authenticated = True
                    st.session_state.email = login_email
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with tab2:
            new_email = st.text_input("Email", key="new_email")
            new_password = st.text_input("Password", type="password", key="new_password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Create Account"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = create_account(new_email, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    return st.session_state.authenticated