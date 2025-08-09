"""
Utilities for creating and working with Zinc Groups and selection.
"""

from enum import Enum

from cmlibs.utils.zinc.field import get_group_list
from cmlibs.utils.zinc.finiteelement import evaluate_mesh_centroid, evaluate_nearest_mesh_location, \
    evaluate_field_nodeset_mean
from cmlibs.utils.zinc.general import ChangeManager, HierarchicalChangeManager
from cmlibs.zinc.element import Element
from cmlibs.zinc.field import Field, FieldGroup
from cmlibs.zinc.result import RESULT_OK
import logging


logger = logging.getLogger(__name__)


class GroupOperator(Enum):
    ADD = 1     # Add elements/nodes to the selected group.
    REMOVE = 2  # Remove elements/nodes from the selected group.


def group_add_group_elements(group: FieldGroup, other_group: FieldGroup, highest_dimension=3, highest_dimension_only=True,
                             conditional_field=None):
    """
    Add to group elements and/or nodes from other_group, which may be in the same or a descendent region.
    Note only objects from other_group's region are added.

    :param group: The FieldGroup to modify.
    :param other_group: FieldGroup within region tree of group's region to add contents from.
    :param highest_dimension: The highest dimension of the mesh to be used for the operation.
    :param highest_dimension_only: If set (default), only add elements of highest dimension mesh group present in other_group,
        otherwise do this for all dimensions.
    :param conditional_field: Zinc Field specifying a condition-based subset of elements from other_group to be used for the operation.
        If None (default) the operation will use the entire set of elements from other_group.
    """
    _group_update_group_elements(group, other_group, highest_dimension, highest_dimension_only, conditional_field, GroupOperator.ADD)


def group_add_not_group_elements(group: FieldGroup, other_group: FieldGroup, highest_dimension=3, highest_dimension_only=True,
                                 conditional_field=None):
    """
    Add to group elements and/or nodes from the underlying model that are not in other_group, which may be in the same or a descendent
    region.
    Note only objects from other_group's region are added.

    :param group: The FieldGroup to modify.
    :param other_group: FieldGroup within region tree of group's region whose complement elements should be added to group.
    :param highest_dimension: The highest dimension of the mesh to be used for the operation.
    :param highest_dimension_only: If set (default), only add elements not in the highest dimension mesh group present in other_group,
        otherwise do this for all dimensions.
    :param conditional_field: Zinc Field specifying a condition-based subset of elements from other_group to be used for the operation.
        If None (default) the operation will use the entire set of elements from other_group.
    """
    _group_update_group_elements(group, other_group, highest_dimension, highest_dimension_only, conditional_field, GroupOperator.ADD,
                                 complement=True)


def group_remove_group_elements(group: FieldGroup, other_group: FieldGroup, highest_dimension=3, highest_dimension_only=True,
                                conditional_field=None):
    """
    Remove from group elements and/or nodes from other_group, which may be in the same or a descendent region.
    Note only objects from other_group's region are removed.

    :param group: The FieldGroup to modify.
    :param other_group: FieldGroup within region tree of group's region whose elements should be removed from group.
    :param highest_dimension: The highest dimension of the mesh to be used for the operation.
    :param highest_dimension_only: If set (default), only remove elements of highest dimension present in other_group, otherwise remove
        elements of all dimensions.
    :param conditional_field: Zinc Field specifying a condition-based subset of elements from other_group to be used for the operation.
        If None (default) the operation will use the entire set of elements from other_group.
    """
    _group_update_group_elements(group, other_group, highest_dimension, highest_dimension_only, conditional_field, GroupOperator.REMOVE)


