import os
import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
# Define the Arrow3D class
# from mpl_toolkits.mplot3d import Axes3D
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# from matplotlib.patches import FancyArrowPatch
# from mpl_toolkits.mplot3d import proj3d

class TransformationMatrix:
    def __init__(self):
        """
        Initialize the transformation matrix as a 4x4 identity matrix.
        """
        self.H = np.eye(4)
        self.info = ["default1", "default2"]
        self.units = "mm"

    @property
    def T(self):
        """Get the translation vector."""
        return self.H[:3, 3]

    @T.setter
    def T(self, t):
        """Set the translation vector."""
        t = np.asarray(t).flatten()
        if t.shape[0] == 3:
            self.H[:3, 3] = t
        else:
            raise ValueError("Translation vector must have 3 elements.")

    @property
    def R(self):
        """Get the rotation matrix."""
        return self.H[:3, :3]

    @R.setter
    def R(self, r):
        """Set the rotation matrix."""
        r = np.asarray(r)
        if r.shape == (3, 3):
            self.H[:3, :3] = r
        else:
            raise ValueError("Rotation matrix must be 3x3.")

    @property
    def angles(self):
        """Get Euler angles in radians (XYZ convention)."""
        return R.from_matrix(self.R).as_euler('xyz')

    @angles.setter
    def angles(self, angles):
        """Set Euler angles (in radians) using XYZ convention."""
        self.R = R.from_euler('xyz', angles).as_matrix()

    @property
    def angles_degree(self):
        """Get Euler angles in degrees."""
        return np.degrees(self.angles)

    @angles_degree.setter
    def angles_degree(self, angles):
        """Set Euler angles in degrees."""
        self.angles = np.radians(angles)

    @property
    def quaternion(self):
        """Get the quaternion representation of the rotation."""
        return R.from_matrix(self.R).as_quat()

    @quaternion.setter
    def quaternion(self, quat):
        """Set the rotation matrix using a quaternion."""
        self.R = R.from_quat(quat).as_matrix()

    def transform(self, points):
        """
        Apply the transformation to a set of 3D points.
        :param points: Nx3 array of points.
        :return: Transformed Nx3 array.
        """
        points = np.asarray(points)
        if points.ndim == 1 and points.shape[0] == 3:
            points = points.reshape(1, 3)
        elif points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("Input points should have shape (N, 3) or (3,)")

        # Convert to homogeneous coordinates
        homogeneous_points = np.hstack((points, np.ones((points.shape[0], 1))))

        # Apply transformation
        transformed_points = (self.H @ homogeneous_points.T).T

        return transformed_points[:, :3]  # Remove the homogeneous coordinate

    def invert(self):
        """Invert the transformation matrix."""
        H_inv= np.linalg.inv(self.H)
        self.info = self.info[::-1]
        self.H = H_inv

    def save_bundler_file(self, output_file, intrinsics = None):
        """
        Write a Bundler file (v0.3) for MeshLab texturing.

        Parameters:
          T : (4,4) np.ndarray
              The provided transformation matrix (assumed camera-to-world).
          K : (3,3) np.ndarray
              The intrinsic matrix.
          output_file : str
              The filename for the output Bundler file.
        """
        # Compute the average focal length from the intrinsics.
        # Bundler expects a single focal length (in pixels).
        if intrinsics==None:
            K = np.array([
        [1.770689941406250000e+03, 0.000000000000000000e+00, 6.852999877929687500e+02],
        [0.000000000000000000e+00, 1.765030029296875000e+03, 4.927000122070312500e+02],
        [0.000000000000000000e+00, 0.000000000000000000e+00, 1.000000000000000000e+00]
    ])
        else:
            K = intrinsics
        f = (K[0, 0] + K[1, 1]) / 2.0

        # If no radial distortion is provided, set them to zero.
        k1, k2 = 0.0, 0.0

        # Extract the rotation matrix (R) and translation vector (t) from T.

        # For Bundler, we need the world-to-camera transformation.
        # If T is camera-to-world, its inverse is:
        #   R_inv = R^T, and t_inv = -R^T * t

        R_inv = self.H[:3, :3]
        t_inv = self.H[:3, 3]
        # Build the Bundler file content.
        lines = []
        lines.append("# Bundle file v0.3")
        lines.append("1 0")  # one camera, zero points
        lines.append(f"{f:.8f} {k1:.8f} {k2:.8f}")

        # Add the rotation matrix rows (world-to-camera rotation).
        for row in R_inv:
            lines.append(" ".join(f"{val:.8f}" for val in row))
        # Add the translation vector.
        lines.append(" ".join(f"{val:.8f}" for val in t_inv))

        bundler_content = "\n".join(lines)

        # Write the content to the specified output file.
        with open(output_file, "w") as f_out:
            f_out.write(bundler_content)

        print(f"Bundler file written to {output_file}")

    def load_bundler_file(self, filename):
        """
        Load the transformation matrix from a Bundler file, ignoring the first 3 lines.
        :param filename: Path to the input file.
        """
        with open(filename, 'r') as f:
            lines = f.readlines()[3:]  # Ignore the first 3 lines

            # Read the rotation matrix
            R = []
            for i in range(3):
                R.append(list(map(float, lines.pop(0).split())))
            self.R = np.array(R)

            # Read the translation vector
            T = list(map(float, lines.pop(0).split()))
            self.T = np.array(T)

    def plot(self, scale=1.0):
        """
        Plot the transformation as a coordinate frame.
        Requires matplotlib.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Define the origin and the end points of the axes in homogeneous coordinates
        origin = np.array([0, 0, 0])
        x_axis = np.array([scale, 0, 0])
        y_axis = np.array([0, scale, 0])
        z_axis = np.array([0, 0, scale])

        # Apply the transformation
        origin_transformed = self.transform(origin)
        x_axis_transformed = self.transform(x_axis)
        y_axis_transformed = self.transform(y_axis)
        z_axis_transformed = self.transform(z_axis)

        # Plot the transformed axes

        ax = fig.add_subplot(111, projection="3d")
        ax.plot([origin_transformed[0, 0]], [origin_transformed[0, 1]], [origin_transformed[0, 2]], 'o', markersize=10,
                color='red', alpha=0.5)
        # Plot the lines
        ax.plot([origin_transformed[0,0], x_axis_transformed[0, 0]], [origin_transformed[0,1], x_axis_transformed[0, 1]], [origin_transformed[0,2], x_axis_transformed[0, 2]],
                color='red',label='X-axis')
        ax.plot([origin_transformed[0,0], y_axis_transformed [0, 0]], [origin_transformed[0,1], y_axis_transformed  [0, 1]], [origin_transformed[0,2], y_axis_transformed [0, 2]],
                color='green',label='Y-axis')
        ax.plot([origin_transformed[0,0], z_axis_transformed[0, 0]], [origin_transformed[0,1], z_axis_transformed[0, 1]], [origin_transformed[0,2], z_axis_transformed[0, 2]],
                color='blue',label='Z-axis')


        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.legend()

        # Set the aspect ratio to be equal
        ax.set_box_aspect([1, 1, 1])

        plt.show()

    def plot_open3d(self, scale=1.0):
        """
        Plot the transformation as a coordinate frame using Open3D.
        Requires open3d.
        """
        # Create the transformation coordinate frame
        import open3d as o3d
        mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=scale, origin=self.T)
        R = self.R
        mesh_frame.rotate(R, center=self.T)

        # Create the base coordinate frame at the origin
        base_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=scale, origin=[0, 0, 0])

        # Create a marker (e.g., a sphere) at the origin
        marker = o3d.geometry.TriangleMesh.create_sphere(radius=0.1)
        marker.translate([0, 0, 0])
        marker.paint_uniform_color([1, 0, 0])  # Red color

        # Visualize both frames and the marker
        o3d.visualization.draw_geometries([mesh_frame, base_frame, marker])

    def copy(self):
        """
        Return a copy of the current instance.
        """
        new_instance = TransformationMatrix()
        new_instance.H = np.copy(self.H)
        new_instance.info = self.info[:]
        new_instance.units = self.units
        return new_instance

    def load_from_json(self, filename):
        import json
        with open(filename, 'r') as f:
            data = json.load(f)

        self.H = np.array(data['H'])
        self.info = data['info']
        self.units = data['units']

    def save_to_json(self, filename):
        import json
        #make sure the directory exists
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        data = {
            'H': self.H.tolist(),
            'info': self.info,
            'units': self.units
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    def __matmul__(self, other):
        """
        Overload the @ operator for transformation chaining.
        """
        if not isinstance(other, TransformationMatrix):
            raise TypeError("Can only multiply with another TransformationMatrix")

        result = TransformationMatrix()
        result.H = self.H @ other.H
        info = [self.info[0], other.info[-1]] # todo, check this
        result.info = info
        return result

    @staticmethod
    def calculate_rigid_transform(A, B):
        """
        Calculates the optimal rigid transformation (rotation and translation)
        that aligns point set A to point set B using SVD.
        Requires at least 3 corresponding points.

        Args:
            A (np.ndarray): An Nx3 array of points in the source coordinate system.
            B (np.ndarray): An Nx3 array of corresponding points in the target coordinate system.

        Returns:
            TransformationMatrix: An object representing the transformation that maps A to B.

        Raises:
            ValueError: If the point sets do not have the same shape, or if fewer
                        than 3 points are provided.
        """
        A = np.asarray(A)
        B = np.asarray(B)

        if A.shape != B.shape:
            raise ValueError("Point sets A and B must have the same shape.")
        if A.shape[0] < 3:
            raise ValueError("At least 3 points are required to calculate the transformation.")
        if A.shape[1] != 3:
            raise ValueError("Points must be 3D.")

        # 1. Find centroids
        centroid_A = np.mean(A, axis=0)
        centroid_B = np.mean(B, axis=0)

        # 2. Center the points (remove translation component)
        A_centered = A - centroid_A
        B_centered = B - centroid_B

        # 3. Calculate the covariance matrix H
        H = A_centered.T @ B_centered

        # 4. Perform SVD
        U, S, Vt = np.linalg.svd(H)

        # 5. Calculate rotation matrix R
        R_calc = Vt.T @ U.T

        # 6. Handle the special case of a reflection (det(R) = -1)
        # This can happen if the data is noisy or degenerate.
        if np.linalg.det(R_calc) < 0:
            # Flip the sign of the last column of V (or U)
            Vt_corrected = Vt.copy()
            Vt_corrected[2, :] *= -1
            R_calc = Vt_corrected.T @ U.T

        # 7. Calculate the translation vector t
        t_calc = centroid_B - R_calc @ centroid_A

        # 8. Create and return the TransformationMatrix object
        transform = TransformationMatrix()
        transform.R = R_calc
        transform.T = t_calc
        return transform


    def __repr__(self):
        return f"TransformationMatrix(\n{self.H})"
