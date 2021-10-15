# syntax=docker/dockerfile:1
FROM python:alpine3.7
COPY . ./app
WORKDIR /app
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install y -r requirements.txt
#EXPOSE 5005
ENTRYPOINT [ "python3" ]
CMD [ "flask_home.py" ]