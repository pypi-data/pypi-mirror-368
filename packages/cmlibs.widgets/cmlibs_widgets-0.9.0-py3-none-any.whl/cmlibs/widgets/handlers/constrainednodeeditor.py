from PySide6 import QtCore

from cmlibs.zinc.field import Field, FieldFindMeshLocation
from cmlibs.zinc.glyph import Glyph
from cmlibs.zinc.graphics import Graphics
from cmlibs.zinc.node import Node
from cmlibs.zinc.result import RESULT_OK
from cmlibs.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_LOCAL

from cmlibs.maths.vectorops import sub, add, div, cross, axis_angle_to_rotation_matrix, matrix_mult, reshape, magnitude, mult
from cmlibs.utils.zinc.finiteelement import create_nodes, get_highest_dimension_mesh
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.utils.zinc.region import determine_appropriate_glyph_size
from cmlibs.utils.zinc.scene import scene_get_or_create_selection_group

from cmlibs.widgets.definitions import ManipulationMode
from cmlibs.widgets.errors import HandlerError
from cmlibs.widgets.handlers.keyactivatedhandler import KeyActivatedHandler


def _get_adjacent_elements(element):
    mesh = element.getMesh()
    field_module = mesh.getFieldmodule()
    adjacent_elements = []
    with ChangeManager(field_module):
        field_group = field_module.createFieldGroup()
        field_group.setName('the_group')
        # field_group.setSubelementHandlingMode(FieldGroup.SUBELEMENT_HANDLING_MODE_FULL)
        mesh_group = field_group.createMeshGroup(mesh)
        mesh_group.addElement(element)
        mesh_group.addAdjacentElements(-1)
        element_iterator = mesh_group.createElementiterator()
        adjacent_element = element_iterator.next()
        while adjacent_element.isValid():
            adjacent_elements.append(adjacent_element)
            adjacent_element = element_iterator.next()

    return adjacent_elements


def _determine_highest_level_elements(current_element):
    highest_level_elements = []
    for i in range(current_element.getNumberOfParents()):
        parent_element = current_element.getParentElement(i + 1)
        if parent_element.getNumberOfParents() == 0 and parent_element not in highest_level_elements:
            highest_level_elements.append(parent_element)
        else:
            for j in range(parent_element.getNumberOfParents()):
                grand_parent_element = parent_element.getParentElement(j + 1)
                if grand_parent_element.getNumberOfParents() == 0 and grand_parent_element not in highest_level_elements:
                    highest_level_elements.append(grand_parent_element)

    return highest_level_elements


