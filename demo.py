import streamlit as st
import time
from utils import get_current_timestamp
from ui import chat_display,settings,sidebar,display_analytics,welcome
from chatbot import stream_response,generate_chat_title, initialize_gemini_chat
from display import ai_message, user_message
import json
import os
from PIL import Image
import streamlit.components.v1 as components

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
def load_conversations():
    if os.path.exists("conversations.json"):
        with open("conversations.json","r") as f:
            data=json.load(f)
        conversations={}
        for title,convo in data.items():
            conversations[title]={"messages":convo["messages"],"chat":initialize_gemini_chat(st.session_state.generation_config,st.session_state.model)}
        conversations['Conversation 1'] = {
            "messages":[],
            "chat":initialize_gemini_chat(st.session_state.generation_config,st.session_state.model)
        }
        return conversations
    return {
        "Conversation 1":{
            "messages":[],
            "chat":initialize_gemini_chat(st.session_state.generation_config,st.session_state.model)
        }
    }
if "model" not in st.session_state:
    st.session_state.model="gemini-3.1-flash-lite"
if "generation_config" not in st.session_state:
    st.session_state.generation_config={
        "temperature":1.0,
        "max_output_tokens":2048,
        "top_p":0.95,
        "top_k":40
    }
if "conversations" not in st.session_state:
    st.session_state.conversations=load_conversations()
        
if "current_convo" not in st.session_state:
    st.session_state.current_convo = 'Conversation 1'
if "current_page" not in st.session_state:
    st.session_state.current_page="chat"
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt=None
def save_conversations():
    data={}
    for title,convo in st.session_state.conversations.items():
        data[title]={"messages":convo["messages"]}
    with open("conversations.json","w") as f:
        json.dump(data,f,indent=4) 
def on_change():
    st.session_state.model = st.session_state.model_widget
    st.session_state.conversations[st.session_state.current_convo]['chat'] = initialize_gemini_chat(st.session_state.generation_config, st.session_state.model)
def model():
    st.selectbox("Model",options=list(MODEL.keys()),index=list(MODEL.keys()).index(st.session_state.model), key='model_widget' ,format_func=lambda key:MODEL[key], on_change=on_change)
current=st.session_state.conversations[st.session_state.current_convo ]
messages=current["messages"]
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
                del st.session_state.conversations[st.session_state.current_convo]
                st.session_state.current_convo = 'New Chat'
                st.session_state.conversations['New Chat']={
                    "messages":[],
                    "chat": initialize_gemini_chat(st.session_state.generation_config, st.session_state.model)
                }
                save_conversations()
                st.rerun()
                #convos = list(st.session_state.conversations.keys())
                #st.session_state.current_page = 'new'
                #if convos:
                #    st.session_state.current_convo = convos[0]
                #     st.rerun()
                # else:
                #     st.session_state.current_convo = 'Conversation 1'
                #     st.session_state.conversations={
                #         "Conversation 1":{
                #             "messages":[],
                #             "chat": initialize_gemini_chat(st.session_state.generation_config, st.session_state.model)
                #         }
                #     }
                #     st.rerun()
page=st.session_state.current_page
chat_display.display(messages)
if page=="analytics":
    display_analytics.show(messages)
elif page=="settings":
    settings.settings()
else:
    chat_input=st.chat_input(placeholder="Ask me anything...",accept_file="multiple")
    prompt=None
    uploaded_files=[]
    if chat_input:
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
        save_conversations()
        if len(messages)==2:
            title=generate_chat_title(st.session_state.pending_prompt)
            old=st.session_state.current_convo
            st.session_state.conversations[title]=st.session_state.conversations.pop(old)
            st.session_state.current_convo=title
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
                            time.sleep(0.01)
                    placeholder.markdown(ai_message(text), unsafe_allow_html=True)
                    messages.append({"role":"assistant","message":text,"timestamps":get_current_timestamp()})
                    save_conversations()
                    st.session_state.pending_prompt=None
                    st.rerun()
            except Exception as e:
                st.error(f"Error:{e}")
    