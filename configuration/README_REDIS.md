###### Deployed here: https://poznajmypolske.pl/

### PRODUCTION
```
sudo apt update
sudo apt upgrade
sudo apt install redis-server

sudo vi /etc/redis/redis.conf => 'supervised systemd'

ensure redis port is blocked (default in this case: 6379)
 - it is blocked by Redis configuration when such line is added:
 - bind 127.0.0.1 ::1

```
