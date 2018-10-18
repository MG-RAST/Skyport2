
Skyport2
========


![skyport logo](data/pictures/skyportlogo.small.jpg) 

Skyport2 is a RESTful framework for large scale data management and reproducible multi-cloud workflow execution. 

Scientists and engineers are accustomed to using a different computer systems to accomplish scientific workflow execution. Skyport2 handles data management and execution of CWL workflows across. Data is stored in the RESTful SHOCK object store that handles indexing, subsetting and format conversions. SHOCK is programmable and can be customized to perform additional functions e.g. convert image formats. AWE worker nodes connect to the AWE resource manager and check execute workflows described in the common workflow language. 


## Quick start

# Install docker 

Install docker, see Docker website for platform specific instructions:

https://www.docker.com/get-docker


E.g. on a recent ubuntu version you can install docker with this command:

```bash
sudo apt-get update && sudo apt-get -y install docker.io
```

Linux: Add user to docker group
```bash
sudo groupadd docker
sudo gpasswd -a $USER docker
newgrp docker
```

# Install docker-compose

Install docker-compose (note that the docker-compose version in the ubuntu repository might be too old) 


https://docs.docker.com/compose/install/

For ubuntu:

```bash
sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose 
```

Note that with a newer version of docker you might need a newer version of docker-compose. (Note to self: Find mechanism to determine correct version) 

# Install Skyport2

Clone the Skyport repository:

```bash
git clone https://github.com/MG-RAST/Skyport2.git
cd Skyport2
```


```bash
sudo ./scripts/add_etc_hosts_entry.sh
source ./init.sh
docker-compose up
```

Open Skyport in your browser:

http://localhost:8001


## IP detection failed ?

This skyport deployment need to detect your IP address. If this fails, you can set the IP address manually:

```bash
export USE_SKYPORT_HOST=<your-ip-address>
source ./init.sh
```


You can execute ```ifconfig -a``` to find your ip address. Do not forget to source ```init.sh```.




## Updates


To get the latest code and docker images you can run the ```update.sh``` script.

```
source ./init.sh
./scripts/update.sh
```


## Finding services

If you need a listing of all skyport services run ```skyport2-overview.sh```: 


```bash
> ./skyport2-overview.sh 

------- Skyport2 -----------------------------
Skyport2 main URL: http://130.202.135.80:8001

AWE monitor:       http://130.202.135.80:8001/awe/api/

AWE server API:    http://130.202.135.80:8001/awe/api/
Shock server API:  http://130.202.135.80:8001/shock/api/

Auth server:       http://130.202.135.80:8001/auth/

----------------------------------------------
```

You can also use ```skyport2.env``` to see the full configuration (i.e. URLs) via environment variables:

```bash
> cat skyport2.env

export TAG=demo
export CONFIGDIR=/Users/wolfganggerlach/git/Skyport2/Config/
export SHOCKDIR=/Users/wolfganggerlach/git/Skyport2/live-data/shock/
export DATADIR=/Users/wolfganggerlach/git/Skyport2/live-data
export LOGDIR=/Users/wolfganggerlach/git/Skyport2/live-data/log/

export SKYPORT_HOST=130.202.135.80
export NGINX_PORT=8001
export SKYPORT_URL=http://130.202.135.80:8001
export AWE_SERVER_URL=http://130.202.135.80:8001/awe/api/
export SHOCK_SERVER_URL=http://130.202.135.80:8001/shock/api/
export AUTH_URL=http://130.202.135.80:8001/auth/

export SKYPORT_DOCKER_GATEWAY=172.18.0.1
export DOCKER_VERSION=17.12.0-ce
export DOCKER_BINARY=/Users/wolfganggerlach/git/Skyport2/live-data/docker-17.12.0-ce
```

and you can source this file to update your environment variables:
```bash
source skyport2.env 
```




### Skyport2 development

The AWE development environment is the basic skyport app service stack whith persistent (mounted) database storage and mounted AWE source repository. Coding can be done outside a container with an editor of your choice while the source code will be compiled inside the awe-server container.

1. `source ./init.sh`
2. `export AWE_ROOT_DIR=`PATH_TO_LOCAL_AWE_REPOSITORY
3. `docker-compose -f Docker/Compose/skyport-awe-devel.yaml config`
4. `docker exec -ti compose_awe-server_1 ash`
5. Inside the container:
    1. `cd /go/src/github.com/MG-RAST/AWE`
    2. `go get -d ./awe-worker/ ./awe-server/`
    3. `./compile.sh`
