FROM python:latest
MAINTAINER Dimitr 'indieagle.games@gmail.com'

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
CMD ["python3", "proxy_server.py"]
