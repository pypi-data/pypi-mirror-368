from PySide6 import QtCore

from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK
from cmlibs.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_LOCAL

from cmlibs.utils.zinc.field import determine_node_field_derivatives
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.utils.zinc.region import determine_appropriate_glyph_size
from cmlibs.utils.zinc.scene import scene_create_node_derivative_graphics

from cmlibs.widgets.definitions import ManipulationMode
from cmlibs.widgets.errors import HandlerError
from cmlibs.widgets.handlers.keyactivatedhandler import KeyActivatedHandler


class NodeEditor(KeyActivatedHandler):

    def __init__(self, key_code):
        super(NodeEditor, self).__init__(key_code)
        self._model = None
        self._alignKeyPressed = False
        self._align_mode = ManipulationMode.NONE
        self._edit_node = None
        self._edit_graphics = None
        self._edit_coordinate_field = None
        self._edit_vector_field = None
        self._last_mouse_pos = None
        self._pixel_scale = -1.0
        self._node_graphics = []

    def enter(self):
        self._align_mode = ManipulationMode.NONE
        self._pixel_scale = self._scene_viewer.get_pixel_scale()

    def leave(self):
        scene = self._scene_viewer.get_zinc_sceneviewer().getScene()
        with ChangeManager(scene):
            selectionGroup = self._scene_viewer.get_or_create_selection_group()
            selectionGroup.clear()

            while len(self._node_graphics):
                graphic = self._node_graphics.pop(0)
                scene.removeGraphics(graphic)
                del graphic

    def set_model(self, model):
        if hasattr(model, 'getOrCreateMeshEditsNodesetGroup'):
            self._model = model
        else:
            raise HandlerError('Given model does not have the required API for node editing')

    def select_node(self, node):
        nodeset = node.getNodeset()
        fieldmodule = nodeset.getFieldmodule()
        with ChangeManager(fieldmodule):
            selectionGroup = self._scene_viewer.get_or_create_selection_group()
            selectionGroup.clear()
            nodesetGroup = selectionGroup.getOrCreateNodesetGroup(nodeset)
            nodesetGroup.addNode(node)

    def mouse_press_event(self, event):
        if not self._edit_node:
            button = event.button()
            if button == QtCore.Qt.MouseButton.LeftButton:
                event_x = event.x() * self._pixel_scale
                event_y = event.y() * self._pixel_scale
                node = self._scene_viewer.get_nearest_node(event_x, event_y)
                edit_graphics = self._scene_viewer.get_nearest_graphics_node(event_x, event_y)
                if node.isValid() and edit_graphics is not None:
                    # print('NodeEditorSceneviewerWidget.mousePressEvent node:', node.getIdentifier())
                    self.select_node(node)
                    self._edit_node = node
                    self._edit_graphics = edit_graphics
                    self._last_mouse_pos = [event_x, event_y]
                    if len(self._node_graphics) == 0:
                        coordinates = edit_graphics.getCoordinateField()
                        zinc_sceneviewer = self._scene_viewer.get_zinc_sceneviewer()
                        scene = zinc_sceneviewer.getScene()
                        region = scene.getRegion()
                        glyph_width = determine_appropriate_glyph_size(region, coordinates)
                        node_derivative_fields = determine_node_field_derivatives(region, coordinates)
                        self._node_graphics = scene_create_node_derivative_graphics(scene, coordinates, node_derivative_fields, glyph_width, display_node_derivatives=1)

        else:
            self._last_mouse_pos = None

    def mouse_move_event(self, event):
        if self._edit_node:
            mousePos = [event.x() * self._pixel_scale, event.y() * self._pixel_scale]
            nodeset = self._edit_node.getNodeset()
            fieldmodule = nodeset.getFieldmodule()
            with ChangeManager(fieldmodule):
                if self._model is not None:
                    meshEditsNodeset = self._model.getOrCreateMeshEditsNodesetGroup(nodeset)
                    meshEditsNodeset.addNode(self._edit_node)
                editCoordinateField = coordinateField = self._edit_graphics.getCoordinateField()
                localScene = self._edit_graphics.getScene()  # need set local scene to get correct transformation
                if coordinateField.getCoordinateSystemType() != Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN:
                    editCoordinateField = fieldmodule.createFieldCoordinateTransformation(coordinateField)
                    editCoordinateField.setCoordinateSystemType(Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN)
                fieldcache = fieldmodule.createFieldcache()
                fieldcache.setNode(self._edit_node)
                componentsCount = coordinateField.getNumberOfComponents()
                result, initialCoordinates = editCoordinateField.evaluateReal(fieldcache, componentsCount)
                if result == RESULT_OK:
                    for c in range(componentsCount, 3):
                        initialCoordinates.append(0.0)
                    pointattr = self._edit_graphics.getGraphicspointattributes()
                    editVectorField = vectorField = pointattr.getOrientationScaleField()
                    pointBaseSize = pointattr.getBaseSize(3)[1][0]
                    pointScaleFactor = pointattr.getScaleFactors(3)[1][0]
                    if editVectorField.isValid() and (vectorField.getNumberOfComponents() == componentsCount) \
                            and (pointBaseSize == 0.0) and (pointScaleFactor != 0.0):
                        if vectorField.getCoordinateSystemType() != Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN:
                            editVectorField = fieldmodule.createFieldCoordinateTransformation(vectorField, coordinateField)
                            editVectorField.setCoordinateSystemType(Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN)
                        result, initialVector = editVectorField.evaluateReal(fieldcache, componentsCount)
                        for c in range(componentsCount, 3):
                            initialVector.append(0.0)
                        initialTipCoordinates = [(initialCoordinates[c] + initialVector[c] * pointScaleFactor) for c in range(3)]
                        windowCoordinates = self._scene_viewer.project(initialTipCoordinates[0], initialTipCoordinates[1], initialTipCoordinates[2], SCENECOORDINATESYSTEM_LOCAL, localScene)
                        finalTipCoordinates = self._scene_viewer.unproject(mousePos[0], -mousePos[1], windowCoordinates[2], SCENECOORDINATESYSTEM_LOCAL, localScene)
                        finalVector = [(finalTipCoordinates[c] - initialCoordinates[c]) / pointScaleFactor for c in range(3)]
                        result = editVectorField.assignReal(fieldcache, finalVector)
                    else:
                        windowCoordinates = self._scene_viewer.project(initialCoordinates[0], initialCoordinates[1], initialCoordinates[2], SCENECOORDINATESYSTEM_LOCAL, localScene)
                        xa = self._scene_viewer.unproject(self._last_mouse_pos[0], -self._last_mouse_pos[1], windowCoordinates[2], SCENECOORDINATESYSTEM_LOCAL, localScene)
                        xb = self._scene_viewer.unproject(mousePos[0], -mousePos[1], windowCoordinates[2], SCENECOORDINATESYSTEM_LOCAL, localScene)
                        finalCoordinates = [(initialCoordinates[c] + xb[c] - xa[c]) for c in range(3)]
                        result = editCoordinateField.assignReal(fieldcache, finalCoordinates)
                    del editVectorField
                del editCoordinateField
                del fieldcache
            self._last_mouse_pos = mousePos

    def mouse_release_event(self, event):
        self._last_mouse_pos = None
        if self._edit_node:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self._edit_node = None
                self._edit_coordinate_field = None
                self._edit_vector_field = None
