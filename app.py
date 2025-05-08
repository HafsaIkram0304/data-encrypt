import streamlit as st
import hashlib
import time
from cryptography.fernet import Fernet

# Set page config
st.set_page_config(page_title="Secure Data System", page_icon="🔒")

# Generate a Fernet key (this should be constant during app run)
if 'KEY' not in st.session_state:
    st.session_state.KEY = Fernet.generate_key()
    st.session_state.cipher = Fernet(st.session_state.KEY)

# In-memory data storage
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}  # {"encrypted_text": {"encrypted_text": "xyz", "passkey": "hashed"}}

if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0

# Function to hash passkey
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Function to encrypt data
def encrypt_data(text):
    return st.session_state.cipher.encrypt(text.encode()).decode()

# Function to decrypt data
def decrypt_data(encrypted_text):
    return st.session_state.cipher.decrypt(encrypted_text.encode()).decode()

# Streamlit UI
st.title("🔒 Secure Data Encryption System")

# Navigation
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.subheader("🏠 Welcome!")
    st.write("Use this app to **securely store and retrieve data** using unique passkeys.")

elif choice == "Store Data":
    st.subheader("📂 Store Data Securely")

    user_data = st.text_area("Enter Data:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Encrypt & Save"):
        if user_data and passkey:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(user_data)
            # Store using encrypted text as key
            st.session_state.stored_data[encrypted_text] = {"encrypted_text": encrypted_text, "passkey": hashed_passkey}
            st.success("✅ Data encrypted and stored successfully!")
            st.info(f"🔐 Save your Encrypted Text:\n\n{encrypted_text}")
        else:
            st.error("⚠️ Both fields are required!")

elif choice == "Retrieve Data":
    st.subheader("🔍 Retrieve Your Data")

    encrypted_text = st.text_area("Enter Encrypted Text:")
    passkey = st.text_input("Enter Passkey:", type="password")

    if st.button("Decrypt"):
        if encrypted_text and passkey:
            hashed_passkey = hash_passkey(passkey)

            entry = st.session_state.stored_data.get(encrypted_text)
            if entry and entry["passkey"] == hashed_passkey:
                # Correct passkey
                decrypted_text = decrypt_data(encrypted_text)
                st.success(f"✅ Decrypted Data: {decrypted_text}")
                st.session_state.failed_attempts = 0  # Reset on success
            else:
                st.session_state.failed_attempts += 1
                attempts_left = 3 - st.session_state.failed_attempts
                st.error(f"❌ Incorrect passkey! Attempts remaining: {attempts_left}")

                if st.session_state.failed_attempts >= 3:
                    st.warning("🔒 Too many failed attempts! Redirecting to Login Page...")
                    time.sleep(1)  # Short delay to show the message
                    st.session_state.failed_attempts = 3  # Lock it
                    st.rerun()
        else:
            st.error("⚠️ Both fields are required!")

elif choice == "Login":
    st.subheader("🔑 Reauthorization Required")

    login_pass = st.text_input("Enter Master Password:", type="password")

    if st.button("Login"):
        if login_pass == "admin123":  # Master Password
            st.session_state.failed_attempts = 0
            st.success("✅ Reauthorized successfully! Redirecting to Retrieve Data page...")
            time.sleep(1)  # Short delay for user to see success message
            st.rerun()
        else:
            st.error("❌ Incorrect password!")
