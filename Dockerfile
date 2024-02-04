FROM python:3.9-slim-buster

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./src /app/
WORKDIR /app


EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--http", "h11"]