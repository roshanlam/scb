#Google Auth
- Utilizes sessions instead of JWT
- setup .env file with oauth clientid and secret once google auth setup in google auth console
- replace google auth clientid in frontend auth page to get it to run
- pip install django-cors-headers

#Setup local postgres
- Create db in local postgres(update settings.py to allow django usage)
- python3 manage.py makemigrations(to initialize the db)
- python3 manage.py migrate(to initialize the db)
- python3 manage.py flush(to reset db)

#General Server Commands
- RUN SERVER: python3 manage.py runserver localhost:8000
