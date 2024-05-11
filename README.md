# SocioCoders
- Sociocoders aims to be a one-stop platform where students can engage in educational content that’s cheap or free. Based on these courses, students will be questioned through the use of Artificial Intelligence and are incentivized through keeping a streak. Users may also talk to others in the forum where they can receive help from others or discuss about other topics.

# Setup
## Google Auth
- Open Google console, go to api's and services, oauth 2.0, click create credentials, create new oauth client id, and paste id into new .env file
- Open index.vue in scf frontend folder and update clientid to your clientid
- pip install django-cors-headers

## Setup local postgres
- Create db 'sociocoders' in local postgres
- Reset DB: python3 manage.py flush
- Reinitialize DB: python3 manage.py makemigrations && python3 manage.py migrate

## Setup Open AI api
- Create open AI account, setup billing, and generate open ai secret key

## Create .env File
- Create '.env' file in '/scb/api'
- Populate with these keys: GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, OPENAI_API_KEY

## Run Server
- Command: python3 manage.py runserver localhost:8000

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