def group_remove_not_group_elements(group: FieldGroup, other_group: FieldGroup, highest_dimension=3, highest_dimension_only=True,
                                    conditional_field=None):
    """
    Remove from group elements and/or nodes from the underlying model that are not in other_group, which may be in the same or a descendent
    region.
    Note only objects from other_group's region are removed.

    :param group: The FieldGroup to modify.
    :param other_group: FieldGroup within region tree of group's region whose complement elements should be removed from group.
    :param highest_dimension: The highest dimension of the mesh to be used for the operation.
    :param highest_dimension_only: If set (default), only remove elements not in the highest dimension mesh group present in other_group,
        otherwise do this for all dimensions.
    :param conditional_field: Zinc Zinc Field specifying a condition-based subset of elements from other_group to be used for the operation.
        If None (default) the operation will use the entire set of elements from other_group.
    """
    _group_update_group_elements(group, other_group, highest_dimension, highest_dimension_only, conditional_field, GroupOperator.REMOVE,
                                 complement=True)


def _group_update_group_elements(group: FieldGroup, other_group: FieldGroup, highest_dimension, highest_dimension_only, conditional_field,
                                 operation, complement=False):
    """
    Base function for add/remove group-elements functions.

    :param group: The FieldGroup to modify.
    :param other_group: FieldGroup within region tree of group's region to use a basis for add/remove operation.
    :param highest_dimension: The highest dimension of the mesh to be used for the operation.
    :param highest_dimension_only: If set (default), only consider elements in the highest dimension mesh group present in other_group,
        otherwise do this for all dimensions. Note this includes dimension 0 = nodes.
    :param conditional_field: Zinc Field specifying a condition-based subset of elements from other_group to be used for the operation.
        If None (default) the operation will use the entire set of elements from other_group.
    :param operation: The operation (Add or Remove) to be performed on the groups.
    :param complement: If set, other_group will be replaced with it's complement element group in the underlying model. Therefore the
        function will use all elements and/or nodes from the underlying model that are NOT in other_group as the basis of the operation.
    """
    region = group.getFieldmodule().getRegion()
    with HierarchicalChangeManager(region):
        other_fieldmodule = other_group.getFieldmodule()
        field = other_fieldmodule.createFieldAnd(other_group, conditional_field) if conditional_field else other_group
        conditional_group = other_fieldmodule.createFieldNot(field) if complement else field
        for dimension in range(highest_dimension, -1, -1):
            if dimension > 0:
                mesh = other_fieldmodule.findMeshByDimension(dimension)
                if mesh.getSize() == 0:
                    continue
                other_mesh_group = other_group.getMeshGroup(mesh)
                if not other_mesh_group.isValid():
                    continue
                if operation == GroupOperator.ADD:
                    mesh_group = group.getOrCreateMeshGroup(mesh)
                    mesh_group.addElementsConditional(conditional_group)
                elif operation == GroupOperator.REMOVE:
                    mesh_group = group.getMeshGroup(mesh)
                    if mesh_group.isValid():
                        mesh_group.removeElementsConditional(conditional_group)
                if highest_dimension_only:
                    break
            elif dimension == 0:
                nodeset = other_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
                if nodeset.getSize() == 0:
                    continue
                other_nodeset_group = other_group.getNodesetGroup(nodeset)
                if not other_nodeset_group.isValid():
                    continue
                if operation == GroupOperator.ADD:
                    nodeset_group = group.getOrCreateNodesetGroup(nodeset)
                    nodeset_group.addNodesConditional(conditional_group)
                elif operation == GroupOperator.REMOVE:
                    nodeset_group = group.getNodesetGroup(nodeset)
                    if nodeset_group.isValid():
                        nodeset_group.removeNodesConditional(conditional_group)
        del conditional_group


def group_add_group_nodes(group: FieldGroup, other_group: FieldGroup, field_domain_type):
    """
    Add to group nodes or datapoints from other_group, which may be in the same or a descendent region.
    Note only objects from other_group's region are added.
    :param group:  Zinc FieldGroup to modify.
    :param other_group:  Zinc FieldGroup to add nodes from.
    :param field_domain_type: Field DOMAIN_TYPE_NODES or DOMAIN_TYPE_DATAPOINTS.
    """
    other_fieldmodule = other_group.getFieldmodule()
    other_nodeset = other_fieldmodule.findNodesetByFieldDomainType(field_domain_type)
    other_nodeset_group = other_group.getNodesetGroup(other_nodeset)
    if other_nodeset_group.isValid() and (other_nodeset_group.getSize() > 0):
        region = group.getFieldmodule().getRegion()
        with HierarchicalChangeManager(region):
            nodeset_group = group.getOrCreateNodesetGroup(other_nodeset)
            nodeset_group.addNodesConditional(other_group)


