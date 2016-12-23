
import os
import time
import socket
import xmlrpclib
import xrenderpy as xr
import SimpleXMLRPCServer as xmlrpc_server

LOCALHOST = socket.gethostname()
SERVER_PORT = 20000
SLAVE_PORT =  20001
KNOWN_BLADES = []
BLADES = dict()
JOBS = dict()
DEBUG = 1


# Used for debug print
def dprint(message):
    if DEBUG:
        print '\tDEBUG: ' + message

def running():
    return True

def listBlades():
    dprint('listBlades() called')
    return BLADES.keys()

def listJobs():
    dprint('listJobs() called')
    return JOBS

def getKnownBlades():
    return KNOWN_BLADES

def update(blade):
    dprint('update() called')
    try:
        return BLADES[blade].update()
    except:
        return False

def ifActive(blade, show, shot, ver):
    dprint('ifActive() called')
    result = BLADES[blade].ifActive(show, shot, ver)

    if result is True:
        dprint('ifActive() is True')
    else:
        dprint('ifActive() is False')
    return result

def releaseBlade(blade, show, shot, ver):
    dprint('releaseBlade() called')

    try:
        result = BLADES[blade].release(show, shot, ver)
    except:
        dprint('releaseBlade() %s couldnt be released, maybe already inactive'
            % blade)
        return False

    if result[0] is '':
        dprint('releaseBlade() not successful: ' + result[1]) 
        return False
    else:
        dprint('releaseBlade() successful: ' + result[0])
        return True

def killBlade(blade):
    dprint('killBlade() called')
    try:
        result = BLADES[blade].kill()
    except:
        dprint('killBlade() %s couldnt be killed, maybe already inactive'
            % blade)
        return False

    return result


def removeBlade(blade):
    dprint('removeBlade() called')
    global KNOWN_BLADES

    try:
        del BLADES[blade]
        for key, val in JOBS.items():
            if val == blade:
                del JOBS[key]
        KNOWN_BLADES[:] = [d for d in KNOWN_BLADES if d.get('blade') != blade]

        dprint('removeBlade() %s successful' % blade)
        return True
    except:
        dprint('removeBlade() %s failed' % blade)
        return False

def initHserver(blade, show, shot, ver):
    dprint('initHserver() called')
    # BLADES[blade] gets server running on blade to call methods
    try:
        result = BLADES[blade].initHserver(show, shot, ver)
    except:
        dprint('initHserver() call failed, blade: %s' % blade)
        return False

    if result[1] is '':
        dprint('initHserver() successful')
        return True
    else:
        dprint('initHserver() not successful: ' + result[1]) 
        return False

def registerBlade(blade, cid):
    dprint('registerBlade() called')
    dprint('Adding %s to server' % blade)
    slave_server = xmlrpclib.Server('http://%s:%i' % (blade, SLAVE_PORT))
    BLADES[blade] = slave_server
    pid = str(xr.getParentID(int(cid)))
    dprint('Slave server created from ParentJobID: %s' % pid)
    JOBS[pid] = blade

    tempDict = {
        'blade' : blade,       
        'jid'   : pid,
    }
    KNOWN_BLADES.append(tempDict)
    return True

def requestBlade(show, shot, user, slaveGroup):
    dprint('requestBlade() called')
    xr.clearAll()
    xr.addKey('show', show)
    xr.addKey('shot', shot)
    xr.addKey('owner', user)
    xr.addKey('startFrame', 1)
    xr.addKey('endFrame', 1)
    xr.addKey('stepFrame', 1)
    xr.addKey('bundleFrame', 10)
    xr.addKey('slaveGroup', slaveGroup) # add slavegroup here?
    xr.addKey('jobType', 'Linux')
    xr.addKey('jobName', 'Distributed Slave')
    xr.addKey('softwareType','distributed')
    xr.addKey('maxblade', 1)
    xr.addKey('batchFile', 'python2.7 %s/slave.py %s' 
        % (os.path.dirname(os.path.realpath(__file__)), LOCALHOST))
    pid = str(xr.createJob())
    dprint('requestBlade(): %s xrenderpy job submitted' % pid)
    xr.clearAll()
    JOBS[pid] = None
    return pid    

def output(print_str):
    dprint('output() called: ' + print_str)
    return True

def bladeOutput(blade, print_str):
    dprint('bladeOutput() called')
    return BLADES[blade].output(print_str)

def updateBlades(updateDict):
    dprint('updateBlades() called')
    global KNOWN_BLADES
    for blade in KNOWN_BLADES:
        if blade['blade'] == updateDict['blade']:               
            blade.update(updateDict)
            try:
                blade['hserverStatus'] = update(blade['blade'])
            except:
                return False
    return True


if __name__ == '__main__':
    server = xmlrpc_server.SimpleXMLRPCServer((LOCALHOST, SERVER_PORT), 
                                                        allow_none=True)
    dprint("Listening on port %d ..." % (SERVER_PORT))

    server.register_function(listBlades)
    server.register_function(listJobs)
    server.register_function(registerBlade)
    server.register_function(requestBlade)
    server.register_function(killBlade)
    server.register_function(releaseBlade)
    server.register_function(initHserver)
    server.register_function(ifActive)
    server.register_function(output)
    server.register_function(bladeOutput)
    server.register_function(running)
    server.register_function(update)
    server.register_function(removeBlade)
    server.register_function(getKnownBlades)
    server.register_function(updateBlades)
    server.serve_forever()

