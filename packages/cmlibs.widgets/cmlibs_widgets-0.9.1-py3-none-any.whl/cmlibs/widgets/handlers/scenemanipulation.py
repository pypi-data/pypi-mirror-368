from cmlibs.zinc.sceneviewerinput import Sceneviewerinput

from cmlibs.widgets.definitions import BUTTON_MAP, modifier_map
from cmlibs.widgets.handlers.abstracthandler import AbstractHandler


class SceneManipulation(AbstractHandler):

    def enter(self):
        pass

    def leave(self):
        pass

    def mouse_press_event(self, event):
        super(SceneManipulation, self).mouse_press_event(event)
        if self._processing_mouse_events:
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            x, y = self.get_scaled_event_position(event)
            scene_input.setPosition(int(x + 0.5), int(y + 0.5))
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_PRESS)
            scene_input.setButtonType(BUTTON_MAP[event.button()])
            scene_input.setModifierFlags(modifier_map(event.modifiers()))
            self._scene_viewer.makeCurrent()
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)

    def mouse_move_event(self, event):
        super(SceneManipulation, self).mouse_move_event(event)
        if self._processing_mouse_events:
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            x, y = self.get_scaled_event_position(event)
            scene_input.setPosition(int(x + 0.5), int(y + 0.5))
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_MOTION_NOTIFY)
            self._scene_viewer.makeCurrent()
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)

    def mouse_release_event(self, event):
        super(SceneManipulation, self).mouse_release_event(event)
        if self._processing_mouse_events:
            scene_input = self._zinc_sceneviewer.createSceneviewerinput()
            x, y = self.get_scaled_event_position(event)
            scene_input.setPosition(int(x + 0.5), int(y + 0.5))
            scene_input.setEventType(Sceneviewerinput.EVENT_TYPE_BUTTON_RELEASE)
            scene_input.setButtonType(BUTTON_MAP[event.button()])
            self._scene_viewer.makeCurrent()
            self._zinc_sceneviewer.processSceneviewerinput(scene_input)
