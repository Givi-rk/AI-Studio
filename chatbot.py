import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError
from config import get_api_key
import time
import re
import json
from file_generate import generate_file
from PIL import Image
from pydantic import BaseModel, Field
from typing import Optional, Literal
client = genai.Client(api_key=get_api_key())
class ChatResponse(BaseModel):
    text: str = Field(description="The natural language reply to the user. Always present.")
    document: bool = Field(
        default=False,
        description="True ONLY if the user explicitly and unambiguously asks for a document/file to be generated."
    )
    extension: Optional[Literal["pdf", "csv", "docx"]] = Field(
        default=None,
        description="Required when document=true. Must be null when document=false."
    )
    html: Optional[str] = Field(
        default=None,
        description="HTML used to build the document. Required when document=true, null otherwise."
    )

SYSTEM = """
You are a helpful, professional assistant.

You must always respond with a JSON object matching this schema:
- text: your natural-language reply, always required.
- document: true ONLY if the user clearly and directly asks you to generate/export a document or file
  (e.g. "generate a PDF", "make this a CSV", "create a Word doc"). Casual mentions of the words
  "pdf"/"csv"/"document" do NOT count. Default false.
- extension: "pdf" | "csv" | "docx", required when document is true, null otherwise.
- html: required when document is true, null otherwise.
    - For "csv": a single well-formed <table> with <thead>/<tbody>, parsable by pandas.read_html.
    - For "pdf": full, styled HTML representing the document layout.
    - For "docx": plain textual content/paragraphs to include.

Rules:
- If document is false, extension and html MUST be null.
- text must always be a complete, friendly answer, even when a document is also generated.
- Never include any explanation or markdown fences outside the JSON object.
"""
def get_youtube_url(text):
    pattern=r"(https?://(?:www\.)?(?:youtube\.com|youtu\.be)[^\s]+)"
    match=re.search(pattern,text)
    return match.group(0) if match else None
# def initialize_gemini_chat(generation_config:dict, model = 'gemini-3.1-flash-lite',web_search=False):
#     config=types.GenerateContentConfig(
#         temperature=generation_config.get("temperature",1.0),
#         max_output_tokens=generation_config.get("max_output_tokens",2048),
#         top_p=generation_config.get("top_p",0.95),
#         top_k=generation_config.get("top_k",40),
#         system_instruction=SYSTEM
#     )
#     if st.session_state.web_search:
#         config.tools=[types.Tool(google_search=types.GoogleSearch())]
#     try:
#         return client.chats.create(model=model,config=config,)
#     except APIError as e:
#         st.error(f"Gemini API error during initialization:{e.message}")
#         return None
#     except Exception as e:
#         st.error(f"An unexpected error occured:{e}")
#         return None
def initialize_gemini_chat(generation_config: dict, model="gemini-3.1-flash-lite", web_search=False):
    config_kwargs = dict(
        temperature=generation_config.get("temperature", 1.0),
        max_output_tokens=generation_config.get("max_output_tokens", 2048),
        top_p=generation_config.get("top_p", 0.95),
        top_k=generation_config.get("top_k", 40),
        system_instruction=None if web_search else SYSTEM,
        response_mime_type=None if web_search else "application/json",
        response_schema=ChatResponse
    )
    if web_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    config = types.GenerateContentConfig(**config_kwargs)
    try:
        return client.chats.create(model=model, config=config)
    except APIError as e:
        st.error(f"Gemini API error during initialization:{e.message}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occured:{e}")
        return None
# def stream_response(chat_session,prompt:str,uploaded_files=None):
#     try:
#         url=get_youtube_url(prompt)
#         contents=[]
#         if prompt:
#             contents.append(prompt.replace(url, '').strip() if url else prompt)
#         if url:
#             contents.append(types.Part.from_uri(file_uri=url, mime_type='video/*'))
#         if uploaded_files:
#             for file in uploaded_files:
#                 if file.type.startswith("image/"):
#                     image=Image.open(file)
#                     contents.append(image)
#                 else:
#                     gemini_file=client.files.upload(file=file,config={"mime_type":file.type})
#                     while gemini_file.state and gemini_file.state.name=="PROCESSING":
#                         time.sleep(2)
#                         gemini_file=client.files.get(name=gemini_file.name)
#                     contents.append(gemini_file)
#         response=chat_session.send_message(contents)
#         response_text= response.text
#         match = re.search(r'\{.*\}', response_text, re.DOTALL)
#         if match:
#             try:
#                 data = json.loads(match.group(0))
#                 if data.get("document"):
#                     file_path = generate_file(data["html"], data["extension"])
#                     return {"text": data["text"], "file_path": file_path}
#             except:
#                 pass
#         return {"text": response_text, "file_path": None}
#     except APIError as e:
#         st.error(f"Gemini API Error:{e.message}")
#     except Exception as e:
#         st.error(f"{e}")
def generate_chat_title(prompt):
    config = types.GenerateContentConfig(system_instruction='''You are a title generator. Return ONLY the title (max 6 words, no punctuation, no quotes)
                                                      ''', max_output_tokens=20)
    response=client.models.generate_content(model="gemini-3.1-flash-lite",
                                            contents=prompt, config=config)
    return response.text.strip()
def stream_response(chat_session, prompt: str, uploaded_files=None):
    try:
        url = get_youtube_url(prompt)
        contents = []
        if prompt:
            contents.append(prompt.replace(url, '').strip() if url else prompt)
        if url:
            contents.append(types.Part.from_uri(file_uri=url, mime_type='video/*'))
        if uploaded_files:
            for file in uploaded_files:
                if file.type.startswith("image/"):
                    image = Image.open(file)
                    contents.append(image)
                else:
                    gemini_file = client.files.upload(file=file, config={"mime_type": file.type})
                    while gemini_file.state and gemini_file.state.name == "PROCESSING":
                        time.sleep(2)
                        gemini_file = client.files.get(name=gemini_file.name)
                    contents.append(gemini_file)
        response = chat_session.send_message(contents)
        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, ChatResponse):
            data = parsed
        else:
            response_text = response.text
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            data = None
            if match:
                try:
                    data = ChatResponse.model_validate(json.loads(match.group(0)))
                except Exception:
                    data = None
            if data is None:
                return {"text": response_text, "file_path": None}
        if data.document and data.extension and data.html:
            file_path = generate_file(data.html, data.extension)
            return {"text": data.text, "file_path": file_path}
        return {"text": data.text, "file_path": None}
    except APIError as e:
        st.error(f"Gemini API Error:{e.message}")
        return None
    except Exception as e:
        st.error(f"{e}")
        return None
