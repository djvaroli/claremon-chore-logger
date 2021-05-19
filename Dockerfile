FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app .

EXPOSE ${PORT}
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]

