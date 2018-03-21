#/bin/bash


if [[ $_ == $0 ]]; then 
  echo "Error: please use command \"source ./get_docker_binary.sh\""
  exit 1
fi


if [ -z "${SKYPORT_TMPDIR}" ]; then
  SKYPORT_TMPDIR="/tmp/"
fi

# target location
if [ -z "${DATADIR}" ]; then
  DATADIR=`pwd`
fi


export DOCKER_VERSION=$(docker --version | grep -o "[0-9]*\.[0-9]*\.[0-9a-z\.-]*")
export DOCKER_BINARY=${DATADIR}/docker-${DOCKER_VERSION}

mkdir -p ${DATADIR}
mkdir -p ${SKYPORT_TMPDIR}

if [ ! -e ${DOCKER_BINARY} ] ; then
  curl -fsSL -o ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz 
  if [ ! -e ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz ] ; then
    echo "download.docker.com did not work, try old location get.docker.com..."
    curl -fsSL -o ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz  https://get.docker.com/builds/Linux/x86_64/docker-${DOCKER_VERSION}.tgz
  fi
  
  if [ ! -e ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz ] ; then
    echo "docker binary not found"
    return 1
  fi
  
  tar -xvzf ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz -C ${SKYPORT_TMPDIR} docker/docker 
  mv ${SKYPORT_TMPDIR}/docker/docker ${DATADIR}/docker-${DOCKER_VERSION}
  rm -rf ${SKYPORT_TMPDIR}/docker
  
fi

echo "DOCKER_BINARY=${DOCKER_BINARY}"
