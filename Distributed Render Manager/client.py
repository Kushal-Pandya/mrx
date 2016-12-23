
import os
import time
import socket
import xmlrpclib
import subprocess

# Setup some stuff
SERVER_PORT = 20000
SLAVE_PORT =  20001
LOCALHOST = socket.gethostname()



class NewClient():
    def __init__(self):
        self.dispatcher = xmlrpclib.Server('http://%s:%i' 
            % (LOCALHOST, SERVER_PORT), allow_none=True)

        self.show       = os.environ.get('SHOW')
        self.shot       = os.environ.get('SHOT')
        self.user       = os.environ.get('USER')
        self.hversion   = os.environ.get('HOUDINI_VERSION')

    def listBlades(self):
        return self.dispatcher.listBlades()

    def listJobs(self):
        return self.dispatcher.listJobs()

    def getKnownBlades(self):
        return self.dispatcher.getKnownBlades()

    # Returns JID of blade requested
    def requestBlade(self, slaveGroup='LINUX'):
        return self.dispatcher.requestBlade(self.show, 
            self.shot, self.user, slaveGroup)

    def ifActive(self, blade):
        return self.dispatcher.ifActive(blade, self.show, 
            self.shot, self.hversion)

    def activateBlade(self, blade):
        return self.dispatcher.initHserver(blade, self.show, 
            self.shot, self.hversion)

    # AKA killJob
    def deactivateBlade(self, blade):
        result = self.dispatcher.killBlade(blade)
        
        self.dispatcher.removeBlade(blade)
        return result
    
    def releaseBlade(self, blade):
        return self.dispatcher.releaseBlade(blade, self.show, 
            self.shot, self.hversion)

    # returns status
    def update(self, blade):
        return self.dispatcher.update(blade)

    def updateDispatcher(self, updateDict):
        return self.dispatcher.updateBlades(updateDict)

    # if dispatcher doesn't exist...
    def launchDispatcher(self):
        proc = subprocess.Popen(['python', '%s/dispatcher.py' 
            % 'MRX_PYTHONPATH27', '&'])
        print proc.pid
        time.sleep(2)
        print 'launching dispatcher, waiting until port becomes active...'


if __name__ == '__main__':


    obj = BladeClient()

    print obj.listBlades()
    print obj.listJobs()
    print obj.requestBlade()

    time.sleep(20)

    print obj.listBlades()
    print obj.listJobs()

    if len(obj.listBlades()) > 0:
        obj.activateBlade(obj.initHserver(obj.listBlades()[0], 
            'show', 'shot', '15.5.123'))
