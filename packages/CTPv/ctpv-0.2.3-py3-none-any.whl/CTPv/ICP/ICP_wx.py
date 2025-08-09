import wx
import numpy as np
from vispy import app

app.use_app('wx')
from vispy import scene
from vispy.scene import cameras
from vispy.geometry import create_sphere
import os
import logging


# --- GUI Classes ---

class VispyCanvas(wx.Panel):
    """A wx.Panel that contains a Vispy SceneCanvas."""

    def __init__(self, parent, size=wx.DefaultSize):
        super(VispyCanvas, self).__init__(parent, size=size)
        # Initialize with show=False. The parent frame will manage showing it.
        self.canvas = scene.SceneCanvas(keys='interactive', parent=self, show=False)
        self.canvas.events.mouse_press.connect(self.on_mouse_press)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas.native, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Point selection attributes
        self.parent_frame = None
        self.canvas_type = None
        self.points = None
        self.view = None
        self.markers_visual = None

    def on_mouse_press(self, event):
        """Handle mouse clicks for point selection."""
        if 'Control' in event.modifiers and self.parent_frame and self.view:
            point_3d = self.get_3d_point_from_click(event.pos)
            if point_3d is not None:
                self.parent_frame.add_selected_point(self.canvas_type, point_3d)
                event.handled = True

    def get_3d_point_from_click(self, screen_pos):
        """
        Convert 2D screen coordinates to a 3D point by finding the nearest point
        in the point cloud, using the visual's transformation.
        """
        if self.points is None or len(self.points) == 0 or self.markers_visual is None:
            return None

        try:
            transform = self.markers_visual.get_transform('visual', 'canvas')
            screen_coords_4d = transform.map(self.points)
            screen_coords = screen_coords_4d[:, :2] / screen_coords_4d[:, 3:4]
            distances = np.sqrt(np.sum((screen_coords - screen_pos) ** 2, axis=1))
            closest_idx = np.argmin(distances)
            if distances[closest_idx] < 20: # Click sensitivity radius
                return self.points[closest_idx]
        except Exception as e:
            logging.warning(f"Error in point selection: {e}")
        return None


