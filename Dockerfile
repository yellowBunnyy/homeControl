# syntax=docker/dockerfile:1
FROM python:alpine3.7
COPY ./app /my_app
WORKDIR /my_app
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt
ENTRYPOINT [ "python3" ]
CMD [ "flask_home.py" ]