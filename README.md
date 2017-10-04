# App-Service-Stack ![ass logo][logo]
 Infrastructure setup for app/service development using MYSQL, MongoDB, Auth , Shock and AWE ([M]ASA).





[logo]: https://github.com/wilke/App-Service-Stack/blob/master/data/pictures/donkey.jpg "Donkey aka ass"



## Building docker images

All builds start within the root directory within this repository.

Set build tag to demo:

export TAG=demo

### ShockBrowser

 - docker build -t shock-browser:${TAG} -f Docker/Dockerfiles/shock-browser.dockerfile .
 
 
## Starting services
 
 Check config:
 docker-compose -f Docker/Compose/ass.yaml config
 
 Start services:
 docker-compose -f Docker/Compose/ass.yaml up 

