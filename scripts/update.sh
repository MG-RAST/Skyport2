#!/bin/bash

# update the git submodules
if [ -d  .git ] ; then
  git pull
  git submodule update
fi


# pulling docker images
docker-compose pull
docker pull mgrast/awe-submitter:develop

