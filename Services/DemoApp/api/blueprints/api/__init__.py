from flask import Blueprint
from flask import Response
from flask import request
from flask import jsonify
#from flask import stream_with_context
import uuid
import logging
import re
import sys
import os
import time
import subprocess
import psutil
import json

from flask import current_app

from subprocess import Popen, PIPE, STDOUT
sys.path.append("../..")
#import export
sys.path.pop()
sys.path.append("..")





#logger = logging.getLogger(__name__)
#logger.debug('logged from thread --------------------------------------- ')

api = Blueprint('api', __name__, template_folder='templates')

#logger = logging.getLogger(__name__)

port = 80
#api_url_internal = 'http://localhost'
#api_url = 'http://submission-api'

# modify /etc/hosts/: 127.0.0.1    localhost submission-api
STATUS_Bad_Request = 400  # A client error
STATUS_Unauthorized = 401
STATUS_Not_Found = 404
STATUS_Server_Error = 500


def execute_command(command, env):
    #global args
    
    print("execute command")
    
    if env:
        for key in env:
            #print("key: %s" % (key))
            search_string = "${"+key+"}"
            #if args.debug:
            #    print("search_string: %s" % (search_string))
            value = env[key]
            command = command.replace(search_string, value)
        
        #if args.debug:
        #   print("exec: %s" % (command), flush=True)
            
        process = subprocess.Popen(command, shell=True,  stdout=PIPE, stderr=STDOUT, close_fds=True, executable='/bin/bash', env=env)
    else:
        #if args.debug:
        print("exec: %s" % (command), flush=True)
        #print("no special environment")
        process = subprocess.Popen(command, shell=True,  stdout=PIPE, stderr=STDOUT, close_fds=True, executable='/bin/bash')
  
    last_line = ''
    while True:
        #print('loop')
        output = process.stdout.readline()
        rc = process.poll()
        if output == '' and process.poll() is not None:
            #print("Cond 1")
            break
        
        if output:
            last_line = output.decode("utf-8").rstrip()
            print(last_line)
        if rc==0:
            #print("Cond 2")
            break
       
    
    #if args.debug:
        #print(last_line)
        
    if process.returncode:
        raise MyException("Command failed (return code %d, command: %s): %s" % (process.returncode, command, last_line[0:500]))    
        
    return last_line


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code and status_code==STATUS_Server_Error:
            logger.warning(message)
        else:
            logger.debug(message)
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@api.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api.route('/submit/<node_id>')
def api_submit(node_id):
    #current_app.logger.info('submit ---------------------------------------')
    logger=current_app.logger
    #status : submitted | error | complete ,
    #result : null |error-text |  status-id
    logger.info("__ api_submit()  node_id = {}".format(node_id))
    
    node_id = node_id.lower()
    
    shock_server_url = None
    if 'SHOCK_SERVER_URL' in os.environ:
        shock_server_url = os.environ['SHOCK_SERVER_URL']
    
    if not shock_server_url:
        shock_server_url = 'http://shock:7445'
    
    logger.info("shock_server_url={}".format(shock_server_url))
    
    awe_server_url = None
    if 'AWE_SERVER_URL' in os.environ:
        awe_server_url = os.environ['AWE_SERVER_URL']
    
    if not awe_server_url:
        awe_server_url = 'http://awe-server:8001'
    
    logger.info("awe_server_url={}".format(awe_server_url))
    
    job_file_content_template = """pdf:
  class: File 
  location: '{}/node/{}?download'""" 

    job_file_content  = job_file_content_template .format(shock_server_url, node_id)
# basename: demo.pdf if required
    
    
    tmp_jobid = str(uuid.uuid4())
    tmp_dir = '/host_tmp/'+tmp_jobid
    os.makedirs(tmp_dir)
    
    
    job_file = tmp_dir + '/input.yaml'
    
    
    logger.debug("writing file {}".format(job_file))
    
    with open(job_file, "w") as text_file:
        text_file.write(job_file_content)
    
    cwl_dir = None
    if 'CWL_DIR' in os.environ:
        cwl_dir = os.environ['CWL_DIR']
   
    
    if not cwl_dir:
        return jsonify({
                'status': 'error',
                'result': 'CWL_DIR is not set',
        })
    
    info = {}
    info['CWL_DIR']=cwl_dir
    
    
    
    command = "docker run" \
     ' --network skyport2_default' \
     ' --rm ' \
     ' -v %s:/CWL/' \
     ' -v /tmp/:/host_tmp/' \
     ' --workdir=/CWL/Data/' \
     ' mgrast/awe-submitter:develop' \
     ' /go/bin/awe-submitter' \
     ' --pack' \
     ' --shockurl=%s '\
     ' --serverurl=%s ' \
     ' --output=%s/results.cwl' \
     ' --wait' \
     ' /CWL/Workflows/pdf2wordcloud.cwl' \
     ' %s/input.yaml'
 
    time.sleep(2)
    final_command = command % ( cwl_dir, shock_server_url, awe_server_url, tmp_dir, tmp_dir)
    logger.debug("execute: {}".format( final_command))
    popen_object = subprocess.Popen(final_command, shell=True)
    
    
    the_pid = popen_object.pid
    
    time.sleep(5) # wait 5 seconds and check if process is still running
    
    p = psutil.Process(the_pid)
    status = p.status()
    if status != psutil.STATUS_RUNNING and status != psutil.STATUS_SLEEPING:
        status = "error"
        result = "awe-submitter container or process died ("+status+")"
    
    
        return jsonify({
                'info' : info,
                'status': status,
                'result': result,
        })
    
    #try:
    #    execute_command(command, None)
    #except Exception as e:
    #    status = "error"
    #    result = str(e)
    #    return jsonify({
    #            'status': status,
    #            'result': result,
    #    })
    
    status = "submitted"
    result = tmp_jobid
    
    
    return jsonify({
            'status': status,
            'result': result,
    })



@api.route('/status/<jobid>')
def api_status(jobid):
    
    
    #status : running | error | complete ,
    #result : null | error-text | node-id

    output_dir = '/host_tmp/'+jobid
    output_file = output_dir+'/results.cwl'


    
    
    

    if os.path.isfile(output_file):
        
        with open(output_file, 'r') as myfile:
            data=myfile.read()
    

        try:
            parsed_json = json.loads(data)
        except Exception as e:
            return jsonify({
                    'status': 'error',
                    'result': "could not parse json: "+str(e),
            })
    
    
        wordCloudImage= None
        if 'wordCloudImage' in parsed_json:
            wordCloudImage = parsed_json['wordCloudImage']
        else:
            return jsonify({
                    'status': 'error',
                    'result': "wordCloudImage not found in json",
            })
    
        location = None
        if 'location' in wordCloudImage:
            location = wordCloudImage['location']
        else:
            return jsonify({
                    'status': 'error',
                    'result': "wordCloudImage/location not found in json",
            })
    
        if location.endswith('?download'):
            location = location[:-9]
    
        node_id = location[-36:]
    
        return jsonify({
                'status': 'complete',
                'result': node_id,
        })
        
    if os.path.exists(output_dir):
        
        status = "running"
    
        return jsonify({
                'status': status
        })
        
        

    status = "error"
    result = "job not found"
    
    return jsonify({
            'status': status,
            'result': result,
    })


@api.route('/testing')
def api_testing():
    return 'this is a test'


@api.route('/')
def api_root():
    return 'This is the Skyport submission server.\n'

