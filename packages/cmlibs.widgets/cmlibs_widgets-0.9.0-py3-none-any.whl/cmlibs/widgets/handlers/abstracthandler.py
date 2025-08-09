from cmlibs.widgets.definitions import BUTTON_MAP


class AbstractHandler:

    def __init__(self):
        self._scene_viewer = None
        self._zinc_sceneviewer = None
        self._ignore_mouse_events = False
        self._processing_mouse_events = False
        self._enabled = True

    def get_mode(self):
        return self.__class__.__name__

    def set_enabled(self, state):
        self._enabled = state

    def is_enabled(self):
        return self._enabled

    def set_ignore_mouse_events(self, value=True):
        self._ignore_mouse_events = value

    def set_scene_viewer(self, scene_viewer):
        self._scene_viewer = scene_viewer
        if self._scene_viewer.is_graphics_initialized():
            self._graphics_ready()
        else:
            self._scene_viewer.graphics_initialized.connect(self._graphics_ready)

    def enter(self):
        raise NotImplementedError()

    def leave(self):
        raise NotImplementedError()

    def mouse_press_event(self, event):
        self._processing_mouse_events = False
        if self._ignore_mouse_events:
            event.ignore()
            return

        if event.button() not in BUTTON_MAP:
            return

        event.accept()
        self._processing_mouse_events = True

    def mouse_move_event(self, event):
        if self._ignore_mouse_events:
            event.ignore()
            return

        event.accept()

    def mouse_release_event(self, event):
        if self._ignore_mouse_events:
            event.ignore()
            return

        if event.button() not in BUTTON_MAP:
            return

        event.accept()

    def mouse_enter_event(self, event):
        if self._ignore_mouse_events:
            event.ignore()
            return

        event.accept()

    def mouse_leave_event(self, event):
        if self._ignore_mouse_events:
            event.ignore()
            return

        event.accept()

    def focus_out_event(self, event):
        pass

    def _graphics_ready(self):
        self._zinc_sceneviewer = self._scene_viewer.get_zinc_sceneviewer()

    def get_scaled_event_position(self, event):
        pixel_scale = self._scene_viewer.get_pixel_scale()
        return event.x() * pixel_scale, event.y() * pixel_scale
