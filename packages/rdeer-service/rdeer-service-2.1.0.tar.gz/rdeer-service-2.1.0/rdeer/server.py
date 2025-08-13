#!/usr/bin/env python3

'''
rdeer-socket is the server part of rdeer-service.
It handle Reindeer running in socket mode.

at start up
- rdeer-server listening for the client
- An instance of Rdeer is created
    - launch a thread scanning the root directory of indexes and state of indexes
    - received clients requests

Starting a Reindeer socket
- When an index is started:
    - launch Reindeer query in waiting mode on specified port (default: 12800) using subprocess.Popen()
    - add info in a dictionnary dict['nom de l'index'] = {'status': 'loading', 'port': 'n°'}
    - wait the moment where index is loaded
    - when port is open, the index is declared 'running' and can be requested
        - update dictionnary entry dict['index name'] = {'status': 'running', 'port': 'n°'}

TODO LIST
 - find for removed indexes : if removed index is running (or loading), stop it !
 - Give a timeout to client queries, depending of the size, to avoid freezes
'''

import os
import sys
import argparse
import socket
import threading
import subprocess
import shutil
import time
from datetime import datetime
from functools import partial
import signal
import pickle
from packaging import version
import requests                 # send error message to ntfy.sh
import tempfile

import info
import common as stream


DEFAULT_PORT       = 12800
REINDEER           = 'reindeer_socket'
WATCHER_SLEEP_TIME = 10
BASE_TMPFILES      = '/tmp'
INDEX_FILES        = ["reindeer_matrix_eqc_info.txt", "reindeer_matrix_eqc_position", "reindeer_matrix_eqc"]
ALLOWED_TYPES      = ['list', 'start', 'stop', 'query', 'check', 'status', 'kill']  # REINDEER_SOCKET COMMANDS
timestamp          = lambda: datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
class RDSock_Mesg:                                                                  # MESSAGES RETURNED BY REINDEER
    HELP  = b' * HELP'
    INDEX = b'INDEX'
    QUERY = b'DONE'
    QUIT  = b"I'm leaving, see you next time !"
    STOP  = b'See you soon'


def main():
    args = usage()

    ### Localize full path or index directory (verify if rdeer-socket is a symlink)
    args.index_dir = os.path.join(os.getcwd(), args.index_dir.rstrip('/'))

    ### object rdeer manipulate indexes (list, start stop, query, check)
    rdeer = Rdeer(args)

    ### Stops running indexes on exit (Ctrl C, kill -15)
    exit_graceful = partial(exit_gracefully, rdeer=rdeer)
    signal.signal(signal.SIGINT, exit_graceful)
    signal.signal(signal.SIGTERM, exit_graceful)

    ### server listen for clients
    run_server(args, rdeer)


def run_server(args, rdeer):
    """ Launch rdeer-server in listening mode """
    port = args.port
    ### run server
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.bind(('', port))
    except OSError:
        sys.exit(f"Error: Address already in use (port: {port}).")
    conn.listen(10)
    ### timestamps server startup
    print(f"{timestamp()}: Server: {socket.gethostname()!r} listening on port {port}.", file=sys.stdout)

    while True:
        client, addr = conn.accept()
        ### run client query in a separated thread
        threading.Thread(target=handle_client, args=(client, addr, rdeer)).start()

    client.close()
    conn.close()


