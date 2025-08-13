#!/usr/bin/env python3

import sys
import os
import argparse
import socket
import pickle

import info
import common as stream


def main():
    """ Function doc """
    args = usage()
    # ~ print(f"SENT to {args.server}:{vars(args)}")
    received = ask_server(vars(args))
    # ~ print(f"RECEIVED from {args.server}: {received}")

    ### SPECIAL CASE, RDEER SERVER IS in v1 VERSION
    if isinstance(received['data'], str) and received['data'].startswith('Error: server and client do not have the same major version'):
        ### CHANGE ARGS TO SIMULATE VERSION 1
        args.version = "1.0.0"
        ### IF type == 'query', NEED TO MODIFY ARGS
        if args.type == "query":
            args.normalize = False
            match args.format:
                case "raw":
                    args.unitig_counts = True
                case "sum":
                    exit_on_version_error("--type sum")
                case "normalize":
                    args.normalize = True
                case "average" | "mean":
                    pass
        ### STATUS and KILL argument are new in v2
        if args.type == "status" or args.type == "kill":
            exit_on_version_error(args.type)

        ### ASK_SERVER AGAIN, BUT WITH v1 ARGS STYLE
        received = ask_server(vars(args))

    client = Client(args, received)
    client.handle_recv()


def exit_on_version_error(err_opt):
    sys.exit(f"Error: rdeer-server not handle the {err_opt!r} option.\n"
             f"       Maybee you could upgrade rdeer-server to version {info.VERSION} or higher.\n"
              "       (don't forget to reload the indexes)")


def ask_server(args):
    """
    args must be a dict(), containing:
        - 'server': the name or IP of rdeer-socket
        - 'port': the TCP port on which rdeer-socket listen
        - 'type' could be 'list', 'start', 'stop', 'query', 'check, 'status'
        - 'index' name of the index (mandatory when 'type' is 'start', 'stop', 'query', 'check')
        - 'query' path/file of a fasta file (mandatory when 'type' is 'query')
    """
    server = args['server']
    port = args['port']
    received = None
    ### CONNECTION TO SERVER RDEER
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.settimeout(4)
        conn.connect((server, port))    # Connect to server
        conn.settimeout(None)
    except socket.timeout:
        received = {
                    'type': args['type'], 'status' : 'error',
                    'data': (f"ErrorConnection: unable to connect to {server} on port {port}"
                            " (server not responding on this port)."),
                    }
        return received
    except socket.gaierror:
        received = {
                    'type': args['type'], 'status' : 'error',
                    'data': f"ErrorConnection: unable to connect to {server} on port {port} (might a name resolution issue).",
                    }
        return received
    except ConnectionRefusedError:
        received = {
                    'type': args['type'], 'status' : 'error',
                    'data': f"Error: unable to connect to {server!r} on port {port}.",
                    }
        return received
    except Exception:
        a,b,c = sys.exc_info()
        received = {
                    'type': args['type'], 'status' : 'error',
                    'data': f"{a.__name__}: {b} (at line {c.tb_lineno})",
                    }
        return received
    ### REQUEST TO SERVER RDEER
    if args['type'] == 'query':
        ### when rdeer-client is used as a program, query is a IO string
        if hasattr(args['query'], 'read'):
            args['query'] = args['query'].read()
        ### query empty
        if not args['query']:
            received = {
                    'type': args['type'],
                    'status' : 'error',
                    'data': "query is empty.",
                    }
            return received
    ### send to rdeer-server, using lib/rdeer_common library
    to_send = pickle.dumps(args)
    stream.send_msg(conn, to_send)


    ### received from rdeer-server
    received = stream.recv_msg(conn)
    received = pickle.loads(received)

    ### close connexion
    conn.close()

    ### some controls
    check_data(received)

    return received


def check_data(received):
    """ Control some stuff """
    ### Sometimes, rdeer-server send only header (because problem with index)
    if received['type'] == 'query':
        data = received['data']
        ## if rdeer-server return only header
        n = data.find('\n')
        if len(data) <= n+2:
            received['status'] = 'error'
            received['data'] = {
                                "rdeer found the index but only header was returned (no counts)."
                                "Try again and contact the administrator if the issue still occurs."
                                }


