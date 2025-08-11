from enum import Enum

from PySide6 import QtCore

from cmlibs.zinc.sceneviewerinput import Sceneviewerinput

SELECTION_GROUP_NAME = '.scene_selection'
SELECTION_RUBBERBAND_NAME = 'selection_rubberband'

# mapping from qt to zinc start
# Create a button map of Qt mouse buttons to Zinc input buttons
BUTTON_MAP = {
    QtCore.Qt.MouseButton.LeftButton: Sceneviewerinput.BUTTON_TYPE_LEFT,
    QtCore.Qt.MouseButton.MiddleButton: Sceneviewerinput.BUTTON_TYPE_MIDDLE,
    QtCore.Qt.MouseButton.RightButton: Sceneviewerinput.BUTTON_TYPE_RIGHT,
    QtCore.Qt.MouseButton.NoButton: None}


# Create a modifier map of Qt modifier keys to Zinc modifier keys
def modifier_map(qt_modifiers):
    """
    Return a Zinc Sceneviewerinput modifiers object that is created from
    the Qt modifier flags passed in.
    """
    modifiers = Sceneviewerinput.MODIFIER_FLAG_NONE

    if qt_modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
        modifiers = modifiers | Sceneviewerinput.MODIFIER_FLAG_SHIFT

    return modifiers


class ProjectionMode(Enum):
    PARALLEL = 0
    PERSPECTIVE = 1


class SelectionMode(Enum):
    NONE = -1
    EXCLUSIVE = 0
    ADDITIVE = 1
    INTERSECTION = 2


class GraphicsSelectionMode(Enum):
    ANY = -1
    DATA = 0
    ELEMENTS = 1
    NODE = 2


class ManipulationMode(Enum):
    NONE = 0
    ROTATION = 1
    SCALE = 2
    TRANSLATION = 3

