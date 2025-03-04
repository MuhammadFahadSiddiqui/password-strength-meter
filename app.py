import re
import random
import string
import time
import json
import streamlit as st

def generate_strong_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(12))

def check_password_strength(password):
    score = 0
    feedback = []
    
    # Length Check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("❌ Password should be at least 8 characters long.")
    
    # Upper & Lowercase Check
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("❌ Include both uppercase and lowercase letters.")
    
    # Digit Check
    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("❌ Add at least one number (0-9).")
    
    # Special Character Check
    if re.search(r"[!@#$%^&*]", password):
        score += 1
    else:
        feedback.append("❌ Include at least one special character (!@#$%^&*).")
    
    # Strength Rating
    if score == 4:
        return "✅ Strong Password!", feedback, "green", score
    elif score == 3:
        return "⚠️ Moderate Password - Consider adding more security features.", feedback, "orange", score
    else:
        feedback.append("🔹 Suggested Strong Password: " + generate_strong_password())
        return "❌ Weak Password - Improve it using the suggestions above.", feedback, "red", score

def check_username(username):
    if re.fullmatch(r"^[a-z0-9_.-]{5,15}$", username):
        return True, "✅ Valid Username!"
    else:
        return False, "❌ Username must be 5-15 characters long and contain only lowercase letters, numbers, '_', '-', and '.'" 

def load_users():
    try:
        with open("users.json", "r") as file:
            data = file.read()
            return json.loads(data) if data.strip() else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

users = load_users()

# Streamlit UI
st.title("🔐 Secure Login System with Advanced Features")

if "page" not in st.session_state:
    st.session_state.page = "home"
    st.session_state.current_user = None

def home_page():
    st.subheader("🏠 Welcome! Please choose an option:")
    if st.button("Login"):
        st.session_state.page = "login"
        st.rerun()
    if st.button("Register"):
        st.session_state.page = "register"
        st.rerun()

def login_page():
    st.subheader("🔑 Login Page")
    login_username = st.text_input("Enter Username:")
    login_password = st.text_input("Enter Password:", type="password")
    if st.button("Login"):
        if login_username in users and users[login_username] == login_password:
            st.success("✅ Login Successful! Redirecting...")
            st.session_state.current_user = login_username
            time.sleep(2)
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("❌ Invalid Username or Password!")
    if st.button("Register Instead"):
        st.session_state.page = "register"
        st.rerun()

def register_page():
    st.subheader("📝 Register Page")
    username = st.text_input("Enter Username:")
    username_valid, username_feedback = check_username(username)
    st.markdown(f'<p style="color:green" if username_valid else "color:red"; font-size:18px; font-weight:bold;">{username_feedback}</p>', unsafe_allow_html=True)
    
    password = st.text_input("Enter Password:", type="password")
    strength, feedback, color, score = check_password_strength(password)
    st.markdown(f'<p style="color:{color}; font-size:18px; font-weight:bold;">{strength}</p>', unsafe_allow_html=True)
    for msg in feedback:
        st.write(msg)
    
    if st.button("Register"):
        if username in users:
            st.error("❌ Username already exists! Choose a different one.")
        elif username_valid and score >= 3:
            users[username] = password
            save_users(users)
            st.success("✅ Registration Successful! Redirecting to Login Page...")
            time.sleep(2)
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("❌ Invalid Username or Weak Password!")
    if st.button("Already Registered? Login Here"):
        st.session_state.page = "login"
        st.rerun()

def dashboard_page():
    st.subheader("⚙️ User Dashboard")
    st.write(f"Welcome, **{st.session_state.current_user}**! You can change your username or password below.")
    
    new_username = st.text_input("Change Username (Optional):")
    new_password = st.text_input("Change Password (Optional):", type="password")
    repeat_password = st.text_input("Repeat New Password:", type="password")
    
    if st.button("Update Credentials"):
        current_user = st.session_state.current_user
        updated = False
        
        if new_username and new_username != current_user:
            username_valid, _ = check_username(new_username)
            if new_username in users:
                st.error("❌ Username already taken! Choose a different one.")
            elif not username_valid:
                st.error("❌ Invalid Username Format!")
            else:
                users[new_username] = users.pop(current_user)
                st.session_state.current_user = new_username
                updated = True
        
        if new_password:
            if new_password != repeat_password:
                st.error("❌ Passwords do not match!")
            else:
                strength, _, _, score = check_password_strength(new_password)
                if score < 3:
                    st.error("❌ Weak Password! Please improve it.")
                else:
                    users[st.session_state.current_user] = new_password
                    updated = True
        
        if updated:
            save_users(users)
            st.success("✅ Credentials Updated Successfully!")
            time.sleep(2)
            st.rerun()
    
    if st.button("Logout"):
        st.session_state.page = "home"
        st.session_state.current_user = None
        st.rerun()

if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "dashboard":
    dashboard_page()