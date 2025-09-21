import streamlit as st
import google.generativeai as genai
import requests
from streamlit_lottie import st_lottie
import os
import pandas as pd
from typing import List, Dict

# --- CONFIGURATION & SETUP ---

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# --- APP LAYOUT & AUTHENTICATION ---
st.set_page_config(page_title="CareerEdge", layout="wide")

if os.path.exists("assets/styles.css"):
    load_css("assets/styles.css")

# Initialize session state for authentication and user data
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'users' not in st.session_state:
    st.session_state['users'] = {"test@example.com": {"password": "password123", "profile": {}}}
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'

# Add the new header content
logo_col, title_col = st.columns([1, 6])
with logo_col:
    # Changed to use use_container_width for a more responsive layout
    st.image("Logo.png", use_container_width=False, width=80)
with title_col:
    st.markdown('<h1 class="app-title">CareerEdge</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Your personalized career assistant</p>', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="fixed-header">
        <div class="profile-icon-container">
            <span class="profile-name">{st.session_state.get('username', 'Guest').split('@')[0].capitalize()}</span>
            <img src="https://i.pravatar.cc/40?u={st.session_state.get('username', 'Guest')}" class="profile-icon" alt="Profile Icon">
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if not st.session_state['authenticated']:
    st.markdown('<h2 class="section-title">Login or Create an Account</h2>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_login, col_social = st.columns([1, 2])
        with col_login:
            if st.button("Login", use_container_width=True):
                if email in st.session_state['users'] and st.session_state['users'][email]['password'] == password:
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = email
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        with col_social:
            st.markdown('<div class="social-login-buttons">', unsafe_allow_html=True)
            st.markdown('<p>or sign in with</p>', unsafe_allow_html=True)
            google_icon, github_icon, linkedin_icon = st.columns([1, 1, 1])
            with google_icon:
                st.markdown('<a href="#"><img src="https://img.icons8.com/color/48/000000/google-logo.png" alt="Google"></a>', unsafe_allow_html=True)
            with github_icon:
                st.markdown('<a href="#"><img src="https://img.icons8.com/ios-filled/48/000000/github.png" alt="GitHub"></a>', unsafe_allow_html=True)
            with linkedin_icon:
                st.markdown('<a href="#"><img src="https://img.icons8.com/color/48/000000/linkedin.png" alt="LinkedIn"></a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        new_email = st.text_input("New Email", key="signup_email")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        if st.button("Signup", use_container_width=True):
            if new_email in st.session_state['users']:
                st.error("User already exists")
            else:
                st.session_state['users'][new_email] = {"password": new_password, "profile": {}}
                st.session_state['authenticated'] = True
                st.session_state['username'] = new_email
                st.success("Signup successful! Please fill out your profile details.")
                st.rerun()

else:
    st.sidebar.title("Navigation")
    st.sidebar.markdown('<p>Use the links below to navigate:</p>', unsafe_allow_html=True)
    
    st.sidebar.page_link("pages/Profile_Form.py", label="Your Profile")
    st.sidebar.page_link("pages/Results.py", label="Your Results")
    
    if st.sidebar.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['username'] = 'Guest'
        st.rerun()

    st.markdown('<h2 class="section-title">Welcome, ' + st.session_state['username'].split('@')[0].capitalize() + '!</h2>', unsafe_allow_html=True)
    st.info("Use the navigation on the sidebar to get started. Fill out your profile first!")

    st.sidebar.markdown("---")
    st.sidebar.title("Extras (demos)")
    st.sidebar.markdown('<div class="sidebar-info-card"><h4>Market Insights</h4><p>DUMMY</p></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-info-card"><h4>Multilingual Support</h4><p>DUMMY</p></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-info-card"><h4>Continuous Updates</h4><p>DUMMY</p></div>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown('<p class="sidebar-footer">© 2025 CareerEdge. All Rights Reserved.</p>', unsafe_allow_html=True)