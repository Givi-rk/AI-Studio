import streamlit as st
def settings():
    st.title("Settings")
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