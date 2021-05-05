FROM python:latest

COPY ./requirements.txt /requirements.txt
COPY ./scripts /app

RUN pip install -r /requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
