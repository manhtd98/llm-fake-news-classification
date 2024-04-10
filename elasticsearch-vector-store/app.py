import dotenv
import base64
import uuid

dotenv.load_dotenv()
from tqdm import tqdm
import uuid
from multiprocessing import Lock

tqdm.set_lock(Lock())  # manually set internal lock
import streamlit as st
from api.logger_helper import configure_logging
from tempfile import NamedTemporaryFile

from audiorecorder import audiorecorder
from text2speech import TEXT2SPEECH
from speech2text import SPEECH2TEXT
from llm_inference import LLM_QA_INFERENCE
from config import CONFIG

configure_logging()

st.set_page_config(page_title="Chatbot hỏi đáp HVKTQS", page_icon=CONFIG.MTA_ICON)


@st.cache_resource(show_spinner=False)
def load_llm_model():
    with st.spinner(
        text="Hệ thống đang thực hiện tải model. Tác vụ này có thể mất một vài phút."
    ):
        LLM_MODEL = LLM_QA_INFERENCE()
        return LLM_MODEL


@st.cache_resource  # 👈 Add the caching decorator
def load_speech2text():
    with st.spinner(text="Hệ thống đang thực hiện tải model speech2text"):
        AUDIO_SPEECH_MODEL = SPEECH2TEXT(
            model_name=CONFIG.SPEECH2TEXT_MODELNAME,
            device=CONFIG.device,
            download_root=CONFIG.cache_dir,
        )
        return AUDIO_SPEECH_MODEL


@st.cache_resource  # 👈 Add the caching decorator
def load_text2speech():
    with st.spinner(text="Hệ thống đang thực hiện tải model text2speech"):
        TEXT_TO_SPEECH_MODEL = TEXT2SPEECH(CONFIG.TEXT2SPEECH_ENDPOINT)
        return TEXT_TO_SPEECH_MODEL


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )


LLM_MODEL = load_llm_model()
SPEECH2TEXT_MODEL = load_speech2text()
TEXT2SPEECH_MODEL = load_text2speech()
ROLE_TO_AVATAR = {
    "assistant": CONFIG.MTA_ICON,
    "user": CONFIG.CHAT_ICON,
}

if "session_id" not in st.session_state.keys():
    st.session_state["session_id"] = str(uuid.uuid4())
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào, Đây là chatbot hỏi đáp của HVKTQS"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=ROLE_TO_AVATAR[message["role"]]):
        st.write(message["content"])

# Streamlit
with st.sidebar:
    wav_audio_record = audiorecorder(
        "Nhấn để bắt đầu hội thoại", "Đang ghi âm", key="recorder"
    )
    voice = st.toggle("Trả lời bằng giọng nói", value=False)

# User-provided prompt
if prompt := st.chat_input("Nhập câu hỏi của bạn"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=ROLE_TO_AVATAR["user"]):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar=ROLE_TO_AVATAR["assistant"]):
        with st.spinner("Đang trả lời..."):
            response, documents = LLM_MODEL(prompt, st.session_state["session_id"])
            st.write(response)
            if len(documents) > 0:
                st.write("#### Tài liệu tham khảo")
                for doc in documents:
                    st.write("> " + doc)

    if voice:
        tts = TEXT2SPEECH_MODEL(response)
        if tts:
            with NamedTemporaryFile(suffix=".mp3") as temp:
                temp.write(tts)
                autoplay_audio(temp.name)
    st.session_state.messages.append({"role": "assistant", "content": response})

### Audio processing
elif len(wav_audio_record) > 0:
    with st.chat_message("user", avatar=ROLE_TO_AVATAR["user"]):
        with st.spinner("Đang nhận diện giọng nói..."):
            prompt = SPEECH2TEXT_MODEL(wav_audio_record)
            if prompt is not None:
                st.write(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

    if prompt is not None:
        with st.chat_message("assistant", avatar=ROLE_TO_AVATAR["assistant"]):
            with st.spinner("Đang trả lời..."):
                response, documents = LLM_MODEL(prompt)
                st.write(response)
                if len(documents) > 0:
                    st.write("#### Tài liệu tham khảo")
                    for doc in documents:
                        st.write("> " + doc)

                if voice:
                    tts = TEXT2SPEECH_MODEL(response)
                    if tts:
                        with NamedTemporaryFile(suffix=".mp3") as temp:
                            temp.write(tts)
                            autoplay_audio(temp.name)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
