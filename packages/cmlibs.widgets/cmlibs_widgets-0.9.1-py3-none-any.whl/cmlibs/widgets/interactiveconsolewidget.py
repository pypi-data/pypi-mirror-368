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
import sys

from code import InteractiveConsole as CodeInteractiveConsole
from io import StringIO
from PySide6 import QtCore, QtWidgets

from cmlibs.widgets.ui.ui_interactiveconsolewidget import Ui_InteractiveConsoleWidget


class InteractiveConsoleInterpreter(CodeInteractiveConsole):
    """InteractiveConsole subclass that sends all output to the GUI."""

    def __init__(self, ui, local_vars=None):
        CodeInteractiveConsole.__init__(self, local_vars)
        self._ui = ui

    def write(self, data):
        if data:
            if data[-1] == "\n":
                data = data[:-1]
            self._ui.outputPlainTextEdit.appendPlainText(data)

    def runsource(self, source, filename="<input>", symbol="single"):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = sys.stderr = collector = StringIO()
        try:
            more = CodeInteractiveConsole.runsource(self, source, filename, symbol)
        finally:
            if sys.stdout is collector:
                sys.stdout = old_stdout
            if sys.stderr is collector:
                sys.stderr = old_stderr
        self.write(collector.getvalue())
        return more


class InteractiveConsoleWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, local_vars=None):
        super(InteractiveConsoleWidget, self).__init__(parent)
        self._ui = Ui_InteractiveConsoleWidget()
        self._ui.setupUi(self)
        self._interpreter = InteractiveConsoleInterpreter(self._ui, local_vars)
        self._ui.inputLineEdit.installEventFilter(self)
        self._ui.inputLineEdit.returnPressed.connect(self._on_enter_line)
        self._history = []
        self._history_pos = 0
        self._document = None

    def set_document(self, document):
        self._document = document
        self._reset_interpreter()

    def _reset_interpreter(self):
        interpreter_variables = {'context': self._document.getZincContext(), 'document': self._document}
        self._interpreter = InteractiveConsoleInterpreter(self._ui, interpreter_variables)
        self._history = []
        self._history_pos = 0
        self._ui.outputPlainTextEdit.clear()

    def _on_enter_line(self):
        line = self._ui.inputLineEdit.text()
        self._ui.inputLineEdit.setText("")
        self._interpreter.write(self._ui.promptLabel.text() + line)
        more = self._interpreter.push(line)
        if line:
            self._history.append(line)
            self._history_pos = len(self._history)
            while len(self._history) > 100:
                self._history = self._history[1:]
                self._history_pos -= 1
        if more:
            self._ui.promptLabel.setText("... ")
        else:
            self._ui.promptLabel.setText(">>> ")

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Up:
                self.go_history(-1)
            elif event.key() == QtCore.Qt.Key.Key_Down:
                self.go_history(1)
        return False

    def go_history(self, offset):
        if offset < 0:
            self._history_pos = max(0, self._history_pos + offset)
        elif offset > 0:
            self._history_pos = min(len(self._history), self._history_pos + offset)
        try:
            line = self._history[self._history_pos]
        except IndexError:
            line = ""
        self._ui.inputLineEdit.setText(line)
