import os
from enum import Enum, auto
from langchain.prompts import PromptTemplate

PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["context", "question"],
    template="""Bạn là một chatbot hỏi đáp thông minh nhận và trả lời các câu hỏi về học viện kỹ thuật quân sự.

Về học viện Kỹ thuật quân sự: 
Học viện Kỹ thuật Quân sự (tiếng Anh: Military Technical Academy – MTA), (mã tuyển sinh là KQH), hay còn được gọi với cái tên dân sự là Trường Đại học Kỹ thuật Lê Quý Đôn là cơ sở nòng cốt để xây dựng, phát triển nền khoa học kỹ thuật, công nghệ quân sự và công nghiệp quốc phòng Việt Nam, trong bối cảnh cuộc cách mạng kỹ thuật quân sự trên thế giới đang phát triển nhanh chóng.

## Instructions:
Chỉ sử dụng các phần ngữ cảnh sau đây để trả lời câu hỏi. Nếu không có thông tin phù hợp chỉ cần nói rằng bạn không biết, đừng cố gắng bịa ra một câu trả lời.

## Ngữ cảnh:
{context}

## Câu hỏi:
{question}

## Câu trả lời:
""",
)


SUMMARIZE_PROMPT_TEMPLATE = PromptTemplate(
    input_variables=["history", "question"],
    template="""Bạn là một công cụ tổng hợp thông tin.
## Instructions:
Sử dụng lịch sử hội thoại sau, chỉ sử dụng các thông tin liên quan tới câu hỏi yêu cầu. Câu hỏi tổng hợp cần ngắn gọn, đúng trọng tâm của câu hỏi yêu cầu, đừng cố gắng bịa ra nội dung bổ sung.

## Lịch sử hội thoại:
{history}

## Câu hỏi yêu cầu:
{question}

## Câu tổng hợp:
""",
)


class ResponseEnum(Enum):
    SUCCESS = "success"
    INDEX_DUPLICATE = "index_duplicate"
    INDEX_NOT_FOUND = "index_not_found"
    EXCEPTION = "error_exception"
    DOCUMENT_INVALID = "document_invalid"


class CONFIG:
    EMBEDDING_MODEL_ID = os.getenv(
        "EMBEDDING_MODEL_ID", "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
    )
    LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "nguyenviet/PhoGPT-4B-Chat-GGUF")

    SPEECH2TEXT_MODELNAME = os.getenv(
        "SPEECH2TEXT_MODELNAME", "manhtd98/whisperPho-FasterWhisper"
    )
    TEXT2SPEECH_ENDPOINT = os.getenv(
        "TEXT2SPEECH_ENDPOINT", "http://localhost:6688/tts"
    )
    ELS_ENDPOINT = os.getenv("ELS_ENDPOINT", "192.168.31.172")
    ELS_USERNAME = os.getenv("ELS_USERNAME", "elastic")
    ELS_PASSWORD = os.getenv("ELS_PASSWORD", "mta2024")
    ELS_INDEXNAME = os.getenv("ELS_INDEXNAME", "mta2024-index")
    ELS_INDEXNAME_QA = os.getenv("ELS_INDEXNAME_QA", "mta2024-index-qa")

    cache_dir = "./cache"
    source_path = "./data/*.json"
    qa_path = "./test/*.xlsx"
    chunk_size = 512
    chunk_overlap = 50
    N_CTX = 2000
    n_gpu_layers = -1
    n_batch = 512
    top_k = 5
    distance_strategy = "COSINE"
    device = os.getenv("DEVICE", "cpu")
    QA_THRESHOLD = 2
    MTA_ICON = "https://raw.githubusercontent.com/manhtd98/public_source/main/styles/Logo_MTA_new.png"
    CHAT_ICON = (
        "https://raw.githubusercontent.com/manhtd98/public_source/main/styles/chat.png"
    )
