#!/bin/bash

#
# usage info
function usage () {
        echo "Usage: start-awe-worker.sh [-d ~/data] -s SKYPORT_HOST "
 }

 # get options
while getopts d:w:j:s: option; do
    case "${option}"
        in
                d) DATADIR=${OPTARG};;
                s) SKYPORT_HOST=${OPTARG};;
                *)
                usage
                ;;
    esac
done

# make sure the required options are present
if [ -z ${SKYPORT_HOST} ]
then
        usage
        exit 1
fi

# set the AWE_SERVER relative to the SKYPORT SERVER
AWE_SERVER=http://${SKYPORT_HOST}:8001/awe/api/

# ensure a local copy of the Skyport repo exists and docker and environment are ready
#git clone --recursive https://github.com/MG-RAST/Skyport2.git
#cd Skyport2
source ./get_docker_binary.sh

# there might be a better directory than this already set via an ENV variable
if [ -z ${DATADIR} ]
then
 export DATADIR=`pwd`/tmp
fi

mkdir -p ${DATADIR}

# define a somewhat unique name for the worker
hostn=`hostname`
WNAME=awe-worker-${hostn}

docker run \
  -d \
  --name ${WNAME}  \
  -v ${DATADIR}/awe-worker:${DATADIR}/awe-worker \
  -v ${DOCKER_BINARY}:/usr/local/bin/docker \
  -v /var/run/docker.sock:/var/run/docker.sock \
  mgrast/awe-worker:develop \
  /go/bin/awe-worker \
    --name external_worker-1 \
    --data=/awe-worker/ \
    --logs=/mnt/data/logs/ \
    --workpath=/awe-worker/work/ \
    --serverurl=${AWE_SERVER} \
    --group=docker \
    --supported_apps=* \
    --auto_clean_dir=false \
    --debuglevel=0
