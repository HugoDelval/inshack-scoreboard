# inshack-scoreboard
A Django scoreboard for CTF

## Build

```bash
docker build -t registry.insecurity-insa.fr/insecurity/scoreboard -f deploy/Dockerfile .
```

## RUN

```bash
docker run -it --cpu-period="100000" --cpu-quota="95000" -d --restart=always --name scoreboard -v /home/ubuntu/logs:/var/log/nginx/ -p 80:8081 registry.insecurity-insa.fr/insecurity/scoreboard
docker stop scoreboard && docker rm -v scoreboard
```

## Login as root

```bash
docker exec -u 0 -it scoreboard bash
```

### Restore old DB

```bash
. venv/bin/activate
curl http://..../data_dump.json
python manage.py loaddata data_dump.json
```
