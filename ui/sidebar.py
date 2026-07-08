import streamlit as st
import chatbot
def new_chat():
    if st.button("+ New Chat",use_container_width=True):
        number=len(st.session_state.conversations)+1
        name=f"Conversation {number}"
        st.session_state.conversations[name]={
            "messages":[],
            "chat":chatbot.initialize_gemini_chat(st.session_state.generation_config, st.session_state.model)
        }
        st.session_state.current_convo=name
        st.session_state.current_page="chat"
        st.rerun()
def analytics():
    if st.button("Analytics",use_container_width=True):
        st.session_state.current_page="analytics"
        st.rerun()
def settings():
    if st.button("Settings",use_container_width=True):
        st.session_state.current_page="settings"
        st.rerun()
def conversation_history():
    st.subheader("Recent chats")
    for name in st.session_state.conversations.keys():
        if st.button(name,use_container_width=True,key=name):
            st.session_state.current_convo=name
            st.session_state.current_page="chat"
            st.rerun()
def sidebar(messages,current):
    with st.sidebar:
        st.header("AI Studio")
        new_chat()
        analytics()
        settings()
        conversation_history()