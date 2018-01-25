#! /bin/bash

############################
# set environment variables
############################



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




# Top level data dir
export DATADIR=${REPO_DIR}/live-data
mkdir -p $DATADIR

# Path to config dir with service specific subdirs. Contains config for demo case
export CONFIGDIR=${REPO_DIR}/Config/
export DOCSDIR=${REPO_DIR}/Documents/
export CWL_DIR=${REPO_DIR}/CWL


export SKYPORT_TMPDIR=$DATADIR/tmp
mkdir -p ${SKYPORT_TMPDIR}


# Path to shock data and log dir
export SHOCKDIR=${DATADIR}/shock/
mkdir -p ${SHOCKDIR}/data
mkdir -p ${SHOCKDIR}/log

# Path to AWE
export AWEDIR=${DATADIR}/awe
mkdir -p ${DATADIR}/awe
mkdir -p ${DATADIR}/awe/db
mkdir -p ${DATADIR}/awe-worker/work






# Path to primary log dir
export LOGDIR=${DATADIR}/log/

# Create log dirs for Shock , nginx
mkdir -p ${LOGDIR}
mkdir -p ${LOGDIR}/shock
mkdir -p ${LOGDIR}/nginx
mkdir -p ${LOGDIR}/awe
mkdir -p ${LOGDIR}/awe-worker



# Docker image tag , used by Dockerfiles and Compose file
export TAG=demo

# Document files for the webserver
cp -f `pwd`/Documents/*.pdf ${CONFIGDIR}/nginx/

# pulling docker images
docker-compose pull
docker pull mgrast/awe-submitter:develop

# update the git submodules
if [ -d  .git ] ; then
  git submodule update
fi


source ./get_docker_binary.sh


echo Set config to:
echo "TAG=${TAG}"
echo "CONFIGDIR=${CONFIGDIR}"
echo "SHOCKDIR=${SHOCKDIR}"
echo "DATADIR=${DATADIR}"
echo "LOGDIR=${LOGDIR}"
echo "DOCKER_VERSION=${DOCKER_VERSION}"
echo "DOCKER_BINARY=${DOCKER_BINARY}"


echo ""
echo "Next step: docker-compose up"
echo ""
