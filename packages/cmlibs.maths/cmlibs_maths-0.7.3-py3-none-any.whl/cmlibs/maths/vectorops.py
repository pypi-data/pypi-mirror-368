"""
A collection of functions that operate on python lists as if
they were vectors.  A basic implementation to forgo the need
to use numpy.
"""
from math import acos, sqrt, cos, sin, fabs, atan2


def magnitude(v):
    """
    return: scalar magnitude of vector v
    """
    return sqrt(sum(c * c for c in v))


def magnitude_squared(v):
    """
    return: Squared scalar magnitude of vector v, avoiding sqrt().
    """
    return sum(c * c for c in v)


def set_magnitude(v, mag):
    """
    return: Vector v with magnitude set to mag.
    """
    scale = mag / magnitude(v)
    return mult(v, scale)


def add(u, v):
    return [u_i + v_i for u_i, v_i in zip(u, v)]


def sub(u, v):
    return [u_i - v_i for u_i, v_i in zip(u, v)]


def distance(u, v):
    """
    :param u: Vector.
    :param v: Vector.
    :return: Scalar Euclidean distance between two points.
    """
    value = 0.0
    for u_i, v_i in zip(u, v):
        w = u_i - v_i
        value += w * w
    return sqrt(value)


def distance_squared(u, v):
    """
    :param u: Vector.
    :param v: Vector.
    :return: Scalar squared Euclidean distance between points, avoiding sqrt().
    """
    value = 0.0
    for u_i, v_i in zip(u, v):
        w = u_i - v_i
        value += w * w
    return value


def mult(v, s):
    """
    Calculate s * v
    :param v: Vector.
    :param s: Scalar.
    :return: [s * v_1, s * v_2, ..., s * v_n]
    """
    return [c * s for c in v]


def div(v, s):
    """
    Calculate v / s
    :param v: Vector.
    :param s: Scalar.
    :return: [v_1 / s, v_2 / s, ..., v_n / s]
    """
    return [c / s for c in v]


def dot(u, v):
    return sum(u_i * v_i for u_i, v_i in zip(u, v))


def eldiv(u, v):
    return [u_i / v_i for u_i, v_i in zip(u, v)]


def elmult(u, v):
    return [u_i * v_i for u_i, v_i in zip(u, v)]


def normalize(v):
    return div(v, magnitude(v))


def cross(u, v):
    c = [u[1] * v[2] - u[2] * v[1],
         u[2] * v[0] - u[0] * v[2],
         u[0] * v[1] - u[1] * v[0]]

    return c


def scalar_projection(v1, v2):
    """
    :return: Scalar projection of v1 onto v2.
    """
    return dot(v1, normalize(v2))


def projection(v1, v2):
    """
    Calculate vector projection of v1 on v2
    :return: A projection vector.
    """
    s1 = scalar_projection(v1, v2)
    return mult(normalize(v2), s1)


def rejection(v1, v2):
    """
    Calculate vector rejection of v1 on v2
    :return: A rejection vector.
    """
    v1p = projection(v1, v2)
    return add_vectors([v1, v1p], [1.0, -1.0])


def angle(u, v):
    """
    Calculate the angle between two non-zero vectors.
    :return: The angle between them in radians.
    """
    d = magnitude(u) * magnitude(v)
    return acos(dot(u, v) / d)


def add_vectors(vectors, scalars=None):
    """
    returns s1*v1+s2*v2+... where scalars = [s1, s2, ...] and vectors=[v1, v2, ...].
    :return: Resultant vector
    """
    if not scalars:
        scalars = [1] * len(vectors)
    else:
        assert len(vectors) == len(scalars)

    vector_dimension = len(vectors[0])
    resultant = [0] * vector_dimension
    for i, vector in enumerate(vectors):
        resultant = [resultant[c] + scalars[i] * vector[c] for c in range(vector_dimension)]
    return resultant


def rotate_vector_around_vector(v, k, a):
    """
    Rotate vector v, by an angle a (right-hand rule) in radians around vector k.
    :return: rotated vector.
    """
    k = normalize(k)
    vperp = add_vectors([v, cross(k, v)], [cos(a), sin(a)])
    vparal = mult(k, dot(k, v) * (1 - cos(a)))
    return add_vectors([vperp, vparal])


def matrix_constant_mult(m, c):
    """
    Multiply components of matrix m by constant c
    """
    return [mult(row_m, c) for row_m in m]