class Client:

    def __init__(self, args, received):
        """ Function doc """
        self.args = args
        self.received = received

    def handle_recv(self):
        """ Function doc """
        received = self.received
        ### Depending on the request to the server and its response, handle received data
        if received['status'] == 'success':
            try:
                getattr(self, received['type'])()
            except KeyError:
                sys.exit(f"{color.RED}Error: unknown type {received['type']!r}.")
        else:
            try:
                getattr(self, received['status'])()
            except KeyError:
                sys.exit(f"{color.RED}Error: unknown status {received['status']!r}.")


    def list(self):
        """Return the list of indexes"""
        if not self.received['data']:
            sys.exit(f"{color.CYAN}Warning: no index found by rdeer-server.")
        if self.args.all:
            LOADCOL  = "\033[1m\033[5;36m"    # blinking and bold cyan
            RUNCOL   ='\033[1;32m'            # green
            AVAILCOL = '\033[1;34m'           # blue
            ERRORCOL = '\033[1;31m'           # red
            color_status = { 'available': AVAILCOL, 'running' : RUNCOL, 'loading': LOADCOL, 'error': ERRORCOL }
            gap = max([len(index) for index in self.received['data']])
            print('\n'.join([ f"{k.ljust(gap)}  [{color_status[v['status']]}{v['status'].center(9)}{color.END}]" for k,v in sorted(self.received['data'].items(), key=lambda v: (v[0].casefold()))]))
        else:
            print('\n'.join([k for k,v in sorted(self.received['data'].items()) if v['status'] == 'running']))


    def status(self):
        print(self.received['data'])


    def start(self):
        print(f"{self.args.index} is now {self.received['data']['status']}")


    def stop(self):
        print(self.received['data'])


    def check(self):
        print(self.received['data'])


    def query(self):
        """ If output file is not specified, print to stdout """
        ### IF --ADD-SEQ IS SET
        if self.args.add_seq:
            self.__add_seq__()
        if not self.args.outfile:
            print(self.received['data'], end='')
        else:
            try:
                with open(self.args.outfile, 'w') as fh:
                    fh.write(self.received['data'])
            except FileNotFoundError:
                sys.exit(f"{color.RED}Error: no such directory {os.path.dirname(self.args.outfile)!r}{color.END}.")
            print(f"{self.args.outfile!r} created succesfully.")


    def kill(self):
        print(self.received['data'])


    def error(self):
        """ Function doc """
        print(self.received['data'])


    def __add_seq__(self):
        """when --add-seq arg is specified, add sequences as second column"""
        ### QUERY AS DICT
        query = {}
        query_fa = [row for row in self.args.query.split('\n') if row]
        seq = ''
        header = query_fa[0].split(' ')[0][1:]
        for line in query_fa[1:]:
            if line.startswith(">"):
                query[header] = seq[:self.args.add_seq]
                header = line.split(' ')[0][1:]
                if header in query:
                    print(f"{color.PURPLE}Warning: {header!r} is duplicated, the '-a/--add-seq' argument cannot be use.{color.END}")
                    return
                seq = ''
            else:
                seq += line.rstrip()
        query[header] = seq[:self.args.add_seq]
        ### ADD COLUMN TO RESULTS
        data = [row for row in self.received['data'].split('\n') if row]
        header = data[0].split("\t")
        header.insert(1,"sequence")
        data[0] = '\t'.join(header)
        for i,row in enumerate(data[1:]):
            row_l = row.split('\t')
            if row_l[0] in query:
                row_l.insert(1, query[row_l[0]])
                data[i+1] = '\t'.join(row_l)
            else:
                data[i+1] = '\t'.join(row.insert(1, ""))
        self.received["data"] = '\n'.join(data) + '\n'


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def usage():
    """
    Help function with argument parser.
    https://docs.python.org/3/howto/argparse.html?highlight=argparse
    """
    ### build parser
    parser = argparse.ArgumentParser()
    global_parser = argparse.ArgumentParser(add_help=False)
    index_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()
    subparsers.dest = 'type'
    subparsers.required = True
    ### Hidden argument to send login name in requests
    parser.add_argument('--user',
                        default=os.getlogin(),
                        help=argparse.SUPPRESS,
                        )
    # arguments for all subcommand
    global_parser.add_argument("-s", "--server",
                        help="SRV: server who hosting index (default localhost)",
                        metavar="SRV",
                        default='localhost',
                       )
    global_parser.add_argument("-p", "--port",
                        help="PORT: listening tcp port (default 12800)",
                        default=12800,
                        metavar='PORT',
                        choices=list(range(1,65537)),
                        type=int,
                       )
    index_parser.add_argument('index',
                        help="INDEX: Reindeer index",
                        metavar="INDEX",
                        )
    # create subparser for the "list" command
    parser_list = subparsers.add_parser("list",
                        parents = [global_parser],
                        help="List all running index",
                        )
    parser_list.add_argument('-a', '--all',
                        action="store_true",
                        help="show all indexes and their status, instead of running indexes only",
                       )
    # create subparser for the "query" command
    parser_query = subparsers.add_parser("query",
                        # ~ aliases=['qu'],
                        parents = [index_parser, global_parser],
                        help="Send a request to a specified index",
                        )
    parser_query.add_argument('-q', '--query',
                        type=argparse.FileType('r'),
                        required=True,
                        help="QUERY: query file as fasta format",
                        )
    parser_query.add_argument('-o', '--outfile',
                        help="OUTFILE: outfile name",
                        )
    parser_query.add_argument('-t', '--threshold',
                        help="THRESHOLD: minimum mean of kmers in dataset (see Reindeer help)",
                        )
    parser_query.add_argument('-f', '--format',
                        choices=['raw', 'sum', 'average', 'mean', 'normalize'],
                        default='average',
                        help="counts format, note that average == mean (default: average)",
                        )
    parser_query.add_argument('-a', '--add-seq',
                        type = int,
                        nargs = '?',
                        const=100,
                        help=("Insert query sequences in the second column, "
                              "up to the specified character (default: 100)"),
                        metavar="max-size",
                        )
    # create subparser for the "check" command
    parser_check = subparsers.add_parser("check",
                        parents=[index_parser, global_parser],
                        help="check specified index",
                        )
    # create subparser for the "status" command
    parser_status = subparsers.add_parser("status",
                        parents=[index_parser, global_parser],
                        help="return status of the specified index",
                        )
    # create subparser for the "start" command
    parser_start = subparsers.add_parser("start",
                        parents=[index_parser, global_parser],
                        help="Start the specifed index",
                        )
    # create subparser for the "stop" command
    parser_stop = subparsers.add_parser("stop",
                        parents=[index_parser, global_parser],
                        help="Stop properly the specifed index",
                        )
    # create subparser for the "kill" command
    parser_kill = subparsers.add_parser("kill",
                        parents=[index_parser, global_parser],
                        help="kill the specifed index",
                        )
    # arguments with special action
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f"{parser.prog} v{info.VERSION}",
                        default=info.VERSION,
                       )

    ### Go to "usage()" without arguments or stdin
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    return parser.parse_args()


if __name__ == "__main__":
    main()
