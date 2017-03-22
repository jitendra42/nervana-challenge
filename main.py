"""
Details the various flask endpoints for processing and retrieving
command details as well as a swagger spec endpoint
"""

from multiprocessing import Process, Queue
import sys
from flask import Flask, request, jsonify, Response
from flask_swagger import swagger
from db import Session, engine
from base import Base, Command
from command_parser import get_valid_commands, process_command_output
import os.path

app = Flask(__name__)

@app.route('/', methods=['GET'])
def server_root():
    return "Welcome to nervana coding challenge"

@app.route('/commands', methods=['GET'])
def get_command_output():
    """
    Returns as json the command details that have been processed
    ---
    tags: [commands]
    responses:
      200:
        description: Commands returned OK
      400:
        description: Commands not found
    """
    try:

        commands = Session().query(Command).all()
        query_result_list = [cmd.to_json() for cmd in commands]
    except Exception as e:
        return "Commands not found", 400
    return jsonify(query_result_list)


@app.route('/commands', methods=['POST'])
def process_commands():
    """
    Processes commmands from a command list
    ---
    tags: [commands]
    parameters:
      - name: filename
        in: formData
        description: filename of the commands text file to parse
                     which exists on the server
        required: true
        type: string
    responses:
      200:
        description: Processing OK
    """
    fi = request.args.get('filename')
    file_data = request.args.get('file_data')
    queue = Queue()
    if file_data:
        get_valid_commands(queue, file_data=file_data)
    else:
        #Check if filename exists on the server else return 400
        if not os.path.isfile(fi):
            return "Command file '{0}'  do not exists on server, Please provide correct file name".format(fi), 400
        get_valid_commands(queue, fi=fi)
    
    processes = [Process(target=process_command_output, args=(queue,))
                 for num in range(queue.qsize())]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    return 'Successfully processed commands.'


@app.route('/database', methods=['POST'])
def make_db():
    """
    Creates database schema
    ---
    tags: [db]
    responses:
      200:
        description: DB Creation OK
    """
    Base.metadata.create_all(engine)
    return 'Database creation successful.'


@app.route('/database', methods=['DELETE'])
def drop_db():
    """
    Drops all db tables
    ---
    tags: [db]
    responses:
      200:
        description: DB table drop OK
    """
    Base.metadata.drop_all(engine)
    return 'Database deletion successful.'

@app.route('/spec', methods=['GET'])
def swagger_spec():
    """
    Display the swagger formatted JSON API specification.
    ---
    tags: [docs]
    responses:
      200:
        description: OK status
    """
    spec = swagger(app)
    spec['info']['title'] = "Nervana cloud challenge API"
    spec['info']['description'] = ("Nervana's cloud challenge " +
                                   "for interns and full-time hires")
    spec['info']['license'] = {
        "name": "Nervana Proprietary License",
        "url": "http://www.nervanasys.com",
    }
    spec['info']['contact'] = {
        "name": "Nervana Systems",
        "url": "http://www.nervanasys.com",
        "email": "info@nervanasys.com",
    }
    spec['schemes'] = ['http']
    spec['tags'] = [
        {"name": "db", "description": "database actions (create, delete)"},
        {"name": "commands", "description": "process and retrieve commands"}
    ]
    return jsonify(spec)

@app.errorhandler(Exception)
def unhandled_exception(e):
    response = Response("Internal server error: {0}".format(str(e)), content_type='text/plain')
    response.status_code = 500
    return response

if __name__ == '__main__':
    """
    Starts up the flask server
    """
    port = 8080
    use_reloader = True

    # provides some configurable options
    for arg in sys.argv[1:]:
        if '--port' in arg:
            port = int(arg.split('=')[1])
        elif '--use_reloader' in arg:
            use_reloader = arg.split('=')[1] == 'true'

    app.run(port=port, debug=True, use_reloader=use_reloader)


