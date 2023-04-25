FROM rasa/rasa
ENV BOT_ENV=production
COPY . /var/www
WORKDIR /var/www
RUN apt-get update
RUN pip install -r requirements.txt
RUN rasa train
ENTRYPOINT [ "rasa", "run", "-p", "8080"]