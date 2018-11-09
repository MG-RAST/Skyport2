#! /bin/bash

############################
# set environment variables
############################


export NGINX_PORT=8001
export SKYPORT_NETWORK_NAME="skyport2_default"



if [[ $_ == $0 ]]; then
  echo "Error: please use command \"source ./init.sh\""
  exit 1
fi

docker -v  > /dev/null
if [[ $? -ne 0 ]]; then
  echo "docker is missing.  Follow instructions at https://docs.docker.com/compose/install/ to install"
  return 1
fi
docker-compose -v  > /dev/null
if [[ $? -ne 0 ]]; then
  echo "docker-compose is missing or not configured.  Follow instructions at https://docs.docker.com/compose/install/ to install"
  return 1
fi

if [[ "$(docker-compose -v)" == "docker-compose version 1.8.0"* ]] ; then
  echo "Version of docker-compose is out of date, follow instructions at https://docs.docker.com/compose/install/"
  echo "Note: the default ubuntu repositories will not help you here."
  return 1
fi



export REPO_DIR=`pwd`

if [ $(basename `pwd`) != "Skyport2" ] ; then
  echo "Please run \"source ./init.sh\" inside the Skyport2 repository directory"
  return
fi


source ./scripts/init-directories.sh



if [ $(cat /etc/hosts | grep "skyport" | wc -l) -eq 0 ] ; then
  echo ""
  echo "skyport entry in your /etc/hosts file is missing. Please execute:"
  echo "> sudo ./scripts/add_etc_hosts_entry.sh"
  echo ""
  echo "Afterwards execute \"source ./init.sh\" again."
  return 1
fi



# we create this docker network to get its IP address
if [ $(docker network list --filter name=${SKYPORT_NETWORK_NAME} -q | wc -l ) -eq 0 ] ; then
    docker network create ${SKYPORT_NETWORK_NAME}
fi


export SKYPORT_DOCKER_GATEWAY=$(docker network inspect ${SKYPORT_NETWORK_NAME} -f '{{(index .IPAM.Config 0).Gateway}}')


# Docker image tag , used by Dockerfiles and Compose file
export TAG=demo


source ./scripts/get_docker_binary.sh

# This script van be used to determine the IP address
#source ./scripts/get_ip_address.sh
#if [ $? -ne 0 ] ; then
#  return 1
#fi  

export SKYPORT_HOST="skyport.local"  # The suffix .local is needed as some older go libraries e.g. as used in the awe-worker cannot handle a domain names without suffix


export SKYPORT_URL=http://${SKYPORT_HOST}:${NGINX_PORT}
export AWE_SERVER_URL=${SKYPORT_URL}/awe/api/
export SHOCK_SERVER_URL=${SKYPORT_URL}/shock/api/
export AUTH_URL=${SKYPORT_URL}/auth/

export AWE_SERVER_URL_INTERNAL=${SKYPORT_DOCKER_GATEWAY}/awe/api/



# create variuos config files from templates

#awe-monitor
sed -e "s;\${AWE_SERVER_URL};${AWE_SERVER_URL};g" -e "s;\${AUTH_URL};${AUTH_URL};g" ${CONFIGDIR}/awe-monitor/config.js_template > ${CONFIGDIR}/awe-monitor/config.js


#ShockBrowser
sed -e "s;\${AWE_SERVER_URL};${AWE_SERVER_URL};g" -e "s;\${SHOCK_SERVER_URL};${SHOCK_SERVER_URL};g" -e "s;\${AUTH_URL};${AUTH_URL};g" ${CONFIGDIR}/ShockBrowser/config.js_template > ${CONFIGDIR}/ShockBrowser/config.js


#AWE server
sed -e "s;\${AWE_SERVER_URL};${AWE_SERVER_URL};g" -e "s;\${AUTH_URL};${AUTH_URL};g" -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" ${CONFIGDIR}/AWE/awe-server.conf_template  > ${CONFIGDIR}/AWE/awe-server.conf

# AWE worker
sed  -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" ${CONFIGDIR}/AWE/awe-worker.cfg_template  > ${CONFIGDIR}/AWE/awe-worker.cfg

# auth
sed -e "s;\${SKYPORT_HOST};${SKYPORT_HOST};g"  Config/authServer/httpd.conf_template > Config/authServer/httpd.conf

sed -e "s;\${AUTH_URL};${AUTH_URL};g" -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" Config/authServer/cgi/ClientConfigShock.pm_template > Config/authServer/cgi/ClientConfigShock.pm

sed -e "s;\${AUTH_URL};${AUTH_URL};g" -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" Config/authServer/cgi/ClientConfigDemoApp.pm_template > Config/authServer/cgi/ClientConfigDemoApp.pm

sed -e "s;\${AUTH_URL};${AUTH_URL};g" -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" Config/authServer/cgi/ClientConfigSkyport.pm_template > Config/authServer/cgi/ClientConfigSkyport.pm

sed -e "s;\${AUTH_URL};${AUTH_URL};g" Config/authServer/cgi/OAuthConfig.pm_template > Config/authServer/cgi/OAuthConfig.pm

sed -e "s;\${AUTH_URL};${AUTH_URL};g" Config/authServer/dbsetup.demo.mysql_template > Config/authServer/dbsetup.demo.mysql


#DemoApp
sed -e "s;\${AUTH_URL};${AUTH_URL};g" -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" -e "s;\${SHOCK_SERVER_URL};${SHOCK_SERVER_URL};g" Config/DemoApp/index.html_template > Config/DemoApp/index.html

sed -e "s;\${AUTH_URL};${AUTH_URL};g" -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" -e "s;\${SHOCK_SERVER_URL};${SHOCK_SERVER_URL};g" Config/DemoApp/config.js_template > Config/DemoApp/config.js

#nginx
sed -e "s;\${AUTH_URL};${AUTH_URL};g" -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" Config/nginx/index.html_template > Config/nginx/index.html

sed -e "s;\${AUTH_URL};${AUTH_URL};g" -e "s;\${SKYPORT_URL};${SKYPORT_URL};g" -e "s;\${SHOCK_SERVER_URL};${SHOCK_SERVER_URL};g" -e "s;\${AWE_SERVER_URL};${AWE_SERVER_URL};g" Config/nginx/services.html_template > Config/nginx/services.html



cat <<EOF > skyport2.env

export TAG=${TAG}
export CONFIGDIR=${CONFIGDIR}
export SHOCKDIR=${SHOCKDIR}
export DATADIR=${DATADIR}
export LOGDIR=${LOGDIR}

export SKYPORT_HOST=${SKYPORT_HOST}
export NGINX_PORT=${NGINX_PORT}
export SKYPORT_URL=${SKYPORT_URL}
export AWE_SERVER_URL=${AWE_SERVER_URL}
export SHOCK_SERVER_URL=${SHOCK_SERVER_URL}
export AUTH_URL=${AUTH_URL}

export SKYPORT_DOCKER_GATEWAY=${SKYPORT_DOCKER_GATEWAY}
export DOCKER_VERSION=${DOCKER_VERSION}
export DOCKER_BINARY=${DOCKER_BINARY}
EOF

cat skyport2.env

# this directory can be mounted by other containers
mkdir -p ${DATADIR}/env/
cp skyport2.env ${DATADIR}/env/


echo "skyport2.env has been written"

echo ""


echo ""
echo ""
echo "Next step: docker-compose up"
echo ""
echo "...then open http://localhost:${NGINX_PORT} (or ${SKYPORT_URL}) in your browser."
echo ""

