
FROM python:2.7
ADD . /cap
WORKDIR /cap
RUN pip install -r requirements.txt
