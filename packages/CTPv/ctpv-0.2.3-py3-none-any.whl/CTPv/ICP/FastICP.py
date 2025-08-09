import time
import logging
import numpy as np
import open3d as o3d

from ICP import *
from ..Transformation.TransformationMatrix import TransformationMatrix


# A module-level logger for the __main__ block
logger = logging.getLogger(__name__)

class FastICPAligner(ICPAligner):
    """
    Inherits from ICPAligner to provide a faster alignment method
    by using random downsampling and a Point-to-Plane ICP metric.
    """

    def __init__(self, source_points, target_points, normal_estimation_radius=None):
        """
        Initializes the FastICPAligner.

        Args:
            source_points (np.ndarray): The source point cloud (Nx3 array).
            target_points (np.ndarray): The target point cloud (Nx3 array).
            normal_estimation_radius (float, optional): Radius for normal estimation.
                                                     If None, it's auto-calculated.
        """
        super().__init__(source_points, target_points)

        self.logger.info("⚡ Pre-computing target normals for faster Point-to-Plane ICP...")

        if normal_estimation_radius is None:
            # Dynamically determine a good radius based on the point cloud's size.
            max_extent = max(self.target_pcd.get_max_bound() - self.target_pcd.get_min_bound())
            normal_estimation_radius = max_extent * 0.05  # Use 5% of the largest dimension
            self.logger.info(f"✅ Dynamically calculated normal estimation radius: {normal_estimation_radius:.4f}")

        # For Point-to-Plane ICP, we only need to estimate normals on the target point cloud.
        # This saves computation time during initialization.
        self.target_pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=normal_estimation_radius, max_nn=30))

    def align(self, fitness=0.5, threshold=0.1, scales=None):
        """
        Overrides the parent align method. Runs a multi-scale ICP for high speed.
        It iteratively refines the alignment from very coarse to full resolution.

        Args:
            threshold (float): The base distance threshold for correspondences.
            scales (list of tuples, optional): A list of (downsample_ratio, max_iterations)
                                              to define the alignment pyramid. Defaults to a
                                              pre-defined 3-stage pyramid.
          Returns:
            TransformationMatrix: The calculated transformation object.
        """

        if scales is None:
            # A default multi-scale pyramid: (downsample_ratio, max_iterations)
            # Start coarse and get finer. The last stage must have a ratio of 1.0.
            scales = [(0.1, 40), (0.25, 25), (1.0, 15)]

        self.logger.info(f"🚀 Running FAST multi-scale ICP ({len(scales)} stages)...")

        # --- Run the multi-scale alignment loop ---
        trans_init = np.identity(4)
        estimation_method = o3d.pipelines.registration.TransformationEstimationPointToPlane()

        for i, (ratio, max_iter) in enumerate(scales):
            is_final_stage = (ratio == 1.0)
            current_threshold = threshold if not is_final_stage else threshold / 2

            self.logger.info(f"--- Stage {i+1}/{len(scales)}: Ratio={ratio}, Max Iter={max_iter}, Threshold={current_threshold:.2f} ---")

            if is_final_stage:
                source_down = self.source_pcd
                target_down = self.target_pcd
                self.logger.info("   (Using full resolution point cloud)")
            else:
                source_down = self.source_pcd.random_down_sample(ratio)
                target_down = self.target_pcd.random_down_sample(ratio)
                self.logger.info(f"   (Downsampling to ~{len(source_down.points)} points)")

            # Run ICP for the current stage
            self.reg_p2p = o3d.pipelines.registration.registration_icp(
                source_down, target_down, current_threshold, trans_init,
                estimation_method,
                o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness = fitness, max_iteration=max_iter)
            )

            # Use the result of this stage as the initial guess for the next one
            trans_init = self.reg_p2p.transformation

        # Store the final, refined results
        transformation = self.reg_p2p.transformation
        T2 = TransformationMatrix()
        T2.H = transformation.copy()
        self.transformation = T2
        self.inlier_rmse = self.reg_p2p.inlier_rmse

        self.logger.info("✅ FAST multi-scale alignment successful!")
        self.print_results()
        return self.transformation


