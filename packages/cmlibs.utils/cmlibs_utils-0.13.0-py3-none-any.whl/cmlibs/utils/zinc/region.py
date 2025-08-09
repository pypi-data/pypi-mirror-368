from cmlibs.utils.zinc.finiteelement import evaluate_field_nodeset_range, get_identifiers, get_maximum_node_identifier
from cmlibs.zinc.field import Field
from cmlibs.zinc.result import RESULT_OK

from cmlibs.utils.zinc.general import ChangeManager


def _find_missing(lst):
    return [i for x, y in zip(lst, lst[1:])
            for i in range(x + 1, y) if y - x > 1]


def convert_nodes_to_datapoints(target_region, source_region, source_nodeset_type=Field.DOMAIN_TYPE_NODES,
                                destroy_after_conversion=True):
    """
    Converts nodes in the source region to datapoints in the target region, renumbering any existing
    datapoints in target region to not clash.
    When the source nodeset type is Field.DOMAIN_TYPE_DATAPOINTS, then datapoints are transferred from the
    source region to the target region.
    :param target_region: Zinc Region to read data into. Existing data points are renumbered to avoid nodes.
    :param source_region: Zinc Region containing nodes to transfer.
    :param source_nodeset_type:  Set to Field.DOMAIN_TYPE_DATAPOINTS or Field.DOMAIN_TYPE_NODES to transfer datapoints
    or convert nodes. Datapoint transfer should only be to different regions [default: Field.DOMAIN_TYPE_NODES].
    :param destroy_after_conversion:  Set to True to destroy nodes that have been successfully converted, or False
    to leave intact in source region [default: True].
    """
    source_fieldmodule = source_region.getFieldmodule()
    target_fieldmodule = target_region.getFieldmodule()
    with ChangeManager(source_fieldmodule), ChangeManager(target_fieldmodule):
        # Could be nodes or datapoints.
        nodes = source_fieldmodule.findNodesetByFieldDomainType(source_nodeset_type)
        if nodes.getSize() > 0:
            datapoints = target_fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
            if datapoints.getSize() > 0:
                existing_nodes_identifiers = sorted(get_identifiers(nodes))
                existing_nodes_identifiers_set = set(existing_nodes_identifiers)
                existing_datapoint_identifiers = sorted(get_identifiers(datapoints))
                in_use_identifiers = sorted(list(set(existing_datapoint_identifiers + existing_nodes_identifiers)))
                max_identifier = in_use_identifiers[-1]
                initial_available_identifiers = [i for i in range(1, in_use_identifiers[0])]
                available_identifiers = initial_available_identifiers + _find_missing(in_use_identifiers)
                datapoint_iterator = datapoints.createNodeiterator()
                datapoint = datapoint_iterator.next()
                identifier_map = {}
                while datapoint.isValid():
                    datapoint_identifier = datapoint.getIdentifier()
                    if datapoint_identifier in existing_nodes_identifiers_set and len(available_identifiers):
                        next_identifier = available_identifiers.pop(0)
                    else:
                        max_identifier += 1
                        next_identifier = max_identifier

                    identifier_map[datapoint_identifier] = next_identifier
                    datapoint = datapoint_iterator.next()

                for current_identifier, new_identifier in identifier_map.items():
                    datapoint = datapoints.findNodeByIdentifier(current_identifier)
                    datapoint.setIdentifier(new_identifier)

            # transfer nodes as datapoints to target_region
            buffer = write_to_buffer(source_region, resource_domain_type=source_nodeset_type)
            if source_nodeset_type == Field.DOMAIN_TYPE_NODES:
                buffer = buffer.replace(bytes("!#nodeset nodes", "utf-8"), bytes("!#nodeset datapoints", "utf-8"))
            result = read_from_buffer(target_region, buffer)
            assert result == RESULT_OK, "Failed to load nodes as datapoints"
            if destroy_after_conversion:
                # note this cannot destroy nodes in use by elements
                nodes.destroyAllNodes()


