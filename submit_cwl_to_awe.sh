#!/bin/sh

# 
# simple AWE submitter

# example use:
#
# PLEASE NOTE: all path info must be relative to DATADIR (in this case ./data)

# ./data/file1.txt
#       /file2.txt
#       /db/userdb.db
# jobinput.yaml
# workflow-simple.yaml

#submit_cwl_to_awe.sh \
        -d  ~/data \             [ set DATADIR]
        -j jobinput.yaml \
        -w workflow-simple.yaml


# usage info
function usage () {
        echo "Usage: submit_cwl_to_awe.sh -d ~/data -j jobinput.yaml  -w workflow-simple.yaml [-s SKYPORT_HOST]"
	echo "if not -S <var> is provided, SKYPORT_HOST environment variable is used, if neither is present default is localhost"
 }

 # get options
while getopts d:w:j:s: option; do
    case "${option}"
        in
                w) WORKFLOW=${OPTARG};;
                j) JOBINPUT=${OPTARG};;
                d) DATADIR=${OPTARG};;
                s) SKYPORT_HOST=${OPTARG};; 
                *)
                usage
                ;;
    esac
done

# make sure the required options are present
if [[ -z ${WORKFLOW} ]]
then
        usage
        exit 1
fi
# make sure the required options are present
if [[ -z ${JOBINPUT} ]]
then
        usage
        exit 1
fi
# make sure the required options are present
if [[ -z ${DATADIR} ]]
then
        usage
        exit 1
fi

# we either used the ENVIRONMENT variable or the cmd-line parameter here with the standard unix order of precedence
if [[ -z ${SKYPORT_HOST}]]
then   
        # set to external host IP
        SKYPORT_HOST=$(/sbin/ip -o -4 addr list eth0 | awk '{print $4}' | cut -d/ -f1)	
fi

WORKFLOWDIR=dirname(${WORKFLOW})
JOBINPUTDIR=dirname(${JOBINPUT}) 

if [ -d ${DATADIR} ]
then
 echo "directory $DATADIR does not exist!"
 exit 1
fi



AWE_SERVER=http://${SKYPORT_HOST}:8001/awe/api/
SHOCK_SERVER=http://${SKYPORT_HOST}:8001/shock/api/

docker run -ti \
  --network compose_default \
  --rm \
  -v `pwd`/CWL/:/CWL/ \
  -v ${WORKFLOWDIR}:/mnt/workflows/ \
  -v ${JOBINPUTDIR}:/mnt/jobinputs/ \
  -v ${DATADIR}:/mnt/data/ \
  -- 1G \
  --workdir=${DATADIR} \
  mgrast/awe-submitter:develop \
  /go/bin/awe-submitter \
  --pack \
  --shockurl=${SHOCK_SERVER} \
  --serverurl=${AWE_SERVER} \
  ${WORKFLOW}



