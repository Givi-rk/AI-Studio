import streamlit as st
# import streamlit.components as components
def user_message(text):
    if text is None:
        return
    return f"""
                <div style="display:flex;
                    justify-content:flex-end;
                    margin:12px 0;">
                    <div style="
                        background:#2563eb;
                        color:white;
                        padding:12px 16px;
                        border-radius:18px 18px 4px 18px;
                        max-width:70%;
                        word-wrap:break-word;">{text}
                    </div>
                </div>
                """
def ai_message(text):
    if text is None:
        return
    return f"""
                <div style="display:flex;
                    justify-content:flex-start;margin:12px 0;">
                    <div style="background:#2d2d2d;
                                color:white;padding:12px 16px;
                                border-radius: 18px 18px 18px 4px;
                                max-width:70%;word-wrap:break-word;
                                position:relative">{text}                       
                    </div>
                </div>
                """
