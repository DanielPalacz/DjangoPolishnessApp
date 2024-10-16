# DjangoPolishnessApp

###### Deployed here: http://poznajmypolske.pl/


### Production deployment
```
1. Setup/ensure ngnix/domain configuration is correct.
    - DNS, SSL, ngnix configuration


2. Run the following:
 - python manage.py makemigration
 - python manage.py migrate
 - python manage.py createsuperuser
 - python manage.py collectstatic

3. Run:
 - export SENDGRID_API_KEY="SENDGRID_API_KEY_VALUE"

4. Run:
 - export UNPLASH_API_KEY="UNPLASH_API_KEY_VALUE"

5. Run:
 - export OPENAI_API_KEY="OPENAI_API_KEY_VALUE"

6. Run:
 - export GUS_DBW_API_KEY="GUS_DBW_API_KEY_VALUE"

3-4-5-6: Instead of these points "create linux service with env vars loaded".
 - sudo vi /etc/systemd/system/polishness.service
 - sudo systemctl enable polishness
 - sudo systemctl start polishness
 - sudo systemctl restart polishness
 
 

7. Prepare database. Run from Django shell:
 - python manage.py shell_plus --ipython
 - import tools
 - tools.populate_db()

```
