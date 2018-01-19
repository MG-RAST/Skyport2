#!/bin/sh
# Skyport2 submit script
#
# submit a CWL workflow, a jobinput file and a data directory for processing


# example use:
#
# in a directory with
# PLEASE NOTE: all path info must be relative to DATADIR (in this case ./data)
# ./data/file1.txt
#       /file2.txt
#       /db/userdb.db
# jobinput.yaml
# workflow-simple.yaml

#skyport2_submit.sh \
        -d  ~/data \             [ set DATADIR]
        -j jobinput.yaml \
        -w workflow-simple.yaml


# usage info
function usage () {
        echo "Usage: skyport2.sh -d ~/data -j jobinput.yaml  -w workflow-simple.yaml "
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
if [[ -z ${SKYPORT_HOST}]]
then   
        # set to external host IP
        # Replace localhost with external host IP
        # SKYPORT_HOST= ....
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



