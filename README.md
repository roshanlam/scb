# Google Auth
- Utilizes sessions instead of JWT
- create new .env file in sim folder and add GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET
- Open Google console, go to api's and services, oauth 2.0, click create credentials, create new oauth client id, and paste id into new .env file
- Open index.vue in scf frontend folder and update clientid to your clientid
- pip install django-cors-headers

# Setup local postgres
- Create db in local postgres (update .env values to allow django usage)
- python3 manage.py makemigrations (to initialize the db)
- python3 manage.py migrate (to initialize the db)
- python3 manage.py flush (to reset db)

# General Server Commands
- RUN SERVER: python3 manage.py runserver localhost:8000


# Run Docker/Docker Compose

1. Install the Docker App and make sure it is running

2. Run the following command: `docker-compose build`

3. Run the following command: `docker-compose up -d`

To check there are no errors run the following: 
`docker-compose logs`

To stop and remove all related Docker containers, networks, and the default volume, use:
`docker-compose down`

To remove data volume (will delete database data):
`docker-compose down -v`