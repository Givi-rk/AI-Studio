import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError
from config import get_api_key
import time
import re
from PIL import Image

client = genai.Client(api_key=get_api_key())
def get_youtube_url(text):
    pattern=r"(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s]+)"
    match=re.search(pattern,text)
    return match.group(0) if match else None
def initialize_gemini_chat(generation_config:dict, model = 'gemini-3.1-flash-lite',web_search=False):
    config=types.GenerateContentConfig(
        temperature=generation_config.get("temperature",1.0),
        max_output_tokens=generation_config.get("max_output_tokens",2048),
        top_p=generation_config.get("top_p",0.95),
        top_k=generation_config.get("top_k",40),
    )
    if st.session_state.web_search:
        config.tools=[types.Tool(google_search=types.GoogleSearch())]
    try:
        return client.chats.create(model=model,config=config,)
    except APIError as e:
        st.error(f"Gemini API error during initialization:{e.message}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occured:{e}")
        return None
def stream_response(chat_session,prompt:str,uploaded_files=None):
    try:
        url=get_youtube_url(prompt)
        contents=[]
        if prompt:
            contents.append(prompt.replace(url, '').strip() if url else prompt)
        if url:
            contents.append(types.Part.from_uri(file_uri=url, mime_type='video/*'))
        if uploaded_files:
            for file in uploaded_files:
                if file.type.startswith("image/"):
                    image=Image.open(file)
                    contents.append(image)
                else:
                    gemini_file=client.files.upload(file=file,config={"mime_type":file.type})
                    while gemini_file.state and gemini_file.state.name=="PROCESSING":
                        time.sleep(2)
                        gemini_file=client.files.get(name=gemini_file.name)
                    contents.append(gemini_file)
        response_stream=chat_session.send_message_stream(contents)
        return response_stream
    except APIError as e:
        st.error(f"Gemini API Error:{e.message}")
    except Exception as e:
        st.error(f"{e}")
def generate_chat_title(prompt):
    config = types.GenerateContentConfig(system_instruction='''You're a chat title generation bot. For the given prompt, you have to make the title of that chat.
                                                      Rules:
                                                      - only return the title.
                                                      - no quotation marks.
                                                      - no punctuation at the end.
                                                      - it should be suitable with the given prompt
                                                      - at most, the words count should be 6
                                                      ''', max_output_tokens=20)
    response=client.models.generate_content(model="gemini-3.1-flash-lite",
                                            contents=prompt, config=config)
    return response.text.strip()

