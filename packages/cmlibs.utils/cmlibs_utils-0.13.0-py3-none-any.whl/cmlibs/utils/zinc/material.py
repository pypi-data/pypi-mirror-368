"""
Utilities for working with Zinc graphics materials.
"""

from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.zinc.field import Field
from cmlibs.zinc.material import Material
from cmlibs.zinc.region import Region


def create_material_using_image_field(region: Region, image_field: Field, colour_mapping_type=None, image_range=None)\
        -> Material:
    """
    Use an image field in a material to create an OpenGL texture.  Returns the
    created material.

    :param region: Used to obtain materialmodule, spectrummodule.
    :param image_field: Zinc FieldImage.
    :param colour_mapping_type: Zinc Spectrumcomponent colour mapping type or None for default rainbow.
    :param image_range: Sequence of minimum, maximum, or None to use default.
    :return: The material that contains the image field as a texture.
    """
    scene = region.getScene()
    materialmodule = scene.getMaterialmodule()
    spectrummodule = scene.getSpectrummodule()
    with ChangeManager(materialmodule), ChangeManager(spectrummodule):
        material = materialmodule.createMaterial()
        spectrum = spectrummodule.createSpectrum()
        component = spectrum.createSpectrumcomponent()
        if colour_mapping_type is None:
            colour_mapping_type = component.COLOUR_MAPPING_TYPE_RAINBOW
        component.setColourMappingType(colour_mapping_type)
        if image_range is not None:
            component.setRangeMinimum(image_range[0])
            component.setRangeMaximum(image_range[1])
        material.setTextureField(1, image_field)
    return material


createMaterialUsingImageField = create_material_using_image_field
