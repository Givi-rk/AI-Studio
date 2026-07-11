import streamlit as st
import time
from utils import get_current_timestamp
from ui import chat_display,settings,sidebar,display_analytics,welcome
from chatbot import stream_response,generate_chat_title, initialize_gemini_chat
from display import ai_message, user_message
import json
import os
from mysql.connector import Error
from PIL import Image
import streamlit.components.v1 as components
from database import get_db_connection
from auth import render_auth_page
import uuid

MODEL={
    "gemini-3.1-flash-lite":"Gemini 3.1 Flash Lite",
    "gemini-2.5-flash":"Gemini 2.5 Flash",
    "gemini-2-flash":"Gemini 2 Flash",
    "gemini-2-flash-lite":"Gemini 2 Flash Lite",
    "gemini-2.5-flash-lite":"Gemini 2.5 Flash Lite"
}

st.set_page_config(page_title="Gemini",layout="wide")
Upload_folder="uploads"
os.makedirs(Upload_folder,exist_ok=True)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if not st.session_state.get("logged_in",False):
    render_auth_page()
    st.stop()
User_id=st.session_state["user_id"]
def load_conversations():
    conn=get_db_connection()
    conversations={}
    if conn:
        try:
            cursor=conn.cursor(dictionary=True)
            cursor.execute("SELECT id,title FROM conversations WHERE user_id=%s ORDER BY updated_at ASC",(User_id,))
            convos=cursor.fetchall()
            for convo in convos:
                title=convo["title"]
                convo_id=convo["id"]
                cursor.execute("SELECT role,message,files,created_at FROM messages WHERE conversation_id=%s ORDER BY created_at ASC",(convo_id,))
                db_messages=cursor.fetchall()
                formatted_msg=[]
                for m in db_messages:
                    files_data=json.loads(m['files']) if m['files'] else []
                    formatted_msg.append({
                        "role":m["role"],
                        "messages":m["message"],
                        "files":files_data,
                        "timestamps":str(m["created_at"])
                    })
                conversations[title]={
                    "db_id":convo_id,
                    "messages":formatted_msg,
                    "chat":initialize_gemini_chat(st.session_state.generation_config,st.session_state.model,st.session_state.web_search)
                }
        except Error as e:
            st.error(f"Failed to load history:{e}")
        finally:
            conn.close()
    if not conversations:
        conversations["Conversation 1"]={
            "db_id":str(uuid.uuid4()),
            "message":[],
            "chat":initialize_gemini_chat(st.session_state.generation_config,st.session_state.model,st.session_state.web_search)
        }
    return conversations
if "model" not in st.session_state:
    st.session_state.model="gemini-3.1-flash-lite"
if "generation_config" not in st.session_state:
    st.session_state.generation_config={
        "temperature":1.0,
        "max_output_tokens":2048,
        "top_p":0.95,
        "top_k":40,
    }
if "web_search" not in st.session_state:
    st.session_state.web_search=False
if "conversations" not in st.session_state:
    st.session_state.conversations=load_conversations()
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "current_convo" not in st.session_state:
    st.session_state.current_convo = 'Conversation 1'