def matrix_vector_mult(m, v):
    """
    Post multiply matrix m by vector v
    """
    return [dot(row_m, v) for row_m in m]


def vector_matrix_mult(v, m):
    """
    Premultiply matrix m by vector v
    """
    rows = len(m)
    if len(v) != rows:
        raise ValueError('vector_matrix_mult mismatched rows')
    columns = len(m[0])
    result = []
    for c in range(columns):
        result.append(sum(v[r] * m[r][c] for r in range(rows)))
    return result


def matrix_mult(a, b):
    """
    Multiply 2 matrices: first index is down row, second is across column.
    Assumes sizes are compatible (number of columns of a == number of rows of b).
    """
    return [vector_matrix_mult(row_a, b) for row_a in a]


def matrix_minor(a, i, j):
    return [row[:j] + row[j + 1:] for row in (a[:i] + a[i + 1:])]


def matrix_det(a):
    if len(a) == 2:
        return a[0][0] * a[1][1] - a[0][1] * a[1][0]

    det = 0.0
    for c in range(len(a)):
        det += ((-1) ** c) * a[0][c] * matrix_det(matrix_minor(a, 0, c))

    return det


def matrix_inv(a):
    """
    Invert a square matrix by compouting the determinant and cofactor matrix.
    """
    len_a = len(a)
    det = matrix_det(a)

    if len_a == 2:
        return matrix_constant_mult([[a[1][1], -1 * a[0][1]], [-1 * a[1][0], a[0][0]]], 1 / det)

    cofactor = []
    for r in range(len_a):
        row = []
        for c in range(len_a):
            minor = matrix_minor(a, r, c)
            row.append(((-1) ** (r + c)) * matrix_det(minor))
        cofactor.append(row)

    cofactor_t = transpose(cofactor)
    return matrix_constant_mult(cofactor_t, 1 / det)


def identity_matrix(size):
    """
    Create an identity matrix of size x size.
    """
    identity = []
    for r in range(size):
        row = []
        for c in range(size):
            row.append(1.0 if r == c else 0.0)

        identity.append(row)

    return identity


def transpose(a):
    return list(map(list, zip(*a)))


def quaternion_to_rotation_matrix(quaternion):
    """
    This method takes a quaternion representing a rotation
    and turns it into a rotation matrix.
    :return: 3x3 rotation matrix suitable for pre-multiplying vector v:
    i.e. v' = Mv
    """
    mag_q = magnitude(quaternion)
    norm_q = div(quaternion, mag_q)
    qw, qx, qy, qz = norm_q
    ww, xx, yy, zz = qw * qw, qx * qx, qy * qy, qz * qz
    wx, wy, wz, xy, xz, yz = qw * qx, qw * qy, qw * qz, qx * qy, qx * qz, qy * qz
    # mx = [[qw * qw + qx * qx - qy * qy - qz * qz, 2 * qx * qy - 2 * qw * qz, 2 * qx * qz + 2 * qw * qy],
    #       [2 * qx * qy + 2 * qw * qz, qw * qw - qx * qx + qy * qy - qz * qz, 2 * qy * qz - 2 * qw * qx],
    #       [2 * qx * qz - 2 * qw * qy, 2 * qy * qz + 2 * qw * qx, qw * qw - qx * qx - qy * qy + qz * qz]]
    # aa, bb, cc, dd = a * a, b * b, c * c, d * d
    # bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d

    mx = [[ww + xx - yy - zz, 2 * (xy + wz), 2 * (xz - wy)],
          [2 * (xy - wz), ww + yy - xx - zz, 2 * (yz + wx)],
          [2 * (xz + wy), 2 * (yz - wx), ww + zz - xx - yy]]
    return mx


def euler_to_rotation_matrix(euler_angles):
    """
    From Zinc graphics_library.cpp, with matrix transposed to row major.
    Matrix is product RzRyRx, giving rotation about x, then y, then z with
    positive angles rotating by right hand rule about axis.
    :param euler_angles: 3 angles in radians, components:
    0 = azimuth (about z)
    1 = elevation (about y)
    2 = roll (about x)
    :return: 3x3 rotation matrix suitable for pre-multiplying vector v:
    i.e. v' = Mv
    """
    cos_azimuth = cos(euler_angles[0])
    sin_azimuth = sin(euler_angles[0])
    cos_elevation = cos(euler_angles[1])
    sin_elevation = sin(euler_angles[1])
    cos_roll = cos(euler_angles[2])
    sin_roll = sin(euler_angles[2])
    mat3x3 = [
        [cos_azimuth * cos_elevation, cos_azimuth * sin_elevation * sin_roll - sin_azimuth * cos_roll,
         cos_azimuth * sin_elevation * cos_roll + sin_azimuth * sin_roll],
        [sin_azimuth * cos_elevation, sin_azimuth * sin_elevation * sin_roll + cos_azimuth * cos_roll,
         sin_azimuth * sin_elevation * cos_roll - cos_azimuth * sin_roll],
        [-sin_elevation, cos_elevation * sin_roll, cos_elevation * cos_roll]]
    return mat3x3


