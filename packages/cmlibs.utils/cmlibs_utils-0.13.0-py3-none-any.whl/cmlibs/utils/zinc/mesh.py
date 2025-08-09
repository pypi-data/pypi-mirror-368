from cmlibs.zinc.field import FieldGroup, Field

from cmlibs.utils.zinc.finiteelement import get_highest_dimension_mesh
from cmlibs.utils.zinc.general import ChangeManager


def _get_element_identifiers(mesh):
    element_iterator = mesh.createElementiterator()
    element = element_iterator.next()
    element_identifiers = []
    while element.isValid():
        element_identifiers.append(element.getIdentifier())
        element = element_iterator.next()

    return element_identifiers


def _calculate_connected_elements(mesh, seed_element_identifier, shared_dimension):
    field_module = mesh.getFieldmodule()
    element = mesh.findElementByIdentifier(seed_element_identifier)

    with ChangeManager(field_module):
        field_group = field_module.createFieldGroup()
        field_group.setName('the_group')
        field_group.setSubelementHandlingMode(FieldGroup.SUBELEMENT_HANDLING_MODE_FULL)
        mesh_group = field_group.createMeshGroup(mesh)

        old_size = mesh_group.getSize()
        mesh_group.addElement(element)
        new_size = mesh_group.getSize()

        while new_size > old_size:
            old_size = new_size
            mesh_group.addAdjacentElements(shared_dimension)
            new_size = mesh_group.getSize()

        element_identifiers = _get_element_identifiers(mesh_group)

        del mesh_group
        del field_group

    return element_identifiers


def _transform_mesh_to_list_form(mesh, mesh_field):
    """
    Transform a mesh to a list of element identifiers and a list of node identifiers.

    :param mesh: The mesh to transform.
    :param mesh_field: A field defined over the elements in the mesh.
    :return: A list of element identifiers, a list of lists of node identifiers.
    """
    element_iterator = mesh.createElementiterator()
    element = element_iterator.next()
    element_nodes = []
    element_identifiers = []
    while element.isValid():
        eft = element.getElementfieldtemplate(mesh_field, -1)
        local_node_count = eft.getNumberOfLocalNodes()
        node_identifiers = []
        for index in range(local_node_count):
            node = element.getNode(eft, index + 1)
            node_identifiers.append(node.getIdentifier())

        element_identifiers.append(element.getIdentifier())
        element_nodes.append(node_identifiers)

        element = element_iterator.next()

    return element_identifiers, element_nodes


def _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh):
    repeats = _find_duplicates(element_nodes)
    for repeat in repeats:
        repeated_element = mesh.findElementByIdentifier(element_identifiers[repeat])
        mesh.destroyElement(repeated_element)
        del element_identifiers[repeat]
        del element_nodes[repeat]


def find_connected_mesh_elements_0d(mesh_field, mesh_dimension=3, remove_repeated=False, ignore_elements=None, progress_callback=None):
    """
    Find the sets of connected elements from the mesh defined over the mesh_field.
    Each list of element identifiers returned is a connected set of elements.

    :param mesh_field: A field defined over the mesh.
    :param mesh_dimension: The dimension of the mesh to work with, default 3.
    :param remove_repeated: Find and remove elements that use the same nodes, default False.
    :param ignore_elements: An iterable of element identifiers to ignore.
    :param progress_callback: A callback to report progress to, should return True if the process
    is to continue and False if the process has been cancelled.
    :return: A list of lists of element identifiers.
    """
    field_module = mesh_field.getFieldmodule()

    mesh = field_module.findMeshByDimension(mesh_dimension)
    element_identifiers, element_nodes = _transform_mesh_to_list_form(mesh, mesh_field)
    if remove_repeated:
        _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh)

    if ignore_elements is None:
        ignore_element_indices = None
    else:
        identifier_map = dict(zip(element_identifiers, range(len(element_identifiers))))
        ignore_element_indices = [identifier_map[i] for i in ignore_elements]

    connected_sets = _find_connected(element_nodes, ignore_element_indices=ignore_element_indices, progress_callback=progress_callback)
    if connected_sets is None:
        return

    el_ids = []
    for connected_set in connected_sets:
        el_ids.append([element_identifiers[index] for index in connected_set])

    return el_ids


def find_connected_mesh_elements_1d(mesh_field, mesh_dimension=3, remove_repeated=False, shared_dimension=2):
    """
    Find the sets of connected elements from the mesh defined over the mesh_field.
    Only considers connected elements to the 1D level.

    :param mesh_field: A field defined over the mesh.
    :param mesh_dimension: The dimension of the mesh to work with, default 3.
    :param remove_repeated: Find and remove elements that use the same nodes, default False.
    :param shared_dimension: The dimension to match adjacent elements to, default 2.
    :return: A list of lists of element identifiers.
    """
    field_module = mesh_field.getFieldmodule()

    mesh = field_module.findMeshByDimension(mesh_dimension)
    element_identifiers, element_nodes = _transform_mesh_to_list_form(mesh, mesh_field)
    if remove_repeated:
        _find_and_remove_repeated_elements(element_identifiers, element_nodes, mesh)
    field_module.defineAllFaces()
    remainder_element_identifiers = element_identifiers[:]

    connected_sets = []
    while len(remainder_element_identifiers):
        connected_element_identifiers = _calculate_connected_elements(mesh, remainder_element_identifiers.pop(0), shared_dimension)
        connected_sets.append(connected_element_identifiers)
        remainder_element_identifiers = list(set(remainder_element_identifiers) - set(connected_element_identifiers))

    # _print_node_sets(mesh_field, connected_sets)
    return connected_sets