class MainFrame(wx.Frame):
    """
    The main application window. It is initialized with the point clouds
    and is responsible only for displaying them.
    """

    def __init__(self, target_points, source_points, num_points_to_select=4):
        super(MainFrame, self).__init__(None, title="Point Cloud Viewer", size=(1200, 650))
        self.target_points = target_points
        self.source_points = source_points
        self.target_color = (0.8, 0.2, 0.2)
        self.source_color = (0.2, 0.2, 0.8)
        self.num_points_to_select = num_points_to_select
        self.selected_target_points = []
        self.selected_source_points = []
        self.target_selection_visuals = []
        self.source_selection_visuals = []

        # Initialize attributes that will be set up after the window is shown
        self.target_markers = None
        self.source_markers = None
        self.target_controls_text = None
        self.source_controls_text = None
        self._scenes_initialized = False # Flag to ensure setup runs only once

        self.selection_color_map = [
            'yellow', 'cyan', 'magenta', 'green',
            'orange', 'white', 'blue', 'red',
        ]

        if self.target_points is not None and len(self.target_points) > 0:
            p_min = self.target_points.min(axis=0)
            p_max = self.target_points.max(axis=0)
            self.selection_radius = np.linalg.norm(p_max - p_min) * 0.01
        else:
            self.selection_radius = 0.5

        self.create_menu_bar()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        canvas_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.target_canvas = VispyCanvas(self)
        self.source_canvas = VispyCanvas(self)
        self.target_canvas.parent_frame = self
        self.target_canvas.canvas_type = 'target'
        self.target_canvas.points = target_points
        self.source_canvas.parent_frame = self
        self.source_canvas.canvas_type = 'source'
        self.source_canvas.points = source_points
        canvas_sizer.Add(self.target_canvas, 1, wx.EXPAND | wx.ALL, 5)
        canvas_sizer.Add(self.source_canvas, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(canvas_sizer, 1, wx.EXPAND)

        self.target_canvas.canvas.bgcolor = 'pink'
        self.source_canvas.canvas.bgcolor = 'pink'

        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        slider_label = wx.StaticText(self, label="Point Size:")
        self.point_size_slider = wx.Slider(self, value=3, minValue=1, maxValue=20, style=wx.SL_HORIZONTAL)
        self.point_size_slider.Bind(wx.EVT_SLIDER, self.on_slider_change)
        self.clear_button = wx.Button(self, label="Clear Selections")
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_selections)
        self.status_text = wx.StaticText(self, label="")
        control_sizer.Add(slider_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        control_sizer.Add(self.point_size_slider, 1, wx.EXPAND | wx.RIGHT, 5)
        control_sizer.Add(self.clear_button, 0, wx.ALL, 5)
        control_sizer.Add(self.status_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        main_sizer.Add(control_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)

        # Bind events
        self.Bind(wx.EVT_SHOW, self.on_show_frame)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.update_status()
        self.Centre()
        self.Show()

    def on_show_frame(self, event):
        """Event handler for when the frame is shown for the first time."""
        if not self._scenes_initialized and event.IsShown():
            # Defer the Vispy setup until the wx event loop is idle.
            # This ensures the window is fully created and shown before Vispy tries to draw.
            wx.CallAfter(self.setup_vispy_scenes)
            self._scenes_initialized = True
        event.Skip()

    def setup_vispy_scenes(self):
        """Initializes the Vispy scenes after the main window is shown."""
        logging.info("Setting up Vispy scenes...")
        self.target_markers, self.target_controls_text, self.target_canvas.view = self.display_point_cloud(
            self.target_canvas, self.target_points, 'Target', self.target_color
        )
        self.target_canvas.markers_visual = self.target_markers

        self.source_markers, self.source_controls_text, self.source_canvas.view = self.display_point_cloud(
            self.source_canvas, self.source_points, 'Source', self.source_color
        )
        self.source_canvas.markers_visual = self.source_markers

        # Now that the scenes are set up, connect resize events
        self.target_canvas.canvas.events.resize.connect(self.on_target_resize)
        self.source_canvas.canvas.events.resize.connect(self.on_source_resize)

        # Explicitly show the canvases now that they are populated
        self.target_canvas.canvas.show()
        self.source_canvas.canvas.show()
        logging.info("Vispy scenes are live.")

    def create_menu_bar(self):
        menubar = wx.MenuBar()
        view_menu = wx.Menu()
        bg_submenu = wx.Menu()
        bg_colors = [
            ('Black', 'black', (0, 0, 0, 1)), ('White', 'white', (1, 1, 1, 1)),
            ('Dark Gray', 'dark_gray', (0.2, 0.2, 0.2, 1)), ('Light Gray', 'light_gray', (0.8, 0.8, 0.8, 1)),
            ('Dark Blue', 'dark_blue', (0.1, 0.1, 0.3, 1)), ('light_pink', 'light_pink', (1.0, 0.71, 0.76, 1.0)),
            ('Custom...', 'custom', None)
        ]
        for name, key, color in bg_colors:
            item = bg_submenu.Append(wx.ID_ANY, name)
            self.Bind(wx.EVT_MENU, lambda evt, c=color: self.on_background_color_change(evt, c), item)
        view_menu.AppendSubMenu(bg_submenu, '&Background Color')
        selection_menu = wx.Menu()
        num_points_item = selection_menu.Append(wx.ID_ANY, '&Set Number of Points...')
        self.Bind(wx.EVT_MENU, self.on_set_num_points, num_points_item)
        menubar.Append(view_menu, '&View')
        menubar.Append(selection_menu, '&Selection')
        self.SetMenuBar(menubar)

    def on_set_num_points(self, event):
        dlg = wx.NumberEntryDialog(self, 'Enter number of points to select from each cloud:',
                                   'Number of Points', 'Point Selection',
                                   self.num_points_to_select, 1, 20)
        if dlg.ShowModal() == wx.ID_OK:
            self.num_points_to_select = dlg.GetValue()
            self.update_status()
            self.on_clear_selections(None)
        dlg.Destroy()

    def on_clear_selections(self, event):
        self.selected_target_points = []
        self.selected_source_points = []
        for visual in self.target_selection_visuals:
            visual.parent = None
        for visual in self.source_selection_visuals:
            visual.parent = None
        self.target_selection_visuals = []
        self.source_selection_visuals = []
        self.target_canvas.canvas.update()
        self.source_canvas.canvas.update()
        self.update_status()

    def add_selected_point(self, canvas_type, point_3d):
        if canvas_type == 'target':
            if len(self.selected_target_points) < self.num_points_to_select:
                self.selected_target_points.append(point_3d)
                point_num = len(self.selected_target_points)
                self.create_selection_visual(self.target_canvas.canvas, point_3d, point_num, 'target')
        else:
            if len(self.selected_source_points) < self.num_points_to_select:
                self.selected_source_points.append(point_3d)
                point_num = len(self.selected_source_points)
                self.create_selection_visual(self.source_canvas.canvas, point_3d, point_num, 'source')
        self.update_status()

    # ✅ UPDATED: This method now color-codes the spheres and creates no text.
    def create_selection_visual(self, canvas, point_3d, point_num, canvas_type):
        """Create visual indicators for selected points."""
        view = self.target_canvas.view if canvas_type == 'target' else self.source_canvas.view
        sphere_radius = self.selection_radius

        # 1. Get the color for this point number from our map
        num_colors = len(self.selection_color_map)
        color_index = (point_num - 1) % num_colors
        point_color = self.selection_color_map[color_index]

        # 2. Create the sphere marker with the selected color
        sphere_visual = scene.visuals.Mesh(
            meshdata=create_sphere(radius=sphere_radius, method='ico'),
            color=point_color,
            parent=view.scene
        )
        sphere_visual.transform = scene.transforms.STTransform(translate=point_3d)

        # 3. Store only the sphere visual
        if canvas_type == 'target':
            self.target_selection_visuals.append(sphere_visual)
        else:
            self.source_selection_visuals.append(sphere_visual)

        canvas.update()

    def update_status(self):
        target_count = len(self.selected_target_points)
        source_count = len(self.selected_source_points)
        status = (f"Target: {target_count}/{self.num_points_to_select}, "
                  f"Source: {source_count}/{self.num_points_to_select} - "
                  f"Hold [Ctrl] and left-click to select points.")
        self.status_text.SetLabel(status)

    def on_background_color_change(self, event, color):
        if color is None:
            data = wx.ColourData()
            dlg = wx.ColourDialog(self, data)
            if dlg.ShowModal() == wx.ID_OK:
                chosen_color = dlg.GetColourData().GetColour()
                color = (chosen_color.Red() / 255.0, chosen_color.Green() / 255.0, chosen_color.Blue() / 255.0, 1.0)
            else:
                dlg.Destroy()
                return
            dlg.Destroy()
        self.target_canvas.canvas.bgcolor = color
        self.source_canvas.canvas.bgcolor = color
        self.target_canvas.canvas.update()
        self.source_canvas.canvas.update()

    def on_slider_change(self, event):
        new_size = self.point_size_slider.GetValue()
        if self.target_markers:
            self.target_markers.set_data(pos=self.target_points, size=new_size, face_color=self.target_color)
        if self.source_markers:
            self.source_markers.set_data(pos=self.source_points, size=new_size, face_color=self.source_color)

    def on_target_resize(self, event):
        self.target_controls_text.pos = (event.size[0] - 15, 15)

    def on_source_resize(self, event):
        self.source_controls_text.pos = (event.size[0] - 15, 15)

    def display_point_cloud(self, vispy_canvas_panel, points, title_text, color):
        canvas = vispy_canvas_panel.canvas
        view = canvas.central_widget.add_view()

        # --- ✅ Calculate center of mass and set camera center ---
        if points is not None and len(points) > 0:
            center_of_mass = np.median(points, axis=0)
            print(f"Center of Mass: {center_of_mass}")
        else:
            center_of_mass = (0, 0, 0)  # Default if no points


        view.camera = cameras.ArcballCamera(
            fov=60,
            up='x',
            center=center_of_mass)

        markers = scene.visuals.Markers(
            pos=points, face_color=color, edge_color=None,
            size=self.point_size_slider.GetValue(), parent=view.scene
        )
        scene.visuals.XYZAxis(parent=view.scene)
        #view.camera.set_range()
        view.camera.scale_factor = 0.550
        view.camera.distance = 300
        scene.visuals.Text(title_text, pos=(30, 30), color='white', font_size=10, bold=True, parent=canvas.scene)
        controls_text_content = (
            "Controls:\nLMB: Orbit\nCtrl+ LMB: Select Point\nRMB / Scroll: Zoom\n"
            "Shift + LMB: Pan\nShift + RMB: FOV"
        )
        controls_text = scene.visuals.Text(
            controls_text_content, color=(0.7, 0.5, 0.5, 1.0), font_size=8,
            anchor_x='right', anchor_y='bottom', parent=canvas.scene
        )
        return markers, controls_text, view

    def on_close(self, event):
        print("\n" + "=" * 50 + "\nSELECTED POINTS SUMMARY\n" + "=" * 50)
        print(f"\nTarget Points ({len(self.selected_target_points)}/{self.num_points_to_select}):")
        for i, point in enumerate(self.selected_target_points, 1):
            print(f"  Point {i}: [{point[0]:.4f}, {point[1]:.4f}, {point[2]:.4f}]")
        print(f"\nSource Points ({len(self.selected_source_points)}/{self.num_points_to_select}):")
        for i, point in enumerate(self.selected_source_points, 1):
            print(f"  Point {i}: [{point[0]:.4f}, {point[1]:.4f}, {point[2]:.4f}]")
        target_array = np.array(self.selected_target_points) if self.selected_target_points else np.empty((0, 3))
        source_array = np.array(self.selected_source_points) if self.selected_source_points else np.empty((0, 3))
        print(
            f"\nTarget points array shape: {target_array.shape}\nSource points array shape: {source_array.shape}\n" + "=" * 50)
        self.result_target_points = target_array
        self.result_source_points = source_array
        self.Destroy()


def create_sample_ply_file(file_path="sample_cloud.ply"):
    num_points_per_face = 200
    all_points = []
    faces = [
        ([0, 0, 0], [1, 0, 0], [0, 1, 0]), ([0, 0, 1], [1, 0, 0], [0, 1, 0]),
        ([0, 0, 0], [1, 0, 0], [0, 0, 1]), ([0, 1, 0], [1, 0, 0], [0, 0, 1]),
        ([0, 0, 0], [0, 1, 0], [0, 0, 1]), ([1, 0, 0], [0, 1, 0], [0, 0, 1]),
    ]
    for origin, v1, v2 in faces:
        samples = np.random.rand(num_points_per_face, 2)
        face_points = np.array(origin) + samples[:, 0:1] * np.array(v1) + samples[:, 1:2] * np.array(v2)
        all_points.append(face_points)
    cloud = np.vstack(all_points) * 10
    with open(file_path, 'w') as f:
        f.write("ply\nformat ascii 1.0\n")
        f.write(f"element vertex {len(cloud)}\n")
        f.write("property float x\nproperty float y\nproperty float z\n")
        f.write("end_header\n")
        np.savetxt(f, cloud, fmt="%.4f")
    logging.info(f"Generated sample file '{file_path}' with {len(cloud)} points.")
    return file_path

# --- Utility Functions ---

def load_ply_points(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    header_end = 0
    for i, line in enumerate(lines):
        if line.strip() == 'end_header':
            header_end = i + 1
            break
    points = np.loadtxt(lines[header_end:])
    return points[:, :3]

def plot_open3d(target_points, source_points2):
    """
    Visualizes two point clouds using Open3D and allows toggling the visibility
    of the source point cloud by pressing the 'T' key.
    """
    import open3d as o3d
    try:
        print("Open3D visualization starting. Press 'T' to toggle the blue cloud. Press 'Q' to close.")

        # --- 1. Create the geometry objects ---
        pcd_target = o3d.geometry.PointCloud()
        pcd_target.points = o3d.utility.Vector3dVector(target_points)
        pcd_target.paint_uniform_color([1, 0, 0])  # Red for target

        pcd_source = o3d.geometry.PointCloud()
        pcd_source.points = o3d.utility.Vector3dVector(source_points2)
        pcd_source.paint_uniform_color([0, 0, 1])  # Blue for transformed source

        # --- 2. Setup the visualizer and state ---
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.create_window()

        # Add the target geometry, which will always be visible
        vis.add_geometry(pcd_target)

        # Variable to track the visibility of the source point cloud
        is_source_visible = True
        vis.add_geometry(pcd_source)

        # --- 3. Define the key callback function ---
        def toggle_source_cloud(visualizer):
            nonlocal is_source_visible
            if is_source_visible:
                visualizer.remove_geometry(pcd_source, reset_bounding_box=False)
            else:
                visualizer.add_geometry(pcd_source, reset_bounding_box=False)
            is_source_visible = not is_source_visible
            # Return False to redraw the scene
            return False

        # --- 4. Register the callback ---
        # The key code for 'T' is 84. For other keys, you can find their ASCII values.
        vis.register_key_callback(84, toggle_source_cloud) # 84 is ASCII for 'T'

        # --- 5. Run the visualizer ---
        vis.run()
        vis.destroy_window()
        print("Open3D visualization complete.")

    except ImportError:
        print("Open3D is not installed. Skipping visualization.")
    except Exception as e:
        print(f"An error occurred during Open3D visualization: {e}")