def handle_client(client, addr, rdeer):
    try:
        ### receive data stream. It won't accept data packet greater than 1024 bytes
        received = stream.recv_msg(client)
        received = pickle.loads(received)
        ### loggin request
        user = received.get('user') or 'unknown'
        if 'index' in received:
            print(f"{timestamp()} client:{addr[0]} type:{received['type']} user:{user} index:{received['index']}", file=sys.stdout)
        else:
            print(f"{timestamp()} client:{addr[0]} type:{received['type']} user:{user}", file=sys.stdout)
    except pickle.UnpicklingError:
        stream.send_msg(client, b"Error: data sent too big.")
        return
    except EOFError:
        stream.send_msg(client, b"Error: ran out of input")
        return
    except TypeError:
        data = "Error: no data to send to Reindeer (Maybe issue comes from client)."
        response = {'type': received['type'], 'status': 'error', 'data': data,}
        stream.send_msg(client, msg.encode())
        return response

    ### CHECK VERSION
    srv_vers = info.VERSION
    clt_vers = received.get('version') or 'unknown'
    if clt_vers=='unknown' or version.parse(clt_vers).major != version.parse(srv_vers).major:
        data = f"Error: server and client do not have the same major version (client: {clt_vers} - server: {srv_vers})."
        response = {'type': received['type'], 'status': 'error', 'data': data,}
        stream.send_msg(client, pickle.dumps(response))
        return response

    ### CALL RDEER METHOD MATCHING TO THE QUERY TYPE
    if received['type'] not in ALLOWED_TYPES:
        msg = f"Error: request type {received['type']!r} not handled. Please contact maintainer"
        response = {'type': received['type'], 'status': 'error', 'data': msg,}
        stream.send_msg(client, pickle.dumps(response))
        return response
    response = getattr(rdeer, received['type'])(received, addr)

    ## If Error message
    if response['status'] == 'Error':
        print(f"{response['status']}: {response['msg']}", file=sys.stderr, flush=True)
        stream.send_msg(client, pickle.dumps(response))

    ### Send response to client
    stream.send_msg(client, pickle.dumps(response))



