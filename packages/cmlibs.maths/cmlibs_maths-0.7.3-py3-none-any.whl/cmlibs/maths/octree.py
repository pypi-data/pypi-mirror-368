"""
Octree for searching for objects by coordinates
"""
import math

from cmlibs.maths.vectorops import sub, dot, add, div


class Octree:
    """
    Octree for searching for objects by coordinates.
    """

    def __init__(self, tolerance=None):
        """
        :param tolerance: If supplied, tolerance to use, or None to compute as 1.0E-12.
        """
        self._tolerance = 1.0E-12 if tolerance is None else tolerance
        self._coordinates = None
        # Octree is either leaf with _object, or has 2**self._dimension children
        self._object = None
        # exactly 2^self._dimension children, cycling in lowest x index fastest
        self._children = None

    def _location_match(self, x):
        return all([math.fabs(x[i] - self._coordinates[i]) < self._tolerance for i in range(3)])

    def _child_index_lookup(self, x):
        switch = [0 if x[i] < self._coordinates[i] else 1 for i in range(3)]
        return switch[0] + 2 * switch[1] + 4 * switch[2]

    def _sq_distance(self, x):
        diff = sub(x, self._coordinates)
        return dot(diff, diff)

    def _find_object_by_coordinates(self, x, nearest=False):
        """
        Find the closest existing object with |x - ox| < tolerance.
        :param x: 3 coordinates in a list.
        :return: nearest distance, nearest object or None, None if none found.
        """
        if self._coordinates is not None and self._location_match(x):
            return 0.0, self._object

        if not nearest and self._children is None:
            return None, None

        if nearest and self._coordinates is None:
            return math.inf, None

        if nearest and self._children is None:
            return 0.0, self._object

        index = self._child_index_lookup(x)
        sq_distance_, object_ = self._children[index]._find_object_by_coordinates(x, nearest)

        if nearest:
            sq_distance = self._sq_distance(x)
            if sq_distance_ < sq_distance:
                return sq_distance_, object_
            else:
                return sq_distance, self._object

        return None, object_

    def tolerance(self):
        return self._tolerance

    def find_object_by_coordinates(self, x):
        """
        Find the closest existing object with |x - ox| < tolerance.
        :param x: 3 coordinates in a list.
        :return: nearest object or None if not found.
        """
        distance, nearest_object = self._find_object_by_coordinates(x)
        return nearest_object

    def find_nearest_object_by_coordinates(self, x):
        distance, nearest_object = self._find_object_by_coordinates(x, True)
        return nearest_object

    def insert_object_at_coordinates(self, x, obj):
        """
        Add object at coordinates to octree.

        :param x: 3 coordinates in a list.
        :param obj: object to store with coordinates.
        """
        if self._coordinates is None:
            self._coordinates = x
            self._object = obj
        else:
            if self._location_match(x):
                self._object = obj
            else:
                index = self._child_index_lookup(x)
                if self._children is None:
                    self._children = [Octree() for _ in range(8)]

                self._children[index].insert_object_at_coordinates(x, obj)

    def __repr__(self):
        if self._children is None:
            return f'\tleaf {self._coordinates}\n'

        return f'{self._coordinates} - \n' + ''.join([f'{c}' for c in self._children])


class VolumeOctreeObject:
    """
    Interface object for the volume octree.
    This class defines the required interface for objects
    given to the VolumeOctree.

    It is not required that you use this object directly.
    It is required that any objects added to the volume octree
    follow this interface.
    """

    def __init__(self, data_object):
        self._data_object = data_object

    def identifier(self):
        return self._data_object.identifier()

    def points(self):
        return self._data_object.points()

    def distance(self, pt, tol):
        return self._data_object.distance(pt, tol)


class VolumeOctree:
    """
    An octree for managing objects with a volume.
    """

    def __init__(self, bounding_box, tolerance=1e-08, depth=0):
        self._bounding_box = bounding_box
        self._centre = div(add(bounding_box[0], bounding_box[1]), 2)
        self._tolerance = tolerance
        self._objects = {}
        self._children = {}
        self._depth = depth

    def _child_index_lookup(self, x):
        switch = [0 if x[i] < c_i else 1 for i, c_i in enumerate(self._centre)]
        return sum([2**i * s for i, s in enumerate(switch)])

    def _sub_bounding_box(self, index):
        masks = [2**i for i in range(len(self._centre))]
        p = [self._bounding_box[0 if index & m == 0 else 1][i] for i, m in enumerate(masks)]
        return [[min(i) for i in zip(p, self._centre)], [max(i) for i in zip(p, self._centre)]]

    def insert_object(self, obj):
        indices = [self._child_index_lookup(pt) for pt in obj.points()]
        if len(set(indices)) == 1:
            required_child = indices[0]
            if required_child not in self._children:
                self._children[required_child] = VolumeOctree(self._sub_bounding_box(required_child), self._tolerance, depth=self._depth + 1)
            # if self._children is None:
            #     self._children = [VolumeOctree(self._sub_bounding_box(i), self._tolerance, depth=self._depth + 1) for i in range(2**len(self._centre))]

            self._children[required_child].insert_object(obj)
        else:
            for i in set(indices):
                if i not in self._objects:
                    self._objects[i] = []
                self._objects[i].append(obj)

    def find_object(self, x):
        """
        Find the closest existing object with |x - ox| < tolerance.
        :param x: Coordinates in a list.
        :return: Nearest object or None.
        """
        octant_index = self._child_index_lookup(x)
        target = self._children[octant_index].find_object(x) if octant_index in self._children else None

        if target is not None:
            return target

        distances = [obj.distance(x, self._tolerance) for obj in self._objects.get(octant_index, [])]
        index = next((i for i, x in enumerate(distances) if x < self._tolerance), None)
        if index is not None:
            return self._objects[octant_index][index]

        return None  # self._children[octant_index].find_object(x) if octant_index in self._children else None

    def __repr__(self):
        indent = [' '] * 2 * self._depth
        indent = ''.join(indent)

        objects_len = ', '.join([f'{o}: {len(self._objects[o])}' for o in self._objects])
        if self._children is None:
            return f'{indent}leaf {self._centre} [{objects_len}]\n'

        return f'{indent}{self._centre} [{objects_len}]- \n' + ''.join([f'{self._children[c]}' for c in self._children])


def define_bounding_box():
    """
    From an initial point define a bounding box that covers everything.
    Return the top, back, left and bottom, front, right points to define
    the box.

    :return: A list of two 3D points defining the extent of the bounding box.
    """
    return [[math.inf, math.inf, math.inf], [-math.inf, -math.inf, -math.inf]]
