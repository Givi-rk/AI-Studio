import streamlit as st
import Analytics
def show(messages):
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