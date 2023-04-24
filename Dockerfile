FROM rasa/rasa
ENV BOT_ENV=production
COPY . /var/www
WORKDIR /var/www
RUN pip install --user -r requirements.txt
RUN rasa train
ENTRYPOINT [ "rasa", "run", "-p", "8080"]