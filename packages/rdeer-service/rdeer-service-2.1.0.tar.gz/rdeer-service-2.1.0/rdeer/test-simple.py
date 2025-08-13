#!/usr/bin/env python3


"""
TESTE SI L'INDEX A FINI DE CHARGER
"""

import sys
import socket
import time

SERVER = "localhost"
PORT = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    ### Je veux juste tester la connexion et redonner la main aussitôt
    sock.settimeout(.5)

    errno = sock.connect((SERVER, PORT))
    print("errno:", errno)
    
    response = sock.recv(255).decode('utf8')
    print("response:", response)
    
    sock.send(b'STOP')

except Exception as err:
    print(err)

finally:
    sock.close()

sock.close()
