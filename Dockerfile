FROM python:3.9-bullseye

RUN python -m pip install rasa

WORKDIR /app
COPY . .

RUN rasa train nlu

USER 1001

ENTRYPOINT [ "rasa"]

CMD [ "run", "--enable-api", "--port", "8080" ]