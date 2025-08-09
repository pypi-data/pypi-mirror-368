"""
Utilities for manipulating Zinc nodes.
"""
from cmlibs.zinc.node import Node
from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK
from cmlibs.maths.vectorops import dot, add, sub, mult, matrix_vector_mult
from cmlibs.utils.zinc.general import ChangeManager


def get_field_values(region, evaluation_field, domain_type=Field.DOMAIN_TYPE_NODES):
    """
    Get the values (real valued) for all the nodes/datapoints in the domain specified by domain_type.
    Returns the values as a list of lists, each list is the size of the number of
    values in the evaluated field.

    :param region: The Zinc Region whose nodes are to be queried.
    :param evaluation_field: A real valued field.
    :param domain_type: The node/datapoint domain to use for evaluating, default is DOMAIN_TYPE_NODES.

    :returns: A list of lists.
    """
    fm = region.getFieldmodule()
    fc = fm.createFieldcache()

    nodes = fm.findNodesetByFieldDomainType(domain_type)
    node_iter = nodes.createNodeiterator()
    number_of_components = evaluation_field.getNumberOfComponents()

    node_values = []
    node = node_iter.next()
    while node.isValid():
        fc.setNode(node)
        result, x = evaluation_field.evaluateReal(fc, number_of_components)
        if result == RESULT_OK:
            node_values.append(x)
        node = node_iter.next()

    return node_values


def rotate_nodes(region, rotation_matrix, rotation_point, node_coordinate_field_name='coordinates', datapoint_coordinate_field_name='coordinates'):
    """
    Rotate all nodes in the given region around the rotation point specified.

    :param region: The Zinc Region whose nodes are to be rotated.
    :param rotation_matrix: A rotation matrix defining the rotation to be applied to the nodes.
    :param rotation_point: The point that the nodes will be rotated around.
    :param node_coordinate_field_name: Optional; The name of the field defining the node coordinates, default 'coordinates'.
    :param datapoint_coordinate_field_name: Optional; The name of the field defining the datapoint coordinates, default 'coordinates'.
    """

    def _transform_fcn(value, point=True):
        return add(matrix_vector_mult(rotation_matrix, sub(value, rotation_point)), rotation_point) if point else matrix_vector_mult(rotation_matrix, value)

    _transform_node_values(region, node_coordinate_field_name, _transform_fcn)
    _transform_datapoint_values(region, datapoint_coordinate_field_name, _transform_fcn)


def translate_nodes(region, delta, coordinate_field_name='coordinates', datapoint_coordinate_field_name='coordinates'):
    """
    Translate all nodes in the given region by the value specified.

    :param region: The Zinc Region whose nodes are to be translated.
    :param delta: A vector specifying the direction and magnitude of the translation.
    :param coordinate_field_name: Optional; The name of the field defining the node coordinates.
    :param datapoint_coordinate_field_name: Optional; The name of the field defining the datapoint coordinates, default 'coordinates'.
    """

    def _transform_fcn(value, point=True):
        return add(value, delta) if point else value

    _transform_node_values(region, coordinate_field_name, _transform_fcn)
    _transform_datapoint_values(region, datapoint_coordinate_field_name, _transform_fcn)


def project_nodes(region, plane_point, plane_normal, coordinate_field_name='coordinates', datapoint_coordinate_field_name='coordinates'):
    """
    Project all nodes in the given region onto the plane specified.

    :param region: The Zinc Region whose nodes are to be projected.
    :param plane_point: The point used to define the plane position.
    :param plane_normal: The normal vector defining the orientation of the plane.
    :param coordinate_field_name: Optional; The name of the field defining the node coordinates.
    :param datapoint_coordinate_field_name: Optional; The name of the field defining the datapoint coordinates, default 'coordinates'.
    """
    def _project_fcn(vec, point=True):
        dist = dot(sub(vec, plane_point) if point else vec, plane_normal)
        return sub(vec, mult(plane_normal, dist))

    _transform_node_values(region, coordinate_field_name, _project_fcn)
    _transform_datapoint_values(region, datapoint_coordinate_field_name, _project_fcn)


def _transform_datapoint_values(region, coordinate_field_name, _node_values_fcn):
    _transform_domain_values(region, coordinate_field_name, _node_values_fcn, Field.DOMAIN_TYPE_DATAPOINTS)


def _transform_node_values(region, coordinate_field_name, _transform_fcn):
    _transform_domain_values(region, coordinate_field_name, _transform_fcn, Field.DOMAIN_TYPE_NODES)


def _transform_domain_values(region, coordinate_field_name, _transform_fcn, domain):
    fm = region.getFieldmodule()
    fc = fm.createFieldcache()
    node_derivatives = [Node.VALUE_LABEL_D_DS1, Node.VALUE_LABEL_D_DS2, Node.VALUE_LABEL_D_DS3,
                        Node.VALUE_LABEL_D2_DS1DS2, Node.VALUE_LABEL_D2_DS1DS3, Node.VALUE_LABEL_D2_DS2DS3, Node.VALUE_LABEL_D3_DS1DS2DS3]
    derivatives_count = len(node_derivatives)

    nodes = fm.findNodesetByFieldDomainType(domain)
    node_template = nodes.createNodetemplate()
    node_iter = nodes.createNodeiterator()

    coordinates = fm.findFieldByName(coordinate_field_name).castFiniteElement()
    components_count = coordinates.getNumberOfComponents()

    with ChangeManager(fm):

        node = node_iter.next()
        while node.isValid():
            fc.setNode(node)
            result, x = coordinates.evaluateReal(fc, components_count)
            if result == RESULT_OK:
                proj_x = _transform_fcn(x)
                coordinates.assignReal(fc, proj_x)

            node_template.defineFieldFromNode(coordinates, node)
            for d in range(derivatives_count):
                version_count = node_template.getValueNumberOfVersions(coordinates, -1, node_derivatives[d])
                for version in range(1, version_count + 1):
                    result, values = coordinates.getNodeParameters(fc, -1, node_derivatives[d], version, components_count)
                    if result == RESULT_OK:
                        proj_param = _transform_fcn(values, point=False)
                        coordinates.setNodeParameters(fc, -1, node_derivatives[d], version, proj_param)

            node = node_iter.next()
