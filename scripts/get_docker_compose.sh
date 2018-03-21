#!/bin/bash
# from https://docs.docker.com/compose/install/#install-compose    2018-01-22
# will probably get stale pretty quick
echo "Attempting to install docker-compose-1.18.0 binary from github...."
sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose && sudo chmod ugo+x /usr/local/bin/docker-compose  && hash -r
