import subprocess

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
import data


class TaskThread(QtCore.QThread):
    def __init__(self, data, parent=None):
        QThread.__init__(self, parent)
        self.data = data
        print(data)

    def run(self):                  #starting Google Drive, Dropbox in seperate thread
        subprocess.call([self.data])


    def openExplorer(self):
        subprocess.Popen(r'explorer /select,"'+self.data+'"')