from pytorch/pytorch:2.1.0-cuda11.8-cudnn8-devel
WORKDIR /app
ADD requirements.txt /app
RUN pip install -r requirements.txt && apt update\
    && apt install -y nano && apt install -y psmisc

ADD . /app
# ENTRYPOINT ["python3", "app.py"]
ENTRYPOINT ["gunicorn", "fast_app_v2:app", "--workers", "2" , "--worker-class", "uvicorn.workers.UvicornWorker", "--log-level", "info", "--timeout", "120", "--bind", "0.0.0.0:6688"]

