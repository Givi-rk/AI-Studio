import streamlit as st
import chatbot
import utils
import json
import time
import Analytics
import streamlit.components.v1 as components
from display import user_message,ai_message
st.set_page_config(
    page_title="Gemini AI Chatbot",
    layout="wide"
)
if "generation_config" not in st.session_state:
    st.session_state.generation_config={
        "temperature":1.0,
        "max_output_tokens":2048,
        "top_p":0.95,
        "top_k":40
    }
if "conversations" not in st.session_state:
    st.session_state.conversations={
        "Conversation 1":{
            "messages":[],
            "chat":chatbot.initialize_gemini_chat(st.session_state.generation_config, st.session_state.model)
        }
    }
if "current_conversation" not in st.session_state:
    st.session_state.current_conversation="Conversation 1"
current=st.session_state.conversations[st.session_state.current_conversation]
messages=current["messages"]
chat=current["chat"]
#====================sidebar===================
with st.sidebar:
    st.header("AI Studio")

    if st.button("+ New Chat",use_container_width=True):
        conversation_num=len(st.session_state.conversations)+1
        name=f"Conversation {conversation_num}"
        st.session_state.conversations[name]={
            "messages":[],
            "chat":chatbot.initialize_gemini_chat(st.session_state.generation_config, st.session_state.model)
        }
        st.session_state.current_conversation=name
        st.rerun()
    # --------download-----------
    st.download_button("Export Chat",data=json.dumps(messages,indent=4),file_name="chat_history.json",mime="application/json",use_container_width=True)
    selected_convo=st.selectbox("History",options=list(st.session_state.conversations.keys()),index=list(st.session_state.conversations.keys()).index(st.session_state.current_conversation))
    if selected_convo != st.session_state.current_conversation:
        st.session_state.current_conversation=selected_convo
        st.rerun() 
    #-----------analytics-----------
    if st.button("Analytics",use_container_width=True):
        st.session_state.show_analytics=True
    if "show_analytics" not in st.session_state:
        st.session_state.show_analytics=False
    #-----------config----------
    temperature=st.slider("Temperature",0.0,2.0,st.session_state.generation_config["temperature"],0.1)
    max_tokens=st.slider("Max Output Tokens",1,8192,st.session_state.generation_config["max_output_tokens"],50)
    top_p=st.slider("Top-P",0.0,1.0,st.session_state.generation_config["top_p"],0.5)
    top_k=st.slider("Top-K",1,100,st.session_state.generation_config["top_k"],1)
    st.caption("Applying new settings start a new AI session.YOur chat history will remain visible.")
    if st.button("Apply Settings",use_container_width=True):
        st.session_state.generation_config={
            "temperature":temperature,
            "max_output_tokens":max_tokens,
            "top_p":top_p,
            "top_k":top_k
        }
        current["chat"]=chatbot.initialize_gemini_chat(st.session_state.generation_config, st.session_stae.model)
    st.divider()
#==================================================================================================
st.title("Gemini 3.1 Flash Lite")
st.divider()
if st.session_state.show_analytics:
    stats=Analytics.get_statistics(messages)
    st.subheader("Conversation Statistics")
    col1,col2=st.columns(2)
    with col1:
        st.metric("Total Messages",stats["total_messages"])
        st.metric("User Messages",stats["user_messages"])
        st.metric("Total Words",stats["total_words"])
    with col2:
        st.metric("AI Messages",stats["ai_messages"])
        st.metric("Duration",stats["duration"])
if len(messages)==0 and not st.session_state.show_analytics:
    st.markdown("<div style='text-align:center;font-size:35px;font-weight:bold'> Welcome to AI Chat Assistant</div>", unsafe_allow_html=True)
    st.write("<div style='text-align:center;font-size:19px;margin-bottom:30px'>Ask anything and receive intelligentb response powered by Gemini.<br>Explore possibilities from complex coding to creative writing.</div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("<div style='font-size:21px;font-weight:bold'>Explain Python decorators</div>",unsafe_allow_html=True)
            st.write("Deep dive into functional programming concepts and syntax")
        with st.container(border=True):
            st.markdown("<div style='font-size:21px;font-weight:bold'> Summarize an article</div>",unsafe_allow_html=True)
            st.write("Extract key insights and bullet points from any long-form text.")
    with c2:
        with st.container(border=True):
            st.markdown("<div style='font-size:21px;font-weight:bold'>Optimize an SQL query</div>",unsafe_allow_html=True)
            st.write("Improve performance of complex joins and nested subqueries")
        with st.container(border=True):
            st.markdown("<div style='font-size:21px;font-weight:bold'>Generate Streamlit code</div>",unsafe_allow_html=True)
            st.write("Build rapid data dashboards with clean Python implementation.")
prompt=st.chat_input(placeholder="Ask me anything...")
if 'pending_prompt' in st.session_state and st.session_state.pending_prompt:
    with st.spinner("Gemini Thinking..."):
        with st.chat_message("assistant"):
            placeholder=st.empty()
            text=""
            try:
                response=chatbot.stream_response(chat_session=chat,prompt=st.session_state.pending_prompt)
                st.session_state.pending_prompt = None
                if response:
                    for chunk in response:
                        text+=chunk.text
                        placeholder.markdown(text+"▌")
                    placeholder.markdown(text)
                    messages.append({"role":"assistant","message":text,"timestamp":utils.get_current_timestamp()})
                    st.rerun()
            except Exception as e:
                st.error(f"Something went wrong:{e}")
for i,msg in enumerate(messages):
    if msg["role"]=="user":
        user_message(msg["message"])
    else:
        ai_message(msg["message"])
    # with st.chat_message(msg["role"]):
    #     st.markdown(msg["message"])
    #     left,mid,right=st.columns([3,1,1])
    #     with mid:
    #         if (msg["role"]=="assistant"):
    #             components.html(f"""
    #                         <button onclick="navigator.clipboard.writeText(`{msg["message"]}`)">©️</button>
    #                             """,height=40)
    if (msg["role"]=="assistant" and i==len(messages)-1):
        if st.button("🔄",key="regenerate"):
            last_prompt=None
            for msg in reversed(messages):
                if msg["role"]=="user": 
                    last_prompt=msg["message"]
                    break
            if messages and messages[-1]["role"]=="assistant":
                messages.pop()
                st.session_state.pending_prompt=last_prompt
                st.rerun()
if prompt:
    with st.chat_message("user"):
        st.session_state.pending_prompt = prompt
        messages.append({"role":"user","message":prompt,"timestamp":utils.get_current_timestamp()})
        st.rerun()
    
