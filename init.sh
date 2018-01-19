#! /bin/bash

############################
# set environment variables
############################



if [[ $_ == $0 ]]; then 
  echo "Error: please use command \"source ./init.sh\""
  exit 1
fi
  


# Top level data dir
export DATADIR=`pwd`/live-data
mkdir -p $DATADIR

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
export LOGDIR=`pwd`/data/log/

# Create log dirs for Shock , nginx
mkdir -p ${LOGDIR}
mkdir -p ${LOGDIR}/shock
mkdir -p ${LOGDIR}/nginx
mkdir -p ${LOGDIR}/awe
mkdir -p ${LOGDIR}/awe-worker

# Path to config dir with service specific subdirs. Contains config for demo case
export CONFIGDIR=`pwd`/Config/

# Docker image tag , used by Dockerfiles and Compose file 
export TAG=demo



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
echo "Next step: docker-compose -f Docker/Compose/skyport-demo.yaml up"
echo ""
