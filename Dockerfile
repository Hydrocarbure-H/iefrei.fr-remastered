FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    pandoc \
    wget \
    apt-transport-https \
    ca-certificates \
    fontconfig

RUN wget https://www.princexml.com/download/prince-15.4.1-linux-generic-x86_64.tar.gz && \
    tar xzf prince-15.4.1-linux-generic-x86_64.tar.gz && \
    cd prince-15.4.1-linux-generic-x86_64 && \
    ./install.sh && \
    cd .. && rm -rf prince-15.4.1-linux-generic-x86_64.tar.gz prince-15.4.1-linux-generic-x86_64


RUN pip install --upgrade pip --root-user-action
RUN pip install -r requirements.txt --root-user-action

EXPOSE 5010

CMD ["python3", "app.py"]