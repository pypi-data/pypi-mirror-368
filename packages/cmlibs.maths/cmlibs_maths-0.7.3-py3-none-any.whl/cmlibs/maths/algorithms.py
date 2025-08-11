from cmlibs.maths.vectorops import sub, dot, add, mult, cross, normalize


def calculate_line_plane_intersection(pt1, pt2, point_on_plane, plane_normal):
    line_direction = sub(pt2, pt1)
    d = dot(sub(point_on_plane, pt1), plane_normal) / dot(line_direction, plane_normal)
    intersection_point = add(mult(line_direction, d), pt1)
    if abs(dot(sub(point_on_plane, intersection_point), plane_normal)) < 1e-08:
        return intersection_point

    return None


def calculate_extents(values):
    """
    Calculate the maximum and minimum for each coordinate x, y, and z
    Return the max's and min's as:

     [x_min, x_max, y_min, y_max, z_min, z_max]

    """
    x_min = 0; x_max = 1
    y_min = 0; y_max = 1
    z_min = 0; z_max = 2
    if values:
        initial_value = values[0]
        x_min = x_max = initial_value[0]
        y_min = y_max = initial_value[1]
        z_min = z_max = initial_value[2]
        for coord in values:
            x_min = min([coord[0], x_min])
            x_max = max([coord[0], x_max])
            y_min = min([coord[1], y_min])
            y_max = max([coord[1], y_max])
            z_min = min([coord[2], z_min])
            z_max = max([coord[2], z_max])

    return [x_min, x_max, y_min, y_max, z_min, z_max]


def calculate_plane_normal(pt1, pt2, pt3):
    dir_1 = sub(pt2, pt1)
    dir_2 = sub(pt3, pt1)
    cross_vec = cross(dir_1, dir_2)
    return normalize(cross_vec)


def calculate_centroid(data_points):
    """
    Calculates the centroid of a list of point coordinates.

    :param data_points: A list containing 'n' lists (coordinates) of size 'm'. With 'n' denoting the number of points and 'm' denoting the
        number of dimensions of the coordinates.
    :return: An m-dimensional list containing the coordinates of the centroid.
    """
    actual_points = list(map(list, zip(*data_points)))
    centroid = [sum(dim_points) / len(dim_points) for dim_points in actual_points]

    return centroid


# Define legacy names.
calculateLinePlaneIntersection = calculate_line_plane_intersection
calculatePlaneNormal = calculate_plane_normal
calculateExtents = calculate_extents