def group_get_highest_dimension_mesh_nodeset_group(group: FieldGroup):
    """
    Get highest dimension non-empty mesh group, if not non-empty nodeset
    group in Zinc group.
    :return: MeshGroup, NodesetGroup, only the highest dimension of which
    will be not None; or None, None if group is empty.
    """
    fieldmodule = group.getFieldmodule()
    for dimension in range(3, 0, -1):
        mesh = fieldmodule.findMeshByDimension(dimension)
        mesh_group = group.getMeshGroup(mesh)
        if mesh_group.isValid() and (mesh_group.getSize() > 0):
            return mesh_group, None
    nodeset = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    nodeset_group = group.getNodesetGroup(nodeset)
    if nodeset_group.isValid() and (nodeset_group.getSize() > 0):
        return None, nodeset_group
    return None, None


def group_get_highest_dimension(group: FieldGroup):
    """
    Get highest dimension of elements or nodes in Zinc group.
    :return: Dimensions from 3-0, or -1 if empty.
    """
    mesh_group, nodeset_group = group_get_highest_dimension_mesh_nodeset_group(group)
    if mesh_group:
        return mesh_group.getDimension()
    elif nodeset_group:
        return 0
    return -1


def identifier_ranges_fix(identifier_ranges):
    """
    Sort from lowest to highest identifier and merge adjacent and overlapping
    ranges.
    :param identifier_ranges: List of identifier ranges. Modified in situ.
    """
    identifier_ranges.sort()
    i = 1
    while i < len(identifier_ranges):
        if identifier_ranges[i][0] <= (identifier_ranges[i - 1][1] + 1):
            if identifier_ranges[i][1] > identifier_ranges[i - 1][1]:
                identifier_ranges[i - 1][1] = identifier_ranges[i][1]
            identifier_ranges.pop(i)
        else:
            i += 1


def identifier_ranges_from_string(identifier_ranges_string):
    """
    Parse string containing identifiers and identifier ranges.
    Function is suitable for processing manual input with whitespace, trailing non-digits.
    Ranges are sorted so strictly increasing. Overlapping ranges are merged.
    Future: migrate to use .. as separator for compatibility with EX file groups and cmgui.
    :param identifier_ranges_string: Identifier ranges as a string e.g. '1-30,55,66-70'.
    '30-1, 55,66-70s' also produces the same result.
    :return: Ordered list of identifier ranges e.g. [[1,30],[55,55],[66,70]]
    """
    identifier_ranges = []
    for identifier_range_string in identifier_ranges_string.split(','):
        try:
            identifier_range_ends = identifier_range_string.split('-')
            # after leading whitespace, stop at first non-digit
            for e in range(len(identifier_range_ends)):
                # strip whitespace, trailing non digits
                digits = identifier_range_ends[e].strip()
                for i in range(len(digits)):
                    if not digits[i].isdigit():
                        digits = digits[:i]
                        break
                identifier_range_ends[e] = digits
            start = int(identifier_range_ends[0])
            if len(identifier_range_ends) == 1:
                stop = start
            else:
                stop = int(identifier_range_ends[1])
                # ensure range is low-high
                if stop < start:
                    start, stop = stop, start
            identifier_ranges.append([start, stop])
        except:
            pass
    identifier_ranges_fix(identifier_ranges)
    return identifier_ranges


def identifier_ranges_to_string(identifier_ranges):
    """
    Convert ranges to a string, contracting single object ranges.
    Future: migrate to use .. as separator for compatibility with EX file groups and cmgui.
    :param identifier_ranges: Ordered list of identifier ranges e.g. [[1,30],[55,55],[66,70]]
    :return: Identifier ranges as a string e.g. '1-30,55,66-70'
    """
    identifier_ranges_string = ''
    first = True
    for identifier_range in identifier_ranges:
        if identifier_range[0] == identifier_range[1]:
            identifier_range_string = str(identifier_range[0])
        else:
            identifier_range_string = str(identifier_range[0]) + '-' + str(identifier_range[1])
        if first:
            identifier_ranges_string = identifier_range_string
            first = False
        else:
            identifier_ranges_string += ',' + identifier_range_string
    return identifier_ranges_string


