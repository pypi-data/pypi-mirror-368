from PySide6 import QtCore

from cmlibs.maths import vectorops
from cmlibs.widgets.errors import HandlerError
from cmlibs.widgets.handlers.keyactivatedhandler import KeyActivatedHandler


class ModelAlignment(KeyActivatedHandler):

    def __init__(self, key_code):
        super(ModelAlignment, self).__init__(key_code)
        self._model = None
        self._active_button = QtCore.Qt.MouseButton.NoButton
        self._lastMousePos = None

    def set_model(self, model):
        if hasattr(model, 'scaleModel') and hasattr(model, 'rotateModel') and hasattr(model, 'offsetModel'):
            self._model = model
        else:
            raise HandlerError('Given model does not have the required API for alignment')

    def enter(self):
        pass

    def leave(self):
        pass

    def mouse_press_event(self, event):
        self._active_button = event.button()
        if hasattr(self._model, 'interactionStart'):
            self._model.interactionStart()

        if self._active_button == QtCore.Qt.MouseButton.LeftButton and event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
            self._active_button = QtCore.Qt.MouseButton.MiddleButton
        self._lastMousePos = self.get_scaled_event_position(event)

    def mouse_move_event(self, event):
        if self._lastMousePos is not None:
            pos = self.get_scaled_event_position(event)
            delta = [pos[0] - self._lastMousePos[0], pos[1] - self._lastMousePos[1]]
            mag = vectorops.magnitude(delta)
            if mag <= 0.0:
                return
            result, eye = self._zinc_sceneviewer.getEyePosition()
            result, lookat = self._zinc_sceneviewer.getLookatPosition()
            result, up = self._zinc_sceneviewer.getUpVector()
            lookatToEye = vectorops.sub(eye, lookat)
            eyeDistance = vectorops.magnitude(lookatToEye)
            front = vectorops.div(lookatToEye, eyeDistance)
            right = vectorops.cross(up, front)
            if self._active_button == QtCore.Qt.MouseButton.LeftButton:
                prop = vectorops.div(delta, mag)
                axis = vectorops.add(vectorops.mult(up, prop[0]), vectorops.mult(right, prop[1]))
                angle = mag * 0.002
                self._model.rotateModel(axis, angle)
            elif self._active_button == QtCore.Qt.MouseButton.MiddleButton:
                far_plane = self._scene_viewer.unproject(pos[0], -pos[1], -1.0)
                near_plane = self._scene_viewer.unproject(pos[0], -pos[1], 1.0)
                old_far_plane = self._scene_viewer.unproject(self._lastMousePos[0], -self._lastMousePos[1], -1.0)
                old_near_plane = self._scene_viewer.unproject(self._lastMousePos[0], -self._lastMousePos[1], 1.0)
                far = self._zinc_sceneviewer.getFarClippingPlane()
                near = self._zinc_sceneviewer.getNearClippingPlane()

                eye_distance = vectorops.magnitude(lookatToEye)
                fact = (eye_distance - near) / (far - near) if far > near and near <= eye_distance <= far else 0.0

                translate_rate = self._zinc_sceneviewer.getTranslationRate()
                offset_1 = vectorops.mult(vectorops.sub(near_plane, old_near_plane), (1.0 - fact))
                offset_2 = vectorops.mult(vectorops.sub(far_plane, old_far_plane), fact)

                offset = vectorops.mult(vectorops.add(offset_1, offset_2), translate_rate)
                self._model.offsetModel(offset)
            elif self._active_button == QtCore.Qt.MouseButton.RightButton:
                factor = 1.0 + delta[1] * 0.0005
                if factor < 0.9:
                    factor = 0.9
                self._model.scaleModel(factor)
            self._lastMousePos = pos

    def mouse_release_event(self, event):
        self._active_button = QtCore.Qt.MouseButton.NoButton
        if hasattr(self._model, "interactionEnd"):
            self._model.interactionEnd()
        self._lastMousePos = None
