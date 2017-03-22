"""
Handles the work of validating and processing command input.
"""
from subprocess import Popen
from subprocess import CalledProcessError
from base import Command
import ConfigParser
from db import Session
import subprocess
import time
import os
import signal
import io


def get_valid_commands(queue, file_data=None, fi=None):
    # TODO: efficiently evaluate commands
    if not file_data and not fi:
        return

    cp = ConfigParser.ConfigParser(allow_no_value=True)
    if file_data:
        cp.readfp(io.StringIO(file_data))
    else:
        cp.read(fi)

    #ConfigeParser removes duplicates. As code challenge mentioned, 
    #we can assume we do not need to store output of the same command.
    # TODO: Following solution will be good enough with small command list, but may not be faster for large list
    #       #1 possibly build trie tree for both COMMAND_LIST and VALID_LIST to searching. 
    #       #2 investigate if Ternary Search Tree better option https://pypi.python.org/pypi/pytst/
    cmd_list = cp.options("COMMAND LIST") 
    valid_cmds = cp.options("VALID COMMANDS")
    for cmd in cmd_list:
        if cmd in valid_cmds:
            queue.put(cmd)
    

def process_command_output(queue):
    # TODO: run the command and put its data in the db
    command = queue.get()
    start_time = time.time()
    try:
        proc = Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        longer_exec_command = False
        #For longer running commands 
        while proc.poll() is None:
            exec_time = time.time() - start_time
            if exec_time > 60:
                #kill the command execution
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                longer_exec_command = True
        stdout, stderr = proc.communicate()
        
        duration = 0 if longer_exec_command else time.time() - start_time
        length = len(command)
        output = stdout if not stderr else stderr
        
        cmd_metadata = Command(command, length, duration, output)
        dbsession = Session()
        dbsession.add(cmd_metadata)
        dbsession.commit()
    except Exception as e:
        raise Exception("DB insertion failed...")
