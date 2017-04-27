import sys
from PyQt5 import QtGui, uic, QtWidgets
import data

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.uic = uic.loadUi('interface.ui', self)
        self.show()
        self.setupLocationsList()
        self.locationsList.doubleClicked.connect(self.locationsListClick)

    def setupLocationsList(self):
        self.locations = {}
        for row in open('dirs.txt'):
            name, path = row.strip().split('#')
            item = QtWidgets.QListWidgetItem(name)
            item.setToolTip(path)
            self.locationsList.addItem(item)
            self.locations[name] = path

    def setupContentList(self, location):
        self.backup = data.BackupData(location)
        self.backup.get_content()
        self.contentList.clear()
        for path in self.backup.content_to_add:
            item = QtWidgets.QListWidgetItem(" +  "+path)
            self.contentList.addItem(item)
        for path in self.backup.content_to_change:
            item = QtWidgets.QListWidgetItem(" o  "+path)
            self.contentList.addItem(item)
        for path in self.backup.content_to_delete:
            item = QtWidgets.QListWidgetItem(" -  "+path)
            self.contentList.addItem(item)

    def locationsListClick(self):
        selected_item = self.locationsList.currentItem().text()
        self.tabWidget.setTabText(0, selected_item)
        self.setupContentList(self.locations[selected_item])

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())