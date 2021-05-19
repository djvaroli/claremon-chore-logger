FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app .

ENTRYPOINT ["/scripts/start.sh"]

