"""
   Copyright 2015 University of Auckland

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
from functools import wraps

from PySide6 import QtCore, QtWidgets


def set_wait_cursor(f):
    """
    Decorator to a gui action method (e.g. methods in QtGui.QWidget) to
    set and unset a wait cursor and unset after the method is finished.
    """

    @wraps(f)
    def do_wait_cursor(*a, **kw):
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
            QtWidgets.QApplication.processEvents()
            return f(*a, **kw)
        finally:
            # Always unset
            QtWidgets.QApplication.restoreOverrideCursor()
    return do_wait_cursor


def display_vector(widget, values, number_format='{:.5g}'):
    """
    Display real vector values in a widget
    """
    newText = ", ".join(number_format.format(value) for value in values)
    widget.setText(newText)


def parse_int(lineedit):
    """
    Return integer from line edit text, or None if invalid.
    """
    try:
        text = lineedit.text()
        return int(text)
    except ValueError:
        pass

    return None


def _parse_real(text, fail_value, non_negative=False):
    try:
        value = float(text)
        return fail_value if non_negative and value < 0.0 else value
    except ValueError:
        pass

    return fail_value


def parse_real(lineedit):
    """
    Return real value from line edit text, or 0.0 if not a float.
    """
    return _parse_real(lineedit.text(), 0.0)


def parse_real_non_negative(lineedit):
    """
    Return non-negative real value from line edit text, or -1.0 if negative or not a float.
    """
    return _parse_real(lineedit.text(), -1.0, True)


def _parse_vector(text, value_count=None):
    try:
        values = [float(value) for value in text.split(",")]
        if value_count is None or len(values) == value_count:
            return values
    except ValueError:
        pass

    return None


def parse_vector_3(lineedit):
    """
    Return 3 component real vector as list from comma separated text in QLineEdit widget
    or None if invalid.
    """
    return _parse_vector(lineedit.text(), 3)


def parse_vector(lineedit):
    """
    Return one or more component real vector as list from comma separated text in QLineEdit widget
    or None if invalid.
    """
    return _parse_vector(lineedit.text())