class Rdeer:
    """ Class doc """

    def __init__(self, args):
        """ Class initialiser """

        self.index_dir = args.index_dir
        self.args = args
        ### controls if Reindeer found
        if not shutil.which(REINDEER):
            sys.exit(f"Error: {REINDEER!r} not found")

        ### watcher : loop to maintain index info, connect to index, check indexes
        self.indexes = {}               # states of all indexes
        self.procs = {}                 # reindeer indexes processus

        watcher = threading.Thread(target=self._watcher, name='watcher')
        watcher.daemon = True
        watcher.start()


    def _watcher(self):
        """ THE INDEX GUARDIAN """
        while True:

            ### Search for indexes
            index_found = []                                     # candidate indexes
            index_list = [index for index in self.indexes]       # list of current indexes

            ### Search for actual indexes
            for index in os.listdir(self.index_dir):
                subpath = os.path.join(self.index_dir, index)
                if os.path.isdir(subpath) and all([f in os.listdir(subpath) for f in INDEX_FILES ]):
                    index_found.append(index)

            ### add new indexes found in self.indexes dict
            for index in index_found:
                if not index in self.indexes:
                    self.indexes[index] = {'status':'available', 'port':None}
                    print(f"{timestamp()} index:{index} status:available", file=sys.stdout)

            ### find for removed indexes
            for index in index_list:
                if not index in index_found:
                    if self.indexes[index]['status'] != 'running':
                        msg = f"Error: {index!r} has been removed, but it still running"
                        print(f"{timestamp()} {msg}", file=sys.stdout)
                        if self.args.ntfy:
                            requests.post("https://ntfy.sh/bio2m-info", data=msg.encode())
                    self.indexes.pop(index)
                    print(f"{timestamp()} index:{index!r} status:removed", file=sys.stdout)

            time.sleep(WATCHER_SLEEP_TIME)


    def list(self, received, addr=None):
        response = {'type': received['type'], 'status': 'success', 'data': self.indexes}
        return response


    def start(self, received, addr=None):
        '''
        Start a Reindeer Index
        '''
        cmd_type = 'start'
        index = received['index']

        ### CHECK if index is in list and no still started/loading
        if not index in self.indexes:
            print(f"{timestamp()} Error: unable to start index {index} from {addr[0]} (not found).", file=sys.stdout)
            return {'type':cmd_type, 'status':'error', 'data':f'Index {index} not found.'}
        if self.indexes[index]['status'] in ['running', 'loading']:
            print(f"{timestamp()} Error: unable to start index {index} from {addr[0]} (still running or loading).", file=sys.stdout)
            return {'type':cmd_type, 'status':'error', 'data':f'index {index} still running or loading.'}
        ### PICK FREE PORT NUMBER
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()
        del(sock)

        ### EXECUTE REINDEER_SOCKET on the specified index
        cmd = f'{REINDEER} -l {os.path.join(self.args.index_dir, index)} -p {port} &'.split(' ')
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError:
            msg = f"Error: index {index} could not be loaded"
            return {'type': received['type'], 'status':'error', 'data': msg}

        ### CHANGE STATUS AND RETURN RESPONSE TO CLIENT
        print(f"{timestamp()} Index:{index} status:loading port:{port}", file=sys.stdout)
        self.indexes[index]['port'] = port
        self.procs[index] = proc
        self.indexes[index]['status'] = 'loading'
        data = self.indexes[index]

        ### WAIT FOR THE REINDEER INDEX TO BE STARTED TO CHANGE STATUS
        wait_run = threading.Thread(target=self._wait_run, args=(index,), name='wait')
        wait_run.start()

        return {'type': received['type'], 'status':'success', 'data': data}


    def stop(self, received, addr=None):
        cmd_type = 'stop'
        index = received['index']

        if index in self.indexes and self.indexes[index]['status'] == 'running':
            ### OPEN A SOCKET AND ASK REINDEER
            port = self.indexes[index]['port']
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('', port))
            ### Welcome message
            sock.recv(255).decode('utf8')
            ### shutdown the Reindeer index
            response = self._ask_index(sock, index, b'QUIT', RDSock_Mesg.QUIT)
            response = self._ask_index(sock, index, b'STOP', RDSock_Mesg.STOP)
            sock.close()

            if response['status'] == 'success':
                # ~ sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                self.indexes[index]['status'] = 'available'
                self.indexes[index]['port'] = None
                self.procs[index].kill()
                self.procs.pop(index)
                print(f'{timestamp()} Index:{index} status:available', file=sys.stdout)
                return {'type':cmd_type, 'status':'success','data':f"Index {index!r} sent: {response['data']!r}."}
            else:
                return {'type':cmd_type, 'status':'error','data':response['data']}
        else:
            msg = f"Unable to stop {index!r} (not found or not running)"
            print(f"{timestamp()} Error: {msg}", file=sys.stdout)
            return {'type':cmd_type, 'status':'error', 'data': msg}


    def check(self, received, addr=None):
        cmd_type = 'check'
        index = received['index']
        if index in self.indexes and self.indexes[index]['status'] == 'running':
            ### OPEN A SOCKET
            port = self.indexes[index]['port']
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.settimeout(1)
                sock.connect(('', port))
                ### Welcome message
                sock.recv(255).decode('utf8')
                ### ASK REINDEER
                response = self._ask_index(sock, index, b'INDEX', RDSock_Mesg.INDEX)
                data = os.path.dirname(response['data'].decode())
                ### CLOSE THE SOCKET
                sock.send(b'STOP')
                sock.recv(255).decode('utf8')
                ### RETURN
                if response['status'] == 'success':
                    return {'type':cmd_type, 'status':'success','data':data}
                else:
                    return {'type':cmd_type, 'status':'error','data':data}
            except Exception as err:
                msg = f"Unable to connect to {index!r} (msg: {err})"
                print(f"{timestamp()} Error: {msg}", file=sys.stdout)
                return {'type':'Error', 'status':'error', 'data':msg}
            finally:
                sock.close()
        else:
            msg = f"Unable to check {index!r} (not found or not running)"
            print(f"{timestamp()} Error: {msg}", file=sys.stdout)
            return {'type':cmd_type, 'status':'error','data': msg}


    def kill(self, received, addr=None):
        cmd_type = 'kill'
        index = received['index']
        if index not in self.indexes:
            return {'type':'kill', 'status':'error','data':f'Index {index!r} not found'}
        elif self.indexes[index]['status'] == 'available':
            return {'type':cmd_type, 'status':'error','data':f'Index {index!r} not started'}
        ### KILL THE PROCESS AND UPDATE INFO
        self.procs[index].kill()
        self.indexes[index] = {'status':'available', 'port':None}
        del self.procs[index]
        msg = f"Index {index!r} is now stopped"
        return {'type':cmd_type, 'status':'success','data':msg}


    def query(self, received, addr=None):
        cmd_type = 'query'
        index = received['index']

        ### INDEX MUST BE FOUND AND RUNNING
        if index not in self.indexes:
            return {'type':cmd_type, 'status':'error','data':f'Index {index!r} not found'}
        elif self.indexes[index]['status'] != 'running':
            return {'type':cmd_type, 'status':'error','data':f'Index {index!r} not running'}

        ### CREATE TMP FILES
        tmp_dir = tempfile.mkdtemp(prefix="rdeer-", dir=BASE_TMPFILES)
        infile = os.path.join(tmp_dir, 'query.fa')
        outfile = os.path.join(tmp_dir, 'reindeer.out')

        ### CREATE QUERY FASTA FILE AND BUILD QUERY
        with open(infile, 'w') as fh:
            fh.write(received['query'])
        threshold = f":THRESHOLD:{received['threshold']}" if received['threshold'] else ''
        mesg = f"FILE:{infile}{threshold}:OUTFILE:{outfile}:FORMAT:{received['format']}".encode()

        ### ASK REINDEER
        port = self.indexes[index]['port']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # ~ print("-----\nASK REINDEER FILE:", mesg)
        try:
            sock.settimeout(2)
            sock.connect(('', port))
            ### Welcome message
            W = sock.recv(255).decode('utf8')
            ### ASK REINDEER
            response = self._ask_index(sock, index, mesg, RDSock_Mesg.QUERY)
            data = os.path.dirname(response['data'])
            # ~ if isinstance(response['data'], bytes):
                # ~ data = data.decode()
                # ~ print("BYTE:", data)
            # ~ else:
                # ~ print("MSG TO REINDEER:", mesg)

        except socket.timeout:
            ### very special case : reindeer_socket create output file, but not responding to sock.recv()
            if os.path.isfile(outfile):
                response['status'] = 'success'
                # ~ print("!!! SPECIAL CASE !!!")
            else:
                msg = f"timeout exceeded querying {index!r}"
                print(f"{timestamp()} Error: {msg}", file=sys.stdout)
                return {'type':cmd_type, 'status':'error', 'data':msg}

        except Exception as err:
            msg = f"{cmd_type}: unable to connect to {index!r} (msg: {err})"
            print(f"{timestamp()} Error: {msg}", file=sys.stdout)
            return {'type':cmd_type, 'status':'error', 'data':msg}

        finally:
            ### CLOSE THE SOCKET
            sock.send(b'STOP')
            # ~ sock.recv(255).decode('utf8')
            sock.close()

        ### IF REINDEER RETURN ERROR
        if not response['status'] == 'success':
            shutil.rmtree(tmp_dir, ignore_errors=True)  # delete temp files
            if response['data'] == "Unknow message returned by Reindeer (b'').":
                self.indexes[index]['status'] = 'error'
            return {'type':cmd_type, 'status':'error', 'data':response['data']}

        ### REINDEER OUTFILE TO tsv
        outfile = os.path.join(os.path.dirname(infile), 'reindeer.out')
        try:
            with open(outfile) as fh:
                data = fh.read()
        except FileNotFoundError:
            time.sleep(.5)
            with open(outfile) as fh:
                data = fh.read()
        shutil.rmtree(tmp_dir, ignore_errors=True)  # delete tempory files
        ### RESPONSE TO CLIENT
        return {'type':cmd_type, 'status':response['status'], 'data':data}


    def _wait_run(self, index):
        time.sleep(0.1)
        port = self.indexes[index]['port']
        ### WHEN REINDEER INDEX IS RUNNING, CHANGE THE STATUS TO "RUNNING"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ### CONNECT TO REINDEER
        try:
            ### attempt connexion
            sock.connect(('', port))
            ### Welcome message
            sock.recv(255).decode('utf8')
            ### deconnection
            sock.send(b'STOP')
            sock.recv(255).decode('utf8')
            ### CHANGE STATUS
            self.indexes[index]['status'] = 'running'
            ### LOGGING
            print(f"{timestamp()} Index:{index} status:running port:{port}", file=sys.stdout)

        except ConnectionRefusedError:
            print(f"{timestamp()} Error: ConnectionRefusedError during connection to {index!r} on port {port}", file=sys.stdout)

        except ConnectionResetError:
            print(f"{timestamp()} Error: ConnectionResetError during loading of {index!r} on port {port}", file=sys.stdout)

        finally:
            sock.close()


    def _ask_index(self, sock, index, mesg, control):
        """ Send/recv to a Reindeer Index instance """
        # ~ print(f"MESG SENT TO REINDEER: {mesg} (index {index!r}).")
        if self.indexes[index]['status'] == 'running':
            try:
                sock.send(mesg)
                recv = sock.recv(1024)
            except:
                return {'status':'error','data':f'Unable to query the {index!r} index.'}
            if recv.startswith(control):
                return {'status':'success','data':recv}
            elif self._index_is_crashed(index):
                msg = f"the index {index!r} crashed during the request"
                print(f"{timestamp()} Error: {msg}", file=sys.stdout)
                return {'status':'error', 'data':msg}
            else:
                return {'status':'error','data':f'Unknow message returned by Reindeer ({recv!r}).'}
        else:
            return {'status':'error','data':f"Index not running (status: {self.indexes[index]['status']!r})"}


    def _index_is_crashed(self, index):
        ### check if Reindeer process running, otherwise, probably it is crashed
        port = self.indexes[index]['port']
        cmd = f'{REINDEER} -l {os.path.join(self.args.index_dir, index)} -p *{port}'
        proc = subprocess.run(f"ps -ef | grep '{cmd}'", shell=True, stdout=subprocess.PIPE)
        if proc.returncode:
            self.indexes[index]['status'] = 'error'
            if self.args.ntfy:
                msgerr = f"{socket.gethostname()}: rdeer-server: {index}: error status"
                requests.post("https://ntfy.sh/bio2m-info", data=msgerr.encode())
            return True
        return False


