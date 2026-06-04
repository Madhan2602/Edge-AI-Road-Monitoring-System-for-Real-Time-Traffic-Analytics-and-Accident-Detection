import streamlit as st
import auth

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'role' not in st.session_state:
        st.session_state['role'] = None

def render_login():
    st.markdown("""
        <style>
            .stTextInput>div>div>input {
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
            }
            .stButton>button {
                width: 100%;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
                background-color: #0056b3;
                color: white;
            }
            .stButton>button:hover {
                background-color: #004494;
            }
            .header-text {
                text-align: center;
                color: #333;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='header-text'>EAIRMS Portal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Secure Stakeholder Access</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Sign In")
            
            if submit_button:
                if username and password:
                    role = auth.authenticate_user(username, password)
                    if role:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.session_state['role'] = role
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
                else:
                    st.warning("Please enter both username and password.")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.rerun()

def render_sidebar_profile():
    st.sidebar.markdown(f"**User:** {st.session_state['username']}")
    st.sidebar.markdown(f"**Role:** `{st.session_state['role']}`")
    if st.sidebar.button("Log Out"):
        logout()

def require_auth():
    init_session_state()
    if not st.session_state['logged_in']:
        render_login()
        st.stop()  # Stop execution of the main script until logged in
    else:
        render_sidebar_profile()
