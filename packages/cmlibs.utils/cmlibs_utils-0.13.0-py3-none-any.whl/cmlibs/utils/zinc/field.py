"""
Utilities for creating and working with Zinc Fields.
"""
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.zinc.element import Mesh
from cmlibs.zinc.field import Field, FieldFiniteElement, FieldGroup, \
    FieldStoredMeshLocation
from cmlibs.zinc.fieldmodule import Fieldmodule
from cmlibs.zinc.node import Node
from cmlibs.zinc.result import RESULT_OK, RESULT_WARNING_PART_DONE

from cmlibs.utils.zinc.region import write_to_buffer, read_from_buffer


def field_is_managed_coordinates(field_in: Field):
    """
    Conditional function returning True if the field is Finite Element
    type, with coordinate type attribute, up to 3 components, and is managed.
    """
    return (field_in is not None) and field_in.isManaged() and\
        (field_in.getNumberOfComponents() <= 3) and\
        field_in.castFiniteElement().isValid() and field_in.isTypeCoordinate()


def field_is_managed_group(field_in: Field):
    """
    Conditional function returning True if the field is a managed Group.
    """
    return field_in.castGroup().isValid() and field_in.isManaged()


def field_is_managed_group_mesh(field_in: Field, mesh: Mesh):
    """
    Chooser conditional function limiting to field group with a mesh group for mesh.
    """
    if field_is_managed_group(field_in):
        mesh_group = field_in.castGroup().getMeshGroup(mesh)
        return mesh_group.isValid()

    return False


def field_is_managed_real_1_to_3_components(field_in: Field):
    """
    Conditional function returning True if the field is real-valued
    with up to 3 components, and is managed.
    Used e.g. for choosing a fibre field.
    """
    return (field_in.getValueType() == Field.VALUE_TYPE_REAL) and \
        (field_in.getNumberOfComponents() <= 3) and field_in.isManaged()


def assign_field_parameters(target_field: Field, source_field: Field):
    """
    Copy parameters from sourceField to targetField.
    Currently only works for node parameters.
    """
    field_assignment = target_field.createFieldassignment(source_field)
    field_assignment.assign()


def create_fields_displacement_gradients(coordinates: Field, reference_coordinates: Field, mesh: Mesh):
    """
    :return: 1st and 2nd displacement gradients of (coordinates - referenceCoordinates) w.r.t. referenceCoordinates.
    """
    assert (coordinates.getNumberOfComponents() == 3) and (reference_coordinates.getNumberOfComponents() == 3)
    fieldmodule = mesh.getFieldmodule()
    dimension = mesh.getDimension()
    with ChangeManager(fieldmodule):
        if dimension == 3:
            u = coordinates - reference_coordinates
            displacement_gradient = fieldmodule.createFieldGradient(u, reference_coordinates)
            displacement_gradient2 = fieldmodule.createFieldGradient(displacement_gradient, reference_coordinates)
        elif dimension == 2:
            # Note this needs improvement as missing cross terms
            # assume xi directions are approximately normal;
            # effect is to penalise elements where this is not so, which is also desired
            dX_dxi1 = fieldmodule.createFieldDerivative(reference_coordinates, 1)
            dX_dxi2 = fieldmodule.createFieldDerivative(reference_coordinates, 2)
            dx_dxi1 = fieldmodule.createFieldDerivative(coordinates, 1)
            dx_dxi2 = fieldmodule.createFieldDerivative(coordinates, 2)
            dS1_dxi1 = fieldmodule.createFieldMagnitude(dX_dxi1)
            dS2_dxi2 = fieldmodule.createFieldMagnitude(dX_dxi2)
            du_dS1 = (dx_dxi1 - dX_dxi1)/dS1_dxi1
            du_dS2 = (dx_dxi2 - dX_dxi2)/dS2_dxi2
            displacement_gradient = fieldmodule.createFieldConcatenate([du_dS1, du_dS2])
            # curvature:
            d2u_dSdxi1 = fieldmodule.createFieldDerivative(displacement_gradient, 1)
            d2u_dSdxi2 = fieldmodule.createFieldDerivative(displacement_gradient, 2)
            displacement_gradient2 = fieldmodule.createFieldConcatenate([ d2u_dSdxi1/dS1_dxi1, d2u_dSdxi2/dS2_dxi2 ])
        else:  # dimension == 1
            dX_dxi1 = fieldmodule.createFieldDerivative(reference_coordinates, 1)
            dx_dxi1 = fieldmodule.createFieldDerivative(coordinates, 1)
            dS1_dxi1 = fieldmodule.createFieldMagnitude(dX_dxi1)
            displacement_gradient = (dx_dxi1 - dX_dxi1)/dS1_dxi1
            # curvature:
            displacement_gradient2 = fieldmodule.createFieldDerivative(displacement_gradient, 1)/dS1_dxi1
    return displacement_gradient, displacement_gradient2