def exit_gracefully(signal, frame, rdeer):
    # I don't know why, but it's no longer necessary to stop running indexes (otherwise an exception will be raise)
    # ~ for index, values in rdeer.indexes.items():
        # ~ if values['status'] == 'running':
            # ~ getattr(rdeer, 'stop')({'index':index})
    print(f"\n{timestamp()}: server:rdeer-server interrupted by signal {signal}.", file=sys.stdout)
    sys.exit()


def usage():
    """
    Help function with argument parser.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("index_dir",
                        type=dir_path,
                        help="base directory of Reindeer indexes",
                        metavar=('index_dir'),
                       )
    parser.add_argument("-p", "--port",
                        help=f"port on which the server is listening (default: {DEFAULT_PORT})",
                        metavar="port",
                        default=DEFAULT_PORT,
                        type=int,
                       )
    parser.add_argument("-n", "--ntfy",
                        help=f"send error notifications to https://ntfy.sh/<your-location>",
                        metavar="ntfy location",
                       )
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f"{parser.prog} v{info.VERSION}",
                       )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    return parser.parse_args()


def dir_path(string):
    ### for usage(), test if argument is a directory)
    if os.path.isdir(string):
        return string
    else:
        sys.exit(f"NotADirectoryError ({string}).")


if __name__ == "__main__":
    main()
