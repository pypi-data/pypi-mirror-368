from PySide6 import QtCore


class InteractionManager:
    handler_activated = QtCore.Signal()
    handler_deactivated = QtCore.Signal()

    def __init__(self):
        self._handlers = {}
        self._key_code_handler_map = {}
        self._active_handler = None
        self._fallback_handler = None

    def register_handler(self, handler):
        if handler is None:
            return

        handler.set_scene_viewer(self)
        self._handlers[handler.get_mode()] = handler

        if hasattr(handler, 'get_key_code'):
            key_code = handler.get_key_code()
            self._key_code_handler_map[key_code] = handler

        if self._fallback_handler is None:
            self._fallback_handler = handler
            self._activate_handler(handler)

    def clear_active_handler(self):
        self.unregister_handler(self._active_handler)

    def unregister_handler(self, handler):
        if handler is None:
            return

        # Check to make sure we are not trying to unregister the fallback handler, that is a no-no.
        # But, we also check to make sure that the handler to unregister is actually registered in the first place.
        if handler != self._fallback_handler and handler.get_mode() in self._handlers:
            self._handlers.pop(handler.get_mode())

            if hasattr(handler, 'get_key_code'):
                key_code = handler.get_key_code()
                self._key_code_handler_map.pop(key_code)

            if self._active_handler == handler:
                self._active_handler = self._fallback_handler

    def set_fallback_handler(self, fallback_handler):
        self._fallback_handler = fallback_handler

    def active_handler(self):
        return self._active_handler

    def _activate_handler(self, handler):
        if not handler.is_enabled():
            return

        if self._active_handler:
            self._active_handler.leave()
            self.handler_deactivated.emit()
        self._active_handler = handler
        self._active_handler.enter()
        self.handler_activated.emit()

    def key_press_event(self, event):
        if event.key() in self._key_code_handler_map and not event.isAutoRepeat():
            event.accept()
            self._activate_handler(self._key_code_handler_map[event.key()])
        else:
            event.ignore()

    def key_release_event(self, event):
        if event.key() in self._key_code_handler_map and not event.isAutoRepeat():
            if self._key_code_handler_map[event.key()] == self._active_handler:
                event.accept()
                self._activate_handler(self._fallback_handler)
            else:
                event.ignore()
        else:
            event.ignore()

    def mouse_enter_event(self, event):
        if self._active_handler is not None:
            self._active_handler.mouse_enter_event(event)

    def mouse_leave_event(self, event):
        if self._active_handler is not None:
            self._active_handler.mouse_leave_event(event)

    def mouse_press_event(self, event):
        if self._active_handler is not None:
            self._active_handler.mouse_press_event(event)

    def mouse_release_event(self, event):
        if self._active_handler is not None:
            self._active_handler.mouse_release_event(event)

    def mouse_move_event(self, event):
        if self._active_handler is not None:
            self._active_handler.mouse_move_event(event)

    def focus_out_event(self, event):
        self._activate_handler(self._fallback_handler)
