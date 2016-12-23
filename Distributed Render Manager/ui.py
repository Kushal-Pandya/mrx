
# -*- coding: utf-8 -*-

import os
import sys
import client
import getpass
from PySide import QtCore, QtGui
from ConfigParser import ConfigParser


BLADE_LIMIT = 2 #DEFAULT
NUM_COLS = 12


class Ui_BladeCheckOut(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Ui_BladeCheckOut, self).__init__(parent)

        self.resize(1300, 300)
        self.setWindowTitle("Blade CheckOut")     
        self.initTopBar()
        self.initTable()

        # Adding all the layouts together
        self.mainVerticalLayout = QtGui.QVBoxLayout()
        self.mainVerticalLayout.addLayout(self.horizontalLayout)
        self.mainVerticalLayout.addWidget(self.table)
        self.setLayout(self.mainVerticalLayout)

        self.loadFromDispatcher()
        self.show()


    def initTopBar(self):
        # Adding Labels 1
        self.slaveGroupLabel = QtGui.QLabel("Slave Group:", self)        
        self.slavegroup_combobox = QtGui.QComboBox(self)
        self.slavegroup_combobox.addItem("LINUX")
        self.slavegroup_combobox.addItem("LINUX_32G")
        self.slavegroup_combobox.addItem("LINUX_64G")
        self.slavegroup_combobox.addItem("LINUX_128G")

        self.requestBladeButton = QtGui.QPushButton("Request Blade", self)
        self.refreshButton = QtGui.QPushButton("Refresh", self)
        self.releaseAllButton = QtGui.QPushButton("Release All", self)

        self.requestBladeButton.clicked.connect(self.requestBlade)
        self.refreshButton.clicked.connect(self.refreshAllBlades)
        self.releaseAllButton.clicked.connect(self.releaseAll)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.addWidget(self.slaveGroupLabel)
        self.horizontalLayout.addWidget(self.slavegroup_combobox)
        self.horizontalLayout.addWidget(self.requestBladeButton)
        self.horizontalLayout.addWidget(self.refreshButton)
        self.horizontalLayout.addWidget(self.releaseAllButton)


    def initTable(self):
        self.table = QtGui.QTableWidget(0, NUM_COLS, self)
        self.headers = ['Blade Name', 'HServer Status', 'Job Status', 
        'Job ID', 'PID', 'Show', 'Shot', 'Version', ' ', ' ', ' ', ' ']
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)


    # Load all existing known blades from dispatcher: KNOWN_BLADES
    # if dispatcher doesn't exist, tell client to launch dispatcher via subprocess
    def loadFromDispatcher(self):
        self.clientObj = client.NewClient()

        try:
            allBlades = self.clientObj.getKnownBlades()
        except:
            print 'No Dispatcher Found, launching in Background...'
            self.clientObj.launchDispatcher()
            allBlades = self.clientObj.getKnownBlades()

        if allBlades is not None:

            # Disable requesting blades if blade limit is reached
            if len(allBlades) >= int(BLADE_LIMIT):
                self.requestBladeButton.setDisabled(True)

            for blade in allBlades:
                if self.clientObj.update(blade['blade']) != False:   
                    self.insertItem(blade)
                else:
                    self.clientObj.deactivateBlade(blade['blade'])


    def insertItem(self, blade):

        # Error message if they do not update the blade to be registered
        #   in the dispatcher
        if blade.get('hserverStatus') == None:
            print 'Warning: %s on %s could not communicate with distributed dispatcher' % \
                (blade.get('blade'), blade.get('jid'))
            self.clientObj.deactivateBlade(blade.get('blade'))
            return

        rowPosition     = self.table.rowCount()        
        updateButton    = QtGui.QPushButton("Update")
        releaseButton   = QtGui.QPushButton("Release")
        releaseButton.setDisabled(True)
        activateButton  = QtGui.QPushButton("Acquire")        
        deactivateButton= QtGui.QPushButton("Kill")
        activateButton.setDisabled(True)
        self.table.insertRow(rowPosition)

        self.table.setItem(rowPosition, 0, QtGui.QTableWidgetItem(blade['blade']))
        self.table.setItem(rowPosition, 1, QtGui.QTableWidgetItem(blade['hserverStatus']))
        self.table.setItem(rowPosition, 2, QtGui.QTableWidgetItem(''))
        self.table.setItem(rowPosition, 3, QtGui.QTableWidgetItem(blade['jid']))
        self.table.setItem(rowPosition, 4, QtGui.QTableWidgetItem(blade['pid']))
        self.table.setItem(rowPosition, 5, QtGui.QTableWidgetItem(blade['show']))
        self.table.setItem(rowPosition, 6, QtGui.QTableWidgetItem(blade['shot']))
        self.table.setItem(rowPosition, 7, QtGui.QTableWidgetItem(blade['hversion']))
        self.table.setCellWidget(rowPosition, 8, activateButton)
        self.table.setCellWidget(rowPosition, 9, releaseButton)
        self.table.setCellWidget(rowPosition, 10, updateButton)
        self.table.setCellWidget(rowPosition, 11, deactivateButton)

        updateButton.clicked.connect(self.update)
        releaseButton.clicked.connect(self.release)
        activateButton.clicked.connect(self.activate)
        deactivateButton.clicked.connect(self.deactivate)


    def requestBlade(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        bladeName       = 'NA'
        jobStatus       = 'queued'
        hserverStatus   = 'inactive'
        clientPID       = str(os.getpid())
        slaveGroup      = self.slavegroup_combobox.currentText()
        jobid           = self.clientObj.requestBlade(slaveGroup)
        show            = self.clientObj.show
        shot            = self.clientObj.shot
        version         = self.clientObj.hversion

        self.rowPosition = self.table.rowCount()
        self.table.insertRow(self.rowPosition)

        self.updateButton = QtGui.QPushButton("Update")
        self.releaseButton = QtGui.QPushButton("Release")
        self.activateButton = QtGui.QPushButton("Acquire")
        self.deactivateButton = QtGui.QPushButton("Kill")

        self.releaseButton.setDisabled(True)
        self.activateButton.setDisabled(True)
        

        self.table.setItem(self.rowPosition, 0, QtGui.QTableWidgetItem(bladeName))
        self.table.setItem(self.rowPosition, 1, QtGui.QTableWidgetItem(hserverStatus))
        self.table.setItem(self.rowPosition, 2, QtGui.QTableWidgetItem(jobStatus))
        self.table.setItem(self.rowPosition, 3, QtGui.QTableWidgetItem(jobid))
        self.table.setItem(self.rowPosition, 4, QtGui.QTableWidgetItem(clientPID))
        self.table.setItem(self.rowPosition, 5, QtGui.QTableWidgetItem(show))
        self.table.setItem(self.rowPosition, 6, QtGui.QTableWidgetItem(shot))
        self.table.setItem(self.rowPosition, 7, QtGui.QTableWidgetItem(version))

        self.table.setCellWidget(self.rowPosition, 8, self.activateButton)
        self.table.setCellWidget(self.rowPosition, 9, self.releaseButton)        
        self.table.setCellWidget(self.rowPosition, 10, self.updateButton)
        self.table.setCellWidget(self.rowPosition, 11, self.deactivateButton)

        self.updateButton.clicked.connect(self.update)
        self.releaseButton.clicked.connect(self.release)
        self.activateButton.clicked.connect(self.activate)
        self.deactivateButton.clicked.connect(self.deactivate)

        # Disable requesting blades if blade limit is reached
        if self.table.rowCount() >= int(BLADE_LIMIT):
            self.requestBladeButton.setDisabled(True)

        QtGui.QApplication.restoreOverrideCursor()


    def jidToBlade(self, position):
        jid = self.table.item(position, 3).text()
        jobs = self.clientObj.listJobs()
        bladeName = jobs[jid]
        return bladeName


    # signal 
    # This should be disabled, only enabled when hserver is active
    def release(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        buttonClicked = self.sender()
        index = self.table.indexAt(buttonClicked.pos())
        position = index.row()

        bladeName = self.jidToBlade(position)
        result =  self.clientObj.releaseBlade(bladeName)

        if result:
            self.table.setItem(position, 1, QtGui.QTableWidgetItem('inactive'))
            self.table.item(position, 1).setBackground(QtGui.QColor(255,102,102))
            activateButton = self.table.cellWidget(position, 8)
            activateButton.setDisabled(False)
            buttonClicked.setDisabled(True)
        QtGui.QApplication.restoreOverrideCursor()


    # This should also call release for each column (or similar to it)
    def releaseAll(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        rowCount = self.table.rowCount()

        if rowCount == 0:
            QtGui.QApplication.restoreOverrideCursor()
            return 0
        
        for row in range(rowCount):            
            bladeName = self.jidToBlade(row)
            result = self.clientObj.releaseBlade(bladeName)
            if result:
                self.table.setItem(row, 1, QtGui.QTableWidgetItem('inactive'))
                self.table.item(row, 1).setBackground(QtGui.QColor(255,102,102))
                activateButton = self.table.cellWidget(row, 8)
                releaseButton = self.table.cellWidget(row, 9)
                activateButton.setDisabled(False)
                releaseButton.setDisabled(True)

        QtGui.QApplication.restoreOverrideCursor()
        return result


    # Acquire the hserver
    def activate(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        buttonClicked = self.sender()
        index = self.table.indexAt(buttonClicked.pos())
        position = index.row()

        bladeName = self.jidToBlade(position)

        result = self.clientObj.activateBlade(bladeName)
        if result:
            self.table.setItem(position, 1, QtGui.QTableWidgetItem('active'))
            self.table.item(position, 1).setBackground(QtGui.QColor(102,204,0))
            releaseButton = self.table.cellWidget(position, 9)
            releaseButton.setDisabled(False)
            buttonClicked.setDisabled(True)
        QtGui.QApplication.restoreOverrideCursor()


    # Aka Kill
    # Removes from hserver and dispatcher and finishes job if running
    def deactivate(self):
        buttonClicked = self.sender()
        index = self.table.indexAt(buttonClicked.pos())
        position = index.row()
        bladeName = self.jidToBlade(position)

        # Confirmation Box
        reply = QtGui.QMessageBox.warning(self, 'Confirmation',
            "Are you sure to kill the job and remove the blade from dispatcher?", 
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, 
            QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.clientObj.deactivateBlade(bladeName)
            self.table.removeRow(position)

            # Enable requesting blades if blade limit is not reached
            if self.table.rowCount() < int(BLADE_LIMIT):
                self.requestBladeButton.setDisabled(False)

            QtGui.QApplication.restoreOverrideCursor()


    def update(self):
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        buttonClicked = QtGui.qApp.focusWidget()
        index = self.table.indexAt(buttonClicked.pos())
        position = index.row()

        bladeName = self.jidToBlade(position)
        self.refreshBlade(bladeName, position)

    # Update all blades
    def refreshAllBlades(self):
        for row in range(self.table.rowCount()):
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            bladeName = self.jidToBlade(row)
            self.refreshBlade(bladeName, row)


    # send individual blades here to refresh
    def refreshBlade(self, bladeName, position):

        # Making sure blade is active
        if bladeName != None:
            # Enable the release button here
            releaseButton = self.table.cellWidget(position, 9)
            activateButton = self.table.cellWidget(position, 8)

            if self.table.item(position, 1).text() != 'active':
                activateButton.setDisabled(False)


            # UPDATING THE KNOWN_BLADES in dispatcher
            updateDict = {
                'blade'         : bladeName,  
                'pid'           : self.table.item(position, 4).text(),
                'show'          : self.table.item(position, 5).text(), 
                'shot'          : self.table.item(position, 6).text(), 
                'hversion'       : self.table.item(position, 7).text(), 
            }
            self.clientObj.updateDispatcher(updateDict)

            newStatus = self.clientObj.update(bladeName)
            if newStatus != False:
                jobStatus = 'running'
            else:
                # if this is the case then the job is no longer active/ and
                # the blade has lost communication with dispatcher
                self.clientObj.deactivateBlade(bladeName)
                self.table.removeRow(position)
                return

            self.table.setItem(position, 0, QtGui.QTableWidgetItem(bladeName))
            self.table.setItem(position, 1, QtGui.QTableWidgetItem(newStatus))
            self.table.setItem(position, 2, QtGui.QTableWidgetItem(jobStatus))

            if newStatus == 'active':
                self.table.item(position, 1).setBackground(QtGui.QColor(102,204,0))

        QtGui.QApplication.restoreOverrideCursor()


def doIt():
    global window
    app = QtGui.QApplication.instance()

    if app is None:
        app = QtGui.QApplication(["houdini"])
    try:
        window.close()
    except NameError as e:
        pass

    window = Ui_BladeCheckOut()
    window.show()
    #sys.exit(app.exec_())

    return

def parseConfig():
    global BLADE_LIMIT

    config = ConfigParser()
    config.read('MRX_PYTHONPATH2.7')

    if config.has_option('limit_overrides', getpass.getuser()):
        BLADE_LIMIT = config.get('limit_overrides', getpass.getuser())
    else:
        BLADE_LIMIT = config.get('default_limit', 'user')


if __name__ == '__main__': 
    parseConfig()
    doIt()