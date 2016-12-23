
import os
import sys
import copy
import time
import socket
import goshow2
import xmlrpclib
import subprocess
import SimpleXMLRPCServer as xmlrpc_server


LOCALHOST   = socket.gethostname()
STATUS      = None
JOB_ID      = None
RUNNING     = True
DISPATCHER  = None
SERVER_PORT = 20000
SLAVE_PORT  = 20001


def output(print_str):
    print print_str
    return True


def ifActive(show, shot, ver):
    global STATUS
    oldEnv = beginGoshow(show, shot, ver)

    proc = subprocess.Popen(
        ['hserver', '-l'], 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()

    if output is '':
        STATUS = 'inactive'
        return False
    else:
        STATUS = 'active'
        return True


def initHserver(show, shot, ver):
    global STATUS
    oldEnv = beginGoshow(show, shot, ver)

    # try to kill previous hserver before activating new one
    proc = subprocess.Popen(['hserver', '-q'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(3)
    proc = subprocess.Popen(['hserver'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()

    endGoshow(oldEnv)
    STATUS = 'active'
    sys.stdout.flush()
    return output, err


def release(show, shot, ver):
    global STATUS

    oldEnv = beginGoshow(show, shot, ver)

    proc = subprocess.Popen(['hserver', '-q'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = proc.communicate()

    STATUS  = 'inactive'
    return output, err


def kill():
    global RUNNING
    RUNNING = False
    return True


# Call this when user hits update
def update():
    global STATUS
    return STATUS


def beginGoshow(show, shot, ver):
    oldEnv = copy.copy(os.environ)
    go = goshow2.GoShow()

    go.setShow(show)
    go.setShot(shot)
    go.setVersion('HOUDINI_VERSION', override=ver)

    go.percolate()
    go.export(export='env')
    os.environ['GOSHOW_DONE'] = '1'

    return oldEnv


def endGoshow(oldEnv):
    # Restore ungoshowed' env
    os.environ = oldEnv
    return


if __name__ == '__main__':

    global STATUS
    DISPATCHER = sys.argv[1]
    dispatcher = xmlrpclib.Server('http://%s:%i' % (DISPATCHER, SERVER_PORT))

    JOB_ID = os.environ.get('JOB_ID', '0')

    print 'Registering %s with %s' % (JOB_ID, LOCALHOST)
    result = dispatcher.registerBlade(LOCALHOST, JOB_ID)
    STATUS = 'inactive'

    server = xmlrpc_server.SimpleXMLRPCServer((LOCALHOST, SLAVE_PORT))
    server.register_function(initHserver)
    server.register_function(output)
    server.register_function(ifActive)
    server.register_function(update)
    server.register_function(kill)
    server.register_function(release)

    while RUNNING:
        server.handle_request()

