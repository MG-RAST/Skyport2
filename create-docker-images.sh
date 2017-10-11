#! /bin/bash

# check if in correct dir


echo Building authServer image
docker build -t mgrast/authserver:${TAG} -f Docker/Dockerfiles/authServer.dockerfile .
 
echo Building shock-browser image 
docker build -t mgrast/shock-browser:${TAG} -f Docker/Dockerfiles/shock-browser.dockerfile .
