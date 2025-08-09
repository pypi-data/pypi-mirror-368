import time
import logging
import numpy as np
import open3d as o3d
from plyfile import PlyData

from ..Transformation.TransformationMatrix import TransformationMatrix


# A module-level logger for static methods or functions
logger = logging.getLogger(__name__)


def pick_points_legacy_support(pcd, window_name="Pick Points"):
    """
    A helper function to replicate o3d.visualization.pick_points for versions
    of Open3D where it might not be available. It uses the VisualizerWithEditing class.
    This function is more robust across different library versions.

    Args:
        pcd (o3d.geometry.PointCloud): The point cloud to pick points from.
        window_name (str): The title of the visualization window.

    Returns:
        list: A list of integers representing the indices of the picked points.
    """
    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window(window_name=window_name)
    vis.add_geometry(pcd)
    # Let the user interact with the window and pick points
    vis.run()
    vis.destroy_window()
    # get_picked_points() returns a list of o3d.visualization.PickedPoint objects.
    # We need to extract the 'index' attribute from each object.
    picked_points = vis.get_picked_points()
    return [p.index for p in picked_points]


class ICPAligner:
    """A class to perform ICP alignment between two point clouds."""

    def __init__(self, source_points, target_points):
        """
        Initializes the ICPAligner.

        Args:
            source_points (np.ndarray): The source point cloud (Nx3 array).
            target_points (np.ndarray): The target point cloud (Nx3 array).
        """
        # Create a logger specific to this class instance for better traceability
        self.logger = logging.getLogger(self.__class__.__name__)
        self.source_points = source_points
        self.target_points = target_points

        self.source_pcd = self._create_pcd_from_points(source_points, color=[1.0, 0.0, 0.0])  # Red
        self.target_pcd = self._create_pcd_from_points(target_points, color=[0.0, 0.0, 1.0])  # Blue

        self.reg_p2p = None
        self.transformation = None
        self.inlier_rmse = None

    @staticmethod
    def _create_pcd_from_points(points, color):
        """Creates an Open3D PointCloud object from a numpy array."""
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.paint_uniform_color(color)
        return pcd

    @staticmethod
    def load_ply(file_path):
        """Loads a PLY file into a numpy array."""
        try:
            plydata = PlyData.read(file_path)
            vertex = plydata['vertex']
            points = np.vstack([vertex['x'], vertex['y'], vertex['z']]).T
            return points
        except Exception as e:
            logger.error(f"Error loading PLY file {file_path}: {e}")
            return None

    def run_manual_pre_alignment(self):
        """
        Opens a UI for the user to manually select at least 4 corresponding points
        on the source and target point clouds to compute an initial transformation.
        """
        self.logger.info("Estimating normals for better visualization...")
        # Estimate normals if they don't exist for better visualization
        if not self.source_pcd.has_normals():
            source_extent = np.max(self.source_pcd.get_max_bound() - self.source_pcd.get_min_bound())
            radius = source_extent * 0.05  # Use 5% of the largest dimension
            self.logger.info(f"Dynamically calculated normal estimation radius for source: {radius:.4f}")
            self.source_pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=30))
            self.source_pcd.orient_normals_consistent_tangent_plane(100)

        if not self.target_pcd.has_normals():
            target_extent = np.max(self.target_pcd.get_max_bound() - self.target_pcd.get_min_bound())
            radius = target_extent * 0.05  # Use 5% of the largest dimension
            self.logger.info(f"Dynamically calculated normal estimation radius for target: {radius:.4f}")
            self.target_pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=30))
            self.target_pcd.orient_normals_consistent_tangent_plane(100)

        self.logger.info("--- Manual Point Selection ---")
        self.logger.info("A window will open for the RED (source) point cloud.")
        self.logger.info("Instructions:")
        self.logger.info("  1. Rotate the view to a recognizable orientation.")
        self.logger.info("  2. Hold [SHIFT] and left-click to select at least 4 points.")
        self.logger.info("  3. Press [Q] to close the window when you are done.")
        self.logger.info("  (Press [H] in the window to see all controls).")

        # Use the new robust helper function instead of the direct call
        picked_idx_source = pick_points_legacy_support(self.source_pcd, window_name="Pick points on SOURCE (RED)")

        if not picked_idx_source or len(picked_idx_source) < 4:
            self.logger.error(f"At least 4 points must be selected. You selected {len(picked_idx_source)}. Aborting.")
            return np.identity(4)

        self.logger.info(f"{len(picked_idx_source)} points selected on the source cloud.")
        self.logger.info("---")
        self.logger.info("A window will now open for the BLUE (target) point cloud.")
        self.logger.info(f"Please select the SAME {len(picked_idx_source)} points in the EXACT SAME ORDER.")

        # Use the new robust helper function again for the target
        picked_idx_target = pick_points_legacy_support(self.target_pcd, window_name="Pick points on TARGET (BLUE)")

        if len(picked_idx_source) != len(picked_idx_target):
            self.logger.error(
                f"Number of points mismatch: {len(picked_idx_source)} on source, "
                f"{len(picked_idx_target)} on target. Aborting."
            )
            return np.identity(4)

        # Create correspondence set from the picked indices
        correspondences = o3d.utility.Vector2iVector(np.asarray([picked_idx_source, picked_idx_target]).T)

        self.logger.info("Calculating initial transformation from selected points...")
        # Estimate transformation from the correspondences
        estimation = o3d.pipelines.registration.TransformationEstimationPointToPoint()
        transformation = estimation.compute_transformation(
            self.source_pcd, self.target_pcd, correspondences
        )

        return transformation

    def align(self, threshold=10, fitness=0.5, max_iteration=2000, manual_pre_alignment=False):
        """
        Runs the ICP algorithm to align the source point cloud to the target.

        Args:
            threshold (float): Distance threshold for correspondences.
            max_iteration (int): Maximum number of ICP iterations.
            manual_pre_alignment (bool): If True, opens a manual point-picking UI
                                         to establish a rough initial alignment.
          Returns:
            TransformationMatrix: The calculated transformation object.
        """
        trans_init = np.identity(4)  # Default initial guess is an identity matrix
        if manual_pre_alignment:
            self.logger.info("Manual pre-alignment step initiated.")
            trans_init = self.run_manual_pre_alignment()
            # Check if the user aborted or failed the selection
            if np.array_equal(trans_init, np.identity(4)):
                self.logger.warning("Manual pre-alignment did not produce a transformation. Using identity matrix.")
            self.logger.info("Manual pre-alignment complete. Proceeding with ICP.")

        self.logger.info("🚀 Running Open3D's standard Point-to-Point ICP alignment...")

        self.reg_p2p = o3d.pipelines.registration.registration_icp(
            self.source_pcd, self.target_pcd, threshold, trans_init,
            o3d.pipelines.registration.TransformationEstimationPointToPoint(),
            o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=fitness, max_iteration=max_iteration)
        )
        transformation = self.reg_p2p.transformation
        T2 = TransformationMatrix()
        T2.H = transformation.copy()
        self.transformation = T2
        self.inlier_rmse = self.reg_p2p.inlier_rmse
        self.logger.info("✅ Alignment successful!")
        return self.transformation

    def print_results(self):
        """Logs the results of the ICP alignment."""
        if self.transformation is None:
            self.logger.warning("Alignment has not been run. Please call align() first.")
            return

        T2 = self.transformation

        # Group results into a single log message for clarity
        results_str = (
            "Transformation is:\n"
            f"  - Translation (T): [{T2.T[0]:.2f}, {T2.T[1]:.2f}, {T2.T[2]:.2f}]\n"
            f"  - Rotation (°):    [{T2.angles_degree[0]:.2f}, {T2.angles_degree[1]:.2f}, {T2.angles_degree[2]:.2f}]\n"
            f"  Inlier RMSE (Average Error): {self.inlier_rmse:.4f}"
        )
        # print the eucledian dicance
        euclidean_distance = np.linalg.norm(T2.T)
        results_str += f"\n  - Euclidean Distance: {euclidean_distance:.2f}"

        self.logger.info(results_str)

    def visualize_before_alignment(self):
        """Visualizes the point clouds before alignment."""
        o3d.visualization.draw_geometries([self.source_pcd, self.target_pcd], window_name="Before Alignment")

    def visualize_after_alignment(self):
        """Visualizes the aligned point clouds."""
        if self.transformation is None:
            self.logger.warning("Alignment has not been run. Cannot visualize result.")
            return

        # Create a copy to transform for visualization
        source_pcd_transformed = o3d.geometry.PointCloud(self.source_pcd)
        source_pcd_transformed.transform(self.transformation.H)
        source_pcd_transformed.paint_uniform_color([0.0, 1.0, 0.0])  # Green
        o3d.visualization.draw_geometries([source_pcd_transformed, self.target_pcd], window_name="After Alignment")

