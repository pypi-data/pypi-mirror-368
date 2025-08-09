from cmlibs.zinc.field import Field
from cmlibs.zinc.glyph import Glyph

from cmlibs.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT
from cmlibs.zinc.sceneviewerinput import Sceneviewerinput

from cmlibs.widgets.definitions import BUTTON_MAP, GraphicsSelectionMode, SelectionMode, SELECTION_GROUP_NAME
from cmlibs.widgets.handlers.keyactivatedhandler import KeyActivatedHandler

from cmlibs.utils.zinc.general import ChangeManager


TEMP_SELECTION = "_temporary_selection"


def _get_highest_dimension_mesh(field_module):
    for d in range(3, 0, -1):
        mesh = field_module.findMeshByDimension(d)
        if mesh.getSize() > 0:
            return mesh
    return None


class SceneSelection(KeyActivatedHandler):

    def __init__(self, key_code):
        super(SceneSelection, self).__init__(key_code)
        self._start_position = None
        self._selection_box = None
        self._selection_box_description = [-1.0, -1.0, -1.0, -1.0]

        self._selection_mode = SelectionMode.NONE
        self._graphics_selection_mode = GraphicsSelectionMode.ANY
        self._selection_tolerance = 3.0

    def enter(self):
        self._selection_mode = SelectionMode.NONE

    def leave(self):
        if self._processing_mouse_events and self._selection_mode != SelectionMode.NONE:
            self._remove_selection_box()
            selection_group = self._get_or_create_selection_group()
            selection_group.clear()

    def mouse_press_event(self, event):
        super(SceneSelection, self).mouse_press_event(event)
        if self._processing_mouse_events:
            x, y = self.get_scaled_event_position(event)
            self._start_position = (x, y)
            if BUTTON_MAP[event.button()] == Sceneviewerinput.BUTTON_TYPE_LEFT:
                self._selection_mode = SelectionMode.EXCLUSIVE
            elif BUTTON_MAP[event.button()] == Sceneviewerinput.BUTTON_TYPE_RIGHT:
                self._selection_mode = SelectionMode.ADDITIVE
            else:
                self._selection_mode = SelectionMode.NONE

    def mouse_move_event(self, event):
        super(SceneSelection, self).mouse_move_event(event)
        if self._processing_mouse_events and self._selection_mode != SelectionMode.NONE:
            self._update_selection_box_description(event.x() * self._scene_viewer.get_pixel_scale(), event.y() * self._scene_viewer.get_pixel_scale())
            self._update_and_or_create_selection_box()

    def _get_temporary_selection_group(self):
        scene = self._zinc_sceneviewer.getScene()
        field_module = scene.getRegion().getFieldmodule()
        selection_group = field_module.findFieldByName(TEMP_SELECTION)
        if selection_group.isValid():
            selection_group = selection_group.castGroup()
            if selection_group.isValid():
                selection_group.setManaged(False)
        if not selection_group.isValid():
            field_module.beginChange()
            selection_group = field_module.createFieldGroup()
            selection_group.setName(TEMP_SELECTION)
            field_module.endChange()
        return selection_group

    def mouse_release_event(self, event):
        super(SceneSelection, self).mouse_release_event(event)
        if self._processing_mouse_events and self._selection_mode != SelectionMode.NONE:
            self._remove_selection_box()
            x = event.x() * self._scene_viewer.get_pixel_scale()
            y = event.y() * self._scene_viewer.get_pixel_scale()
            self._update_selection_box_description(x, y)
            # Construct a small frustum to look for nodes in.
            scene = self._zinc_sceneviewer.getScene()
            region = scene.getRegion()
            region.beginHierarchicalChange()

            with ChangeManager(scene):
                scene_picker = self._scene_viewer.get_scenepicker()
                if (x != self._start_position[0]) or (y != self._start_position[1]):
                    # box select
                    left = min(x, self._start_position[0])
                    right = max(x, self._start_position[0])
                    bottom = min(y, self._start_position[1])
                    top = max(y, self._start_position[1])
                    scene_picker.setSceneviewerRectangle(self._zinc_sceneviewer,
                                                         SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                         left, bottom, right, top)
                    if self._selection_mode == SelectionMode.EXCLUSIVE:
                        self.clear_selection()

                    if self._selection_mode == SelectionMode.INTERSECTION:
                        selection_group = self._get_temporary_selection_group()
                    else:
                        selection_group = self._get_or_create_selection_group()

                    if self._selecting_points():
                        scene_picker.addPickedNodesToFieldGroup(selection_group)
                    if self._selecting_elements():
                        scene_picker.addPickedElementsToFieldGroup(selection_group)

                    if self._selection_mode == SelectionMode.INTERSECTION:
                        previous_selection = self._get_or_create_selection_group()

                        def select_intersection_recursive(_region):
                            select_intersection(_region)
                            child_region = _region.getFirstChild()
                            while child_region.isValid():
                                select_intersection_recursive(child_region)
                                child_region = child_region.getNextSibling()

                        def select_intersection(_region):
                            field_module = _region.getFieldmodule()
                            selection_field = field_module.findFieldByName(TEMP_SELECTION).castGroup()

                            if selection_field.isValid():
                                with ChangeManager(field_module):
                                    not_field = field_module.createFieldNot(selection_field)
                                    if self._selecting_points():
                                        for domain_type in (Field.DOMAIN_TYPE_NODES, Field.DOMAIN_TYPE_DATAPOINTS):
                                            _node_set = field_module.findNodesetByFieldDomainType(domain_type)
                                            node_set_group = previous_selection.getNodesetGroup(_node_set)
                                            node_set_group.removeNodesConditional(not_field)
                                    if self._selecting_elements():
                                        _mesh = _get_highest_dimension_mesh(field_module)
                                        if _mesh:
                                            mesh_group = previous_selection.getMeshGroup(_mesh)
                                            mesh_group.removeElementsConditional(not_field)
                                    del not_field

                        select_intersection_recursive(region)
                        scene.setSelectionField(previous_selection)
                        selection_group.clear()

                else:
                    # point select - get nearest object only
                    scene_picker.setSceneviewerRectangle(self._zinc_sceneviewer, SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT,
                                                         x - self._selection_tolerance,
                                                         y - self._selection_tolerance,
                                                         x + self._selection_tolerance,
                                                         y + self._selection_tolerance)
                    nearest_graphics = scene_picker.getNearestGraphics()
                    if (self._selection_mode == SelectionMode.EXCLUSIVE
                            or self._selection_mode == SelectionMode.INTERSECTION) \
                            and not nearest_graphics.isValid():
                        self.clear_selection()

                    if self._selecting_points() and \
                            (nearest_graphics.getFieldDomainType() == Field.DOMAIN_TYPE_NODES or
                             nearest_graphics.getFieldDomainType() == Field.DOMAIN_TYPE_DATAPOINTS):
                        node = scene_picker.getNearestNode()
                        if node.isValid():
                            nodeset = node.getNodeset()
                            selection_group = self._get_or_create_selection_group()
                            nodeset_group = selection_group.getOrCreateNodesetGroup(nodeset)
                            if self._selection_mode == SelectionMode.EXCLUSIVE:
                                remove_current = (nodeset_group.getSize() == 1) and nodeset_group.containsNode(node)
                                selection_group.clear()
                                if not remove_current:
                                    # re-find node group lost by above clear()
                                    nodeset_group = selection_group.getOrCreateNodesetGroup(nodeset)
                                    nodeset_group.addNode(node)
                            elif self._selection_mode == SelectionMode.ADDITIVE:
                                if nodeset_group.containsNode(node):
                                    nodeset_group.removeNode(node)
                                else:
                                    nodeset_group.addNode(node)
                            elif self._selection_mode == SelectionMode.INTERSECTION:
                                node_selected = True if nodeset_group.containsNode(node) else False
                                selection_group.clear()
                                if node_selected:
                                    # re-find node group lost by above clear()
                                    nodeset_group = selection_group.getOrCreateNodesetGroup(nodeset)
                                    nodeset_group.addNode(node)

                    if self._selecting_elements() and \
                            (nearest_graphics.getFieldDomainType() in
                             [Field.DOMAIN_TYPE_MESH1D, Field.DOMAIN_TYPE_MESH2D,
                              Field.DOMAIN_TYPE_MESH3D, Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION]):
                        elem = scene_picker.getNearestElement()
                        if elem.isValid():
                            mesh = elem.getMesh()
                            selection_group = self._get_or_create_selection_group()
                            mesh_group = selection_group.getOrCreateMeshGroup(mesh)
                            if self._selection_mode == SelectionMode.EXCLUSIVE:
                                remove_current = (mesh_group.getSize() == 1) and mesh_group.containsElement(elem)
                                selection_group.clear()
                                if not remove_current:
                                    # re-find element group lost by above clear()
                                    mesh_group = selection_group.getOrCreateMeshGroup(mesh)
                                    mesh_group.addElement(elem)
                            elif self._selection_mode == SelectionMode.ADDITIVE:
                                if mesh_group.containsElement(elem):
                                    mesh_group.removeElement(elem)
                                else:
                                    mesh_group.addElement(elem)
                            elif self._selection_mode == SelectionMode.INTERSECTION:
                                node_selected = True if mesh_group.containsElement(elem) else False
                                selection_group.clear()
                                if node_selected:
                                    # re-find element group lost by above clear()
                                    mesh_group = selection_group.getOrCreateMeshGroup(mesh)
                                    mesh_group.addElement(elem)

            region.endHierarchicalChange()
            self._selection_mode = SelectionMode.NONE

    def clear_selection(self):
        """
        If there is a selection group, clears it and removes it from scene.
        """
        selection_group = self.get_selection_group()
        if selection_group is not None:
            selection_group.clear()
            selection_group = Field()  # NULL
            scene = self._zinc_sceneviewer.getScene()
            scene.setSelectionField(selection_group)

    def get_selection_box_description(self):
        return self._selection_box_description

    def get_selection_group(self):
        """
        :return: Valid current selection group field or None.
        """
        scene = self._zinc_sceneviewer.getScene()
        selection_group = scene.getSelectionField()
        if selection_group.isValid():
            selection_group = selection_group.castGroup()
            if selection_group.isValid():
                return selection_group
        return None

    def set_graphics_selection_mode(self, mode):
        self._graphics_selection_mode = mode

    def get_graphics_selection_mode(self):
        return self._graphics_selection_mode

    def _get_or_create_selection_group(self):
        selection_group = self.get_selection_group()
        if selection_group is not None:
            return selection_group
        scene = self._zinc_sceneviewer.getScene()
        region = scene.getRegion()
        field_module = region.getFieldmodule()
        selection_group = field_module.findFieldByName(SELECTION_GROUP_NAME)
        if selection_group.isValid():
            selection_group = selection_group.castGroup()
            if selection_group.isValid():
                selection_group.setManaged(False)
        if not selection_group.isValid():
            field_module.beginChange()
            selection_group = field_module.createFieldGroup()
            selection_group.setName(SELECTION_GROUP_NAME)
            field_module.endChange()
        scene.setSelectionField(selection_group)
        return selection_group

    def _update_selection_box_description(self, x, y):
        x_diff = float(x - self._start_position[0])
        y_diff = float(y - self._start_position[1])
        if abs(x_diff) < 0.0001:
            x_diff = 1
        if abs(y_diff) < 0.0001:
            y_diff = 1
        x_off = float(self._start_position[0]) / x_diff + 0.5
        y_off = float(self._start_position[1]) / y_diff + 0.5
        self._selection_box_description = [x_diff, y_diff, x_off, y_off]

    def _update_and_or_create_selection_box(self):
        # Using a non-ideal workaround for creating a rubber band for selection.
        # This will create strange visual artifacts when using two scene viewers looking at
        # the same scene.  Waiting on a proper solution in the API.
        # Note if the standard glyphs haven't been defined then the
        # selection box will not be visible
        x_diff = self._selection_box_description[0]
        y_diff = self._selection_box_description[1]
        x_off = self._selection_box_description[2]
        y_off = self._selection_box_description[3]

        scene = self._zinc_sceneviewer.getScene()
        scene.beginChange()
        if self._selection_box is None:
            self._selection_box = scene.createGraphicsPoints()
            self._selection_box.setScenecoordinatesystem(SCENECOORDINATESYSTEM_WINDOW_PIXEL_TOP_LEFT)
        attributes = self._selection_box.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_CUBE_WIREFRAME)
        attributes.setBaseSize([x_diff, y_diff, 0.999])
        attributes.setGlyphOffset([x_off, -y_off, 0])
        scene.endChange()

    def _remove_selection_box(self):
        if self._selection_box is not None:
            scene = self._selection_box.getScene()
            scene.removeGraphics(self._selection_box)
            self._selection_box = None

    def _selecting_any(self):
        return self._graphics_selection_mode == GraphicsSelectionMode.ANY

    def _selecting_elements(self):
        return self._graphics_selection_mode == GraphicsSelectionMode.ELEMENTS or \
               self._selecting_any()

    def _selecting_points(self):
        return self._graphics_selection_mode == GraphicsSelectionMode.DATA or \
               self._graphics_selection_mode == GraphicsSelectionMode.NODE or \
               self._selecting_any()
