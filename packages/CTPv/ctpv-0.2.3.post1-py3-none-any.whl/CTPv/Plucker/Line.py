import matplotlib.pyplot as plt
import numpy as np

def intersection_between_2_lines(L1, L2):
    """
    Compute the intersection point and distance between two lines in 3D space.

    Parameters:
    L1, L2 : Line objects
        Line objects containing start points and direction vectors.

    Returns:
    Point : numpy array of shape (3,)
        The midpoint of the closest points on the two lines.
    distance : float
        The shortest distance between the two lines.
    """
    p1, u = L1.Ps, L1.V
    p3, v = L2.Ps, L2.V
    w = (p1 + u) - (p3 + v)
    b = np.sum(u * v, axis=1)
    d = np.sum(u * w, axis=1)
    e = np.sum(v * w, axis=1)
    D = 1 - b ** 2

    # Avoid division by zero for parallel lines
    D[D == 0] = np.finfo(float).eps

    sc = (b * e - d) / D
    tc = (e - b * d) / D

    point1 = p1 + u + (sc[:, np.newaxis] * u)
    point2 = p3 + v + (tc[:, np.newaxis] * v)

    Points = (point1 + point2) / 2

    dP = w + (sc[:, np.newaxis] * u) - (tc[:, np.newaxis] * v)
    distances = np.linalg.norm(dP, axis=1)

    return Points, distances