def domain_iterator_to_identifier_ranges(iterator):
    """
    Extract sorted identifier ranges from iterator.
    Currently requires iterator to be in lowest-highest identifier order.
    Objects must support getIdentifier() method returning unique integer.
    :param iterator: A Zinc Elementiterator or Nodeiterator.
    :return: List of sorted identifier ranges [start,stop] e.g. [[1,30],[55,55],[66,70]]
    """
    identifier_ranges = []
    obj = iterator.next()
    if obj.isValid():
        stop = start = obj.getIdentifier()
        obj = iterator.next()
        while obj.isValid():
            identifier = obj.getIdentifier()
            if identifier == (stop + 1):
                stop = identifier
            else:
                identifier_ranges.append([ start, stop ])
                stop = start = identifier
            obj = iterator.next()
        identifier_ranges.append([ start, stop ])
    return identifier_ranges


def mesh_group_add_identifier_ranges(mesh_group, identifier_ranges):
    """
    Add elements with the supplied identifier ranges to mesh_group.
    :param mesh_group: Zinc MeshGroup to modify.
    """
    mesh = mesh_group.getMasterMesh()
    fieldmodule = mesh.getFieldmodule()
    with ChangeManager(fieldmodule):
        for identifier_range in identifier_ranges:
            for identifier in range(identifier_range[0], identifier_range[1] + 1):
                element = mesh.findElementByIdentifier(identifier)
                mesh_group.addElement(element)


def mesh_group_to_identifier_ranges(mesh_group):
    """
    :param mesh_group: Zinc MeshGroup.
    :return: Ordered list of element identifier ranges e.g. [[1,30],[55,55],[66,70]]
    """
    return domain_iterator_to_identifier_ranges(mesh_group.createElementiterator())


def nodeset_group_add_identifier_ranges(nodeset_group, identifier_ranges):
    """
    Add nodes with the supplied identifier ranges to nodeset_group.
    :param nodeset_group: Zinc NodesetGroup to modify.
    """
    nodeset = nodeset_group.getMasterNodeset()
    fieldmodule = nodeset.getFieldmodule()
    with ChangeManager(fieldmodule):
        for identifier_range in identifier_ranges:
            for identifier in range(identifier_range[0], identifier_range[1] + 1):
                node = nodeset.findNodeByIdentifier(identifier)
                nodeset_group.addNode(node)


def nodeset_group_to_identifier_ranges(nodeset_group):
    """
    :param nodeset_group: Zinc NodesetGroup.
    :return: Ordered list of node identifier ranges e.g. [[1,30],[55,55],[66,70]]
    """
    return domain_iterator_to_identifier_ranges(nodeset_group.createNodeiterator())


def group_evaluate_centroid(group, coordinate_field, number_of_integration_points=4):
    """
    Get the mean/centroid of field over group.
    Integrates over highest dimension mesh in group, otherwise gets mean over nodes, if defined.
    :param group: Zinc group to query.
    :param coordinate_field: Field to evaluate mean/centroid of. Must be real-valued with number of components
    equal or greater than highest mesh dimension, up to a maximum of 3.
    :param number_of_integration_points: Number of integration points in each element direction, if dimension > 0.
    :return: Mean/centroid field values, or None if empty group or field not defined.
    """
    mesh_group, nodeset_group = group_get_highest_dimension_mesh_nodeset_group(group)
    if mesh_group:
        return evaluate_mesh_centroid(coordinate_field, mesh_group, number_of_integration_points)
    elif nodeset_group:
        return evaluate_field_nodeset_mean(coordinate_field, nodeset_group)
    return None


