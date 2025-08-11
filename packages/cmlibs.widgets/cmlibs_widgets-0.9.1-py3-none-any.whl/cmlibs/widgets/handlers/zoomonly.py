from cmlibs.zinc.sceneviewerinput import Sceneviewerinput
from cmlibs.widgets.definitions import modifier_map
from cmlibs.widgets.handlers.abstracthandler import AbstractHandler, BUTTON_MAP


class ZoomOnly(AbstractHandler):

    def __init__(self):
        super(ZoomOnly, self).__init__()
        self._zooming = False

    def enter(self):
        pass

    def leave(self):
        pass

    @staticmethod
    def _using_zoom_mouse_button(event):
        return BUTTON_MAP[event.button()] == Sceneviewerinput.BUTTON_TYPE_RIGHT

    def mouse_press_event(self, event):
        super(ZoomOnly, self).mouse_press_event(event)
        self._zooming = self._processing_mouse_events and self._using_zoom_mouse_button(event)
        if self._zooming:
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            x, y = self.get_scaled_event_position(event)
            scene_input.setPosition(int(x + 0.5), int(y + 0.5))
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
            scene_input.setButtonType(BUTTON_MAP[event.button()])
            scene_input.setModifierFlags(modifier_map(event.modifiers()))
            self._scene_viewer.makeCurrent()
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)

    def mouse_move_event(self, event):
        super(ZoomOnly, self).mouse_move_event(event)
        if self._zooming:
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            x, y = self.get_scaled_event_position(event)
            scene_input.setPosition(int(x + 0.5), int(y + 0.5))
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
            self._scene_viewer.makeCurrent()
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)

    def mouse_release_event(self, event):
        super(ZoomOnly, self).mouse_release_event(event)
        if self._zooming:
            self._zooming = False
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            x, y = self.get_scaled_event_position(event)
            scene_input.setPosition(int(x + 0.5), int(y + 0.5))
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
            scene_input.setButtonType(BUTTON_MAP[event.button()])
            self._scene_viewer.makeCurrent()
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)
