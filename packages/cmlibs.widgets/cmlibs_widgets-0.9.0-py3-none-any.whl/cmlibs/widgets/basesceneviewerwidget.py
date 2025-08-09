"""
Zinc Sceneviewer Widget

Implements a Zinc Sceneviewer Widget on Python using PySide or PyQt,
which renders the Zinc Scene with OpenGL and allows interactive
transformation of the view.
Widget is derived from QtOpenGL.QGLWidget.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
# This python module is intended to facilitate users creating their own applications that use Zinc
# See the examples at https://svn.physiomeproject.org/svn/cmiss/zinc/bindings/trunk/python/ for further
# information.
from PySide6 import QtCore, QtOpenGLWidgets, QtGui

from cmlibs.zinc.sceneviewer import Sceneviewer, Sceneviewerevent
from cmlibs.zinc.scenecoordinatesystem import \
    SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, \
    SCENECOORDINATESYSTEM_WORLD
from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK

from cmlibs.utils.zinc.scene import scene_get_or_create_selection_group, scene_clear_selection_group
from cmlibs.widgets.handlers.interactionmanager import InteractionManager
from cmlibs.widgets.definitions import ProjectionMode


class BaseSceneviewerWidget(QtOpenGLWidgets.QOpenGLWidget, InteractionManager):
    # Create a signal to notify when the OpenGL scene is ready.
    graphics_initialized = QtCore.Signal()
    pixel_scale_changed = QtCore.Signal(float)
    became_active = QtCore.Signal()

    def __init__(self, parent=None):
        """
        Call the super class init functions, set the  Zinc context and the scene viewer handle to None.
        Initialise other attributes that deal with selection and the rotation of the plane.
        """
        QtOpenGLWidgets.QOpenGLWidget.__init__(self, parent)
        InteractionManager.__init__(self)
        # Create a Zinc context from which all other objects can be derived either directly or indirectly.
        self._graphics_initialized = False
        self._context = None
        self._sceneviewer = None
        self._scene_picker = None
        self._is_active = False
        self._grab_focus = False

        # Client-specified filter which is used in logical AND with sceneviewer filter in selection
        self._selection_filter = None
        self._selection_tolerance = 3.0  # Number of pixels to set the selection tolerance to.
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self._pixel_scale = 1.0
        self._width = -1
        self._height = -1
        self._border_pen = QtGui.QPen(QtGui.QBrush(QtCore.Qt.GlobalColor.magenta), 2)

    def set_context(self, context):
        """
        Sets the context for this Zinc scene viewer widget. Prompts creation of a new Zinc
        scene viewer, once graphics are initialised.
        """
        self._context = context
        if self._graphics_initialized:
            self._create_sceneviewer()

    def get_context(self):
        if self._context is not None:
            return self._context
        else:
            raise RuntimeError("Zinc context has not been set in base scene viewer widget.")

    def set_scene(self, scene):
        if self._sceneviewer is not None:
            self._sceneviewer.setScene(scene)
            self._scene_picker = scene.createScenepicker()
            self.set_selection_filter(self._selection_filter)

    def set_border_colour(self, colour):
        self._border_pen = QtGui.QPen(QtGui.QBrush(colour), 2)

    def set_border_off(self):
        self._border_pen = None

    def set_grab_focus(self, grab_focus):
        self._grab_focus = grab_focus

    def set_active_state(self, state):
        self._is_active = state
        self.update()

    def get_pixel_scale(self):
        return self._pixel_scale

    def get_zinc_sceneviewer(self):
        """
        Get the scene viewer for this ZincWidget.
        """
        return self._sceneviewer

    def is_graphics_initialized(self):
        return self._graphics_initialized

    def set_projection_mode(self, mode):
        if mode == ProjectionMode.PARALLEL:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PARALLEL)
        elif mode == ProjectionMode.PERSPECTIVE:
            self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)

    def get_projection_mode(self):
        if self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PARALLEL:
            return ProjectionMode.PARALLEL
        elif self._sceneviewer.getProjectionMode() == Sceneviewer.PROJECTION_MODE_PERSPECTIVE:
            return ProjectionMode.PERSPECTIVE

    def get_view_parameters(self):
        result, eye, lookat, up = self._sceneviewer.getLookatParameters()
        if result == RESULT_OK:
            angle = self._sceneviewer.getViewAngle()
            return eye, lookat, up, angle

        return None

    def set_view_parameters(self, eye, lookat, up, angle):
        self._sceneviewer.beginChange()
        self._sceneviewer.setLookatParametersNonSkew(eye, lookat, up)
        self._sceneviewer.setViewAngle(angle)
        self._sceneviewer.endChange()

    def set_scenefilter(self, scenefilter):
        self._sceneviewer.setScenefilter(scenefilter)

    def get_scenefilter(self):
        return self._sceneviewer.getScenefilter()

    def get_scenepicker(self):
        return self._scene_picker

    def set_scenepicker(self, scenepicker):
        self._scene_picker = scenepicker

    def set_picking_rectangle(self, coordinate_system, left, bottom, right, top):
        self._scene_picker.setSceneviewerRectangle(self._sceneviewer, coordinate_system, left, bottom, right, top)

    def set_selection_filter(self, scene_filter):
        """
        Set filter to be applied in logical AND with sceneviewer filter during selection
        """
        self._selection_filter = scene_filter
        scene_viewer_filter = self._sceneviewer.getScenefilter()
        if self._selection_filter is not None:
            scene_filter_module = self._context.getScenefiltermodule()
            scene_filter = scene_filter_module.createScenefilterOperatorAnd()
            scene_filter.appendOperand(scene_viewer_filter)
            if self._selection_filter is not None:
                scene_filter.appendOperand(self._selection_filter)
        else:
            scene_filter = scene_viewer_filter
        self._scene_picker.setScenefilter(scene_filter)

    def get_selection_filter(self):
        return self._selection_filter

    def project(self, x, y, z, reference_coordinates=SCENECOORDINATESYSTEM_WORLD, local_scene=None):
        """
        Project the given point in global coordinates into window pixel coordinates
        with the origin at the window's top left pixel.
        Note the z pixel coordinate is a depth which is mapped so that -1 is
        on the far clipping plane, and +1 is on the near clipping plane.
        """
        in_coordinates = [x, y, z]
        reference_scene = self._sceneviewer.getScene() if local_scene is None else local_scene
        result, out_coordinates = self._sceneviewer.transformCoordinates(reference_coordinates, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, reference_scene,
                                                                         in_coordinates)
        if result == RESULT_OK:
            return out_coordinates  # [out_coordinates[0] / out_coordinates[3], out_coordinates[1] / out_coordinates[3], out_coordinates[2] / out_coordinates[3]]

        return None

    def unproject(self, x, y, z, reference_coordinates=SCENECOORDINATESYSTEM_WORLD, local_scene=None):
        """
        Unproject the given point in window pixel coordinates where the origin is
        at the window's top left pixel into global coordinates.
        Note the z pixel coordinate is a depth which is mapped so that -1 is
        on the far clipping plane, and +1 is on the near clipping plane.
        """
        in_coordinates = [x, y, z]
        reference_scene = self._sceneviewer.getScene() if local_scene is None else local_scene
        result, out_coordinates = self._sceneviewer.transformCoordinates(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT, reference_coordinates, reference_scene,
                                                                         in_coordinates)
        if result == RESULT_OK:
            return out_coordinates  # [out_coordinates[0] / out_coordinates[3], out_coordinates[1] / out_coordinates[3], out_coordinates[2] / out_coordinates[3]]

        return None

    def get_viewport_size(self):
        result, width, height = self._sceneviewer.getViewportSize()
        if result == RESULT_OK:
            return width, height

        return None

    def set_tumble_rate(self, rate):
        self._sceneviewer.setTumbleRate(rate)

    def get_picking_volume_centre(self):
        result, centre = self._scene_picker.getPickingVolumeCentre()
        if result == RESULT_OK:
            return centre

        return None

    def _set_scene_picker_rect(self, x, y):
        self._scene_picker.setSceneviewerRectangle(self._sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                   x - self._selection_tolerance, y - self._selection_tolerance,
                                                   x + self._selection_tolerance, y + self._selection_tolerance)

    def _get_nearest_graphic(self, x, y, domain_type):
        self._set_scene_picker_rect(x, y)
        nearest_graphics = self._scene_picker.getNearestGraphics()
        if nearest_graphics.isValid() and nearest_graphics.getFieldDomainType() == domain_type:
            return nearest_graphics

        return None

    def get_nearest_graphics(self):
        return self._scene_picker.getNearestGraphics()

    def get_nearest_graphics_node(self, x, y):
        self._set_scene_picker_rect(x, y)
        return self._scene_picker.getNearestNodeGraphics()

    def get_nearest_graphics_point(self, x, y):
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_POINT)

    def get_nearest_graphics_datapoint(self, x, y):
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_DATAPOINTS)

    def get_nearest_graphics_element(self, x, y):
        self._set_scene_picker_rect(x, y)
        return self._scene_picker.getNearestElementGraphics()

    def get_nearest_element(self, x, y):
        self._set_scene_picker_rect(x, y)
        return self._scene_picker.getNearestElement()

    def get_nearest_graphics_mesh_3d(self, x, y):
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_MESH3D)

    def get_nearest_graphics_mesh_2d(self, x, y):
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_MESH2D)

    def get_nearest_graphics_mesh_1d(self, x, y):
        return self._get_nearest_graphic(x, y, Field.DOMAIN_TYPE_MESH1D)

    def get_nearest_node(self, x, y):
        self._set_scene_picker_rect(x, y)
        return self._scene_picker.getNearestNode()

    def add_picked_nodes_to_field_group(self, selection_group):
        self._scene_picker.addPickedNodesToFieldGroup(selection_group)

    def view_all(self):
        """
        Helper method to set the current scene viewer to view everything
        visible in the current scene.
        """
        self._sceneviewer.viewAll()

    def _zinc_sceneviewer_event(self, event):
        """
        Process a scene viewer event.  The update() method is called for a
        repaint required event all other events are ignored.
        """
        if event.getChangeFlags() & Sceneviewerevent.CHANGE_FLAG_REPAINT_REQUIRED:
            QtCore.QTimer.singleShot(0, self.update)

    #  Not applicable at the current point in time.
    #     def _zincSelectionEvent(self, event):
    #         print(event.getChangeFlags())
    #         print('go the selection change')

    def _create_sceneviewer(self):
        # From the scene viewer module we can create a scene viewer, we set up the
        # scene viewer to have the same OpenGL properties as the QGLWidget.
        scene_viewer_module = self._context.getSceneviewermodule()
        self._sceneviewer = scene_viewer_module.createSceneviewer(Sceneviewer.BUFFERING_MODE_DOUBLE,
                                                                  Sceneviewer.STEREO_MODE_DEFAULT)
        self._sceneviewer.setProjectionMode(Sceneviewer.PROJECTION_MODE_PERSPECTIVE)
        self._sceneviewer.setViewportSize(int(self.width() * self._pixel_scale + 0.5), int(self.height() * self._pixel_scale + 0.5))

        # Get the default scene filter, which filters by visibility flags
        scene_filter_module = self._context.getScenefiltermodule()
        scene_filter = scene_filter_module.getDefaultScenefilter()
        self._sceneviewer.setScenefilter(scene_filter)

        region = self._context.getDefaultRegion()
        scene = region.getScene()
        self.set_scene(scene)

        self._sceneviewer_notifier = self._sceneviewer.createSceneviewernotifier()
        self._sceneviewer_notifier.setCallback(self._zinc_sceneviewer_event)

        self._sceneviewer.viewAll()

    def clear_selection(self):
        """
        If there is a selection group, clears it and removes it from scene.
        """
        scene = self._sceneviewer.getScene()
        scene_clear_selection_group(scene)

    def get_or_create_selection_group(self):
        scene = self._sceneviewer.getScene()
        return scene_get_or_create_selection_group(scene)

    def _update_pixel_scale(self, pixel_scale):
        changed = False
        if pixel_scale != self._pixel_scale:
            self._pixel_scale = pixel_scale
            self.pixel_scale_changed.emit(self._pixel_scale)
            changed = True

        return changed

    def _update_viewport_size(self, width, height):
        if self._update_pixel_scale(self.devicePixelRatio()) or width != self._width or height != self._height:
            self._width = width
            self._height = height
            self._sceneviewer.setViewportSize(int(width * self._pixel_scale + 0.5), int(height * self._pixel_scale + 0.5))

    def paintEvent(self, event):
        super(BaseSceneviewerWidget, self).paintEvent(event)

        if self._is_active and self._border_pen:
            painter = QtGui.QPainter(self)
            painter.setPen(self._border_pen)
            painter.drawRect(QtCore.QRect(1, 1, self.width() - 2, self.height() - 2))

    def focusInEvent(self, event) -> None:
        super(QtOpenGLWidgets.QOpenGLWidget, self).focusInEvent(event)
        if not self._is_active:
            self._is_active = True
            self.became_active.emit()

    def initializeGL(self):
        """
        The OpenGL context is ready for use. If Zinc Context has been set, create Zinc Sceneviewer, otherwise
        inform client who is required to set Context at a later time.
        """
        self._graphics_initialized = True
        self._update_pixel_scale(self.devicePixelRatio())
        if self._context:
            self._create_sceneviewer()
        self.graphics_initialized.emit()

    def paintGL(self):
        """
        Render the scene for this scene viewer.  The QOpenGLWidget has already set up the
        correct OpenGL buffer for us so all we need do is render into it.  The scene viewer
        will clear the background so any OpenGL drawing of your own needs to go after this
        API call.
        """
        if self._sceneviewer:
            # handle change of device pixel ratio when window moved between screens:
            self._update_viewport_size(self.width(), self.height())
            self._sceneviewer.renderScene()

    def resizeGL(self, width, height):
        """
        Respond to widget resize events.
        """
        if self._sceneviewer:
            self._update_viewport_size(width, height)

    def keyPressEvent(self, event):
        self.key_press_event(event)

    def keyReleaseEvent(self, event):
        self.key_release_event(event)

    def enterEvent(self, event):
        self.mouse_enter_event(event)
        if self._grab_focus:
            self.setFocus()

    def leaveEvent(self, event):
        self.mouse_leave_event(event)

    def mousePressEvent(self, event):
        self.mouse_press_event(event)

    def mouseMoveEvent(self, event):
        self.mouse_move_event(event)

    def mouseReleaseEvent(self, event):
        self.mouse_release_event(event)

    def focusOutEvent(self, event):
        self.focus_out_event(event)
