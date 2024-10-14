# DjangoPolishnessApp: Ngnix

### SSL:
```
SSL:
sudo apt update
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx

Certificate is saved at: /etc/letsencrypt/live/poznajmypolske.pl/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/poznajmypolske.pl/privkey.pem

certbot install --cert-name poznajmypolske.pl www.poznajmypolske.pl
```
