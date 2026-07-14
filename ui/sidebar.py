import streamlit as st
from chatbot import initialize_gemini_chat
from database import get_db_connection
from mysql.connector import Error
import uuid
import json
from config import cookie_controller as controller
def new_chat():
    if st.button("+ New Chat",use_container_width=True):
        current=st.session_state.current_convo
        if len(st.session_state.conversations[current]["messages"])==0:
            st.session_state.current_page="chat"
            st.rerun()
        name="New Chat"
        st.session_state.conversations[name]={
            "db_id":str(uuid.uuid4()),
            "messages":[],
            "chat":initialize_gemini_chat(st.session_state.generation_config, st.session_state.model,st.session_state.web_search),
            "pinned":False
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
@st.dialog("Delete Conversation")
def delete_convo(convo_name):
    st.warning(f"Are you sure you want to delete this conversation{convo_name}? This action cannot be undone.")
    col1,col2 =st.columns(2)
    with col1:
        if st.button("Cancel",use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Yes,Delete",type='primary',use_container_width=True):
            if convo_name in st.session_state.conversations:
                convo_id=st.session_state.conversations[convo_name]["db_id"]
                del st.session_state.conversations[convo_name]
                conn=get_db_connection()
                if not conn: return
                try:
                    cursor=conn.cursor()
                    cursor.execute("DELETE FROM conversations WHERE id=%s",(convo_id,))
                    conn.commit()
                except Error as e:
                    st.error(f"Failed to delete chat:{e}")
                finally:
                    conn.close()
            st.session_state.current_convo = 'New Chat'
            if st.session_state.current_convo==convo_name:
                st.session_state.conversations['New Chat']={
                    "db_id":str(uuid.uuid4()),
                    "messages":[],
                    "chat": initialize_gemini_chat(st.session_state.generation_config, st.session_state.model,st.session_state.web_search),
                    "pinned":False
                }
            st.rerun()
def conversation_history(container_target):
    with container_target:
        st.subheader("Recent chats")
        st.text_input(
            "Search chats...", 
            key="chat_search", 
            placeholder="Search chats...", 
            label_visibility="collapsed"
        )
        all_convos = st.session_state.conversations
        filtered_convos=all_convos
        if st.session_state.chat_search and st.session_state.chat_search.strip():
            filtered_convos = {
                name: data for name, data in all_convos.items() 
                if st.session_state.chat_search.strip().lower() in name.lower()
            }
        pinned_chat=[]
        unpinned_chat=[]
        for name,data in filtered_convos.items():
            if data.get("pinned",False):
                pinned_chat.append(name)
            else:
                unpinned_chat.append(name)
        pinned_chat.reverse()
        unpinned_chat.reverse()
        sorted_chats=pinned_chat+unpinned_chat
        if not sorted_chats:
            st.info("No chats found.")
            return
        for name in sorted_chats:
            messages=st.session_state.conversations[name]["messages"]
            has_messages=len(messages)>0
            col_btn,col_menu=st.columns([8.5,1.5])
            with col_btn:
                is_active=(st.session_state.get("current_convo")==name)
                btn_type="primary" if is_active else "secondary"
                if st.button(name,icon=':material/keep:'if name in pinned_chat else None,use_container_width=True,type=btn_type,key=f"go_{name}"):
                    st.session_state.current_convo=name
                    st.session_state.current_page="chat"
                    st.rerun()
            if has_messages:
                with col_menu:
                    with st.popover("⋮",use_container_width=True):
                        pin_label="Unpin" if name in pinned_chat else "Pin"
                        if st.button(f"{pin_label} Chat",key=f"pin_{name}",use_container_width=True):
                            current_pin_state=st.session_state.conversations[name].get("pinned",False)
                            new_pin_state= not current_pin_state
                            st.session_state.conversations[name]["pinned"]=new_pin_state
                            try:
                                conn=get_db_connection()
                                if conn:
                                    cursor=conn.cursor()
                                    convo_id=st.session_state.conversations[name]["db_id"]
                                    cursor.execute("UPDATE conversations SET pinned=%s WHERE id=%s",(int(new_pin_state),convo_id,))
                                    conn.commit()
                                    conn.close()
                            except Error as e:
                                st.error(f"Failed to Pin:{e}")
                            st.rerun()
                        #-------export--------
                        with st.popover("Export Chat",use_container_width=True):
                            chat_messages=st.session_state.conversations[name].get("messages",[])
                            json_data=json.dumps({"messages":chat_messages},indent=4)
                            st.download_button("JSON",data=json_data,file_name=f"{name.replace(' ','_')}.json",mime="application/json",key=f"export_{name}",use_container_width=True)
                            #---text---
                            text_data=f"Chat:{name}"+"\n\n"
                            for m in messages:
                                role="User" if m['role']=="user" else "AI"
                                text_data+=f"\n{role}:{m['message']}\n"
                            st.download_button("TXT",data=text_data,file_name=f"{name.replace(' ','_')}.txt",mime="text/plain",key=f"export_txt_{name}",use_container_width=True)
                        if st.button("Delete Chat",key=f"delete_{name}",use_container_width=True):
                            delete_convo(name)
def sidebar(messages,current):
    with st.sidebar:
        st.header("AI Studio")
        new_chat()
        analytics()
        settings()
        scroll_container=st.container()
        sidebar_bottom=st.container(key='sidebar_bottom')
        conversation_history(scroll_container)
        st.markdown("""
            <style>
                [data-testid="stSidebarUserContent"] > div > div[data-testid="stVerticalBlock"] {
            position: relative;
        }
        .st-key-sidebar_bottom {
            position: fixed;
            bottom: 0;
            left: 0;
            width: inherit;
            max-width: 21rem;
            padding: 1rem 1.5rem 1.5rem 1.5rem;
            background-color: var(--secondary-background-color);
            z-index: 99;
            border-top: 1px solid rgba(49, 51, 63, 0.1);
        }
        [data-testid="stSidebarUserContent"] {
            padding-bottom: 90px !important;
        }
            </style>
        """, unsafe_allow_html=True)
        with sidebar_bottom:
            current_user=st.session_state.get("user_name","User")
            with st.popover(f"{current_user}",use_container_width=True):
                st.caption(f"Signed in as {current_user}")
                if st.button("Logout",key="logout_button",type="primary",use_container_width=True):
                    controller.remove("user_id")
                    st.session_state["logged_in"]=False
                    st.session_state["user_id"]=None
                    st.session_state["user_name"]=None
                    if "conversations" in st.session_state:
                        del st.session_state["conversations"]
                    if "current_convo" in st.session_state:
                        del st.session_state["current_convo"]
                    st.rerun()
