# App-Service-Stack ![ass logo][logo]
 Infrastructure setup for app/service development using MYSQL, MongoDB, Auth , Shock and AWE ([M]ASA).





[logo]: https://github.com/wilke/App-Service-Stack/blob/master/data/pictures/donkey.jpg "Donkey aka ass"



## Building docker images

All builds start within the root directory within this repository.

1. `source ./init.sh`
2. `./create-docker-images.sh`

If you want to build the imagaes manually you have to set build tag. The image tag is derived from the TAG environment variable:
`export TAG=demo`

### ShockBrowser

 `docker build -t shock-browser:${TAG} -f Docker/Dockerfiles/shock-browser.dockerfile .`
 
### authServer
 
 `docker build -t auth:${TAG} -f Docker/Dockerfiles/authServer.dockerfile .`

### 
 
## Starting services

- Check config:

  `docker-compose -f Docker/Compose/ass.yaml config`
- Start services:

  `docker-compose -f Docker/Compose/ass.yaml up` 

  This will start the databases and shock. The ui and api can reached via http://localhost:8001 :
  - Shock browser: http://localhost:8001/shock
  - Shock API: http://localhost:8001/shock/api
  - Mysql broser: http://localhost:8001/mysql