

## Building docker images

By default Skyport2 uses docker images hostes on docker hub. You can use these instructions to build the required docker images yourself.



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

