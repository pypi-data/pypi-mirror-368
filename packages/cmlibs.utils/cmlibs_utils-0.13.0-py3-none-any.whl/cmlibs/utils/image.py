import dicom
import os

from cmlibs.maths import vectorops


def extractImageCorners(directory, filename):
    """
    Extract the image corners from an image that is assumed to be
    a DICOM image.
    Corners are returned as:

    [bottom left (bl), bottom right (br), top left (tl), top right (tr)]

    :param directory: the directory where the file given with filename exists.
    :param filename: the filename of the file to interrogate.
    :return: the corners of the image [bl, br, tl, tr]
    """
    ds = dicom.read_file(os.path.join(directory, filename))
    pixel_spacing = ds.PixelSpacing
    # delta_i = float(0.1)
    # delta_j = float(0.1)
    delta_i = float(pixel_spacing[0])
    delta_j = float(pixel_spacing[1])
    orient = [float(iop) for iop in ds.ImageOrientationPatient]
    pos = [float(ipp) for ipp in ds.ImagePositionPatient]
    rows = ds.Rows
    columns = ds.Columns
    # vectorops version
    orient_1 = orient[:3]
    orient_2 = orient[3:]
    pos_o = pos[:]
    pos = vectorops.sub(pos_o, vectorops.mult(vectorops.add(vectorops.mult(orient_1, 0.5),
                                                            vectorops.mult(orient_2, 0.5)), delta_i))

    A = [[orient[0]*delta_i, orient[3]*delta_j, 0, pos[0]],
         [orient[1]*delta_i, orient[4]*delta_j, 0, pos[1]],
         [orient[2]*delta_i, orient[5]*delta_j, 0, pos[2]],
         [                0,                 0, 0,      1]]
    b_tl = [0, 0, 0, 1]
    b_tr = [rows, 0, 0, 1]
    b_bl = [0, columns, 0, 1]
    b_br = [rows, columns, 0, 1]
    tl = vectorops.mxvectormult(A, b_tl)
    tr = vectorops.mxvectormult(A, b_tr)
    bl = vectorops.mxvectormult(A, b_bl)
    br = vectorops.mxvectormult(A, b_br)

    return [bl[:3], br[:3], tl[:3], tr[:3]]
    # numpy version
    # orient_1 = np.array(orient[:3])
    # orient_2 = np.array(orient[3:])
    # pos = np.array(pos_o) - delta_i * (0.5 * orient_1 + 0.5 * orient_2)
    # A = np.array([orient[0]*delta_i, orient[3]*delta_j, 0, pos[0],
    #               orient[1]*delta_i, orient[4]*delta_j, 0, pos[1],
    #               orient[2]*delta_i, orient[5]*delta_j, 0, pos[2],
    #                               0,                 0, 0,      1]).reshape(4, 4)
    # b_tl = np.array([0, 0, 0, 1])
    # b_tr = np.array([rows, 0, 0, 1])
    # b_bl = np.array([0, columns, 0, 1])
    # b_br = np.array([rows, columns, 0, 1])
    # tl = np.dot(A, b_tl)
    # tr = np.dot(A, b_tr)
    # bl = np.dot(A, b_bl)
    # br = np.dot(A, b_br)
    #
    # return [bl[:3].tolist(), br[:3].tolist(), tl[:3].tolist(), tr[:3].tolist()]