def rotation_matrix_to_euler(matrix):
    """
    From Zinc graphics_library.cpp, with matrix transposed to row major.
    Inverse function to euler_to_rotation_matrix.
    """
    MATRIX_TO_EULER_TOLERANCE = 1.0E-12
    euler_angles = [0.0, 0.0, 0.0]
    if fabs(matrix[0][0]) > MATRIX_TO_EULER_TOLERANCE:
        euler_angles[0] = atan2(matrix[1][0], matrix[0][0])
        euler_angles[2] = atan2(matrix[2][1], matrix[2][2])
        euler_angles[1] = atan2(-matrix[2][0], matrix[0][0] / cos(euler_angles[0]))
    elif fabs(matrix[0][1]) > MATRIX_TO_EULER_TOLERANCE:
        euler_angles[0] = atan2(matrix[1][0], matrix[0][0])
        euler_angles[2] = atan2(matrix[2][1], matrix[2][2])
        euler_angles[1] = atan2(-matrix[2][0], matrix[1][0] / sin(euler_angles[0]))
    else:
        euler_angles[1] = atan2(-matrix[2][0], 0)  # get +/-1
        euler_angles[0] = 0
        euler_angles[2] = atan2(-matrix[1][2], -matrix[0][2] * matrix[2][0])
    return euler_angles


def axis_angle_to_quaternion(axis, theta):
    """
    :param axis: Unit vector axis of rotation.
    :param theta: Angle of rotation in right hand sense around axis, in radians.
    :return: Quaternion representing rotation.
    """
    sin_half_angle = sin(theta / 2)
    return [cos(theta / 2), axis[0] * sin_half_angle, axis[1] * sin_half_angle, axis[2] * sin_half_angle]


def axis_angle_to_rotation_matrix(axis, theta):
    """
    Convert axis angle to a rotation matrix.

    :param axis: Unit vector axis of rotation.
    :param theta: Angle of rotation in right hand sense around axis, in radians.
    :return: 3x3 rotation matrix suitable for pre-multiplying vector v: i.e. v' = Mv
    """
    mag_axis = magnitude(axis)
    norm_axis = axis if mag_axis == 0.0 else div(axis, mag_axis)
    a = cos(theta / 2.0)
    b, c, d = mult(norm_axis, -sin(theta / 2.0))
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return [[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]]


def rotate_about_z_axis(v, theta):
    """
    Rotate the given vector v about the z-axis by theta radians.
    :param v: vector to be rotated.
    :param theta: angle of rotation.
    :return rotated vector.
    """
    cos_theta = cos(theta)
    sin_theta = sin(theta)

    return [v[0] * cos_theta - v[1] * sin_theta, v[0] * sin_theta + v[1] * cos_theta, v[2]]


def reshape(a, new_shape):
    b = []
    if isinstance(new_shape, tuple):
        index = 0
        for x in range(new_shape[0]):
            row = []
            for y in range(new_shape[1]):
                row.append(a[index])
                index += 1
            b.append(row)
    elif isinstance(new_shape, int):
        flat_list = [item for sublist in a for item in sublist]
        if 0 <= new_shape < len(flat_list):
            b = flat_list[:new_shape]
        else:
            b = flat_list

    return b


# legacy function names
rotmx = quaternion_to_rotation_matrix
mxconstantmult = matrix_constant_mult
mxvectormult = matrix_vector_mult
vectormxmult = vectormatrixmult = vector_matrix_mult
mxmult = matrixmult = matrix_mult
eulerToRotationMatrix3 = euler_to_rotation_matrix
rotationMatrix3ToEuler = rotation_matrix_to_euler
axisAngleToQuaternion = axis_angle_to_quaternion
axisAngleToRotationMatrix = axis_angle_to_rotation_matrix
