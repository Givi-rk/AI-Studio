import streamlit as st
CSS="""
<style 
.prompt-card button{
    width:100%;
    height: 120px;
    border-radius: 18px;
    border: 1px solid #3b3b3b;
    background: #1f1f1f;
    color: white;
    text-align: left;
    padding: 18px;
    transition: all .2s ease;
    cursor: pointer;
}

.prompt-card button:hover {
    border-color: #5e8cff;
    background: #292929;
    transform: translateY(-3px);
    box-shadow: 0 8px 18px rgba(0,0,0,.35);
}
"""
Prompts=[
    (
        "🐍 Explain Python decorators",
        "Deep dive into functional programming concepts and syntax.",
        "Explain Python decorators with simple examples and when they should be used."
    ),
    (
        "📰 Summarize an article",
        "Extract key insights and bullet points from long-form text.",
        "Summarize the following article into concise bullet points."
    ),
    (
        "🗄️ Optimize an SQL query",
        "Improve performance of joins and nested subqueries.",
        "Optimize this SQL query for maximum performance and explain the improvements."
    ),
    (
        "🚀 Generate Streamlit code",
        "Build clean and modern Streamlit applications.",
        "Generate a beautiful Streamlit application with best practices."
    )
]
def card(title,desc,prompt,key):
    st.markdown("<div class='prompt-card'>",unsafe_allow_html=True)
    if st.button(f"###{title}\n\n{desc}",key=key,use_container_width=True):
        st.session_state.pending_prompt=prompt
        st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)
def show():
    st.markdown(CSS,unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center'>How can I help you?</h1>",unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="large")
    with c1:
        card(*Prompts[0],"card1")
        card(*Prompts[1],"card2")
    with c2:
        card(*Prompts[2],"card3")
        card(*Prompts[3],"card4")
    # st.markdown("<div style='text-align:center;font-size:35px;font-weight:bold'> Welcome to AI Chat Assistant</div>", unsafe_allow_html=True)
    # st.write("<div style='text-align:center;font-size:19px;margin-bottom:30px'>Ask anything and receive intelligentb response powered by Gemini.<br>Explore possibilities from complex coding to creative writing.</div>",unsafe_allow_html=True)
    # c1,c2=st.columns(2)
    # with c1:
    #     with st.container(border=True):
    #         st.markdown("<div style='font-size:21px;font-weight:bold'>Explain Python decorators</div>",unsafe_allow_html=True)
    #         st.write("Deep dive into functional programming concepts and syntax")
    #     with st.container(border=True):
    #         st.markdown("<div style='font-size:21px;font-weight:bold'> Summarize an article</div>",unsafe_allow_html=True)
    #         st.write("Extract key insights and bullet points from any long-form text.")
    # with c2:
    #     with st.container(border=True):
    #         st.markdown("<div style='font-size:21px;font-weight:bold'>Optimize an SQL query</div>",unsafe_allow_html=True)
    #         st.write("Improve performance of complex joins and nested subqueries")
    #     with st.container(border=True):
    #         st.markdown("<div style='font-size:21px;font-weight:bold'>Generate Streamlit code</div>",unsafe_allow_html=True)
    #         st.write("Build rapid data dashboards with clean Python implementation.")