if "current_page" not in st.session_state:
    st.session_state.current_page="chat"
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt=None
def save_conversations(convo_title,role,message_text,files_list=None):
    conn=get_db_connection()
    if not conn: return
    current_convo=st.session_state.conversations[convo_title]
    convo_id=current_convo.get("db_id")
    files_json=json.dumps(files_list) if files_list else None
    try:
        cursor=conn.cursor()
        cursor.execute("SELECT id from conversations WHERE id=%s",(convo_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO conversations (id,user_id,title) VALUES (%s,%s,%s)",(convo_id,User_id,convo_title,))
        cursor.execute("INSERT INTO messages (id,conversation_id,role,message,files) VALUES (%s,%s,%s,%s,%s)",(str(uuid.uuid4()),convo_id,role,message_text,files_json,))
        cursor.execute("UPDATE conversations SET updated_at=CURRENT_TIMESTAMP WHERE id=%s",(convo_id,))
        conn.commit()
    except Error as e:
        st.error(f"Error:{e}")
    finally:
        conn.close()
def update_title(old_title,new_title):
    conn=get_db_connection()
    if not conn: return
    convo_id=st.session_state.conversations[new_title]["db_id"]
    try:
        cursor=conn.cursor()
        cursor.execute("UPDATE conversations SET title=%s WHERE id=%s",(new_title,convo_id,))
        conn.commit()
    except Error as e:
        st.error(f"Failed to update title:{e}")
    finally:
        conn.close()
def delete_convo(convo_title):
    conn=get_db_connection()
    if not conn: return
    convo_id=st.session_state.conversations[convo_title]["db_id"]
    try:
        cursor=conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id=%s",(convo_id,))
        conn.commit()
    except Error as e:
        st.error(f"Failed to delete chat:{e}")
    finally:
        conn.close()
def on_change():
    st.session_state.model = st.session_state.model_widget
    st.session_state.conversations[st.session_state.current_convo]['chat'] = initialize_gemini_chat(st.session_state.generation_config, st.session_state.model,st.session_state.web_search)
def model():
    st.selectbox("Model",options=list(MODEL.keys()),index=list(MODEL.keys()).index(st.session_state.model), key='model_widget' ,format_func=lambda key:MODEL[key], on_change=on_change)
current=st.session_state.conversations[st.session_state.current_convo ]
messages=current["message"]
chat=current["chat"]
sidebar.sidebar(messages,current)
col1,col2=st.columns([7,5])
with col1:
    st.markdown(f"""<div 
                style="display:flex;justify-content:flex-start;font-size:40px;font-weight:bold; margin-top: -40px;">{MODEL[st.session_state.model]}</div>
                """,unsafe_allow_html=True)
with col2:
    model()
st.divider()
if st.session_state.current_page=="chat" and len(messages)>=1:
    col3,col4=st.columns([7,4])
    with col4:
        c1,c2=st.columns(2)
        with c1:
            st.download_button("Export Chat",data=json.dumps({ 'messages': current['messages'] },indent=4),file_name="chat_history.json",mime="application/json",use_container_width=True)
        with c2:
            if st.button("Clear Chat",use_container_width=True):
                delete_convo(st.session_state.current_convo)
                del st.session_state.conversations[st.session_state.current_convo]
                st.session_state.current_convo = 'New Chat'
                st.session_state.conversations['New Chat']={
                    "db_id":str(uuid.uuid4()),
                    "messages":[],
                    "chat": initialize_gemini_chat(st.session_state.generation_config, st.session_state.model,st.session_state.web_search)
                }
                save_conversations()
                st.rerun()
page=st.session_state.current_page
if st.session_state.current_page=="chat":
    chat_display.display(messages)
if page=="analytics":
    display_analytics.show()
elif page=="settings":
    settings.settings()
else:
    _,__,c0=st.columns([5,5,2])
    with c0:
        st.toggle("🌐 Web Search",key="web_search", disabled=st.session_state.is_generating)
        if "last_web_search" not in st.session_state:
            st.session_state.last_web_search=st.session_state.web_search
        if st.session_state.last_web_search!=st.session_state.web_search:
            st.session_state.last_web_search=st.session_state.web_search
            st.session_state.conversations[st.session_state.current_convo]["chat"]=initialize_gemini_chat(st.session_state.generation_config,st.session_state.model,st.session_state.web_search)
            chat=st.session_state.conversations[st.session_state.current_convo]["chat"]
    chat_input=st.chat_input(placeholder="Ask me anything...",accept_file="multiple", disabled=st.session_state.is_generating)
    prompt=None
    uploaded_files=[]
    if chat_input:
        st.session_state.is_generating = True
        prompt=chat_input.text
        uploaded_files=chat_input.files
    if len(messages)==0:
        welcome.show()
    if prompt:
        st.markdown(user_message(prompt), unsafe_allow_html=True)
        st.session_state.pending_prompt=prompt
        saved_files=[]
        for file in uploaded_files:
            path=os.path.join(Upload_folder,file.name)
            with open(path,"wb")as f:
                f.write(file.getbuffer())
            if file.type.startswith("image/"):
                #image=Image.open(file)
                st.image(file)

            elif file.type.startswith("video/"):
                st.video(file)

            elif file.type == "application/pdf":
                st.write(f"📄 {file.name}")

            else:
                st.write(f"📎 {file.name}")

            saved_files.append({"path":path,"type":file.type})
            
        messages.append({"role":"user","message":prompt,"files":saved_files,"timestamps":get_current_timestamp()})
        save_conversations(st.session_state.current_convo,"user",prompt)
        if len(messages)<=2:
            title=generate_chat_title(st.session_state.pending_prompt)
            old=st.session_state.current_convo
            st.session_state.conversations[title]=st.session_state.conversations.pop(old)
            st.session_state.current_convo=title
            update_title(old,title)
            st.rerun()
    if st.session_state.pending_prompt:
        with st.spinner("Gemini Thinking"):
            placeholder=st.empty()
            text=""
            try:
                response=stream_response(chat,st.session_state.pending_prompt,uploaded_files)
                if response:
                    for chunk in response:
                        for ch in chunk.text:
                            text+=ch
                            placeholder.markdown(ai_message(text+"|"), unsafe_allow_html=True)
                            time.sleep(0.001)
                    placeholder.markdown(ai_message(text), unsafe_allow_html=True)
                    messages.append({"role":"assistant","message":text,"timestamps":get_current_timestamp()})
                    save_conversations(st.session_state.current_convo,"assistant",text)
                    st.session_state.is_generating = False
                    st.session_state.pending_prompt=None
                    st.rerun()
            except Exception as e:
                st.error(f"Error:{e}")
    