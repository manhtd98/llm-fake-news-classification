from core import helpers
import numpy as np 
from scipy.io import wavfile
import torch
import tempfile
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from core import init
import threading
from core.expire import setting_env
from nltk.tokenize import sent_tokenize
import uvicorn


app = FastAPI()

origins = [
    "http://localhost:3003",
    "http://192.168.6.18:3003",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_audio(sentences, model, speaker_id):
    wavs = []
    for sent in sentences:
        if sent.strip().rstrip() =="":
            continue
        if sent == "########":
            silence_duration = int(0.3 * 22050)
            silence = np.zeros(silence_duration)
            wavs.append(silence)
            continue
        wav = model( sent, speaker_id)
        wavs.append(wav)
        silence_duration = int(0.1 * 22050)
        silence = np.zeros(silence_duration)
        wavs.append(silence)

    wav = np.concatenate(tuple(wavs))
    return wav



async def save_upload_file_temporarily(upload_file):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(upload_file.file.read())
    temp_file.close()
    return temp_file.name



@app.post("/tts")
async def tts(text: str = Form(...)):
    
    if text =="":
        return 400
    torch.cuda.empty_cache()
    sentences = helpers.clean_text(text)
    model = init.vietnamese_model
    wav = get_audio(sentences, model , speaker_id=None)
   
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        wavfile.write(tmp.name, rate=22050, data=wav.astype(np.int16))
        torch.cuda.empty_cache()
        return FileResponse(tmp.name, media_type='audio/wav', filename=tmp.name)

# uvicorn.run(app, host="0.0.0.0", port=6688)
t = threading.Thread(target=setting_env)
t.start()