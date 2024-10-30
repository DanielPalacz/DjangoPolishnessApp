# DjangoPolishnessApp

###### Deployed here: https://poznajmypolske.pl/

### Development usage
```
Additional tools used in development / debug phase:
1. pre-commit
https://pre-commit.com/

2. Django Debug Toolbar:
https://django-debug-toolbar.readthedocs.io/en/latest/index.html
```


### Production deployment
```
1. Download repository, create virtual env, install python requirements:
 - git clone <repositoty link>
 - python -m venv <virtual env>
 - pip install -r requirments.txt

2. Setup/ensure ngnix/domain configuration is correct:
    - DNS, SSL, ngnix configuration

3. Run the following:
 - python manage.py makemigration
 - python manage.py migrate
 - python manage.py createsuperuser
 - python manage.py collectstatic

4. Prepare database. Run from Django shell:
 - python manage.py shell_plus --ipython
 - import tools
 - tools.populate_monument_db_table()
 - tools.populate_archeological_monument_db_table()
 - tools.populate_geographical_object_table()

5A. Setup env variables:
 - export SENDGRID_API_KEY="SENDGRID_API_KEY_VALUE"
 - export UNPLASH_API_KEY="UNPLASH_API_KEY_VALUE"
 - export OPENAI_API_KEY="OPENAI_API_KEY_VALUE"
 - export GUS_DBW_API_KEY="GUS_DBW_API_KEY_VALUE"
 - export LOG_LEVEL_NAME="LOG_LEVEL_NAME_VALUE"
   (one of the values:  "CRITICAL", "FATAL", "ERROR", "WARNING", "INFO", "DEBUG")

5B. Instead of manually exporting env variables - create linux service with env vars loaded.
 - Use configuration README.md
 - sudo vi /etc/systemd/system/polishness.service
 - sudo systemctl enable polishness
 - sudo systemctl start polishness
 - sudo systemctl restart polishness

5C. Also, for some time when you may manually run gunicorn.
    gunicorn  --workers 3 --pythonpath mysite mysite.wsgi:application

```
