###### Deployed here: https://poznajmypolske.pl/

### FLOWER USAGE
```
celery --broker=redis://localhost:6379/0 flower --port=8888 --address='poznajmypolske.pl' --basic-auth="user1:password1,user2:password2"

http://127.0.0.1:8888/
```