class ConstrainedNodeEditor(KeyActivatedHandler):

    def __init__(self, key_code):
        super(ConstrainedNodeEditor, self).__init__(key_code)
        self._model = None
        self._alignKeyPressed = False
        self._align_mode = ManipulationMode.NONE

        self._edit_node = None
        self._edit_graphics = None
        self._edit_element_info = None

        self._last_mouse_pos = None
        self._pixel_scale = -1.0

        self._find_mesh_location_field = None
        self._find_mesh_search_cache = {}
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
                graphic_scene = graphic.getScene()
                graphic_scene.removeGraphics(graphic)
                del graphic

    def set_model(self, model):
        if hasattr(model, 'new') and hasattr(model, 'update') and hasattr(model, 'parameter'):
            self._model = model
        else:
            raise HandlerError('Given model does not have the required API for node editing')

    def _get_search_elements(self):
        if self._edit_element_info[0] in self._find_mesh_search_cache:
            return self._find_mesh_search_cache[self._edit_element_info[0]]

        element = self._get_element_with_info()
        search_elements = []
        new_elements = _get_adjacent_elements(element)
        for new_element in new_elements:
            if new_element not in search_elements:
                search_elements.append(new_element)

        self._find_mesh_search_cache[self._edit_element_info[0]] = search_elements
        return search_elements

    def _get_element_with_info(self):
        fm = self._find_mesh_location_field.getFieldmodule()
        mesh = fm.findMeshByDimension(self._edit_element_info[1])
        return mesh.findElementByIdentifier(self._edit_element_info[0])

    def _select_node(self, node):
        nodeset = node.getNodeset()
        fm = nodeset.getFieldmodule()
        with ChangeManager(fm):
            selection_group = self._scene_viewer.get_or_create_selection_group()
            selection_group.clear()
            nodeset_group = selection_group.getOrCreateNodesetGroup(nodeset)
            nodeset_group.addNode(node)

    def _fix_node_to_mesh(self, fc, node, coordinates):
        mesh = self._find_mesh_location_field.getMesh()
        found_element, xi = self._find_mesh_location_field.evaluateMeshLocation(fc, mesh.getDimension())
        if found_element.isValid():
            fc.setMeshLocation(found_element, xi)
            result, values = coordinates.evaluateReal(fc, 3)
            fc.setNode(node)
            if self._model:
                element_info = (found_element.getIdentifier(), found_element.getDimension())
                self._model.update(node, parameter='element_info', payload=element_info)
                self._edit_element_info = element_info

            coordinates.assignReal(fc, values)
            return True

        return False

    def mouse_press_event(self, event):
        button = event.button()
        if button == QtCore.Qt.MouseButton.LeftButton:
            event_x = event.x() * self._pixel_scale
            event_y = event.y() * self._pixel_scale

            self._scene_viewer.makeCurrent()
            datapoint = self._scene_viewer.get_nearest_node(event_x, event_y)
            element = self._scene_viewer.get_nearest_element(event_x, event_y)
            datapoint_graphics = self._scene_viewer.get_nearest_graphics_datapoint(event_x, event_y)
            edit_graphics = self._scene_viewer.get_nearest_graphics_element(event_x, event_y)
            if datapoint.isValid() and datapoint_graphics is not None:
                self._last_mouse_pos = [event_x, event_y]
                self._edit_node = datapoint
                self._edit_graphics = datapoint_graphics
                self._edit_element_info = None
                if self._model:
                    self._edit_element_info = self._model.parameter(datapoint, name='element_info')

                if len(self._node_graphics) == 0:
                    coordinates = datapoint_graphics.getCoordinateField()
                    fm = coordinates.getFieldmodule()
                    region = fm.getRegion()
                    scene = datapoint_graphics.getScene()
                    glyph_width = determine_appropriate_glyph_size(region, coordinates)
                    default_orientation = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                    with ChangeManager(fm):
                        scale_field = fm.createFieldConstant([1, 1, 1])
                        orientation_field = fm.createFieldConstant(reshape(default_orientation, 9))

                    if self._model:
                        orientation_field = self._model.parameter(datapoint, name='orientation')
                        scale_field = self._model.parameter(datapoint, name='orientation_scale')

                    self._node_graphics = _create_orientation_axes(scene, coordinates, glyph_width, orientation_field, domain=Field.DOMAIN_TYPE_DATAPOINTS, scale_field=scale_field)

                    if self._model:
                        label_field = self._model.parameter(datapoint, name='label')
                        self._node_graphics.append(_create_label_graphic(scene, coordinates, glyph_width, label_field, domain=Field.DOMAIN_TYPE_DATAPOINTS))

                self._select_node(datapoint)
            elif element.isValid() and edit_graphics is not None and datapoint_graphics is None:
                self._last_mouse_pos = [event_x, event_y]

                coordinates = edit_graphics.getCoordinateField()
                fm = coordinates.getFieldmodule()
                scene = edit_graphics.getScene()

                far_location = self._scene_viewer.unproject(event_x, -event_y, -1.0)
                near_location = self._scene_viewer.unproject(event_x, -event_y, 1.0)
                initial_location = div(add(near_location, far_location), 2.0)

                with ChangeManager(fm):
                    fc = fm.createFieldcache()
                    created_nodes = create_nodes(coordinates, [initial_location], 'datapoints')

                    if len(created_nodes) == 1:
                        placing_node = created_nodes[0]
                    else:
                        print('bad things.')

                    if self._find_mesh_location_field is None:
                        highest_dimension_mesh = get_highest_dimension_mesh(fm)
                        self._find_mesh_location_field = fm.createFieldFindMeshLocation(coordinates, coordinates, highest_dimension_mesh)
                        self._find_mesh_location_field.setSearchMode(FieldFindMeshLocation.SEARCH_MODE_NEAREST)

                    fc.setNode(placing_node)
                    selection_group = scene_get_or_create_selection_group(scene)
                    highest_level_elements = _determine_highest_level_elements(element)
                    element = highest_level_elements[0]
                    mesh_group = selection_group.getOrCreateMeshGroup(element.getMesh())
                    mesh_group.addElement(element)
                    self._find_mesh_location_field.setSearchMesh(mesh_group)
                    self._fix_node_to_mesh(fc, placing_node, coordinates)
                    if self._model:
                        self._model.new(placing_node, coordinates, element.getIdentifier(), element.getDimension())

                    selection_group.clear()
                    del mesh_group
                    del selection_group
        else:
            self._last_mouse_pos = None

    def mouse_move_event(self, event):
        if self._edit_node:
            mousePos = self.get_scaled_event_position(event)
            update_last_mouse_pos = True
            nodeset = self._edit_node.getNodeset()
            fieldmodule = nodeset.getFieldmodule()
            with ChangeManager(fieldmodule):
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
                    point_attr = self._edit_graphics.getGraphicspointattributes()
                    editVectorField = vectorField = point_attr.getOrientationScaleField()
                    pointBaseSize = point_attr.getBaseSize(3)[1][0]
                    pointScaleFactor = point_attr.getScaleFactors(3)[1][0]
                    if editVectorField.isValid() and (vectorField.getNumberOfComponents() == 3 * componentsCount) \
                            and (pointBaseSize == 0.0) and (pointScaleFactor != 0.0):
                        if vectorField.getCoordinateSystemType() != Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN:
                            editVectorField = fieldmodule.createFieldCoordinateTransformation(vectorField, coordinateField)
                            editVectorField.setCoordinateSystemType(Field.COORDINATE_SYSTEM_TYPE_RECTANGULAR_CARTESIAN)
                        result, initialVector = editVectorField.evaluateReal(fieldcache, 3 * componentsCount)
                        # initialTipCoordinates = [(initialCoordinates[c] + initialVector[c] * pointScaleFactor) for c in range(3)]
                        # initial_position = self._scene_viewer.unproject(self._last_mouse_pos[0], -self._last_mouse_pos[1], -1.0, SCENECOORDINATESYSTEM_LOCAL, localScene)
                        # final_position = self._scene_viewer.unproject(mousePos[0], -mousePos[1], -1.0, SCENECOORDINATESYSTEM_LOCAL, localScene)
                        # finalVector = [(finalTipCoordinates[c] - initialCoordinates[c]) / pointScaleFactor for c in range(3)]
                        delta = sub(self._last_mouse_pos, mousePos)
                        mag = magnitude(delta)
                        if mag == 0.0:
                            update_last_mouse_pos = False
                        else:
                            result, eye = self._zinc_sceneviewer.getEyePosition()
                            result, lookat = self._zinc_sceneviewer.getLookatPosition()
                            result, up = self._zinc_sceneviewer.getUpVector()
                            lookatToEye = sub(eye, lookat)
                            eyeDistance = magnitude(lookatToEye)
                            front = div(lookatToEye, eyeDistance)
                            right = cross(up, front)
                            prop = div(delta, mag)
                            axis = add(mult(up, prop[0]), mult(right, prop[1]))
                            theta = mag * 0.002
                            # theta = 10*angle(final_position, initial_position)
                            # axis = normalize(cross(initial_position, final_position))
                            mx = axis_angle_to_rotation_matrix(axis, theta)
                            final_vector = matrix_mult(mx, reshape(initialVector, (3, 3)))
                            result = editVectorField.assignReal(fieldcache, reshape(final_vector, 9))
                            if self._model:
                                self._model.update(self._edit_node, parameter='orientation')
                    elif self._edit_element_info is not None:
                        windowCoordinates = self._scene_viewer.project(initialCoordinates[0], initialCoordinates[1], initialCoordinates[2], SCENECOORDINATESYSTEM_LOCAL, localScene)
                        xa = self._scene_viewer.unproject(self._last_mouse_pos[0], -self._last_mouse_pos[1], windowCoordinates[2], SCENECOORDINATESYSTEM_LOCAL, localScene)
                        xb = self._scene_viewer.unproject(mousePos[0], -mousePos[1], windowCoordinates[2], SCENECOORDINATESYSTEM_LOCAL, localScene)
                        finalCoordinates = [(initialCoordinates[c] + xb[c] - xa[c]) for c in range(3)]
                        editCoordinateField.assignReal(fieldcache, finalCoordinates)
                        element = self._get_element_with_info()
                        if element.isValid():
                            group = fieldmodule.createFieldGroup()
                            mesh = element.getMesh()
                            mesh_group = group.getOrCreateMeshGroup(mesh)
                            search_elements = self._get_search_elements()
                            for e in search_elements:
                                mesh_group.addElement(e)
                            self._find_mesh_location_field.setSearchMesh(mesh_group)
                            self._fix_node_to_mesh(fieldcache, self._edit_node, editCoordinateField)
                        if self._model:
                            self._model.update(self._edit_node, parameter='coordinate')
                    del editVectorField
                del editCoordinateField
                del fieldcache

            if update_last_mouse_pos:
                self._last_mouse_pos = mousePos

    def mouse_release_event(self, event):
        self._last_mouse_pos = None
        if self._edit_node:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self._edit_node = None
                self._edit_graphics = None
                self._edit_element_info = None


