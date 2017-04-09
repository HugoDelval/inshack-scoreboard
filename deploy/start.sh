#!/usr/bin/env bash

service mysql restart
mysqladmin -u root password CHANGE_ME
mysql -uroot -pCHANGE_ME -e "CREATE USER 'inshack'@'localhost' IDENTIFIED BY 'CHANGE_ME';CREATE DATABASE inshack CHARACTER SET utf8 COLLATE utf8_bin;GRANT ALL PRIVILEGES ON inshack.* TO 'inshack'@'localhost';GRANT GRANT OPTION ON inshack.* TO 'inshack'@'localhost';"

su -c "cd /home/scoreboard/inshack-scoreboard
../venv_ctf/bin/python manage.py makemigrations
../venv_ctf/bin/python manage.py migrate
../venv_ctf/bin/python manage.py collectstatic --noinput
../venv_ctf/bin/python manage.py loaddata deploy/fixtures.json
rm deploy/fixtures.json
echo \"from django.contrib.auth.models import User;from challenges.models import CTFSettings; User.objects.create_superuser('adminctf', 'me@gmail.com', 'CHANGE_ME');CTFSettings.objects.create(url_challenges_state='http://213.32.77.192/')\" | ../venv_ctf/bin/python manage.py shell" scoreboard

service supervisor start
supervisorctl reread
supervisorctl update
service nginx restart
service sysstat restart
service cron start
tail -f /var/log/nginx/scoreboard.error.log
