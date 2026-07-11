import os
import mysql.connector 
from mysql.connector import Error
import streamlit as st
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ai_chat_app"
        )
    except mysql.connector.Error as e:
        st.error(f"Error:{e}")
        return None
    