class Line:
    kind = 'Line'  # class variable shared by all instances

    def __init__(self, *args):
        """
        Initialize a Line object.

        Parameters:
        *args : variable length argument list
            If no arguments are provided, Ps and Pe are set to None.
            If one argument is provided, it is assumed to be the Plucker coordinates.
            If two arguments are provided, they are assumed to be the start and end points.
        """
        if len(args) == 0:
            self.Ps = None
            self.Pe = None
        elif len(args) == 1:
            self.Plucker = args[0]
        elif len(args) == 2:
            self.Ps = args[0]
            self.Pe = args[1]
        else:
            raise ValueError("Invalid number of arguments!")

    @property
    def V(self):
        """
        Get the direction vector of the line.

        Returns:
        numpy array of shape (3,)
            The direction vector from Ps to Pe.
        """
        if self.Ps is not None and self.Pe is not None:
            return self._normalize_vectors(self.Pe - self.Ps)
        return None

    @V.setter
    def V(self, value):
        """
        Set the direction vector of the line.

        Parameters:
        value : numpy array of shape (3,)
            The new direction vector.
        """
        if self.Ps is not None:
            self.Pe = value + self.Ps

    @property
    def Plucker(self):
        """
        Get the Plucker coordinates of the line.

        Returns:
        numpy array of shape (6,)
            The Plucker coordinates [V, U] where V is the direction vector and U is the moment vector.
        """
        V = self.V
        U = np.cross(self.Ps, self.Ps + V)
        return np.hstack((V, U))

    @Plucker.setter
    def Plucker(self, value):
        """
        Set the Plucker coordinates of the line.

        Parameters:
        value : numpy array of shape (6,)
            The Plucker coordinates [V, U] where V is the direction vector and U is the moment vector.
        """
        Vp = value[:, :3]
        Up = value[:, 3:]
        self.Ps = np.cross(Vp, Up)
        self.V = Vp

    @property
    def Plucker2(self):
        """
        Get not normalised representation of the Plucker coordinates of the line.

        Returns:
        numpy array of shape (6,)
            The not normalised Plucker coordinates [m, b] where m is the moment vector and b is the direction vector.
        """
        m = np.cross(self.Ps, self.Pe)
        return np.hstack((m, self.Pe - self.Ps))

    @Plucker2.setter
    def Plucker2(self, value):
        """
        Set the not normalised Plucker coordinates of the line.

        Parameters:
        value : numpy array of shape (6,)
            The not normalised Plucker coordinates [m, b] where m is the moment vector and b is the direction vector.
        """
        a = value[:, :3]
        b = value[:, 3:]
        self.Ps = np.column_stack((-a[:, 1] / b[:, 2], a[:, 0] / b[:, 2], np.zeros(a.shape[0])))
        self.V = b

    def GetAngle(self):
        """
        Compute the angle between the line and the z-axis.

        Returns:
        numpy array of shape (n, 1)
            The angles in degrees between the line and the z-axis for each start point.
        """
        v = np.array([0, 0, 1])
        ThetaInDegrees = np.zeros((self.Ps.shape[0], 1))
        for i in range(self.Ps.shape[0]):
            ThetaInDegrees[i, 0] = np.degrees(np.arctan2(np.linalg.norm(np.cross(self.V[i, :], v)), np.dot(self.V[i, :], v)))
        return ThetaInDegrees

    def TransformLines(self, H):
        """
        Transform the line using a homogeneous transformation matrix.

        Parameters:
        H : Homogeneous transformation matrix
            The transformation matrix to apply to the line.
        """
        self.Ps = H.transform(self.Ps)
        self.Pe = H.transform(self.Pe)

    def plot(self, limits=None, colors=None, linewidth=2, linestyle='-'):
        """
        Plot the lines in 3D space.

        Parameters:
        limits : list of floats, optional
            The limits of the plot in the format [xmin, xmax, ymin, ymax, zmin, zmax].
        colors : numpy array, optional
            The colors to use for the lines.
        linewidth : float, optional
            The width of the lines.
        linestyle : str, optional
            The style of the lines.
        """
        if limits is None:
            limits = [-5, 5, -5, 5, -5, 5]
        if colors is None:
            colors = plt.cm.jet(np.linspace(0, 1, self.Ps.shape[0]))
        elif colors.shape[0] < self.Ps.shape[0]:
            colors = np.tile(colors, (self.Ps.shape[0], 1))

        xmin, xmax, ymin, ymax, zmin, zmax = limits
        dirs = self.V
        k_min = (np.array([xmin, ymin, zmin]) - self.Ps) / dirs
        k_max = (np.array([xmax, ymax, zmax]) - self.Ps) / dirs

        valid_x_min = self._is_within_bounds(self.Ps + dirs * k_min[:, 0], ymin, ymax, zmin, zmax)
        valid_y_min = self._is_within_bounds(self.Ps + dirs * k_min[:, 1], xmin, xmax, zmin, zmax)
        valid_z_min = self._is_within_bounds(self.Ps + dirs * k_min[:, 2], xmin, xmax, ymin, ymax)

        valid_x_max = self._is_within_bounds(self.Ps + dirs * k_max[:, 0], ymin, ymax, zmin, zmax)
        valid_y_max = self._is_within_bounds(self.Ps + dirs * k_max[:, 1], xmin, xmax, zmin, zmax)
        valid_z_max = self._is_within_bounds(self.Ps + dirs * k_max[:, 2], xmin, xmax, ymin, ymax)

        valid = np.column_stack((valid_x_min, valid_y_min, valid_z_min, valid_x_max, valid_y_max, valid_z_max))
        assert np.all(np.sum(valid, axis=1) == 2), 'Not all lines fit in window range!'

        k = np.column_stack((k_min, k_max))
        k_valid = k[valid].reshape(2, -1).T
        start_points = self.Ps + dirs * k_valid[:, 0]
        end_points = self.Ps + dirs * k_valid[:, 1]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for i in range(start_points.shape[0]):
            ax.plot([start_points[i, 0], end_points[i, 0]],
                    [start_points[i, 1], end_points[i, 1]],
                    [start_points[i, 2], end_points[i, 2]],
                    color=colors[i], linewidth=linewidth, linestyle=linestyle)
        plt.show()

    def PlotLine(self, colori = 'g', linewidth = 2, *args):
        """
        Plot a single line in 3D space.

        Parameters:
        colori : str, optional
            The color of the line.
        linewidth : float, optional
            The width of the line.
        *args : variable length argument list
            If one argument is provided, it is assumed to be the end point.
        """
        P1 = self.Ps
        if len(args) == 1:
            P3 = self.Pe
        else:
            P3 = self.Ps + self.V

        if P1.shape[0] > 500:
            P1 = self._downsample(P1, round(P1.shape[0] / 500) + 1)
            P3 = self._downsample(P3, round(P3.shape[0] / 500) + 1)
            print('Too many lines to plot, showing downsampled version')

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for i in range(P1.shape[0]):
            color = 'b' if i == 0 or i == 4 else 'k' if i == 4 else 'b'
            ax.plot([P1[i, 0], P3[i, 0]], [P1[i, 1], P3[i, 1]], [P1[i, 2], P3[i, 2]], color=color, linewidth=linewidth)
            if i > 500:
                print('Too many lines to plot')
                break
        plt.show()

    def FindXYZNearestLine(self, XYZ):
        """
        Find the index of the line closest to a given point.

        Parameters:
        XYZ : numpy array of shape (3,)
            The point to find the closest line to.

        Returns:
        int
            The index of the closest line.
        """
        distances = self.DistanceLinePoint(XYZ)
        return np.argmin(distances)

    def FitLine(self, XYZ):
        """
        Fit a line to a set of points.

        Parameters:
        XYZ : numpy array of shape (n, 3)
            The points to fit the line to.
        """
        l = self._fitline3d(XYZ.T).T
        self.Ps = l[0]
        self.Pe = l[1]

    def FitLineRansac(self, XYZ, t=10):
        """
        Fit a line to a set of points using the RANSAC algorithm.

        Parameters:
        XYZ : numpy array of shape (n, 3)
            The points to fit the line to.
        t : float, optional
            The threshold distance for a point to be considered an inlier.
        """
        Ps, Pe = self._ransac_fit_line(XYZ.T, t)
        self.Ps = Ps.T
        self.Pe = Pe.T

    def NormaliseLine(self):
        """
        Normalize the line so that the z-coordinate of the start point is zero.
        """
        try:
            scale = -self.Ps[:, 2] / self.V[:, 2]
            self.Ps = self.Ps + scale[:, np.newaxis] * self.V
        except:
            pass

    def DistanceLinePoint(self, XYZ):
        """
        Compute the distance from a point to the line.

        Parameters:
        XYZ : numpy array of shape (3,)
            The point to compute the distance to.

        Returns:
        numpy array of shape (n,)
            The distances from the point to each line.
        """
        return np.linalg.norm(np.cross(self.Pe - self.Ps, self.Ps - XYZ), axis=1) / np.linalg.norm(self.Pe - self.Ps, axis=1)

    def Lenght(self):
        """
        Compute the length of the line.

        Returns:
        numpy array of shape (n,)
            The lengths of the lines.
        """
        return np.linalg.norm(self.Ps - self.Pe, axis=1)

    @staticmethod
    def FromStartEnd(start_point, end_point):
        """
        Create a Line object from start and end points.

        Parameters:
        start_point : numpy array of shape (3,)
            The start point of the line.
        end_point : numpy array of shape (3,)
            The end point of the line.

        Returns:
        Line object
            The line object created from the start and end points.
        """
        line_object = Line()
        line_object.Ps = start_point
        line_object.Pe = end_point
        return line_object

    @staticmethod
    def FromPlucker(VU):
        """
        Create a Line object from Plucker coordinates.

        Parameters:
        VU : numpy array of shape (6,)
            The Plucker coordinates [V, U] where V is the direction vector and U is the moment vector.

        Returns:
        Line object
            The line object created from the Plucker coordinates.
        """
        line_object = Line()
        line_object.Plucker = VU
        return line_object

    def _normalize_vectors(self, vectors):
        """
        Normalize a set of vectors.

        Parameters:
        vectors : numpy array of shape (n, 3)
            The vectors to normalize.

        Returns:
        numpy array of shape (n, 3)
            The normalized vectors.
        """
        norms = np.linalg.norm(vectors, axis=1)
        return vectors / norms[:, np.newaxis]

    def _is_within_bounds(self, points, xmin, xmax, ymin, ymax, zmin, zmax):
        """
        Check if points are within a given bounding box.

        Parameters:
        points : numpy array of shape (n, 3)
            The points to check.
        xmin, xmax, ymin, ymax, zmin, zmax : float
            The bounds of the box.

        Returns:
        numpy array of shape (n,)
            A boolean array indicating whether each point is within the bounds.
        """
        return (points[:, 0] >= xmin) & (points[:, 0] <= xmax) & \
               (points[:, 1] >= ymin) & (points[:, 1] <= ymax) & \
               (points[:, 2] >= zmin) & (points[:, 2] <= zmax)

    def _downsample(self, points, factor):
        """
        Downsample a set of points.

        Parameters:
        points : numpy array of shape (n, 3)
            The points to downsample.
        factor : int
            The downsampling factor.

        Returns:
        numpy array of shape (n/factor, 3)
            The downsampled points.
        """
        return points[::factor]

    def _fitline3d(self, XYZ):
        """
        Fit a line to a set of points in 3D space.

        Parameters:
        XYZ : numpy array of shape (3, n)
            The points to fit the line to.

        Returns:
        numpy array of shape (2, 3)
            The start and end points of the fitted line.
        """
        # Placeholder for the actual fitline3d implementation
        pass

    def AngleBetweenLines(self, L1, L2):
        """
        Compute the angle between two lines.

        Parameters:
        L1, L2 : Line objects
            The lines to compute the angle between.

        Returns:
        tuple of floats
            The angle in radians and degrees between the lines.
        """
        T1 = (np.cross(L1.V, L2.V))
        T2 = (np.dot(L1.V, np.transpose(L2.V)))
        T1R = np.linalg.norm((T1))
        Theta = np.arctan2(T1R, T2)
        ThetaDegree = Theta * 180 / np.pi
        return (Theta, ThetaDegree)

    def _ransac_fit_line(self, XYZ, t):
        """
        Fit a line to a set of points using the RANSAC algorithm.

        Parameters:
        XYZ : numpy array of shape (3, n)
            The points to fit the line to.
        t : float
            The threshold distance for a point to be considered an inlier.

        Returns:
        tuple of numpy arrays
            The start and end points of the fitted line.
        """
        # Placeholder for the actual RANSAC fit line implementation
        pass

    def HomogeneousTransformation(self, H, points):
        """
        Apply a homogeneous transformation to a set of points.

        Parameters:
        H : numpy array of shape (4, 4)
            The homogeneous transformation matrix.
        points : numpy array of shape (n, 3)
            The points to transform.

        Returns:
        numpy array of shape (n, 3)
            The transformed points.
        """
        # Placeholder for the actual homogeneous transformation implementation
        pass

    def GenerateRay(self, I, uv, visualize = False):
        """
        Generate rays from a sensor grid.

        Parameters:
        I : Sensor object
            The sensor to generate rays from.
        uv : numpy array of shape (n, 2)
            The sensor grid points.
        visualize : bool, optional
            Whether to visualize the rays.

        Returns:
        Line object
            The rays generated from the sensor grid.
        """
        rays = Line()
        Ps = uv.copy()  # sensor points

        # Adjust sensor points
        Ps[:, 0] = Ps[:, 0] - I.cx
        Ps[:, 1] = Ps[:, 1] - I.cy
        scale = 2 / 1  # just so the 'sensor' is not bigger than the object (only for visualization)
        Ps[:, 0] = Ps[:, 0] / I.fx * scale
        Ps[:, 1] = Ps[:, 1] / I.fy * scale  # f van Y
        Ps[:, 2] = 1 * scale

        Pf = np.zeros(Ps.shape)
        Pf[:, 2] = 0 * scale

        rays.Pe = Ps
        rays.Ps = Pf

        if visualize:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.plot(rays.Pe[:, 0], rays.Pe[:, 1], rays.Pe[:, 2], 'g', linewidth=5)
            ax.plot(rays.Ps[:, 0], rays.Ps[:, 1], rays.Ps[:, 2], 'g', linewidth=5)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z')
            ax.set_aspect('equal')
            plt.show()

        return rays
