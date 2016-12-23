
import sys
import main
import subprocess
import json
import os
import re
from os.path import expanduser
from optparse import OptionParser

from PySide.QtCore import *
from PySide.QtGui import *

# Default settings
theDict = {'toggleDone':False, 'toggleKilled':False, 'toggleCrash':False,
    'toggleJobComplete':False, 'toggleJobIdle':False, 'popupTime': 20} 

# Notification contents and user
newPrint = 'temp' 
newMsg = 'temp'
user = 'temp'


class SystemIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(SystemIcon, self).__init__(parent)

        self.createMenu()  # Add context menu.
        self.createTray()
        
        self.i = 0
        self.isDone = []
        self.tempPath = None
        
        self.show()
        # Starts the qtimer
        self.startProcessing()


    def createMenu(self):
        self.menu = QMenu()
        self.oldNotifAction = self.menu.addAction("&Show previous notification")
        self.oldNotifAction.triggered.connect(self.openOld)
        self.settingAction = self.menu.addAction("&Notification Settings")
        self.settingAction.triggered.connect(self.setting) 
        self.xrenderAction = self.menu.addAction("&Open XRender Client")
        self.xrenderAction.triggered.connect(self.openXrender)

        self.showRendersMenu = self.menu.addMenu('&View Rendered Frames')
        self.showRendersMenu.setDisabled(True)
        self.clearRenderAction = self.showRendersMenu.addAction('Clear Menu')
        self.clearRenderAction.triggered.connect(self.clearRenderMenu)
        self.clearRenderAction.setDisabled(True)
        self.showRendersMenu.addSeparator()

        self.menu.addSeparator() 
        self.exitAction = self.menu.addAction("&Quit")
        self.exitAction.triggered.connect(sys.exit)


    def addViewMenu(self):

        try:
            self.showRendersAction.removeAction()
        except:
            pass

    # code to implement menu for multiple notifs
        self.showRendersMenu.setEnabled(True)
        self.clearRenderAction.setEnabled(True)
        self.showRendersAction = self.showRendersMenu.addAction('View: %s'% self.theJob)
        self.showRendersAction.triggered.connect(self.openFramesM)


    def openFramesM(self):
        try:
            subprocess.Popen(['mplay', self.path])
        except:
            print 'Something went wrong with viewing rendered frames in mplay'
            print 'mplay', self.path


    # Doesnt work all the time IDK, using ^ for now
    def openFramesR(self):
        try:
            subprocess.Popen(['rv', self.path])
        except:
            print 'Something went wrong with viewing rendered frames in rv'


    def clearRenderMenu(self):
        self.showRendersMenu.clear()
        self.clearRenderAction = self.showRendersMenu.addAction('Clear Menu')
        self.clearRenderAction.triggered.connect(self.clearRenderMenu)
        self.showRendersMenu.addSeparator()


    def createTray(self):
        self.icon = QIcon("MRX_PYTHONPATH27/chicken.png")
        self.setIcon(self.icon)
        self.setToolTip("Render Farm Notification")
        self.setContextMenu(self.menu)  


    def startProcessing(self):
        global user, theDict

        try:
            timer = QTimer()
            timer.timeout.connect(self.startProcessing)
            timer.start(60000) # Polling db every 60 seconds

            #Reading settings from hidden folder under user's home directory
            home = expanduser("~")

            try:
                f = open(home + 'MRX_PYTHONPATH27/userSettings.txt', 'r')
                theDict = json.load(f)
                f.close()

            except IOError: #If file doesnt exist, use default settings
                pass

            # Revert back to grey icon after 60 seconds
            self.icon = QIcon("MRX_PYTHONPATH27/chicken.png")
            self.setIcon(self.icon)

            message, self.i, self.isDone = main.initMain(theDict, self.i, self.isDone, user)

            if message['msg'] != 'temp':
                global newMsg, newPrint
                newMsg = message['msg']
                newPrint = message['toPrint']
                info = message['dict']

                self.show_message()
                # View render only if job/frame is completed
                if 'Completed' in message['msg']: 
                    # only works right now for vray and mantra jobs
                    # NEED TO CHANGE LATER TO ACCEPT NUKE/HSCRIPT JOBS
                    if 'mantra' in info['job'] or 'vray' in info['job']:
                        self.viewFrames(info)
                    elif (('xpub' not in info['job']) and 
                        'comp' in info['job'] or 'slap' in info['job']):
                        self.viewFramesComp(info)                           

        finally:
            QTimer.singleShot(60000, self.startProcessing)   


    def viewFrames(self, info):

        show = info['show']
        shot = info['shot']
        theUser = user

    # BELOW ARE SOME SAMPLE TEST CASES
        # show = 'detroit'
        # shot = 'ME300'
        # theUser = 'aditi'
        # info['job'] = 'ME300_Smoke_Trail_mantra_v001'

        # show = 'detroit'
        # shot = 'BD160'
        # theUser = 'vimal'
        # info['job'] = 'BD160_GROUND_BARREL_FIRE_1_mantra_v006'

        # show = 'vikings4'
        # shot = '1539B_005'
        # theUser = 'tie'
        # info['job'] = '1539B_005_v010_01_thin_LAYOUT_vray_v001'

        # show = 'detroit'
        # shot = 'KF965'
        # theUser = 'viduttam'
        # info['job'] = 'KF965_lighting_v004_bloodshot_vray_v001'


        #NEED THIS DONT DELETE 
        self.theJob = info['job']

    # new regex
        regex = '(?P<shot>('+ shot +')[_])(?P<stuff>[\w+_\d+?-]*)[_](?P<mantra>(mantra|vray)[_](v\d\d\d))'
        ifVer = re.search(regex, info['job'])
        if ifVer:
            version = ifVer.group(6)
            name = ifVer.group(3)
            self.jobName = name
            self.getPath(show, shot, version, theUser)

        else:
            version = ''
            name = ''
            print 'Couldnt find version or name..'


    def getPath(self, show, shot, version, theUser):
        tempPath = 'MRX_PYTHONPATH27' % (show, 
            shot, theUser, self.jobName, version, self.jobName)   

        if (os.path.exists(tempPath)):  #.exr to .*
            self.tempPath = tempPath
            self.path = tempPath + '%s_%s_%s.*.*' % (shot, self.jobName, version)        
            print 'path: ' + self.path
            self.addViewMenu()
        else:
            try:                                                            
                self.path = 'MRX_PYTHONPATH27' % (
                    show, shot, theUser, self.jobName, version, shot, self.jobName, version)        
                print 'path: ' + self.path
                self.tempPath = 'MRX_PYTHONPATH27' % (show, 
                    shot, theUser, self.jobName, version)
                self.addViewMenu()
            except:
                print 'Viewing Frames Failed: Path is not correct'


    def viewFramesComp(self, info):
        show = info['show']
        shot = info['shot']
        theUser = user

    # Test Cases
        # show = 'benhur'
        # shot = '803_CR_4635'
        # theUser = 'danielk'
        # info['job'] = '803_CR_4635_slapblocking_v01'

        self.theJob = info['job']     
        self.jobName = self.theJob
        self.getPathComp(show, shot, theUser)


    def getPathComp(self, show, shot, theUser):
        # Just need to check if this exists -> if true: 
        tempPath = 'MRX_PYTHONPATH27' % (
            show, shot, theUser, self.jobName)

        if (os.path.exists(tempPath)): 

            if os.listdir(tempPath) == []:
                print 'Comp: No files found in directory'  
                return 

            self.tempPath = tempPath
            self.path = tempPath + '%s.*.*' % (self.jobName)  #.exr to #.*      
            print 'path: ' + self.path
            self.addViewMenu()
        else:
            print 'View Frames: render path doesnt exist'


    def openXrender(self):
        proc = subprocess.Popen(['wine_xclient'])


    def openOld(self):
        self.oldNotif = QDialog()
        self.oldNotif.resize(300, 200)
        self.oldNotif.setWindowTitle("Previous Notification")
        self.text = QLabel(self.oldNotif)
        self.text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.okButton = QPushButton('OK', self.oldNotif)
        self.okButton.clicked.connect(self.closeDialog)

        global newMsg

        if self.tempPath != None:
            printPath = 'Possible Path: ' + self.tempPath
        else:
            printPath = ''

        if newMsg != 'temp':
            self.text.setText(newMsg + '\n' + newPrint + '\n' + printPath)
        else:
            self.text.setText("No Previous Notification")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.okButton)
        self.oldNotif.setLayout(self.layout)
        self.oldNotif.exec_()
        

    def closeDialog(self):
        self.oldNotif.reject()


    def setting(self):
        self.dialog = QDialog()
        self.dialog.resize(340, 240)
        self.dialog.setWindowTitle("Notification Settings")

        self.messageSpinBox = QSpinBox(self.dialog)
        self.messageSpinBox.setRange(1, 59)
        self.messageSpinBox.setSingleStep(1)
        self.messageSpinBox.setPrefix('Message Timeout: ')
        self.messageSpinBox.setSuffix('(s)')

        self.toggleDone = QCheckBox('Disable First Frames Complete Notifications', self.dialog)
        self.toggleCrash = QCheckBox('Disable Crash Notifications', self.dialog)
        self.toggleKilled = QCheckBox('Disable Killed Notifications', self.dialog)
        self.toggleJobComplete = QCheckBox('Disable Job Complete Notifications', self.dialog)
        self.toggleJobIdle = QCheckBox('Disable Job Idle Notifications', self.dialog)
        saveButton = QPushButton('Save', self.dialog)
        cancelButton = QPushButton('Cancel', self.dialog)
        cancelButton.setDefault(True)

        self.messageSpinBox.move(100, 20)
        self.toggleDone.move(20, 60)
        self.toggleCrash.move(20, 80)
        self.toggleKilled.move(20, 100)
        self.toggleJobComplete.move(20, 120)
        self.toggleJobIdle.move(20, 140)
        saveButton.move(60, 180)
        cancelButton.move(150, 180)

        self.initSettings()
        saveButton.clicked.connect(self.settingsUpdated)
        cancelButton.clicked.connect(self.setCancel)

        self.dialog.exec_()


    def initSettings(self):
        global theDict

        self.settingsDict = theDict

        if 'popupTime' in theDict:
            self.messageSpinBox.setValue(theDict.get('popupTime'))
        else:
            theDict['popupTime'] = 20
            self.messageSpinBox.setValue(theDict.get('popupTime'))
        self.toggleDone.setChecked(theDict.get('toggleDone'))
        self.toggleCrash.setChecked(theDict.get('toggleCrash'))
        self.toggleKilled.setChecked(theDict.get('toggleKilled'))
        self.toggleJobComplete.setChecked(theDict.get('toggleJobComplete'))
        self.toggleJobIdle.setChecked(theDict.get('toggleJobIdle'))


    def setCancel(self):
        self.dialog.reject()


    def settingsUpdated(self):
        self.dialog.accept()

        self.settingsDict['popupTime']          = self.messageSpinBox.value()
        self.settingsDict['toggleDone']         = self.toggleDone.isChecked()
        self.settingsDict['toggleCrash']        = self.toggleCrash.isChecked()
        self.settingsDict['toggleKilled']       = self.toggleKilled.isChecked()
        self.settingsDict['toggleJobComplete']  = self.toggleJobComplete.isChecked()
        self.settingsDict['toggleJobIdle']      = self.toggleJobIdle.isChecked()

        global theDict
        theDict = self.settingsDict

        #Saving settings to file under hidden folder in user's home directory
        home = expanduser("~")
        if not os.path.exists(home + '/.mrx/XNotif/'):
            os.makedirs(home + '/.mrx/XNotif/')

        f = open(home + '/.mrx/XNotif/userSettings.txt', 'w')
        json.dump(theDict, f)
        f.close()


    def show_message(self): 

        if 'Completed' in newMsg:
            self.icon = QIcon("/MRX_PYTHONPATH27/greenChicken.png")
            self.setIcon(self.icon)
        elif 'Killed' in newMsg:
            self.icon = QIcon("/MRX_PYTHONPATH27/redChicken.png")
            self.setIcon(self.icon)
        else:
            self.icon = QIcon("/MRX_PYTHONPATH27/orangeChicken.png")
            self.setIcon(self.icon)

        # Popup notification for 20s as default
        value = int(theDict['popupTime'])*1000
        self.showMessage(newMsg, newPrint, self.Information, value)


def initUser():

    global user

    parser = OptionParser()
    parser.add_option('-u', '--user', nargs=1, action='store', 
        type='string', dest='user', default= os.environ['USER'],
        help='Select user option')
    (options, args) = parser.parse_args()

    user = options.user


def initSystray():

    initUser()

    app = QApplication(sys.argv)
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None,
            "Systray",
            "I couldn't detect any system tray on this system.")
        sys.exit(1)

    QApplication.setQuitOnLastWindowClosed(False)

    icon = SystemIcon()
    sys.exit(app.exec_())


initSystray()
