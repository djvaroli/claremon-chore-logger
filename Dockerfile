FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app
RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app .

RUN ["chmod", "+x", "scripts/start.sh"]
ENTRYPOINT ["scripts/start.sh"]

