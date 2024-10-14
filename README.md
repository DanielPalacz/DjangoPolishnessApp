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

6. Prepare database. Run from Django shell:
 - python manage.py shell_plus --ipython
 - import tools
 - tools.populate_db()

```
