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
from subprocess import Popen, PIPE, STDOUT
sys.path.append("../..")
#import export
sys.path.pop()
sys.path.append("..")



api = Blueprint('api', __name__, template_folder='templates')

logger = logging.getLogger(__name__)

port = 80
api_url_internal = 'http://localhost'
api_url = 'http://submission-api'

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
    
    #status : submitted | error | complete ,
    #result : null |error-text |  status-id
    logger.info("__ api_submit()  node_id = {}".format(node_id))
    
    node_id = node_id.lower()
    
    # TODO: Create job input from node_id
    
    
    
    tmp_jobid = str(uuid.uuid4())
    tmp_dir = '/tmp/'+tmp_jobid
    os.makedirs(tmp_dir)
    
    cwl_dir = os.environ['CWL_DIR']
    
    
    info = {}
    info['CWL_DIR']=cwl_dir
    
    if not cwl_dir:
        return jsonify({
                'status': 'error',
                'result': 'CWL_DIR is not set',
        })
    
    
    
    
    
    command = "docker run" \
     ' --network skyport2_default' \
     ' --rm ' \
     ' -v %s:/CWL/' \
     ' --workdir=/CWL/Data/' \
     ' mgrast/awe-submitter:develop' \
     ' /go/bin/awe-submitter' \
     ' --pack' \
     ' --shockurl=http://shock:7445' \
     ' --serverurl=http://awe-server:8001' \
     ' --output=%s/results.cwl' \
     ' --wait' \
     ' /CWL/Workflows/simple-bioinformatic-example.cwl' \
     ' /CWL/Workflows/simple-bioinformatic-example.job.yaml'
 

    final_command = command % ( cwl_dir, tmp_dir)
    print("execute: "+ final_command)
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

    output_dir = '/tmp/'+jobid
    output_file = output_dir+'/results.cwl'

    if os.path.isfile(output_file):
        
        status = "complete"
        
    
        data = None
        with open(output_file, 'r') as myfile:
            data=myfile.read()
            
        result = str(data[:])# TODO  should be result = "shock_node_id_of_output" 
        return jsonify({
                'status': status,
                'result': result,
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

