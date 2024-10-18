# DjangoPolishnessApp: Ngnix

### 1. Create symbolic link to app configuration
```
/etc/nginx/sites-enabled
ls -l
ngnix_polishness.conf -> /etc/nginx/sites-available/ngnix_polishness.conf
```

### 2. Ensure that domain is linked to your IP.

### 3a. Run gunicorn workers for the app:
```
gunicorn --pythonpath mysite mysite.wsgi:application
```

### 3b. create service
```
sudo vi /etc/systemd/system/polishness.service
sudo systemctl enable polishness
sudo systemctl start polishness
sudo systemctl restart polishness
```
