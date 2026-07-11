import streamlit as st
import re 
import bcrypt
import uuid
import time
from database import get_db_connection

def hash_password(password:str)->str:
    return bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")
def verify_password(password:str,hash_password:str)->bool:
    return bcrypt.checkpw(password.encode('utf-8'),hash_password.encode('utf-8'))
def is_valid_email(email:str)->bool:
    pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern,email) is not None
def register_user_db(conn,full_name,email,password):
    if not conn:
        st.error("Database connection failed!")
        return
    try:
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE email_id=%s",(email,))
        if cursor.fetchone():
            st.error("An account with this email already exists.")
            return
        user_id=str(uuid.uuid4())
        hash_pw=hash_password(password)
        cursor.execute("INSERT INTO users (id,full_name,email_id,password_hash)VALUES (%s,%s,%s,%s)", (user_id,full_name,email,hash_pw))
        conn.commit()
        st.success("Account created successfully. You can now log in.")
        return
    except Exception as e:
        st.error(f"Database error:{e}")
        return
    finally:
        cursor.close()
def authenticate_user(conn,email,password):
    if not conn:
        st.error("Database connection failed!")
        return None
    try:
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT id,full_name,password_hash FROM users WHERE email_id=%s",(email,))
        user=cursor.fetchone()
        if user and verify_password(password,user['password_hash']):
            st.success("Login Successfully.")
            return {"id":user["id"],"full_name":user["full_name"]}
        else:
            st.error("Invalid email or password.")
            return None
    except Exception as e:
        st.error(f"Database error:{e}")
        return None
    finally:
        cursor.close()
def render_auth_page():
    st.title("Welcome To Gemini AI Chat")
    st.markdown("Please login or create an account to continue.")
    tab1,tab2=st.tabs(['Login','Register'])
    with tab1:
        st.subheader("Login to your account")
        with st.form("login Form",clear_on_submit=True):
            login_email=st.text_input("email")
            show_pwd=st.checkbox("Show Password",key="show_pwd_login")
            pwd_type="default" if show_pwd else "password"
            login_pwd=st.text_input("password",type=pwd_type)
            remember_me=st.checkbox("Remember Me")
            submit=st.form_submit_button("Login")
            if submit:
                if not login_email or not login_pwd :
                    st.warning("Please fill in both email and password.")
                else:
                    conn=get_db_connection()
                    user_data=authenticate_user(conn,login_email,login_pwd)
                    if conn: conn.close()
                    if user_data:
                        st.session_state["logged_in"]=True
                        st.session_state["user_id"]=user_data["id"]
                        st.session_state["user_name"]=user_data["full_name"]
                        time.sleep(1)
                        st.rerun()
    with tab2:
        st.subheader("Create a new account.")
        with st.form("Register Form"):
            reg_name=st.text_input("Full Name")
            reg_email=st.text_input("Email")
            show_pwd_reg=st.checkbox("Show Password",key="show_pwd_reg")
            reg_pwd_type="default" if show_pwd_reg else "password"
            reg_password=st.text_input("Password",type=reg_pwd_type)
            reg_confirm_pwd=st.text_input("Confirm Password",type=reg_pwd_type)
            submit_reg=st.form_submit_button("Create Account")
            if submit_reg:
                if not all ([reg_name,reg_email,reg_password,reg_confirm_pwd]):
                    st.warning("Please fill out all fields.")
                elif not is_valid_email(reg_email):
                    st.error("Please enter a valid email address.")
                elif len(reg_password)<6:
                    st.error("Password must be at least 6 characters long.")
                elif reg_password != reg_confirm_pwd:
                    st.error("Password do not match.")
                else:
                    conn=get_db_connection()
                    register_user_db(conn,reg_name,reg_email,reg_password)
                    if conn: conn.close()

