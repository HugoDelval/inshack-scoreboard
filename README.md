# inshack-scoreboard
A Django scoreboard for CTF

## Build

```bash
docker build -t registry.insecurity-insa.fr/insecurity/scoreboard -f deploy/Dockerfile .
```

## Setup the DB on a separate server

```bash
$ mysql -uroot -p
mysql> CRATE DATABASE inshack;
mysql> CREATE USER 'inshack'@'localhost' IDENTIFIED BY 'password';
mysql> GRANT ALL PRIVILEGES ON inshack.* TO 'inshack'@'localhost';
mysql> exit
```

Modify *inshack_scoreboard/settings.py* accordingly. Then launch the migrations on the mysql host:

```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

## Populate DB

```bash
echo "from django.contrib.auth.models import User; \
from challenges.models import CTFSettings; \
User.objects.create_superuser('adminctf', 'me@gmail.com', 'CHANGE_ME'); \
CTFSettings.objects.create(url_challenges_state='http://IP_OF_CHALLENGE_MONITORING/')
" | python3 manage.py shell
```

## Run

```bash
docker run --rm -it --cpu-period="100000" --cpu-quota="95000" --name scoreboard -p 80:8081 registry.insecurity-insa.fr/insecurity/scoreboard
```

## Login as root

```bash
docker exec -u 0 -it scoreboard bash
```
