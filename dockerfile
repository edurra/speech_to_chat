FROM python:3.9
RUN apt-get update && apt-get install ffmpeg -y
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT python web.py
