import sys
import threading

from PyQt5 import QtGui, uic, QtWidgets, QtCore
from builtins import set
import random
from multiprocessing import Process

import data
import os
from worker import *
class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.uic = uic.loadUi('interface.ui', self)
        self.show()
        self.setupLocationsList()
        self.locationsList.doubleClicked.connect(self.locationsListClick)
        self.saveHistoryBtn.clicked.connect(self.saveHistory)
        self.clearHistoryBtn.clicked.connect(self.clearHistory)
        self.servicesBtn.clicked.connect(self.startService)
        self.refreshBtn.clicked.connect(self.refreshContent)
        self.backupBtn.clicked.connect(self.backupContent)
        self.checkAllBtn.clicked.connect(self.checkAll)

        self.loadOnStartup()


    def loadOnStartup(self):
        self.selected_item = "Računalnik"

        self.initButtons()
        if os.path.exists(self.locations[self.selected_item]):
            self.tabWidget.setTabText(0, self.selected_item)
            self.setupContentList(self.locations[self.selected_item])
            self.setupDestinationsList()
        else:
            self.consoleEdit.append("<span style=\"  color:#DB5652;\" >[Error] Directory doesn't exist.\n</span>")

        self.servicesBtn.setEnabled(self.selected_item in self.backup.sync_services)


    def initButtons(self):
        self.backupBtn.setEnabled(True)
        self.refreshBtn.setEnabled(True)
        self.saveHistoryBtn.setEnabled(True)
        self.clearHistoryBtn.setEnabled(True)
        self.checkAllBtn.setEnabled(True)

    def setupLocationsList(self):
        self.locations = {}
        for row in open('dirs.txt'):
            name, path = row.strip().split('#')
            item = QtWidgets.QListWidgetItem(name)
            item.setToolTip(path)
            self.locationsList.addItem(item)
            self.locations[name] = path


    def setupDestinationsList(self):
        self.destinations = {}
        self.destinationsList.clear()
        for row in open('dirs.txt'):
            name, path = row.strip().split('#')
            if name != self.selected_item:
                item = QtWidgets.QListWidgetItem(name)
                item.setToolTip(path)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.destinationsList.addItem(item)
                self.destinations[name] = path


    def setupContentList(self, location):
        self.backup = data.BackupData(location)
        self.backup.get_content()
        self.contentList.clear()
        self.changesLabel.setText("Changes ("+str(len(self.backup.content_to_add)+len(self.backup.content_to_delete)+len(self.backup.content_to_change))+")")
        for path in self.backup.content_to_add:
            item = QtWidgets.QListWidgetItem(" +  "+path)
            item.setForeground(QtGui.QColor('#44bd51'))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.contentList.addItem(item)
        for path in self.backup.content_to_change:
            item = QtWidgets.QListWidgetItem(" o  "+path)
            item.setForeground(QtGui.QColor('#4A90D4'))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.contentList.addItem(item)
        for path in self.backup.content_to_delete:
            item = QtWidgets.QListWidgetItem(" -  "+path)
            item.setForeground(QtGui.QColor('#DB5652'))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.contentList.addItem(item)

    def locationsListClick(self):
        self.selected_item = self.locationsList.currentItem().text()
        self.initButtons()

        if os.path.exists(self.locations[self.selected_item]):
            self.tabWidget.setTabText(0, self.selected_item)
            self.setupContentList(self.locations[self.selected_item])
            self.setupDestinationsList()
        else:
            self.consoleEdit.append("<span style=\"  color:#DB5652;\" >[Error] Directory doesn't exist.\n</span>")

        self.servicesBtn.setEnabled(self.selected_item in self.backup.sync_services)

    def saveHistory(self):
        self.backup.saveLog()
        self.consoleEdit.append("Saved history\n")
        self.refreshContent()



    def clearHistory(self):
        self.backup.clearLog()
        self.consoleEdit.append("Cleared history\n")
        self.refreshContent()


    def refreshContent(self):
        self.backup.get_content()
        self.locationsListClick()

    def startService(self):
        self.consoleEdit.append("\nStarting {} ...".format(self.selected_item))

        self.myLongTask = TaskThread(data=self.backup.sync_services[self.selected_item])
        self.myLongTask.start() #start Google Drive, Dropbox in a seperate thread to prevent UI blocking

        self.consoleEdit.append("{} is now syncing changes ...\n".format(self.selected_item))




    def backupContent(self):
        destinations = []
        self.consoleEdit.append('Starting to backup ...\n')
        for i in range(self.destinationsList.count()):
            if self.destinationsList.item(i).checkState() == QtCore.Qt.Checked:
                destinations.append(self.destinations[self.destinationsList.item(i).text()])


        for i in range(self.contentList.count()):
            path = self.contentList.item(i).text().replace(" +  ", "").replace(" o  ", "").replace(" -  ", "")
            if self.contentList.item(i).checkState() == QtCore.Qt.Unchecked:
                if " + " in self.contentList.item(i).text() and path in self.backup.content_to_add:
                    self.backup.content_to_add.remove(path)
                elif " o " in self.contentList.item(i).text() and path in self.backup.content_to_change:
                    self.backup.content_to_change.remove(path)
                elif " - " in self.contentList.item(i).text() and path in self.backup.content_to_delete:
                    self.backup.content_to_delete.remove(path)
            else:
                if " + " in self.contentList.item(i).text() and path not in self.backup.content_to_add:
                    self.backup.content_to_add.append(path)
                elif " o " in self.contentList.item(i).text() and path not in self.backup.content_to_change:
                    self.backup.content_to_change.append(path)
                elif " - " in self.contentList.item(i).text() and path not in self.backup.content_to_delete:
                    self.backup.content_to_delete.append(path)


        self.backup.setDestinations(destinations)
        self.backup.backup()
        self.consoleEdit.append('Backup finished.\n')


    def checkAll(self):
        self.checkAllBtn.setText('Check All' if self.checkAllBtn.text() == "Uncheck all" else "Uncheck all")
        for i in range(self.contentList.count()):
            self.contentList.item(i).setCheckState(QtCore.Qt.Checked if self.checkAllBtn.text() == "Uncheck all" else QtCore.Qt.Unchecked)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())