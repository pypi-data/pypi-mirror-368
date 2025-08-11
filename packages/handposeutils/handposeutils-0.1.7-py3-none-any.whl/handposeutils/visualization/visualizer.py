import open3d as o3d
import numpy as np
from scipy.spatial import ConvexHull
import time

class HandPoseVisualizer:
    """
    Visualizer for hand poses using Open3D.

    Attributes
    ----------
    window_name : str
        Name of the Open3D visualization window.
    colors : dict
        Color profile for landmarks, ligaments, and palm.
    """
    def __init__(self, window_name="Hand Pose Visualizer", color_profile: dict = None):
        """
        Initialize visualizer window and default colors.

        Parameters
        ----------
        window_name : str, optional
            Title of the visualization window.
        color_profile : dict, optional
            Custom colors for different hand parts.
        """
        self.window_name = window_name
        self.vis = o3d.visualization.Visualizer()
        self.window_created = False

        self.hand_poses = []
        self.geometry = []

        self.landmark_spheres = []  # List of list[Mesh] — one sublist per hand
        self.ligament_cylinders = []  # List of list[Mesh]
        self.palm_meshes = []  # List[Mesh] — one palm mesh per hand
        self.cache_initialized = False

        self.FINGERS = {
            "thumb": [1, 2, 3, 4],
            "index": [5, 6, 7, 8],
            "middle": [9, 10, 11, 12],
            "ring": [13, 14, 15, 16],
            "pinky": [17, 18, 19, 20]
        }

        self.COLORS_DEFAULT = {
            "landmarks": [0.1, 0.6, 0.9],
            "proximals": [0.5, 0, 0],
            "intermediates": [0, 1, 0.5],
            "distals": [0, 0.5, 1],
            "palm": [0, 0, 1],
        }

        self.colors = self.COLORS_DEFAULT if color_profile is None else color_profile

    def initialize_window(self):
        if not self.window_created:
            self.vis.create_window(window_name=self.window_name)
            self.window_created = True


    def set_hand_poses(self, hand_pose_list):
        """
        Set the list of HandPose objects to visualize.

        Parameters
        ----------
        hand_pose_list : list
            List of HandPose instances.
        """
        if len(self.hand_poses) != len(hand_pose_list):
            self.cache_initialized = False
            self._reset_geometry()
        self.hand_poses = hand_pose_list


    def set_colors(self, colors: dict):
        """
        Update color profile for visualization.

        Parameters
        ----------
        colors : dict
            Colors to use for landmarks, ligaments, and palm.
        """
        self.colors = colors

    def __create_sphere(self, center, radius=1.0, resolution=5, color=None):
        """
        Create a colored sphere mesh at a given center.

        Parameters
        ----------
        center : array-like
            3D coordinates for sphere center.
        radius : float, optional
            Sphere radius.
        resolution : int, optional
            Sphere resolution/detail.
        color : array-like, optional
            RGB color for the sphere.

        Returns
        -------
        o3d.geometry.TriangleMesh
            Sphere mesh.
        """
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius, resolution=resolution)
        sphere.translate(center)
        sphere.paint_uniform_color(color or self.colors["landmarks"])
        return sphere

    def __create_cylinder_between(self, p1, p2, radius=0.8, resolution=5, color=[1, 0, 0]):
        """
        Create a cylinder mesh connecting points p1 and p2.

        Parameters
        ----------
        p1, p2 : array-like
            3D endpoints of the cylinder.
        radius : float, optional
            Cylinder radius.
        resolution : int, optional
            Mesh resolution.
        color : array-like, optional
            RGB color of the cylinder.

        Returns
        -------
        o3d.geometry.TriangleMesh or None
            Cylinder mesh or None if zero-length.
        """
        p1 = np.array(p1, dtype=np.float64)
        p2 = np.array(p2, dtype=np.float64)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        if length == 0:
            return None
        axis /= length

        cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=radius, height=length, resolution=resolution)
        cylinder.paint_uniform_color(color)

        z_axis = np.array([0, 0, 1])
        v = np.cross(z_axis, axis)
        c = np.dot(z_axis, axis)
        if np.linalg.norm(v) < 1e-6:
            R = np.eye(3) if c > 0 else -np.eye(3)
        else:
            skew = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
            R = np.eye(3) + skew + skew @ skew * ((1 - c) / (np.linalg.norm(v) ** 2))
        cylinder.rotate(R, center=(0, 0, 0))
        midpoint = (p1 + p2) / 2
        cylinder.translate(midpoint)
        return cylinder

    def _build_geometry(self, finger_tips_shown=True, ligaments_shown=True, palm_shown=True):
        """
        Build Open3D geometry for current hand poses.

        Parameters
        ----------
        finger_tips_shown : bool, optional
            Whether to show landmark spheres.
        ligaments_shown : bool, optional
            Whether to show ligament cylinders.
        palm_shown : bool, optional
            Whether to show palm mesh.
        """
        self.geometry.clear()

        for hand_pose in self.hand_poses:
            coords = hand_pose.get_all_coordinates()
            landmark_points = np.array([[pt.x, pt.y, pt.z] for pt in coords])

            highlighted_finger = getattr(hand_pose, "getHighlightedFinger", lambda: None)()
            highlight_color = np.array(getattr(hand_pose, "getHighlightColor", lambda: (1.0, 1.0, 0.0))()) * 0.3

            # Landmarks
            if finger_tips_shown:
                for pt in landmark_points:
                    self.geometry.append(self.__create_sphere(pt, radius=1.0))

            # Ligaments
            if ligaments_shown:
                for finger_name, indices in self.FINGERS.items():
                    for i in range(len(indices) - 1):
                        p1 = landmark_points[indices[i]]
                        p2 = landmark_points[indices[i + 1]]
                        color = self.colors["proximals"] if i == 0 else \
                                self.colors["intermediates"] if i == 1 else \
                                self.colors["distals"]
                        cyl = self.__create_cylinder_between(p1, p2, radius=0.8, color=color)
                        if cyl:
                            self.geometry.append(cyl)

            # Palm
            if palm_shown:
                palm_indices = [0, 1, 5, 9, 13, 17]
                palm_points = landmark_points[palm_indices]
                hull = ConvexHull(palm_points[:, :2], qhull_options='QJ')
                hull_indices = hull.vertices
                triangles = []
                for i in range(1, len(hull_indices) - 1):
                    triangles.append([hull_indices[0], hull_indices[i], hull_indices[i + 1]])
                mesh = o3d.geometry.TriangleMesh()
                mesh.vertices = o3d.utility.Vector3dVector(palm_points)
                mesh.triangles = o3d.utility.Vector3iVector(triangles)
                mesh.paint_uniform_color(self.colors["palm"])
                mesh.compute_vertex_normals()
                self.geometry.append(mesh)

            # Highlight Glow
            if highlighted_finger in self.FINGERS:
                indices = self.FINGERS[highlighted_finger]
                for i in range(len(indices) - 1):
                    p1 = landmark_points[indices[i]]
                    p2 = landmark_points[indices[i + 1]]
                    glow_cyl = self.__create_cylinder_between(p1, p2, radius=1.5, color=highlight_color)
                    if glow_cyl:
                        self.geometry.append(glow_cyl)

            # Annotation
            annotation = getattr(hand_pose, "getAnnotation", lambda: None)()
            if annotation:
                wrist_coord = landmark_points[0]
                self.geometry.append(self.__create_sphere(wrist_coord + np.array([0, 0.02, 0]),
                                                          radius=1.0, color=(1.0, 1.0, 1.0)))
                print(f"[Annotation] {annotation} @ wrist: {wrist_coord}")


    def show_pose(self, finger_tips_shown=True, ligaments_shown=True, palm_shown=True):
        """
        Display the current hand poses in an interactive Open3D window.

        Parameters
        ----------
        finger_tips_shown : bool, optional
            Show landmark spheres.
        ligaments_shown : bool, optional
            Show ligament cylinders.
        palm_shown : bool, optional
            Show palm mesh.
        """

        self.initialize_window()

        if not self.hand_poses:
            print("[!] No pose to show.")
            return

        self.build_cached_geometry(self.hand_poses)  # List of poses

        print("[🖱️] Use left mouse to rotate, right mouse to pan, scroll to zoom. Press 'q' to quit.")
        self.vis.run()
        self.vis.destroy_window()

    def update_pose(self, finger_tips_shown=True, ligaments_shown=True, palm_shown=True):
        """
        Update the visualization with the current hand poses.

        Parameters
        ----------
        finger_tips_shown : bool, optional
            Show landmark spheres.
        ligaments_shown : bool, optional
            Show ligament cylinders.
        palm_shown : bool, optional
            Show palm mesh.
        """
        if not self.hand_poses:
            return

        if not self.cache_initialized:
            self.build_cached_geometry(self.hand_poses)

        self.update_cached_geometry(self.hand_poses)

    def _reset_geometry(self):
        """Clear all cached geometries and reset visualizer."""
        self.geometry = []
        self.landmark_spheres = []
        self.ligament_cylinders = []
        self.palm_meshes = []
        self.vis.clear_geometries()

    def close(self):
        """Close the Open3D visualization window."""
        try:
            self.vis.destroy_window()
            self.window_created = False
        except Exception as e:
            raise e

    def play_sequence(self, hand_pose_sequence, fps=30, loop=False):
        """
        Play a timed sequence of hand poses as animation.

        Parameters
        ----------
        hand_pose_sequence : list
            HandPoseSequence to play.
        fps : int, optional
            Frames per second playback rate.
        loop : bool, optional
            Whether to loop playback indefinitely. Defaults to false.
        """

        self.initialize_window()
        frame_duration = 1.0 / fps
        index = 0

        print(f"[Visualizer] Playing sequence at {fps} FPS...")

        # === Build geometry from the first pose ===
        if len(hand_pose_sequence) == 0:
            print("[!] Empty sequence.")
            return

        first_pose = hand_pose_sequence[0].pose
        self.build_cached_geometry([first_pose])

        try:
            while True:
                if index >= len(hand_pose_sequence):
                    if loop:
                        index = 0
                    else:
                        break

                timed_pose = hand_pose_sequence[index]
                pose = timed_pose.pose

                self.update_cached_geometry([pose])

                time.sleep(frame_duration)
                index += 1
        except KeyboardInterrupt:
            print("[Visualizer] Playback interrupted.")

    def build_cached_geometry(self, hand_poses):
        """
        Build and cache Open3D geometry for a list of hand poses.

        Parameters
        ----------
        hand_poses : list
            List of HandPose instances.
        """
        if not isinstance(hand_poses, list):
            raise TypeError(f"[Visualizer] Expected list of HandPose, got {type(hand_poses)}")

        self.hand_poses = hand_poses
        self.landmark_spheres.clear()
        self.ligament_cylinders.clear()
        self.palm_meshes.clear()


        for pose in hand_poses:
            coords = pose.get_all_coordinates()
            landmark_points = np.array([[pt.x, pt.y, pt.z] for pt in coords])

            scale = self._compute_pose_scale(pose)
            scale_factor = scale * 0.05  # Tunable coefficient

            # === Landmarks ===
            hand_spheres = []
            for pt in landmark_points:
                radius = scale_factor * 1.0  # Was: 1.0

                sphere = self.__create_sphere(pt, radius=radius)
                self.vis.add_geometry(sphere)
                hand_spheres.append(sphere)
            self.landmark_spheres.append(hand_spheres)

            # === Ligaments ===
            hand_cyls = []
            for finger_name, indices in self.FINGERS.items():
                for i in range(len(indices) - 1):
                    p1 = landmark_points[indices[i]]
                    p2 = landmark_points[indices[i + 1]]
                    color = self.colors["proximals"] if i == 0 else \
                        self.colors["intermediates"] if i == 1 else \
                            self.colors["distals"]
                    radius = scale_factor * 0.8  # Was: 0.8
                    cyl = self.__create_cylinder_between(p1, p2, radius=radius, color=color)
                    if cyl:
                        self.vis.add_geometry(cyl)
                        hand_cyls.append(cyl)
            self.ligament_cylinders.append(hand_cyls)

            # === Palm ===
            palm_indices = [0, 1, 5, 9, 13, 17]
            palm_points = landmark_points[palm_indices]
            hull = ConvexHull(palm_points[:, :2], qhull_options='QJ')
            triangles = [[hull.vertices[0], hull.vertices[i], hull.vertices[i + 1]]
                         for i in range(1, len(hull.vertices) - 1)]

            mesh = o3d.geometry.TriangleMesh()
            mesh.vertices = o3d.utility.Vector3dVector(palm_points)
            mesh.triangles = o3d.utility.Vector3iVector(triangles)
            mesh.paint_uniform_color(self.colors["palm"])
            mesh.compute_vertex_normals()
            self.vis.add_geometry(mesh)
            self.palm_meshes.append(mesh)

        self.cache_initialized = True

    def update_cached_geometry(self, hand_poses):
        """
        Update cached geometry meshes with new hand pose coordinates.

        Parameters
        ----------
        hand_poses : list
            List of HandPose instances.
        """
        if len(hand_poses) != len(self.landmark_spheres):
            self._reset_geometry()
            # self.build_cached_geometry(hand_poses)
            # return

        for h_index, pose in enumerate(hand_poses):
            coords = pose.get_all_coordinates()
            landmark_points = np.array([[pt.x, pt.y, pt.z] for pt in coords])

            # === Update Landmarks ===
            for i, pt in enumerate(landmark_points):
                mesh = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=5)
                mesh.translate(pt)
                self.landmark_spheres[h_index][i].vertices = mesh.vertices
                self.landmark_spheres[h_index][i].compute_vertex_normals()
                self.vis.update_geometry(self.landmark_spheres[h_index][i])

            # === Update Ligaments ===
            lig_index = 0
            for finger_name, indices in self.FINGERS.items():
                for i in range(len(indices) - 1):
                    p1 = landmark_points[indices[i]]
                    p2 = landmark_points[indices[i + 1]]
                    new_cyl = self.__create_cylinder_between(p1, p2, radius=0.8, resolution=5)
                    cyl = self.ligament_cylinders[h_index][lig_index]
                    cyl.vertices = new_cyl.vertices
                    cyl.triangles = new_cyl.triangles
                    cyl.compute_vertex_normals()
                    self.vis.update_geometry(cyl)
                    lig_index += 1

            # === Update Palm ===
            palm_points = landmark_points[[0, 1, 5, 9, 13, 17]]
            palm = self.palm_meshes[h_index]
            palm.vertices = o3d.utility.Vector3dVector(palm_points)
            palm.compute_vertex_normals()
            self.vis.update_geometry(palm)

        self.vis.poll_events()
        self.vis.update_renderer()

    def _compute_pose_scale(self, hand_pose):
        """
        Helper to compute scale factor for a hand pose based on bounding box size.
        This is necessary to normalize sphere/cylinder sizes when displaying non-normalized HandPoses.
        TODO: This function is still being fixed and handposes may not always be rescaled, it'll be added to the issue tracker.

        Parameters
        ----------
        hand_pose : HandPose
            Single hand pose.

        Returns
        -------
        float
            Maximum span of pose coordinates across x, y, z axes.
        """
        coords = hand_pose.get_all_coordinates()
        min_x = min(c.x for c in coords)
        max_x = max(c.x for c in coords)
        min_y = min(c.y for c in coords)
        max_y = max(c.y for c in coords)
        min_z = min(c.z for c in coords)
        max_z = max(c.z for c in coords)

        range_x = max_x - min_x
        range_y = max_y - min_y
        range_z = max_z - min_z

        return max(range_x, range_y, range_z)  # largest dimension span

    def visualize_pose_similarity(self, pose1, pose2, method='euclidean', offset=False):
        """
        Visualize similarity between two hand poses via color-coded landmarks.

        Parameters
        ----------
        pose1 : HandPose
            Reference pose.
        pose2 : HandPose
            Pose to compare.
        method : str, optional
            Similarity method, currently supports 'euclidean', 'cosine', and 'joint_angle'.
        offset : bool, optional
            Offset second pose along x-axis for side-by-side comparison.
        """
        if not pose1 or not pose2:
            raise ValueError("Both poses must be provided.")

        coords1 = np.array([c.as_tuple() for c in pose1.get_all_coordinates()])
        coords2 = np.array([c.as_tuple() for c in pose2.get_all_coordinates()])

        if offset:
            coords2 = coords2 + np.array([0.15, 0.0, 0.0])

        if method == "euclidean":
            errors = np.linalg.norm(coords1 - coords2, axis=1)

        elif method == "cosine":
            dot_products = np.sum(coords1 * coords2, axis=1)
            norms1 = np.linalg.norm(coords1, axis=1)
            norms2 = np.linalg.norm(coords2, axis=1)
            cosine_sim = dot_products / (norms1 * norms2 + 1e-6)
            errors = 1 - cosine_sim  # Error = 1 - similarity

        elif method == "joint_angle":
            from handposeutils.calculations import compute_joint_angle_errors
            joint_errors = compute_joint_angle_errors(pose1, pose2)

            # Map each angle error to its middle joint in the 3-point triplet
            # Then build a 21-element array with zeros, and inject errors at the joint indices
            errors = np.zeros(21)
            angle_joint_indices = [2, 3, 6, 7, 10, 11, 14, 15, 18, 19]  # middle point in each angle triplet
            for idx, joint_idx in enumerate(angle_joint_indices):
                errors[joint_idx] = joint_errors[idx]

        else:
            raise NotImplementedError(f"Method '{method}' is not supported.")

        # === Visualize ===
        max_error = np.max(errors) + 1e-6
        self.initialize_window()
        self.vis.clear_geometries()

        # Pose2 (colored by similarity)
        for i in range(len(coords2)):
            color = self.error_to_color(errors[i], max_error)
            self.vis.add_geometry(self.__create_sphere(coords2[i], radius=0.1, color=color))

        # Pose1 (reference)
        for pt in coords1:
            self.vis.add_geometry(self.__create_sphere(pt, radius=0.1, color=(0.2, 0.8, 1.0)))

        print("[HandPoseVisualizer] Comparing poses: red = most different, blue = similar, yellow = identical")
        print("[HandPoseVisualizer] Use mouse to interact. Press 'q' to quit.")
        print(f"[HandPoseVisualizer] Similarity visualized using method: {method}")
        self.vis.run()
        self.vis.destroy_window()

    def error_to_color(self, error, max_error):
        """
        Convert an error value to an RGB color between blue (low) and red (high).

        Parameters
        ----------
        error : float
            Error magnitude.
        max_error : float
            Maximum error value for normalization.

        Returns
        -------
        tuple
            RGB color tuple.
        """
        ratio = np.clip(error / max_error, 0.0, 1.0)
        return (ratio, 0.0, 1.0 - ratio)


