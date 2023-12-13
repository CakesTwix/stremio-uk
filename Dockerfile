FROM python:3.10

WORKDIR /app

COPY /app /app
COPY requirements.txt /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "stremio:app", "--host", "0.0.0.0", "--port", "8000"]