def create_field_euler_angles_rotation_matrix(fieldmodule: Fieldmodule, euler_angles: Field) -> Field:
    """
    From Zinc graphics_library.cpp, matrix transposed to row major.
    Matrix is product RzRyRx, giving rotation about x, then y, then z with
    positive angles rotating by right hand rule about axis.
    :param fieldmodule: The fieldmodule to create the field in.
    :param euler_angles: 3-component field of angles in radians, components:
    0 = azimuth (about z)
    1 = elevation (about y)
    2 = roll (about x)
    :return: 3x3 rotation matrix field suitable for pre-multiplying vector v
    i.e. v' = Mv
    """
    assert euler_angles.getNumberOfComponents() == 3
    with ChangeManager(fieldmodule):
        azimuth = fieldmodule.createFieldComponent(euler_angles, 1)
        cos_azimuth = fieldmodule.createFieldCos(azimuth)
        sin_azimuth = fieldmodule.createFieldSin(azimuth)
        elevation = fieldmodule.createFieldComponent(euler_angles, 2)
        cos_elevation = fieldmodule.createFieldCos(elevation)
        sin_elevation = fieldmodule.createFieldSin(elevation)
        roll = fieldmodule.createFieldComponent(euler_angles, 3)
        cos_roll = fieldmodule.createFieldCos(roll)
        sin_roll = fieldmodule.createFieldSin(roll)
        minus_one = fieldmodule.createFieldConstant([-1.0])
        cos_azimuth_sin_elevation = cos_azimuth*sin_elevation
        sin_azimuth_sin_elevation = sin_azimuth*sin_elevation
        matrix_components = [
            cos_azimuth*cos_elevation,
            cos_azimuth_sin_elevation*sin_roll - sin_azimuth*cos_roll,
            cos_azimuth_sin_elevation*cos_roll + sin_azimuth*sin_roll,
            sin_azimuth*cos_elevation,
            sin_azimuth_sin_elevation*sin_roll + cos_azimuth*cos_roll,
            sin_azimuth_sin_elevation*cos_roll - cos_azimuth*sin_roll,
            minus_one*sin_elevation,
            cos_elevation*sin_roll,
            cos_elevation*cos_roll]
        rotation_matrix = fieldmodule.createFieldConcatenate(matrix_components)
    return rotation_matrix


def create_field_mesh_integral(coordinates: Field, mesh: Mesh, number_of_points=3):
    """
    Create a field integrating the coordinates to give scalar volume/area/length over
    the mesh, depending on its dimension.
    :param coordinates:
    :param mesh:
    :param number_of_points: Number of Gauss points.
    :return: Field giving volume of coordinates field over mesh via Gaussian quadrature.
    """
    fieldmodule = coordinates.getFieldmodule()
    with ChangeManager(fieldmodule):
        mesh_integral_field = fieldmodule.createFieldMeshIntegral(fieldmodule.createFieldConstant(1.0),
                                                                  coordinates, mesh)
        mesh_integral_field.setNumbersOfPoints(number_of_points)
    return mesh_integral_field