def _print_node_sets(mesh_field, sets):
    field_module = mesh_field.getFieldmodule()

    print("=======")
    mesh = field_module.findMeshByDimension(2)
    element_identifiers, element_nodes = _transform_mesh_to_list_form(mesh, mesh_field)
    for s in sets:
        node_ids = set()
        for el_id in s:
            index = element_identifiers.index(el_id)
            nodes = element_nodes[index]
            for n in nodes:
                node_ids.add(n)

        print(sorted(node_ids))


def _find_connected(element_nodes, seed_index=None, ignore_element_indices=None, progress_callback=None):
    seeded = True
    if seed_index is None:
        seeded = False
        seed_index = 0

    num_elements = len(element_nodes)
    index_deletion_map = {}
    if ignore_element_indices is not None:
        element_indices = list(range(num_elements))
        element_nodes = element_nodes[:]
        for i in sorted(ignore_element_indices, reverse=True):
            del element_nodes[i]
            del element_indices[i]
        index_deletion_map = {v: k for v, k in enumerate(element_indices)}

    update_indexes = {}
    if progress_callback is not None:
        update_interval = max(1, int(num_elements * 0.01))
        update_indexes = set([i for i in range(update_interval)] + [i for i in range(update_interval, num_elements, update_interval)])

    connected_elements = [[seed_index]]
    connected_nodes = [set(element_nodes[seed_index])]
    for element_index, element in enumerate(element_nodes):
        if element_index == seed_index:
            continue

        if element_index in update_indexes:
            if progress_callback(element_index):
                return None

        working_index = len(connected_nodes)
        working_set = set(element_nodes[element_index])
        connected_elements.append([element_index])
        connected_nodes.append(working_set)

        connection_indices = []
        for target_index in range(working_index - 1, -1, -1):
            target_set = connected_nodes[target_index]
            if working_set & target_set:
                connection_indices.append(target_index)

        for connection_index in connection_indices:
            connected_elements[connection_index].extend(connected_elements[working_index])
            connected_nodes[connection_index].update(connected_nodes[working_index])
            del connected_elements[working_index]
            del connected_nodes[working_index]
            working_index = connection_index

    if ignore_element_indices is not None:
        remapped_connected_elements = []
        for connected_element in connected_elements:
            remapped_connected_elements.append([index_deletion_map[c] for c in connected_element])

        connected_elements = remapped_connected_elements

    return connected_elements[0] if seeded else connected_elements


def _find_duplicates(element_nodes):
    """
    Given a list of integers, returns a list of all duplicate elements (with multiple duplicities).
    """
    num_count = {}
    duplicates = []

    for index, nodes in enumerate(element_nodes):
        sorted_nodes = tuple(sorted(nodes))
        if sorted_nodes in num_count:
            num_count[sorted_nodes].append(index)
        else:
            num_count[sorted_nodes] = [index]

    # Add duplicates to the result list
    for num, count in num_count.items():
        if len(count) > 1:
            duplicates.extend(count[1:])

    return sorted(duplicates, reverse=True)


def _undefine_field_on_elements(field, mesh_group):
    element_template = mesh_group.createElementtemplate()
    element_template.undefineField(field)
    element_iter = mesh_group.createElementiterator()
    element = element_iter.next()
    while element.isValid():
        element.merge(element_template)
        element = element_iter.next()


def undefine_field(field):
    """
    Undefine field over whole mesh in the given fields field module.
    :param field: Finite element field to undefine.
    """
    fm = field.getFieldmodule()
    mesh = get_highest_dimension_mesh(fm)
    nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    nodeset_group = nodes
    with ChangeManager(fm):
        # Undefine over nodes
        node_template = nodeset_group.createNodetemplate()
        node_template.undefineField(field)
        node_iter = nodeset_group.createNodeiterator()
        node = node_iter.next()
        while node.isValid():
            node.merge(node_template)
            node = node_iter.next()

        # Undefine over elements
        for i in range(mesh.getDimension(), 0, -1):
            mesh = fm.findMeshByDimension(i)
            mesh_group = mesh
            _undefine_field_on_elements(field, mesh_group)


def element_or_ancestor_is_in_mesh(element, mesh):
    """
    Query whether element is in mesh or is from its tree of faces, lines etc.
    :param element: Element to query.
    :param mesh: Equal or higher dimension ancestor mesh or mesh group to check.
    :return: True if element or any parent/ancestor is in mesh.
    """
    if mesh.containsElement(element):
        return True
    for p in range(1, element.getNumberOfParents() + 1):
        if element_or_ancestor_is_in_mesh(element.getParentElement(p), mesh):
            return True
    return False
