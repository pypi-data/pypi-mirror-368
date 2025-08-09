from cmlibs.widgets.handlers.abstracthandler import AbstractHandler


class Fixed(AbstractHandler):

    def __init__(self):
        super(Fixed, self).__init__()

    def enter(self):
        pass

    def leave(self):
        pass

    def mouse_press_event(self, event):
        super(Fixed, self).mouse_press_event(event)

    def mouse_move_event(self, event):
        super(Fixed, self).mouse_move_event(event)

    def mouse_release_event(self, event):
        super(Fixed, self).mouse_release_event(event)