def _create_plane_equation_formulation(fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
    """
    Create an iso-scalar field that is based on the plane equation.
    """
    d = fieldmodule.createFieldDotProduct(plane_normal_field, point_on_plane_field)
    iso_scalar_field = fieldmodule.createFieldDotProduct(finite_element_field, plane_normal_field) - d

    return iso_scalar_field


def create_field_image(fieldmodule, image_filename, name='image'):
    """
    Create an image field using the given fieldmodule.  The image filename must exist and
    be a known image type.

    :param fieldmodule: The fieldmodule to create the field in.
    :param image_filename: Image filename.
    :param name: Optional name of the image field, defaults to 'image'.
    :return: The image field created.
    """
    image_field = fieldmodule.createFieldImage()
    image_field.setName(name)
    image_field.setFilterMode(image_field.FILTER_MODE_LINEAR)

    # Create a stream information object that we can use to read the
    # image file from disk
    stream_information = image_field.createStreaminformationImage()

    # We are reading in a file from the local disk so our resource is a file.
    stream_information.createStreamresourceFile(image_filename)

    # Actually read in the image file into the image field.
    image_field.read(stream_information)

    return image_field


def create_fields_transformations(coordinates: Field, rotation_angles=None, scale_value=1.0, translation_offsets=None):
    """
    Create constant fields for rotation, scale and translation containing the supplied
    values, plus the transformed coordinates applying them in the supplied order.

    See create_field_euler_angles_rotation_matrix.

    :param coordinates: The coordinate field to scale, 3 components.
    :param rotation_angles: List of euler angles, length = number of components.
    :param scale_value: Scalar to multiply all components of coordinates.
    :param translation_offsets: List of offsets, length = number of components.
    :return: 4 fields: transformedCoordinates, rotation, scale, translation
    """
    if rotation_angles is None:
        rotation_angles = [0.0, 0.0, 0.0]
    if translation_offsets is None:
        translation_offsets = [0.0, 0.0, 0.0]
    components_count = coordinates.getNumberOfComponents()
    assert (components_count == 3) and (len(rotation_angles) == components_count) and isinstance(scale_value, float) \
        and (len(translation_offsets) == components_count), "createTransformationFields.  Invalid arguments"
    fieldmodule = coordinates.getFieldmodule()
    with ChangeManager(fieldmodule):
        # scale, translate and rotate model, in that order
        rotation = fieldmodule.createFieldConstant(rotation_angles)
        scale = fieldmodule.createFieldConstant(scale_value)
        translation = fieldmodule.createFieldConstant(translation_offsets)
        rotation_matrix = create_field_euler_angles_rotation_matrix(fieldmodule, rotation)
        rotated_coordinates = fieldmodule.createFieldMatrixMultiply(components_count, rotation_matrix, coordinates)
        transformed_coordinates = rotated_coordinates*scale + translation
        assert transformed_coordinates.isValid()
    return transformed_coordinates, rotation, scale, translation


def create_field_volume_image(fieldmodule, image_filenames, name='volume_image'):
    """
    Create an image field using the given fieldmodule.  The image filename must exist and
    be a known image type.

    :param fieldmodule: The fieldmodule to create the field in.
    :param image_filenames: Image filename.
    :param name: Optional name of the image field, defaults to 'volume_image'.
    :return: The image field created.
    """
    image_field = fieldmodule.createFieldImage()
    image_field.setName(name)
    image_field.setFilterMode(image_field.FILTER_MODE_LINEAR)

    # Create a stream information object that we can use to read the
    # image file from disk
    stream_information = image_field.createStreaminformationImage()

    # We are reading in a file from the local disk so our resource is a file.
    for image_filename in image_filenames:
        stream_information.createStreamresourceFile(image_filename)

    # Actually read in the image file into the image field.
    image_field.read(stream_information)

    return image_field


def create_field_plane_visibility(fieldmodule, finite_element_field, plane_normal_field, point_on_plane_field):
    """
    Create a visibility field that is based on the plane equation.
    """
    d = fieldmodule.createFieldSubtract(finite_element_field, point_on_plane_field)
    p = fieldmodule.createFieldDotProduct(d, plane_normal_field)
    t = fieldmodule.createFieldConstant(0.1)

    v = fieldmodule.createFieldLessThan(p, t)

    return v


def create_field_visibility_for_plane(fieldmodule: Fieldmodule, coordinate_field, plane):
    """
    Create a visibility field for a plane.
    :param fieldmodule: Fieldmodule to own new field.
    :param coordinate_field:
    :param plane:
    :return:
    """
    with ChangeManager(fieldmodule):
        normal_field = plane.getNormalField()
        rotation_point_field = plane.getRotationPointField()
        visibility_field = create_field_plane_visibility(fieldmodule, coordinate_field,
                                                         normal_field, rotation_point_field)
    return visibility_field


def create_field_iso_scalar_for_plane(fieldmodule: Fieldmodule, coordinate_field, plane):
    """
    Create iso-scalar field for use with plane.
    :param fieldmodule: Fieldmodule to own new field.
    :param coordinate_field:
    :param plane: Plane description object.
    """
    with ChangeManager(fieldmodule):
        normal_field = plane.getNormalField()
        rotation_point_field = plane.getRotationPointField()
        iso_scalar_field = _create_plane_equation_formulation(fieldmodule, coordinate_field, normal_field,
                                                              rotation_point_field)
    return iso_scalar_field


def get_group_list(fieldmodule):
    """
    Get list of Zinc groups (FieldGroup) in fieldmodule.
    """
    groups = []
    field_iter = fieldmodule.createFielditerator()
    field = field_iter.next()
    while field.isValid():
        group = field.castGroup()
        if group.isValid():
            groups.append(group)
        field = field_iter.next()
    return groups


def get_managed_field_names(fieldmodule):
    """
    Get names of managed fields in fieldmodule.
    """
    field_names = []
    field_iter = fieldmodule.createFielditerator()
    field = field_iter.next()
    while field.isValid():
        if field.isManaged():
            field_names.append(field.getName())
        field = field_iter.next()
    return field_names


def field_exists(fieldmodule: Fieldmodule, name: str, field_type, components_count) -> bool:
    """
    Tests to determine if the field with the given name exists in the given field module.

    :param fieldmodule: Zinc field module to search.
    :param name: Name of field to find.
    :param field_type: Type of field if derived type. Default: finiteelement.
    :param components_count: Number of components in the field. Default: 3.
    :return: True if the field is found in the module with the given name and number of components,
             false otherwise.
    """
    field = fieldmodule.findFieldByName(name)
    if field.isValid():
        if hasattr(field, 'cast' + field_type):
            field = getattr(field, 'cast' + field_type)()
            return field.isValid() and field.getNumberOfComponents() == components_count

        return field.getNumberOfComponents() == components_count

    return False


def create_field_finite_element(fieldmodule: Fieldmodule, name: str, components_count: int,
                                component_names=None, managed=False, type_coordinate=False) -> FieldFiniteElement:
    with ChangeManager(fieldmodule):
        field = fieldmodule.createFieldFiniteElement(components_count)
        field.setName(name)
        field.setManaged(managed)
        field.setTypeCoordinate(type_coordinate)
        if component_names is not None:
            for index, component_name in enumerate(component_names[:components_count]):
                field.setComponentName(index + 1, component_name)

    return field


def create_field_finite_element_clone(source_field: Field, name: str, managed=False) -> FieldFiniteElement:
    """
    Copy an existing Finite Element Field to a new field of supplied name.
    Note: does not handle time-varying parameters.
    New field is not managed by default.
    :param source_field: Zinc finite element field to copy.
    :param name: The name of the new field, asserts that no field of that name exists.
    :param managed: Managed state of field created here.
    :return: New identically defined field with supplied name.
    """
    assert source_field.castFiniteElement().isValid(), \
        "cmlibs.utils.zinc.field.createFieldFiniteElementClone.  Not a Zinc finite element field"
    fieldmodule = source_field.getFieldmodule()
    field = fieldmodule.findFieldByName(name)
    assert not field.isValid(), "cmlibs.utils.zinc.field.createFieldFiniteElementClone.  Target field name is in use"
    with ChangeManager(fieldmodule):
        # Zinc needs a function to do this efficiently; currently serialise to string, replace field name and reload!
        source_name = source_field.getName()
        region = fieldmodule.getRegion()
        buffer = write_to_buffer(region, field_names=[source_name])
        # small risk of modifying other text here:
        source_bytes = bytes(") " + source_name + ",", "utf-8")
        target_bytes = bytes(") " + name + ",", "utf-8")
        buffer = buffer.replace(source_bytes, target_bytes)
        result = read_from_buffer(region, buffer)
        assert result == RESULT_OK
    # note currently must have called endChange before field can be found
    field = fieldmodule.findFieldByName(name).castFiniteElement()
    field.setManaged(managed)
    assert field.isValid()
    return field


def find_or_create_field_finite_element(fieldmodule: Fieldmodule, name: str, components_count: int,
                                        component_names=None, managed=False, type_coordinate=False)\
        -> FieldFiniteElement:
    """
    Finds or creates a finite element field for the specified number of real components.

    :param fieldmodule:  Zinc Fieldmodule to find or create field in.
    :param name:  Name of field to find or create.
    :param components_count: Number of components / dimension of field, from 1 to 3.
    :param component_names: Optional list of component names.
    :param managed: Managed state of field if created here.
    :param type_coordinate: Default value of flag indicating field gives geometric coordinates.
    :return: Zinc FieldFiniteElement, invalid if error.
    """
    assert (components_count > 0), "cmlibs.utils.zinc.field.find_or_create_field_finite_element." \
                                   "  Invalid components_count"
    assert (not component_names) or (len(component_names) >= components_count),\
        "cmlibs.utils.zinc.field.find_or_create_field_finite_element.  Invalid component_names"
    if field_exists(fieldmodule, name, 'FiniteElement', components_count):
        existing_field = fieldmodule.findFieldByName(name)
        return existing_field.castFiniteElement()

    return create_field_finite_element(fieldmodule, name, components_count,
                                       component_names, managed, type_coordinate)


def create_field_coordinates(fieldmodule: Fieldmodule, name="coordinates", components_count=3, managed=False)\
        -> FieldFiniteElement:
    """
    Create RC coordinates finite element field of supplied name with
    number of components 1, 2, or 3 and the components named "x", "y" and "z" if used.
    New field is not managed by default.
    """
    return create_field_finite_element(fieldmodule, name, components_count,
                                       component_names=("x", "y", "z"), managed=managed, type_coordinate=True)


def find_or_create_field_coordinates(fieldmodule: Fieldmodule, name="coordinates", components_count=3, managed=True) \
        -> FieldFiniteElement:
    """
    Get or create RC coordinates finite element field of supplied name with
    number of components 1, 2, or 3 and the components named "x", "y" and "z" if used.
    New field is managed by default.
    """
    assert 1 <= components_count <= 3
    return find_or_create_field_finite_element(fieldmodule, name, components_count,
                                               component_names=("x", "y", "z"), managed=managed, type_coordinate=True)


def create_field_fibres(fieldmodule: Fieldmodule, name="fibres", components_count=3, managed=False)\
        -> FieldFiniteElement:
    """
    Finds or creates a finite element fibre field.
    New field has component names: "fibre angle", "imbrication angle", "sheet angle".
    New field is not managed by default.

    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param name:  Name of field to find or create.
    :param components_count: Number of components of field, from 1 to 3.
    :param managed: Managed state of field if created here.
    :return: Zinc FieldFiniteElement
    """
    assert 1 <= components_count <= 3
    with ChangeManager(fieldmodule):
        fibres = create_field_finite_element(fieldmodule, name, components_count,
                                             component_names=["fibre angle", "imbrication angle", "sheet angle"],
                                             managed=managed)
        fibres.setCoordinateSystemType(Field.COORDINATE_SYSTEM_TYPE_FIBRE)
    return fibres


def find_or_create_field_fibres(fieldmodule: Fieldmodule, name="fibres", components_count=3, managed=True) \
        -> FieldFiniteElement:
    """
    Finds or creates a finite element fibre field.
    New field has component names: "fibre angle", "imbrication angle", "sheet angle".
    New field is managed by default.

    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param name:  Name of field to find or create.
    :param components_count: Number of components of field, from 1 to 3.
    :param managed: Managed state of field if created here.
    :return: Zinc FieldFiniteElement
    """
    assert 1 <= components_count <= 3
    if field_exists(fieldmodule, name, 'FiniteElement', components_count):
        fibres = fieldmodule.findFieldByName(name).castFiniteElement()
        if fibres.getCoordinateSystemType() == Field.COORDINATE_SYSTEM_TYPE_FIBRE:
            return fibres
    return create_field_fibres(fieldmodule, name, components_count, managed=managed)


def create_field_group(fieldmodule: Fieldmodule, name: str, managed=False) -> FieldGroup:
    """
    Finds or creates a Group field of the supplied name.
    New field is not managed by default.

    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param name:  Name of field to find or create.
    :param managed: Managed state of field if created here.
    :return: Zinc FieldGroup.
    """
    with ChangeManager(fieldmodule):
        group = fieldmodule.createFieldGroup()
        group.setName(name)
        group.setManaged(managed)
    return group


def find_or_create_field_group(fieldmodule: Fieldmodule, name: str, managed=True) -> FieldGroup:
    """
    Finds or creates a Group field of the supplied name.
    New field is managed by default.

    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param name:  Name of field to find or create.
    :param managed: Managed state of field if created here.
    :return: Zinc FieldGroup.
    """
    field = fieldmodule.findFieldByName(name)
    if field.isValid():
        group = field.castGroup()
        if group:
            return group
    return create_field_group(fieldmodule, name, managed=managed)


def create_field_texture_coordinates(fieldmodule: Fieldmodule, name="texture coordinates", components_count=3,
                                     managed=False) -> FieldFiniteElement:
    """
    Create texture coordinates finite element field of supplied name with
    number of components 1, 2, or 3 and the components named "u", "v" and "w" if used.
    New field is not managed by default.
    """
    return create_field_finite_element(fieldmodule, name, components_count,
                                       component_names=("u", "v", "w"), managed=managed, type_coordinate=True)


def find_or_create_field_texture_coordinates(fieldmodule: Fieldmodule, name="texture coordinates", components_count=3,
                                             managed=True) -> FieldFiniteElement:
    """
    Create texture coordinates finite element field of supplied name with
    number of components 1, 2, or 3 and the components named "u", "v" and "w" if used.
    New field is managed by default.
    """
    assert 1 <= components_count <= 3
    return find_or_create_field_finite_element(fieldmodule, name, components_count,
                                               component_names=("u", "v", "w"), managed=managed, type_coordinate=True)


def create_field_stored_mesh_location(fieldmodule: Fieldmodule, mesh: Mesh, name=None, managed=False) -> FieldStoredMeshLocation:
    """
    Create a stored mesh location field for storing locations in the
    supplied mesh, used for storing data projections.
    New field is not managed by default.

    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param mesh:  Mesh to store locations in, from same fieldmodule.
    :param name:  Name of new field. If not defined, defaults to "location\_" + mesh.getName().
    :param managed: Managed state of field.
    :return: Zinc FieldStoredMeshLocation
    """
    if not name:
        name = "location_" + mesh.getName()
    with ChangeManager(fieldmodule):
        mesh_location_field = fieldmodule.createFieldStoredMeshLocation(mesh)
        mesh_location_field.setName(name)
        mesh_location_field.setManaged(managed)
    return mesh_location_field


def find_or_create_field_stored_mesh_location(fieldmodule: Fieldmodule, mesh: Mesh, name=None, managed=True) -> FieldStoredMeshLocation:
    """
    Get or create a stored mesh location field for storing locations in the
    supplied mesh, used for storing data projections.
    Note can't currently verify existing field stores locations in the supplied mesh.
    New field is managed by default.

    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param mesh:  Mesh to store locations in, from same fieldmodule.
    :param name:  Name of new field. If not defined, defaults to "location\_" + mesh.getName().
    :param managed: Managed state of field if created here.
    """
    if not name:
        name = "location_" + mesh.getName()
    field = fieldmodule.findFieldByName(name)
    # StoredMeshLocation field can only have 1 component; its value is an element + xi coordinates
    if field_exists(fieldmodule, name, 'StoredMeshLocation', 1):
        mesh_location_field = field.castStoredMeshLocation()
        return mesh_location_field
        
    return create_field_stored_mesh_location(fieldmodule, mesh, name=name, managed=managed)


def create_field_stored_string(fieldmodule: Fieldmodule, name="name", managed=False) -> Field:
    """
    Creates a stored string field for defining names on nodes or datapoints.
    New field is not managed by default.

    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param name:  Name of field to find or create.
    :param managed: Managed state of field if created here.
    :return: Zinc Field.
    """
    with ChangeManager(fieldmodule):
        stored_string_field = fieldmodule.createFieldStoredString()
        stored_string_field.setName(name)
        stored_string_field.setManaged(managed)
    return stored_string_field


def find_or_create_field_stored_string(fieldmodule: Fieldmodule, name="name", managed=True) -> Field:
    """
    Finds or creates a stored string field for defining names on nodes or
    datapoints. Note can't use Field.castStoredString API as not released.
    New field is managed by default.

    :param fieldmodule:  Zinc fieldmodule to find or create field in.
    :param name:  Name of field to find or create.
    :param managed: Managed state of field if created here.
    :return: Zinc Field.
    """
    field = fieldmodule.findFieldByName(name)
    if field.isValid():
        if field.getValueType() == Field.VALUE_TYPE_STRING:
            return field
    return create_field_stored_string(fieldmodule, name, managed=managed)


def get_unique_field_name(fieldmodule: Fieldmodule, name: str) -> str:
    """
    Return a unique field name in fieldmodule either equal to name or
    appending a number starting at 1 and increasing.

    :param fieldmodule: The fieldmodule to get a unique name in.
    :param name: The name to match or append a number to.
    """
    field = fieldmodule.findFieldByName(name)
    if not field.isValid():
        return name
    number = 1
    while True:
        next_name = name + str(number)
        field = fieldmodule.findFieldByName(next_name)
        if not field.isValid():
            return next_name
        number += 1


def orphan_field_by_name(fieldmodule: Fieldmodule, name: str):
    """
    Find existing field with the name in fieldmodule.
    If it exists, uniquely rename it (prefix with ".destroy_" and append unique number)
    and unmanage it so destroyed when no longer in use.
    """
    field = fieldmodule.findFieldByName(name)
    if field.isValid():
        field.setName(get_unique_field_name(fieldmodule, ".destroy_" + name))
        field.setManaged(False)


def determine_node_field_derivatives(region, coordinates, include_versions=False):
    """
    Create Node Value fields for each node derivative.
    Expensive as needs to query parameters across nodes.
    :param region: Region coordinates field belongs to.
    :param coordinates: Finite element field to query.
    :param include_versions: Set to True to search for versions above 1, False to return version 1 only.
    :return: List over node derivatives D1, D2, D12, D3, D13, D23, D123 of list of Node Value fields giving
    the derivative value for either version 1 or versions 1..N of those parameters at any node.
    """
    fm = region.getFieldmodule()
    with ChangeManager(fm):
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        fc = fm.createFieldcache()
        coordinates = coordinates.castFiniteElement()
        if not coordinates.isValid():
            return []

        components_count = coordinates.getNumberOfComponents()

        # determine field derivatives for all versions in use: fairly expensive
        # fields in same order as self._nodeDerivativeLabels
        node_derivatives = [Node.VALUE_LABEL_D_DS1, Node.VALUE_LABEL_D_DS2, Node.VALUE_LABEL_D_DS3,
                            Node.VALUE_LABEL_D2_DS1DS2, Node.VALUE_LABEL_D2_DS1DS3, Node.VALUE_LABEL_D2_DS2DS3, Node.VALUE_LABEL_D3_DS1DS2DS3]
        node_derivative_fields = [[fm.createFieldNodeValue(coordinates, nodeDerivative, 1)] for nodeDerivative in node_derivatives]
        derivatives_count = len(node_derivatives)
        max_versions = [1] * derivatives_count
        last_version = 1
        version = 2
        new_found_count = 1 if include_versions else 0
        while new_found_count > 0:
            nodeIter = nodes.createNodeiterator()
            node = nodeIter.next()
            found_count = sum((1 if (v < last_version) else 0) for v in max_versions)
            new_found_count = 0
            while (node.isValid()) and (found_count < derivatives_count):
                fc.setNode(node)
                for d in range(derivatives_count):
                    if max_versions[d] == last_version:  # only look one higher than last version found
                        result, values = coordinates.getNodeParameters(fc, -1, node_derivatives[d], version, components_count)
                        if (result == RESULT_OK) or (result == RESULT_WARNING_PART_DONE):
                            max_versions[d] = version
                            node_derivative_fields[d].append(fm.createFieldNodeValue(coordinates, node_derivatives[d], version))
                            found_count += 1
                            new_found_count += 1
                node = nodeIter.next()
            last_version = version
            version += 1

    return node_derivative_fields


def find_coordinate_fields(region, dimension=None):
    """
    Identifies coordinate fields within a given Zinc region.

    A coordinate field is defined as a finite element field that:
    - Is marked with the type 'coordinate'.
    - Has a number of components equal to the specified dimension (default is 3).

    If a field named 'coordinates' exists and meets the criteria, it will be placed first in the returned list.

    Parameters:
        region (Region): The Zinc region to search for coordinate fields.
        dimension (int, optional): The expected number of components in the coordinate fields. Defaults to 3.

    Returns:
        List[Field]: A list of matching coordinate fields, with 'coordinates' field first if found.
    """
    target_dimension = 3 if dimension is None else dimension
    fm = region.getFieldmodule()
    fi = fm.createFielditerator()
    field = fi.next()
    coordinate_field = None
    field_list = []
    while field.isValid():
        field = field.castFiniteElement()
        if field.isValid() and field.isTypeCoordinate() and (field.getNumberOfComponents() == target_dimension):
            if field.getName() == "coordinates":
                coordinate_field = field
            else:
                field_list.append(field)

        field = fi.next()

    if coordinate_field is not None:
        field_list.insert(0, coordinate_field)

    return field_list


def _is_3_component_real_valued_field(field):
    return field is not None and field.isValid() and (field.getNumberOfComponents() == 3) and (field.getValueType() == Field.VALUE_TYPE_REAL)


def create_jacobian_determinant_field(coordinates, reference_coordinates, name=None):
    """
    Create the Jacobian determinant of a 3-component coordinate field
    w.r.t. 3-D element reference coordinates.
    This value should always be positive for valid right-handed elements, negative if the
    element volume becomes negative or is left-handed w.r.t. the reference coordinates.
    If the coordinate field or reference field is not suitable for calculating
    the Jacobian determinant, the function returns None.
    :param coordinates: Geometric coordinate field.
    :param reference_coordinates: Reference geometric coordinate field.
    :param name: String to set as the name of the field.
    :return: Jacobian determinant field.
    """
    jacobian_determinant = None
    if _is_3_component_real_valued_field(coordinates) and _is_3_component_real_valued_field(reference_coordinates):
        fm = coordinates.getFieldmodule()
        with ChangeManager(fm):
            jacobian_determinant = fm.createFieldDeterminant(fm.createFieldGradient(coordinates, reference_coordinates))
            if name is not None:
                jacobian_determinant.setName(name)

    return jacobian_determinant


def create_xi_reference_jacobian_determinant_field(coordinates, name=None):
    """
    Calculate the Jacobian determinant w.r.t the 'xi' field.
    Returns None if the coordinates field is not a valid field.
    See also :func:create_jacobian_determinant_field.
    :param coordinates: Geometric coordinate field.
    :param name: String to set as the name of the field, optional defaults to 'Jacobian_determinant_wrt_xi'.
    :return: Jacobian determinant field.
    """
    jacobian_determinant = None
    if isinstance(coordinates, Field) and coordinates.isValid():
        fm = coordinates.getFieldmodule()
        jacobian_determinant = create_jacobian_determinant_field(coordinates, fm.findFieldByName("xi"), "Jacobian_determinant_wrt_xi" if name is None else name)

    return jacobian_determinant


# Create C++ style aliases for names of functions.
createFieldsDisplacementGradients = create_fields_displacement_gradients
createFieldsTransformations = create_fields_transformations
createFieldEulerAnglesRotationMatrix = create_field_euler_angles_rotation_matrix
createFieldFiniteElementClone = create_field_finite_element_clone
createFieldMeshIntegral = create_field_mesh_integral
createFieldVolumeImage = create_field_volume_image
createFieldPlaneVisibility = create_field_plane_visibility
createFieldVisibilityForPlane = create_field_visibility_for_plane
createFieldIsoScalarForPlane = create_field_iso_scalar_for_plane
createFieldImage = create_field_image
createFieldCoordinates = create_field_coordinates
createFieldFibres = create_field_fibres
createFieldFiniteElement = create_field_finite_element
createFieldGroup = create_field_group
createFieldStoredMeshLocation = create_field_stored_mesh_location
createFieldStoredString = create_field_stored_string
createFieldTextureCoordinates = create_field_texture_coordinates
getGroupList = get_group_list
getManagedFieldNames = get_managed_field_names
findOrCreateFieldCoordinates = find_or_create_field_coordinates
findOrCreateFieldFiniteElement = find_or_create_field_finite_element
findOrCreateFieldFibres = find_or_create_field_fibres
findOrCreateFieldGroup = find_or_create_field_group
findOrCreateFieldStoredMeshLocation = find_or_create_field_stored_mesh_location
findOrCreateFieldStoredString = find_or_create_field_stored_string
findOrCreateFieldTextureCoordinates = find_or_create_field_texture_coordinates
getUniqueFieldName = get_unique_field_name
orphanFieldByName = orphan_field_by_name
fieldIsManagedCoordinates = field_is_managed_coordinates
fieldIsManagedGroup = field_is_managed_group
assignFieldParameters = assign_field_parameters
fieldExists = field_exists