def _define_node_axis_fields(node, region, coordinates):
    fm = region.getFieldmodule()
    fc = fm.createFieldcache()
    with ChangeManager(fm):
        coordinates = coordinates.castFiniteElement()
        node_derivatives = [Node.VALUE_LABEL_D_DS1, Node.VALUE_LABEL_D_DS2, Node.VALUE_LABEL_D_DS3]
        node_axis_initial_values = [[10, 0, 0], [0, 10, 0], [0, 0, 10]]
        node_axis_fields = [[fm.createFieldNodeValue(coordinates, nodeDerivative, 1)] for nodeDerivative in node_derivatives]

        fc.setNode(node)

        component_count = coordinates.getNumberOfComponents()
        result, value = coordinates.evaluateReal(fc, component_count)

        label_field = fm.createFieldStoredString('')

        nodes = node.getNodeset()
        node_template = nodes.createNodetemplate()
        node_template.defineField(coordinates)
        node_template.defineField(label_field)
        for value_label in node_derivatives:
            node_template.setValueNumberOfVersions(coordinates, -1, value_label, 1)

        node.merge(node_template)
        coordinates.assignReal(fc, value)
        for index, value_label in enumerate(node_derivatives):
            node_axis_fields[index][0].setName(f"node_value_{value_label}")
            coordinates.setNodeParameters(fc, -1, value_label, 1, node_axis_initial_values[index])

    return node_axis_fields


