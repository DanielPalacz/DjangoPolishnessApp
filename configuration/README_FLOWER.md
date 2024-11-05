###### Deployed here: https://poznajmypolske.pl/

### FLOWER USAGE
```
celery -A mysite.celery_setup.app flower --port=8888 --address='poznajmypolske.pl' --basic-auth="user1:password1,user2:password2"

only http:
    http://127.0.0.1:8888/
    http://poznajmypolske.pl:8888/
```
