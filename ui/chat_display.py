import streamlit as st
from display import ai_message,user_message
from st_copy import copy_button
import os
CSS = '''
<style>
.file-container {
    max-width: 400px;
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 10px;
    background-color: var(--secondary-background-color);
}
button[data-testid="stBaseButton-secondary"] {
    right: 40px;
    margin-top: -10px;
}
</style>
'''
def display(messages):
    st.markdown(CSS, unsafe_allow_html=True)
    length = len(messages)
    for i,msg in enumerate(messages):
        if msg["role"]=="user":
            if "files" in msg and msg["files"]:
                with st.container():
                    st.markdown('<div class="file-container">', unsafe_allow_html=True)
                    for file in msg["files"]:

                        if file["type"].startswith("image/"):
                            st.image(file["path"])

                        elif file["type"].startswith("video/"):
                            st.video(file["path"])

                        elif file["type"] == "application/pdf":
                            st.write(f"📄 {file['path']}")

                        else:
                            st.write(f"📎 {file['path']}")
                    st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(user_message(msg["message"]), unsafe_allow_html=True)
        if msg["role"]=="assistant":
            st.markdown(ai_message(msg["message"]), unsafe_allow_html=True)
            if msg.get("files"):
                for file_path in msg["files"]:
                    if file_path and os.path.exists(file_path):
                        extension = os.path.splitext(file_path)[1].lstrip(".")
                        unique_key=f"dl_{i}_{os.path.basename(file_path)}"
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label=f"📥 Download {extension.upper()}",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="application/octet-stream",
                                key=unique_key
                            )
            c1,c2, _=st.columns([0.5, 1, 20], gap='xxsmall')
                    
            with c1:
                copy_button(msg["message"],key=f"copy{i}")
            if i + 1 == length:
                with c2:
                    if st.button(":material/refresh:",key=f"regenerate{i}"):
                        last_prompt=None
                        for msg in reversed(messages):
                            if msg["role"]=="user": 
                                last_prompt=msg["message"]
                                break
                        if messages and messages[-1]["role"]=="assistant":
                            messages.pop()
                            st.session_state.pending_prompt=last_prompt
                            st.rerun()
        