def _create_orientation_axes(scene, coordinates, glyph_width, orientation_field, domain=Field.DOMAIN_TYPE_NODES, display_node_orientation=1, scale_field=None):
    node_orientation_graphics = []
    with ChangeManager(scene):
        orientation_glyph = scene.createGraphicsPoints()
        node_orientation_graphics.append(orientation_glyph)
        orientation_glyph.setFieldDomainType(domain)
        orientation_glyph.setCoordinateField(coordinates)
        point_attr = orientation_glyph.getGraphicspointattributes()
        point_attr.setGlyphShapeType(Glyph.SHAPE_TYPE_AXES_SOLID_COLOUR)
        point_attr.setBaseSize([0.0, glyph_width, glyph_width])
        # point_attr.setScaleFactors([derivativeScales[i], 0.0, 0.0])
        point_attr.setOrientationScaleField(orientation_field)
        if scale_field is not None:
            point_attr.setSignedScaleField(scale_field)

        orientation_glyph.setName('displayNodeOrientation')

        orientation_glyph.setSelectMode(Graphics.SELECT_MODE_DRAW_SELECTED if (display_node_orientation == 1) else Graphics.SELECT_MODE_ON)
        # orientation_glyph.setVisibilityFlag(bool(display_node_derivatives) and node_derivative_label in display_node_derivative_labels)

    return node_orientation_graphics


def _create_label_graphic(scene, coordinates, glyph_width, label_field, domain=Field.DOMAIN_TYPE_NODES, display_node_label=1):
    with ChangeManager(scene):
        glyph = scene.createGraphicsPoints()
        glyph.setFieldDomainType(domain)
        glyph.setCoordinateField(coordinates)
        point_attr = glyph.getGraphicspointattributes()
        # point_attr.setScaleFactors([derivativeScales[i], 0.0, 0.0])
        point_attr.setLabelField(label_field)
        point_attr.setGlyphOffset([glyph_width, 0.0, 0.0])
        # font = point_attr.getFont()
        # point_size = font.getPointSize()
        # font.setPointSize(int(point_size * glyph_width + 0.5))

        glyph.setName('displayNodeLabel')

        glyph.setSelectMode(Graphics.SELECT_MODE_DRAW_SELECTED if (display_node_label == 1) else Graphics.SELECT_MODE_ON)
        # glyph.setVisibilityFlag(bool(display_node_derivatives) and node_derivative_label in display_node_derivative_labels)

    return glyph
