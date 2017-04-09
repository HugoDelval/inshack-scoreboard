FROM ubuntu:latest

RUN useradd scoreboard -m -s /bin/bash
RUN apt-get update && \
    apt-get install -y apt-utils && \
    { \
        echo debconf debconf/frontend select Noninteractive; \
        echo mysql-community-server mysql-community-server/data-dir \
            select ''; \
        echo mysql-community-server mysql-community-server/root-pass \
            password 'CHANGE_ME'; \
        echo mysql-community-server mysql-community-server/re-root-pass \
            password 'CHANGE_ME'; \
        echo mysql-community-server mysql-community-server/remove-test-db \
            select true; \
    } | debconf-set-selections && \
    apt-get install -y nginx mysql-server python3 python3-pip python3-dev python3-venv zlib1g-dev libjpeg-dev gifsicle curl cron sysstat supervisor bc
RUN mkdir /srv/web/ && \
    chown scoreboard:www-data /srv/web/ && \
    sed -i -- 's/false/true/g' /etc/default/sysstat && \
    mkdir /home/scoreboard/logs/ && \
    chown scoreboard:scoreboard /home/scoreboard/logs/

USER scoreboard
RUN cd /home/scoreboard && \
    python3 -m venv venv_ctf && \
    venv_ctf/bin/pip install pymysql django Pillow gunicorn requests

USER root
ADD . /home/scoreboard/inshack-scoreboard
RUN mv /home/scoreboard/inshack-scoreboard/deploy/loadMon.sh /loadMon.sh && \
    mv /home/scoreboard/inshack-scoreboard/deploy/dumpdb.sh /dumpdb.sh && \
    mv /home/scoreboard/inshack-scoreboard/deploy/start.sh /start.sh && \
    mv /home/scoreboard/inshack-scoreboard/deploy/restoredb.sh /restoredb.sh && \
    chown root:root /loadMon.sh && chmod 700 /loadMon.sh && \
    chown root:root /dumpdb.sh && chmod 700 /dumpdb.sh && \
    chown root:root /start.sh && chmod 700 /start.sh && \
    chown root:root /restoredb.sh && chmod 700 /restoredb.sh && \
    echo "*/10 * * * * root /loadMon.sh" >> /etc/crontab && \
    echo "*/20 * * * * root /dumpdb.sh" >> /etc/crontab && \
    echo >> /etc/crontab && \
    mv /home/scoreboard/inshack-scoreboard/deploy/supervisor.gunicorn /etc/supervisor/conf.d/gunicorn.conf && \
    mv /home/scoreboard/inshack-scoreboard/deploy/nginx-site /etc/nginx/sites-available/scoreboard && \
    ln -s /etc/nginx/sites-available/scoreboard /etc/nginx/sites-enabled && \
    chown scoreboard:scoreboard /home/scoreboard/inshack-scoreboard -R

CMD /start.sh
