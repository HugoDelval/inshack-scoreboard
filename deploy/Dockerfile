FROM ubuntu:latest

RUN useradd scoreboard -m -s /bin/bash
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nginx python3-pip supervisor

RUN mkdir /srv/web/ && \
    chown scoreboard:www-data /srv/web/ && \
    mkdir /home/scoreboard/logs/ && \
    chown scoreboard:scoreboard /home/scoreboard/logs/

ADD ./deploy /tmp/
RUN pip3 install -r /tmp/requirements.txt && \
    mv /tmp/supervisor.gunicorn /etc/supervisor/conf.d/gunicorn.conf && \
    mv /tmp/nginx-site /etc/nginx/sites-available/scoreboard && \
    ln -s /etc/nginx/sites-available/scoreboard /etc/nginx/sites-enabled && \
    rm /etc/nginx/sites-enabled/default

ADD app /home/scoreboard/inshack-scoreboard
RUN chown scoreboard:scoreboard /home/scoreboard/inshack-scoreboard -R
RUN cd /home/scoreboard/inshack-scoreboard/ && python3 manage.py collectstatic --noinput

EXPOSE 8081

CMD service supervisor start && \
    service nginx restart && \
    bash -c "tail -f {/var/log/nginx/scoreboard.*.log,/home/scoreboard/logs/error,/home/scoreboard/logs/access}"