def copy_fitting_data(target_region, source_region):
    """
    Copy nodes and data points from source_region to target_region, converting nodes to data points and
    offsetting data point identifiers to not clash. All groups and fields in use are transferred.
    This is used for setting up fitting problems where data needs to be in datapoints only.
    :param target_region: Zinc Region to read nodes/data into.
    :param source_region: Zinc Region containing nodes/data to transfer. Unmodified.
    """
    for domain_type in [Field.DOMAIN_TYPE_DATAPOINTS, Field.DOMAIN_TYPE_NODES]:
        convert_nodes_to_datapoints(target_region, source_region, source_nodeset_type=domain_type,
                                    destroy_after_conversion=False)


def copy_nodeset(region, nodeset):
    """
    Copy nodeset to another region.
    Expects the corresponding nodeset in the region the nodeset is being copied to, to be empty.
    """
    source_region = nodeset.getFieldmodule().getRegion()
    resource_domain_type = Field.DOMAIN_TYPE_DATAPOINTS if nodeset.getName() == "datapoints" else Field.DOMAIN_TYPE_NODES
    buffer = write_to_buffer(source_region, resource_domain_type=resource_domain_type)
    result = read_from_buffer(region, buffer)
    assert result == RESULT_OK, f"Failed to load {nodeset.getName()}, result " + str(result)


def determine_appropriate_glyph_size(region, coordinates):
    fm = region.getFieldmodule()
    with ChangeManager(fm):
        fieldcache = fm.createFieldcache()
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        components_count = coordinates.getNumberOfComponents()
        # fixed width glyph size is based on average element size in all dimensions
        mesh1d = fm.findMeshByDimension(1)
        line_count = mesh1d.getSize()
        if line_count > 0:
            one = fm.createFieldConstant(1.0)
            sum_line_length = fm.createFieldMeshIntegral(one, coordinates, mesh1d)
            result, total_line_length = sum_line_length.evaluateReal(fieldcache, 1)
            glyph_width = 0.1 * total_line_length / line_count
            del sum_line_length
            del one
        if (line_count == 0) or (glyph_width == 0.0):
            # Default glyph width if no other information.
            glyph_width = 0.01
            if nodes.getSize() > 0:
                # fallback if no lines: use graphics range
                min_x, max_x = evaluate_field_nodeset_range(coordinates, nodes)
                # use function of coordinate range if no elements
                if components_count == 1:
                    max_scale = max_x - min_x
                else:
                    first = True
                    for c in range(components_count):
                        scale = max_x[c] - min_x[c]
                        if first or (scale > max_scale):
                            max_scale = scale
                            first = False
                if max_scale == 0.0:
                    max_scale = 1.0
                glyph_width = 0.01 * max_scale
        del fieldcache

    return glyph_width


def write_to_buffer(region, resource_domain_type=None, field_names=None):
    """
    Write the contents of the given region to a buffer.
    The content written to the buffer can be controlled with resource domain type and field names.

    :param region: The Zinc Region to write the content from.
    :param resource_domain_type: Should be either Field.DOMAIN_TYPE_DATAPOINTS or Field.DOMAIN_TYPE_NODES.
    :param field_names: A list of field names to output.
    :return: The buffer in bytes written from the region.
    """
    sir = region.createStreaminformationRegion()
    srm = sir.createStreamresourceMemory()
    if resource_domain_type is not None:
        sir.setResourceDomainTypes(srm, resource_domain_type)
    if field_names is not None:
        sir.setFieldNames(field_names)
    region.write(sir)
    result, buffer = srm.getBuffer()
    return buffer if result == RESULT_OK else None


def read_from_buffer(region, buffer):
    """
    Read the given buffer into the given region.

    :param region: A Zinc Region to read the buffer into.
    :param buffer: A buffer of bytes.
    :return: The result of the region read operation.
    """
    temp_sir = region.createStreaminformationRegion()
    temp_sir.createStreamresourceMemoryBuffer(buffer)
    return region.read(temp_sir)
