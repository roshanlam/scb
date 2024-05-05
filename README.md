#Google Auth
- Utilizes sessions instead of JWT
- create new .env file in sim folder and add GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET
- Open Google console, go to api's and services, oauth 2.0, click create credentials, create new oauth client id, and paste id into new .env file
- Open index.vue in scf frontend folder and update clientid to your clientid
- pip install django-cors-headers

#Setup local postgres
- Create db in local postgres(update settings.py to allow django usage)
- python3 manage.py makemigrations(to initialize the db)
- python3 manage.py migrate(to initialize the db)
- python3 manage.py flush(to reset db)

#General Server Commands
- RUN SERVER: python3 manage.py runserver localhost:8000
