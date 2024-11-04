###### Deployed here: https://poznajmypolske.pl/

### PRODUCTION
```
Creating services for Celery[worker] and Celery Beat:
mkdir -p /var/run/celery
mkdir -p /var/log/celery
mkdir -p /etc/celery
create '/etc/celery/celery_setup_env' file
create '/etc/systemd/system/celery.service' file
create '/etc/systemd/system/celerybeat.service'

create dedicated user named celery (group celery)

systemctl daemon-reload
systemctl enable celery.service
systemctl start celery.service
systemctl enable celerybeat.service
systemctl start celerybeat.service


Debugging issues:
journalctl -u celery.service -b
sudo systemctl daemon-reload
sudo systemctl restart celery.service
sudo systemctl status celery.service
sudo systemctl restart celerybeat.service
sudo systemctl status celerybeat.service
```

### LOCALLY
```
celery -A mysite.celery_setup worker --loglevel=info -B
```
