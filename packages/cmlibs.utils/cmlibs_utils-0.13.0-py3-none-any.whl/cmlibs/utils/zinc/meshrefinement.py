"""
Class for refining a mesh from one region to another.
"""
import math

from cmlibs.maths.octree import Octree
from cmlibs.utils.zinc.field import findOrCreateFieldCoordinates
from cmlibs.zinc.element import Element, Elementbasis
from cmlibs.zinc.field import Field
from cmlibs.zinc.node import Node
from cmlibs.zinc.result import RESULT_OK as ZINC_OK

from cmlibs.utils.zinc.finiteelement import interpolate_cubic_hermite_derivative


class MeshRefinement:
    """
    Class for refining a mesh from one region to another.
    """

    def __init__(self, source_region, target_region, basis=Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE):
        """
        Assumes targetRegion is empty.
        A copy containing the refined elements is created by the MeshRefinement.
        """
        self._source_region = source_region
        self._source_fm = source_region.getFieldmodule()
        self._source_cache = self._source_fm.createFieldcache()
        self._source_coordinates = findOrCreateFieldCoordinates(self._source_fm)
        # get range of source coordinates for octree range
        self._source_fm.beginChange()
        source_nodes = self._source_fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        mean_field = self._source_fm.createFieldNodesetMean(self._source_coordinates, source_nodes)
        result, mean = mean_field.evaluateReal(self._source_cache, 3)
        assert result == ZINC_OK, 'MeshRefinement failed to get mean coordinates'

        self._source_mesh = self._source_fm.findMeshByDimension(3)
        self._source_nodes = self._source_fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        self._source_elementiterator = self._source_mesh.createElementiterator()

        evaluation = self._evaluate_mesh()
        if not evaluation[Element.SHAPE_TYPE_CUBE]:
            raise ValueError('Element shape type is not a cube.')

        self._octree = Octree()
        self._octree.insert_object_at_coordinates(mean, -1)

        self._target_region = target_region
        self._target_fm = target_region.getFieldmodule()
        self._target_fm.beginChange()
        self._target_cache = self._target_fm.createFieldcache()
        self._target_coordinates = findOrCreateFieldCoordinates(self._target_fm)

        self._target_nodes = self._target_fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        self._nodetemplate = self._target_nodes.createNodetemplate()
        self._nodetemplate.defineField(self._target_coordinates)

        self._target_mesh = self._target_fm.findMeshByDimension(3)
        self._target_elementtemplate = self._target_mesh.createElementtemplate()
        self._target_elementtemplate.setElementShapeType(Element.SHAPE_TYPE_CUBE)

        self._target_basis = self._target_fm.createElementbasis(3, basis)
        self._target_eft = self._target_mesh.createElementfieldtemplate(self._target_basis)
        self._target_elementtemplate.defineField(self._target_coordinates, -1, self._target_eft)

        self._node_identifier = 1
        self._element_identifier = 1

    def __del__(self):
        self._source_fm.endChange()
        self._target_fm.endChange()

    def _evaluate_mesh(self):
        element = self._source_elementiterator.next()
        evaluation = {
            Element.SHAPE_TYPE_CUBE: True,
        }
        while element.isValid():
            if element.getShapeType() != Element.SHAPE_TYPE_CUBE:
                evaluation[Element.SHAPE_TYPE_CUBE] = False
            element = self._source_elementiterator.next()

        return evaluation

    def _refine_linear_lagrange_element_cube_standard3d(self, source_element, number_in_xi1, number_in_xi2, number_in_xi3, add_new_nodes_to_octree=True):
        node_ids = []
        nx = []
        xi = [0.0, 0.0, 0.0]
        for k in range(number_in_xi3 + 1):
            kExterior = (k == 0) or (k == number_in_xi3)
            xi[2] = k / number_in_xi3
            for j in range(number_in_xi2 + 1):
                jExterior = kExterior or (j == 0) or (j == number_in_xi2)
                xi[1] = j / number_in_xi2
                for i in range(number_in_xi1 + 1):
                    iExterior = jExterior or (i == 0) or (i == number_in_xi1)
                    xi[0] = i / number_in_xi1
                    self._source_cache.setMeshLocation(source_element, xi)
                    result, x = self._source_coordinates.evaluateReal(self._source_cache, 3)
                    # only exterior points are ever common:
                    node_id = None
                    if iExterior:
                        node_id = self._octree.find_object_by_coordinates(x)
                    if node_id is None:
                        node = self._target_nodes.createNode(self._node_identifier, self._nodetemplate)
                        self._target_cache.setNode(node)
                        result = self._target_coordinates.setNodeParameters(self._target_cache, -1, Node.VALUE_LABEL_VALUE, 1, x)
                        if result != ZINC_OK:
                            raise ValueError(f'Failed to set node ({self._node_identifier}) value parameters: {x}')

                        node_id = self._node_identifier
                        if iExterior and add_new_nodes_to_octree:
                            self._octree.insert_object_at_coordinates(x, node_id)
                        self._node_identifier += 1
                    node_ids.append(node_id)
                    nx.append(x)
        # create elements
        for k in range(number_in_xi3):
            ok = (number_in_xi2 + 1) * (number_in_xi1 + 1)
            for j in range(number_in_xi2):
                oj = (number_in_xi1 + 1)
                for i in range(number_in_xi1):
                    bni = k * ok + j * oj + i
                    element = self._target_mesh.createElement(self._element_identifier, self._target_elementtemplate)
                    el_node_ids = [node_ids[bni], node_ids[bni + 1], node_ids[bni + oj], node_ids[bni + oj + 1],
                                   node_ids[bni + ok], node_ids[bni + ok + 1], node_ids[bni + ok + oj], node_ids[bni + ok + oj + 1]]
                    result = element.setNodesByIdentifier(self._target_eft, el_node_ids)
                    if result != ZINC_OK:
                        raise ValueError(f'Failed to set element ({self._element_identifier}) node ids: {el_node_ids}')
                    self._element_identifier += 1

        return node_ids, nx

    def _refine_cubic_lagrange_element_cube_standard3d(self, source_element, number_in_xi1, number_in_xi2, number_in_xi3, add_new_nodes_to_octree=True):
        node_ids = []
        nx = []
        xi = [0.0, 0.0, 0.0]
        for k in range(3 * number_in_xi3 + 1):
            kExterior = (k == 0) or (k == 3 * number_in_xi3)
            xi[2] = k / (3 * number_in_xi3)
            for j in range(3 * number_in_xi2 + 1):
                jExterior = kExterior or (j == 0) or (j == 3 * number_in_xi2)
                xi[1] = j / (3 * number_in_xi2)
                for i in range(3 * number_in_xi1 + 1):
                    iExterior = jExterior or (i == 0) or (i == 3 * number_in_xi1)
                    xi[0] = i / (3 * number_in_xi1)
                    self._source_cache.setMeshLocation(source_element, xi)
                    result, x = self._source_coordinates.evaluateReal(self._source_cache, 3)
                    # only exterior points are ever common:
                    node_id = None
                    if iExterior:
                        node_id = self._octree.find_object_by_coordinates(x)
                    if node_id is None:
                        node = self._target_nodes.createNode(self._node_identifier, self._nodetemplate)
                        self._target_cache.setNode(node)
                        result = self._target_coordinates.setNodeParameters(self._target_cache, -1, Node.VALUE_LABEL_VALUE, 1, x)
                        if result != ZINC_OK:
                            raise ValueError(f'Failed to set node ({self._node_identifier}) value parameters: {x}')

                        node_id = self._node_identifier
                        if iExterior and add_new_nodes_to_octree:
                            self._octree.insert_object_at_coordinates(x, node_id)
                        self._node_identifier += 1
                    node_ids.append(node_id)
                    nx.append(x)
        # create elements
        for k in range(number_in_xi3):
            ok = (3 * number_in_xi2 + 1) * (3 * number_in_xi1 + 1)
            for j in range(number_in_xi2):
                oj = (3 * number_in_xi1 + 1)
                for i in range(number_in_xi1):
                    oi = 3 * (k * ok + j * oj + i)
                    element = self._target_mesh.createElement(self._element_identifier, self._target_elementtemplate)
                    el_node_ids = []
                    for ck in range(4):
                        for cj in range(4):
                            for ci in range(4):
                                el_node_ids.append(node_ids[oi + cj * oj + ck * ok + ci])

                    result = element.setNodesByIdentifier(self._target_eft, el_node_ids)
                    if result != ZINC_OK:
                        raise ValueError(f'Failed to set element ({self._element_identifier}) node ids: {el_node_ids}')
                    self._element_identifier += 1

        return node_ids, nx

    def refine_element_cube_standard3d(self, source_element, number_in_xi1, number_in_xi2, number_in_xi3,
                                       add_new_nodes_to_octree=True, share_node_ids=None, share_node_coordinates=None):
        """
        Refine cube sourceElement to numberInXi1*numberInXi2*numberInXi3 linear cube
        sub-elements, evenly spaced in xi.
        :param source_element:
        :param number_in_xi1:
        :param number_in_xi2:
        :param number_in_xi3:
        :param add_new_nodes_to_octree: If True (default) add newly created nodes to
        octree to be found when refining later elements. Set to False when nodes are at the
        same location and not intended to be shared.
        :param share_node_ids: and
        :param share_node_coordinates: Arrays of identifiers and coordinates of
        nodes which may be shared in refining this element. If supplied, these are preferentially
        used ahead of points in the octree. Used to control merging with known nodes, e.g.
        those returned by this function for elements which used add_new_nodes_to_octree=False.
        :return: Node identifiers, node coordinates used in refinement of source_element.
        """
        assert (share_node_ids and share_node_coordinates) or (not share_node_ids and not share_node_coordinates), \
            'refine_element_cube_standard3d.  Must supply both of shareNodeIds and shareNodeCoordinates, or neither'
        shareNodesCount = len(share_node_ids) if share_node_ids else 0
        # create nodes

        element_basis_type = self._target_basis.getFunctionType(-1)
        if element_basis_type == Elementbasis.FUNCTION_TYPE_LINEAR_LAGRANGE:
            fcn = self._refine_linear_lagrange_element_cube_standard3d
        elif element_basis_type == Elementbasis.FUNCTION_TYPE_CUBIC_LAGRANGE:
            fcn = self._refine_cubic_lagrange_element_cube_standard3d
        else:
            raise ValueError(f'Refinement of element basis: {Elementbasis.FunctionTypeEnumToString(element_basis_type)}, not supported.')

        return fcn(source_element, number_in_xi1, number_in_xi2, number_in_xi3, add_new_nodes_to_octree)

    def refine_all_elements_cube_standard3d(self, number_in_xi1, number_in_xi2, number_in_xi3):
        element = self._source_elementiterator.next()
        while element.isValid():
            self.refine_element_cube_standard3d(element, number_in_xi1, number_in_xi2, number_in_xi3)
            element = self._source_elementiterator.next()
