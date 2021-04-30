FROM tiangolo/uvicorn-gunicorn-fastapi:latest

COPY ./requirements.txt /requirements.txt
COPY ./scripts /app
RUN pip install -r /requirements.txt