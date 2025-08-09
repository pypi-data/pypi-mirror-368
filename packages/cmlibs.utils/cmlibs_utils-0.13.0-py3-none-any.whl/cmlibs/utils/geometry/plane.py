import json


class ZincPlane(object):
    """
    A description of a plane in Zinc terms.
    The plane is described by a 3D point and a normal vector.
    """

    def __init__(self, fieldmodule):
        self._normal_field = self._createNormalField(fieldmodule)
        self._rotation_point_field = self._createRotationPointField(fieldmodule)

    def _createNormalField(self, fieldmodule):
        plane_normal_field = fieldmodule.createFieldConstant([0, 0, 1])
        return plane_normal_field

    def _createRotationPointField(self, fieldmodule):
        point_on_plane_field = fieldmodule.createFieldConstant([0, 0, 0])
        return point_on_plane_field

    def getRegion(self):
        return self._normal_field.getFieldmodule().getRegion()

    def getNormalField(self):
        return self._normal_field

    def getRotationPointField(self):
        return self._rotation_point_field

    def getNormal(self):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, normal = self._normal_field.evaluateReal(fieldcache, 3)

        return normal

    def getRotationPoint(self):
        fieldmodule = self._rotation_point_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        _, point = self._rotation_point_field.evaluateReal(fieldcache, 3)

        return point

    def setPlaneEquation(self, normal, point):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._normal_field.assignReal(fieldcache, normal)
        self._rotation_point_field.assignReal(fieldcache, point)
        fieldmodule.endChange()

    def setNormal(self, normal):
        fieldmodule = self._normal_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._normal_field.assignReal(fieldcache, normal)
        fieldmodule.endChange()

    def setRotationPoint(self, point):
        fieldmodule = self._rotation_point_field.getFieldmodule()
        fieldcache = fieldmodule.createFieldcache()
        fieldmodule.beginChange()
        self._rotation_point_field.assignReal(fieldcache, point)
        fieldmodule.endChange()

    def getAttitude(self):
        pa = PlaneAttitude(self.getRotationPoint(), self.getNormal())
        return pa


class PlaneAttitude(object):
    """
    A class to help serialise and compare Plane attitudes.
    """

    precision = 12

    def __init__(self, point, normal):
        self._point = point
        self._normal = normal

    def serialize(self):
        return json.dumps(self.__dict__)

    def deserialize(self, str_rep):
        self.__dict__ = json.loads(str_rep)

    def getNormal(self):
        return self._normal

    def getPoint(self):
        return self._point

    def setPoint(self, point):
        self._point = point

    def __hash__(self, *args, **kwargs):
        p = [str(int(v * (10 ** self.precision))) for v in self._point]
        n = [str(int(v * (10 ** self.precision))) for v in self._normal]
        str_repr = ''.join(p) + ''.join(n)
        return hash(str_repr)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)