def group_evaluate_representative_point(group, coordinate_field,
                                        is_exterior=False, is_on_face=Element.FACE_TYPE_INVALID):
    """
    Get a single point representing the centre of coordinates over group.
    Initially start with the centroid.
    If on a mesh group, find the nearest mesh location and return coordinates there.
    If the region has 3-D elements, optionally restrict nearest search to the exterior and/or specified face type.
    :param is_exterior: 3-D only: optional flag: if True restrict search to faces of mesh on exterior of model.
    :param is_on_face: 3-D only: Optional element face type to restrict search to faces of mesh with face type.
    :return: Representative point coordinates, or None if empty group or field not defined.
    """
    mesh_group, nodeset_group = group_get_highest_dimension_mesh_nodeset_group(group)
    if mesh_group:
        fieldmodule = group.getFieldmodule()
        is_3d = fieldmodule.findMeshByDimension(3).getSize() > 0
        centroid = evaluate_mesh_centroid(coordinate_field, mesh_group)
        element, xi = evaluate_nearest_mesh_location(
            centroid, coordinate_field, mesh_group,
            is_exterior and is_3d,
            is_on_face if is_3d else Element.FACE_TYPE_INVALID)
        if element:
            fieldcache = fieldmodule.createFieldcache()
            fieldcache.setMeshLocation(element, xi)
            result, coordinates = coordinate_field.evaluateReal(fieldcache, coordinate_field.getNumberOfComponents())
            if result == RESULT_OK:
                return coordinates
    elif nodeset_group:
        return evaluate_field_nodeset_mean(coordinate_field, nodeset_group)
    return None


def groups_have_same_local_contents(group1, group2):
    """
    Determine if two groups have the same contents in the local/owning region only.
    Empty and non-existent mesh/nodeset groups are considered to be the same.
    :param group1: Zinc group.
    :param group2: Zinc group from same region as group1.
    :return: True if same contents, otherwise False. False is returned if region mismatch.
    """
    fieldmodule = group1.getFieldmodule()
    if fieldmodule.getRegion() != group2.getFieldmodule().getRegion():
        return False

    for dimension in range(3, 0, -1):
        mesh = fieldmodule.findMeshByDimension(dimension)
        if not _have_same_content(group1, group2, mesh, "getMeshGroup", "createElementiterator"):
            return False
    for field_domain_type in (Field.DOMAIN_TYPE_NODES, Field.DOMAIN_TYPE_DATAPOINTS):
        nodeset = fieldmodule.findNodesetByFieldDomainType(field_domain_type)
        if not _have_same_content(group1, group2, nodeset, "getNodesetGroup", "createNodeiterator"):
            return False

    return True


def _have_same_content(group1, group2, content_source, get_content_group_method, create_iterator_method):
    get_content_group1 = getattr(group1, get_content_group_method)
    get_content_group2 = getattr(group2, get_content_group_method)
    content_group1 = get_content_group1(content_source)
    size1 = content_group1.getSize() if content_group1.isValid() else 0
    content_group2 = get_content_group2(content_source)
    size2 = content_group2.getSize() if content_group2.isValid() else 0
    if size1 != size2:
        return False
    if size1 > 0:
        create_iterator1 = getattr(content_group1, create_iterator_method)
        create_iterator2 = getattr(content_group2, create_iterator_method)
        content_iter1 = create_iterator1()
        content_iter2 = create_iterator2()
        item1 = content_iter1.next()
        item2 = content_iter2.next()
        while item1.isValid():
            if item1 != item2:
                return False
            item1 = content_iter1.next()
            item2 = content_iter2.next()

    return True


