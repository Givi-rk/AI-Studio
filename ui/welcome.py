import streamlit as st
def show():
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