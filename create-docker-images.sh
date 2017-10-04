#! /bin/bash

# check if in correct dir


echo Building authServer image
docker build -t auth:${TAG} -f Docker/Dockerfiles/authServer.dockerfile .
 
echo Building shock-browser image 
docker build -t shock-browser:${TAG} -f Docker/Dockerfiles/shock-browser.dockerfile .