class DeprecatedHandPoseVisualizer:
    def __init__(self, window_name="Hand Pose Visualizer", color_profile: dict = None):
        self.window_name = window_name
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name=self.window_name)
        self.geometry_added = False

        self.landmark_points = []
        self.geometry = []

        # Landmark connections for each finger
        self.FINGERS = {
            "thumb": [1, 2, 3, 4],
            "index": [5, 6, 7, 8],
            "middle": [9, 10, 11, 12],
            "ring": [13, 14, 15, 16],
            "pinky": [17, 18, 19, 20]
        }

        self.COLORS_DEFAULT = {
            "landmarks": [0.1, 0.6, 0.9],
            "proximals": [0.5,0,1],
            "intermediates": [0,1,0.5],
            "distals": [0,0.5,1],
            "palm": [1,1,0],
        }
        self.colors = None
        if color_profile is None:
            self.set_colors(self.COLORS_DEFAULT)
        else:
            self.set_colors(color_profile)

    def __create_sphere(self, center, radius=5.0, color=None):
        if color is None:
            color = self.colors.get("landmarks")
        else:
            color = color
        """
        :param center: center of sphere
        :param radius: radius of sphere
        :param color: color of sphere (rgb scaled to [[0.0-1.0],_,_])
        :return: o3d sphere object
        """
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius)
        sphere.translate(center)
        sphere.paint_uniform_color(color)
        return sphere


    def __create_cylinder_between(self, p1, p2, radius=0.8, resolution=5, color=[1, 0, 0]):
        """
        :param p1: point 1 (start point of cylinder)
        :param p2: point 2 (end point of cylinder)
        :param radius: radius of cylinder
        :param resolution: resolution of cylinder
        :param color: color of cylinder (rgb scaled [[0.0-1.0],_,_])
        :return: o3d cylinder object
        """
        p1 = np.array(p1, dtype=np.float64)
        p2 = np.array(p2, dtype=np.float64)
        axis = p2 - p1
        length = np.linalg.norm(axis)
        if length == 0:
            return None
        axis /= length

        # Step 1: Create the default cylinder along z-axis centered at origin
        cylinder = o3d.geometry.TriangleMesh.create_cylinder(radius=radius, height=length, resolution=resolution)
        cylinder.paint_uniform_color(color)

        # Step 2: Align Z-axis with the target axis (rotate cylinder)
        z_axis = np.array([0, 0, 1])
        v = np.cross(z_axis, axis)
        c = np.dot(z_axis, axis)
        if np.linalg.norm(v) < 1e-6:
            R = np.eye(3) if c > 0 else -np.eye(3)  # 180° flip if facing backward
        else:
            skew = np.array([[0, -v[2], v[1]],
                            [v[2], 0, -v[0]],
                            [-v[1], v[0], 0]])
            R = np.eye(3) + skew + skew @ skew * ((1 - c) / (np.linalg.norm(v) ** 2))

        cylinder.rotate(R, center=(0, 0, 0))

        # Step 3: Translate to the midpoint between p1 and p2
        midpoint = (p1 + p2) / 2
        cylinder.translate(midpoint)

        return cylinder

    def add_geometry(self, geometry):
        """
        :param geometry: single open3d shape to add to visulizer window
        """
        self.geometry.append(geometry)

    def return_geometry(self):
        """
        :return: visualizer geometry
        """
        return self.geometry

    def set_landmark_points(self, points_array):
        """
        :param points_array: array containing landmark points to update the screen with
        """
        self.landmark_points = points_array

    def return_landmark_points(self):
        return np.array(self.landmark_points)

    def get_landmark_point(self, index):
        """
        :param index: index of the landmark point to get
        NOTE: will probably not work as expected if more than one hand is stored in the landmark_points list
        :return: landmark point at index
        """
        try:
            return self.landmark_points[index]
        except Exception as e:
            raise e

    def update_visualizer(self):
        # Typically always called after show_pose()
        # Add all geometries to the visualizer window
        self.vis.clear_geometries()
        self.vis.update_renderer()

        for geo in self.geometry:
            self.vis.add_geometry(geo)

        self.vis.poll_events()
        self.vis.update_renderer()


    def show_pose(self, finger_tips_shown = True, ligaments_shown = True, palm_shown = True):
        """
        Shows the pose in the visualizer window
        :param finger_tips_shown: boolean to show/hide finger tips
        :param ligaments_shown: boolean to show/hide ligaments
        :param palm_shown: boolean to show/hide palm
        :return: None
        """

        # Clear previous frame geometries
        self.vis.clear_geometries()
        self.geometry = []

        # Update the geometries list
        if finger_tips_shown:
            for joint in self.landmark_points:
                s = self.__create_sphere(np.array(joint), 1.0)
                self.add_geometry(s)

        if ligaments_shown:
            # Check if we have multiple hands (more than 21 landmarks)
            num_hands = len(self.landmark_points) // 21

            # NOTE: this probably isn't the best implementation of this, but it works for now lol
            temp_finger_colors_array = []
            temp_finger_colors_array.extend([self.colors.get("proximals")])
            temp_finger_colors_array.extend([self.colors.get("intermediates")])
            temp_finger_colors_array.extend([self.colors.get("distals")])

            for hand_idx in range(num_hands):
                # Calculate offset for this hand
                offset = hand_idx * 21

                # Create adjusted finger indices for this hand
                adjusted_fingers = {}
                for finger_name, indices in self.FINGERS.items():
                    adjusted_fingers[finger_name] = [idx + offset for idx in indices]

                # Draw ligaments for this hand
                for finger_indices in adjusted_fingers.values():
                    for i in range(len(finger_indices) - 1):
                        p1 = self.landmark_points[finger_indices[i]]
                        p2 = self.landmark_points[finger_indices[i+1]]
                        c = self.__create_cylinder_between(p1, p2, radius=0.8, color=temp_finger_colors_array[i])
                        if c: self.add_geometry(c)

        if palm_shown:
            # Handle multiple hands for palm visualization
            num_hands = len(self.landmark_points) // 21

            for hand_idx in range(num_hands):
                # Calculate offset for this hand
                offset = hand_idx * 21

                # Indices of points forming the palm boundary (adjusted for this hand)
                palm_indices = [0, 1, 5, 9, 13, 17]
                adjusted_palm_indices = [idx + offset for idx in palm_indices]

                # Extract palm points
                palm_points = np.array([self.landmark_points[i] for i in adjusted_palm_indices])
                palm_2d = palm_points[:, :2]

                # Create convex hull in 2D to find palm outline
                hull = ConvexHull(palm_2d, qhull_options='QJ')
                hull_indices = hull.vertices
                hull_triangles = []

                # Triangulate using fan method (good for convex shapes)
                for i in range(1, len(hull_indices) - 1):
                    hull_triangles.append([hull_indices[0], hull_indices[i], hull_indices[i + 1]])
                # Front face (blue side)
                plane_front = o3d.geometry.TriangleMesh()
                plane_front.vertices = o3d.utility.Vector3dVector(palm_points)
                plane_front.triangles = o3d.utility.Vector3iVector(hull_triangles)
                plane_front.paint_uniform_color([0, 0, 1])
                plane_front.compute_vertex_normals()

                self.add_geometry(plane_front)

        self.update_visualizer()

    def read_multi_landmarks(self, multi_hand_landmarks):
        """
        :param multi_hand_landmarks: landmarks from Mediapipe input
        :return: None
        """
        self.landmark_points = []

        for _, hand in enumerate(multi_hand_landmarks):
            self.read_hand_landmarks(hand)



    def read_hand_landmarks(self, hand, POSE_CENTER = np.array([0,0,0])):
        """
        :param landmarks: landmarks from Mediapipe input
        :param POSE_CENTER: center of hand - EITHER np.array([x,y,z]) OR list index from landmarks of desired center [0-20]
        :return: None
        """
        # Add points to list
        try:
            if type(POSE_CENTER) == np.ndarray:
                POSE_CENTER = POSE_CENTER # center at pose
            elif type(POSE_CENTER) == int:
                POSE_CENTER = np.array([hand.landmark[POSE_CENTER].x * 100, (1-hand.landmark[POSE_CENTER].y) * 100, (1-hand.landmark[POSE_CENTER].z) * 100])
                # Hand is centered at landmark --> landmark[int]
            else:
                POSE_CENTER = np.array([0,0,0]) # Hand is not centered

            for _, landmark in enumerate(hand.landmark):
                # Center points @ POSE_CENTER
                point = np.array([round(landmark.x * 100, 3), round((1 - landmark.y) * 100, 3),
                                            round((1 - landmark.z) * 100, 3)]) - POSE_CENTER
                self.landmark_points.append(point)

        except Exception as e:
            raise e

    def set_colors(self, colors: dict):
        '''
        :param colors: dictionary of colors for each part of the hand
        default: {"landmarks": [0.1, 0.6, 0.9], "thumb": [0.5,0,1], "index": [0,0.5,1], "middle": [0,1,0.5], "ring": [1,1,0], "pinky": [1,0,0], "palm": [0,1,1]}
        :return: None
        '''
        self.colors = colors


    def close(self):
        try:
            self.vis.destroy_window()
        except Exception as e:
            raise e