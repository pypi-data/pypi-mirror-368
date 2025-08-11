"""
   Copyright 2016 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from PySide6 import QtGui, QtWidgets

from cmlibs.widgets.ui.ui_logviewerwidget import Ui_LogViewerWidget
from cmlibs.argon.argonlogger import CustomStream


class LogViewerWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._ui = Ui_LogViewerWidget()
        self._ui.setupUi(self)

        self._make_connections()

    def writeMessage(self, message, levelstring):
        if levelstring == "ERROR":
            self._ui.logText.setTextColor(QtGui.QColor(255, 0, 0))
        elif levelstring == "WARNING":
            self._ui.logText.setTextColor(QtGui.QColor(255, 100, 0))
        elif levelstring == "INFORMATION":
            self._ui.logText.setTextColor(QtGui.QColor(0, 0, 0))
        self._ui.logText.insertPlainText(message)

    def _make_connections(self):
        stdout = CustomStream.stdout()
        stderr = CustomStream.stderr()
        if hasattr(stdout, 'messageWritten'):
            stdout.messageWritten.connect(self.writeMessage)
        if hasattr(stderr, 'messageWritten'):
            stderr.messageWritten.connect(self.writeMessage)

    def copyToClipboard(self):
        QtGui.QGuiApplication.clipboard().setText(self._ui.logText.toPlainText())

    def clearAll(self):
        self._ui.logText.clear()
