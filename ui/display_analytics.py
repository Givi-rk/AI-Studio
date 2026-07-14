import streamlit as st
import Analytics
def show():
    stats=Analytics.get_statistics(st.session_state.user_id)
    st.subheader("Conversation Statistics")
    col1,col2=st.columns(2)
    with col1:
        st.metric("Total Messages",stats["total_messages"],border=True)
        st.metric("User Messages",stats["user_messages"],border=True)
        st.metric("Total Words",stats["total_words"],border=True)
    with col2:
        st.metric("AI Messages",stats["ai_messages"],border=True)
        st.metric("Duration",stats["duration"],border=True)