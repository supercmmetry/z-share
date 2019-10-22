import sys
import os
from PySide2 import QtCore, QtGui, QtQuick, QtQml
from qmlModels import window
from qmlModels import contact_model
from qmlModels import file_model
import socket
import utils
from utils import getContactsFromDB


backendWindow = window.BackendWindow()
contactModelProvider = contact_model.ContactModelProvider([])
fileModelProvider = file_model.FileModelProvider([])
currContacts = []


class MainBackend(QtCore.QObject):
    ipsignal = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.engine = None
        self._ipaddr = socket.gethostbyname(socket.gethostname())
    
    @QtCore.Slot(str)
    def search(self, data):
        filtered_contacts = []
        if data == "":
            contactModelProvider.model.reset(currContacts)
            return
        for contact in currContacts:
            if data.lower() in contact["name"].lower():
                filtered_contacts.append(contact)
        contactModelProvider.model.reset(filtered_contacts)
    
    @QtCore.Slot(str)
    def addFile(self, filename):
        filename_nu = filename.replace("file://", "")
        utils.addIntFileToDB(filename_nu)

    @QtCore.Slot()
    def openAddContactsWindow(self):
        engine.load(QtCore.QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), "qml/addContacts.qml")))

    @QtCore.Slot(str)
    def loadChat(self, ip):
        if ip == "127.0.0.1":
            fp = utils.getFilesDB()
            fileModelProvider.model.reset(fp)
        else:
            fileModelProvider.model.reset([])

    @QtCore.Slot(str, str)
    def addContact(self, ip, name):
        utils.addContactToDB(ip, name)
        loadContacts()

    @QtCore.Property(str, notify=ipsignal)
    def ipaddr(self):
        return self._ipaddr
    
    @ipaddr.setter
    def set_ipaddr(self):
        self.ipsignal.emit()

    @QtCore.Slot(str)
    def deleteFile(self, filename):
        filename_nu = filename.replace("file://", "")
        utils.removeFile(filename_nu)
        #os.remove(filename_nu)
        fp = utils.getFilesDB()
        fileModelProvider.model.reset(fp)
    
    @QtCore.Slot(str)
    def makePublic(self, filename):
        filename_nu = filename.replace("file://", "")
        utils.makePublic(filename_nu)
        fp = utils.getFilesDB()
        fileModelProvider.model.reset(fp)
    
    @QtCore.Slot(str)
    def makePrivate(self, filename):
        filename_nu = filename.replace("file://", "")
        utils.makePrivate(filename_nu)
        fp = utils.getFilesDB()
        fileModelProvider.model.reset(fp)


mainBackend = MainBackend()


def qtBind(engine):
    mainBackend.engine = engine

    engine.rootContext().setContextProperty("backendWindow", backendWindow)
    engine.rootContext().setContextProperty("contactModelProvider", contactModelProvider)
    engine.rootContext().setContextProperty("fileModelProvider", fileModelProvider)
    engine.rootContext().setContextProperty("mainBackend", mainBackend)

    directory = os.path.dirname(os.path.abspath(__file__))
    engine.load(QtCore.QUrl.fromLocalFile(os.path.join(directory, 'qml/main.qml')))
    if not engine.rootObjects():
        print("Error while enumerating root objects..")


def loadContacts():
    global currContacts
    currContacts = getContactsFromDB()
    contactModelProvider.model.reset([])
    for contact in currContacts:
        contactModelProvider.model.appendRow(contact)


if __name__ == '__main__':
    app = QtGui.QGuiApplication(sys.argv)
    engine = QtQml.QQmlApplicationEngine()
    qtBind(engine)
    loadContacts()
    app.exec_()