def group_add_group_local_contents(group, source_group):
    """
    Add to group i.e. ensure it contains the local contents (nodes, elements) of source group.
    :param group: Zinc group to add to. Its SubelementHandlingMode affects behaviour.
    :param source_group: Zinc group from same region as group with local contents to add.
    """
    fieldmodule = group.getFieldmodule()
    if fieldmodule.getRegion() != source_group.getFieldmodule().getRegion():
        return  # not supported
    with ChangeManager(fieldmodule):
        for dimension in range(3, 0, -1):
            mesh = fieldmodule.findMeshByDimension(dimension)
            source_mesh_group = source_group.getMeshGroup(mesh)
            if source_mesh_group.isValid() and (source_mesh_group.getSize() > 0):
                mesh_group = group.getOrCreateMeshGroup(mesh)
                mesh_group.addElementsConditional(source_group)
        for field_domain_type in (Field.DOMAIN_TYPE_NODES, Field.DOMAIN_TYPE_DATAPOINTS):
            nodeset = fieldmodule.findNodesetByFieldDomainType(field_domain_type)
            source_nodeset_group = source_group.getNodesetGroup(nodeset)
            if source_nodeset_group.isValid() and (source_nodeset_group.getSize() > 0):
                nodeset_group = group.getOrCreateNodesetGroup(nodeset)
                nodeset_group.addNodesConditional(source_group)


def group_remove_group_local_contents(group, source_group):
    """
    Remove from group i.e. ensure it does not contain the local contents (nodes, elements) of source group.
    :param group: Zinc group to remove from. Its SubelementHandlingMode affects behaviour.
    :param source_group: Zinc group from same region as group with local contents to remove.
    """
    fieldmodule = group.getFieldmodule()
    if fieldmodule.getRegion() != source_group.getFieldmodule().getRegion():
        return  # not supported
    with ChangeManager(fieldmodule):
        for dimension in range(3, 0, -1):
            mesh = fieldmodule.findMeshByDimension(dimension)
            source_mesh_group = source_group.getMeshGroup(mesh)
            if source_mesh_group.isValid() and (source_mesh_group.getSize() > 0):
                mesh_group = group.getMeshGroup(mesh)
                if mesh_group.isValid() and (mesh_group.getSize() > 0):
                    mesh_group.removeElementsConditional(source_group)
        for field_domain_type in (Field.DOMAIN_TYPE_NODES, Field.DOMAIN_TYPE_DATAPOINTS):
            nodeset = fieldmodule.findNodesetByFieldDomainType(field_domain_type)
            source_nodeset_group = source_group.getNodesetGroup(nodeset)
            if source_nodeset_group.isValid() and (source_nodeset_group.getSize() > 0):
                nodeset_group = group.getNodesetGroup(nodeset)
                if nodeset_group.isValid() and (nodeset_group.getSize() > 0):
                    nodeset_group.removeNodesConditional(source_group)


def match_fitting_group_names(data_fieldmodule, model_fieldmodule, log_diagnostics=False):
    """
    Used for fitting problems. Rename any group names in the data fieldmodule that differ only in
    case and whitespace from any in the model fieldmodule, to the accepted values from the model,
    which are expected to be lower case without leading or trailing whitespace characters.
    Note that internal whitespace must be exactly matched.
    :param data_fieldmodule:  Data Fieldmodule whose group names may be modified.
    :param model_fieldmodule:  Model Fieldmodule containing preferred group names.
    :param log_diagnostics:  Set to True to write diagonstic messages about name matches and changes to logging.
    """
    # future: match with annotation terms
    model_names = [group.getName() for group in get_group_list(model_fieldmodule)]
    for data_group in get_group_list(data_fieldmodule):
        data_name = data_group.getName()
        compare_name = data_name.strip().casefold()
        for model_name in model_names:
            if model_name == data_name:
                if log_diagnostics:
                    logger.info("Data group '" + data_name + "' found in model")
                break
            elif model_name.strip().casefold() == compare_name:
                result = data_group.setName(model_name)
                if result == RESULT_OK:
                    if log_diagnostics:
                        logger.info("Data group '" + data_name + "' found in model as '" +
                                    model_name + "'. Renaming to match.")
                else:
                    logger.error("Error: Data group '" + data_name + "' found in model as '" +
                          model_name + "'. Renaming to match FAILED.")
                    if fieldmodule.findFieldByName(model_name).isValid():
                        logger.error("    Reason: field of that name already exists.")
                break
        else:
            if log_diagnostics:
                logger.info("Data group '" + data_name + "' not found in model")
