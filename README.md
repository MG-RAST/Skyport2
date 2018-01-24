

# ![skyport logo](data/pictures/skyportlogo.small.jpg) Skyport2
 Infrastructure setup for app/service development using MySQL, MongoDB, Auth , Shock and AWE ([M]ASA).





[logo]: https://github.com/wilke/App-Service-Stack/blob/master/data/pictures/donkey.jpg "Donkey aka ass"
[skyport]: https://github.com/wilke/App-Service-Stack/blob/master/data/pictures/skyportlogo.png "Containerized infrastructure"


## Quick start

All docker images required for the quick start are available at Docker Hub. To start the demo environment run:

1. ```source ./init.sh ```
2. ```docker-compose up```




## Building docker images

All builds start within the root directory within this repository.

1. git submodule init
2. git submodule update or `git submodule update --remote`  
3. `source ./init.sh`
4. `./create-docker-images.sh`

If you want to build the images manually you have to set build tag. The image tag is derived from the TAG environment variable:
`export TAG=demo`

### Shock Browser

 `docker build -t shock-browser:${TAG} -f Docker/Dockerfiles/shock-browser.dockerfile .`

### authServer

 `docker build -t auth:${TAG} -f Docker/Dockerfiles/authServer.dockerfile .`



## Starting services




### Skyport demo

To run the demo with a full stack of services:

- Check config:

  `docker-compose config`
- Start services:

  `docker-compose up`

  The web services are mapped to port 8001 on localhost[http:/localhost:8001]:

  - Shock browser: http://localhost:8001/shock
  - Shock API: http://localhost:8001/shock/api
  - AWE browser: http://localhost:8001/awe
  - AWE API: http://localhost:8001/awe/api
  - MySQL browser: http://localhost:8001/mysql

### Skyport - AWE development stack

The AWE development environment is the basic skyport app service stack whith persistent (mounted) database storage and mounted AWE source repository. Coding can be done outside a container with an editor of your choice while the source code will be compiled inside the awe-server container.

1. `source ./init.sh`
2. `export AWE_ROOT_DIR=`PATH_TO_LOCAL_AWE_REPOSITORY
3. `docker-compose -f Docker/Compose/skyport-awe-devel.yaml config`
4. `docker exec -ti compose_awe-server_1 ash`
5. Inside the container:
    1. `cd /go/src/github.com/MG-RAST/AWE`
    2. `go get -d ./awe-worker/ ./awe-server/`
    3. `./compile.sh`
