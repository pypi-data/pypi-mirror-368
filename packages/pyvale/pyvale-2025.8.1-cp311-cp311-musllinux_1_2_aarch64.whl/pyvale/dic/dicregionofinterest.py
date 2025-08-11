# ================================================================================
# pyvale: the python validation engine
# License: MIT
# Copyright (C) 2025 The Computer Aided Validation Team
# ================================================================================

from pyqtgraph.Qt import QtWidgets, QtCore
import pyqtgraph as pg
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as mplPath
import math
import yaml
import os
from pathlib import Path

class RegionOfInterest:
    """
    A class for interactively selecting and manipulating ROI of an image before passing to the DIC engine. 

    Users can:
    - Interactively select rectangular, circular, or polygonal regions on the image.
    - Add or subtract selected regions from the mask.
    - Undo and reset the mask changes.
    - read in previously created ROIs 
    - save created ROI as text or binary file.
    - Display/save the ROI overlayed over the reference.
    - Programatically select a rectangular ROI for consistency.
    
    Public attributes:
        image (np.ndarray): The image on which regions of interest are selected.
        mask (np.ndarray): A binary mask representing the selected regions of interest.
    """
    
    def __init__(self, ref_image: str | np.ndarray | Path):
        """
        Parameters
        ----------
        ref_image : str, numpy.ndarray, pathlib.Path
            location of the reference image.
        
        Raises
        ------
            ValueError: If the image cannot be loaded or is invalid.
        """
        if isinstance(ref_image, str):
            self.ref_image = cv2.imread(ref_image)
        elif isinstance(ref_image, Path):
            self.ref_image = cv2.imread(str(ref_image))
        else:
            self.ref_image = ref_image.copy()

        if self.ref_image is None:
            raise ValueError("Invalid image input")

        self.mask = np.zeros(self.ref_image.shape[:2], dtype=bool)
        self.seed = []
        self.__roi_selected = False
        self.roi_list = []
        self.add_list = []
        self.undo_list = []
        
        # Drawing states
        self.drawing_modes = {
            'seed': False,
            'rect': False,
            'circle': False,
            'poly': False
        }
        self.removing_modes = {
            'rect': False,
            'circle': False,
            'poly': False
        }
        
        # GUI elements (initialized in interactive_selection)
        self.main_view = None
        self.fill_layer = None
        self.buttons = {}
        self.poly_points = []
        self.temp_mask = None
        self.fill_array = None
        self.height = None
        self.width = None
        self.subset_size = None
        self.coord_label = None

    def interactive_selection(self, subset_size):
        """
        Interactive GUI to select a region of interest (ROI) in the image using openCV.
        """
        self.subset_size = subset_size
        self.__roi_selected = True
        
        # Initialize GUI
        self._setup_gui()
        self._setup_graphics()
        self._connect_signals()
        
        # Show and run
        self.main_window.show()
        pg.exec()
        
        # Process final mask and seed
        self._finalize_selection()

    def _setup_gui(self):
        """Setup the main GUI window and sidebar."""
        app = pg.mkQApp("ROI GUI")
        self.main_window = CustomMainWindow(dic_obj=self)
        main_layout = QtWidgets.QHBoxLayout()
        self.main_window.setLayout(main_layout)
        self.main_window.resize(1000, 1000)

        # Create sidebar
        sidebar = self._create_sidebar()
        
        # Create graphics widget
        self.graphics_widget = pg.GraphicsLayoutWidget()


        
        main_layout.addLayout(sidebar)
        main_layout.addWidget(self.graphics_widget)

    def _create_sidebar(self):
        """Create the sidebar with all buttons."""
        sidebar = QtWidgets.QVBoxLayout()
        
        # Helper function for styled titles
        def make_title(text):
            label = QtWidgets.QLabel(text)
            label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
            return label

        # Create all buttons
        button_configs = [
            ("FILE ACTIONS", [("open_roi", "Open ROI..."),
                              ("save_roi", "Save Current ROI...")]),

            ("ADD SHAPES TO ROI", [("add_rect", "Add Rectangle"),
                                   ("add_circle", "Add Circle"),
                                   ("add_poly", "Add Polygon")]),

            ("REMOVE SHAPES FROM ROI", [("sub_rect", "Remove Rectangle"),
                                        ("sub_circle", "Remove Circle"),
                                        ("sub_poly", "Remove Polygon")]),

            ("SEED LOCATION", [("add_seed", "Add Reliability Guided Seed Location")]),

            ("UNDO / REDO SHAPES", [("undo_prev", "Undo Shape"),
                                    ("redo_prev", "Redo Shape")]),

            ("COMPLETION", [("finished", "ROI Completed")])
        ]

        self.buttons = {}
        for section_title, button_list in button_configs:
            sidebar.addWidget(make_title(section_title))
            for btn_id, btn_text in button_list:
                btn = QtWidgets.QPushButton(btn_text)
                self.buttons[btn_id] = btn
                sidebar.addWidget(btn)
            sidebar.addSpacing(20)

        # Initial button states
        self.buttons['undo_prev'].setEnabled(False)
        self.buttons['redo_prev'].setEnabled(False)
        
        self.coord_label = QtWidgets.QLabel("(-, -)")
        self.coord_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        # Set fixed width to handle largest expected value comfortably
        self.coord_label.setMinimumWidth(350)
        self.coord_label.setMaximumWidth(350)

        self.coord_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                padding: 5px;
                border-radius: 3px;
                font-family: monospace;
                font-size: 12px;
            }
        """)
        
        sidebar.addStretch()
        sidebar.addWidget(self.coord_label)
        
        return sidebar

    def _setup_graphics(self):
        """Setup the graphics view and image display."""
        self.main_view = self.graphics_widget.addViewBox(lockAspect=True)
        
        # Setup image
        rotated = np.rot90(self.ref_image, k=-1)
        img = pg.ImageItem(rotated)
        self.main_view.addItem(img)
        self.main_view.disableAutoRange('xy')
        self.main_view.autoRange()

        # Setup fill layer
        self.fill_layer = pg.ImageItem()
        self.fill_layer.setZValue(1)
        self.main_view.addItem(self.fill_layer)

        self.height, self.width = rotated.shape[:2]
        self.fill_array = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        self.temp_mask = np.zeros((self.height, self.width), dtype=bool)

        # Setup drawing overlays
        self._setup_drawing_overlays()

    def _setup_drawing_overlays(self):
        """Setup scatter plots and lines for polygon drawing."""
        self.add_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush('b'))
        self.sub_scatter = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush('r'))
        self.add_line = pg.PlotDataItem(pen=pg.mkPen('b', width=3))
        self.sub_line = pg.PlotDataItem(pen=pg.mkPen('r', width=3))
        
        for item in [self.add_scatter, self.sub_scatter, self.add_line, self.sub_line]:
            self.main_view.addItem(item)

    def _connect_signals(self):
        """Connect all button signals to their handlers."""
        signal_map = {
            'add_seed': lambda: self._start_drawing_mode('seed'),
            'add_rect': lambda: self._start_drawing_mode('rect'),
            'add_circle': lambda: self._start_drawing_mode('circle'),
            'add_poly': lambda: self._start_drawing_mode('poly'),
            'sub_rect': lambda: self._start_removing_mode('rect'),
            'sub_circle': lambda: self._start_removing_mode('circle'),
            'sub_poly': lambda: self._start_removing_mode('poly'),
            'undo_prev': self._undo_last,
            'redo_prev': self._redo_last,
            'save_roi': self._save_interactive_roi,
            'open_roi': self._open_interactive_roi,
            'finished': self._finish
        }

        for btn_id, handler in signal_map.items():
            self.buttons[btn_id].clicked.connect(handler)

        self.main_view.scene().sigMouseClicked.connect(self._mouse_clicked)
        self.main_view.scene().sigMouseMoved.connect(self._mouse_moved)


    def _mouse_moved(self, pos):
        """Handle mouse movement to update coordinate display."""
        if self.main_view.sceneBoundingRect().contains(pos):
            mouse_point = self.main_view.mapSceneToView(pos)
            # Convert from graphics coordinates to image coordinates
            img_x = int(round(mouse_point.x()))
            img_y = int(round(self.width - mouse_point.y()))
            
            # Clamp coordinates to image bounds
            img_x = max(0, min(img_x, self.height - 1))
            img_y = max(0, min(img_y, self.width - 1))
            
            self.coord_label.setText(f"({img_x}, {img_y})")
        else:
            self.coord_label.setText("(-, -)")

    def _start_drawing_mode(self, mode):
        """Start drawing mode for specified shape type."""
        self._reset_all_modes()
        self.drawing_modes[mode] = True
        self.main_view.setCursor(QtCore.Qt.CursorShape.CrossCursor)
        
        if mode == 'poly':
            self.poly_points = []
            self.add_scatter.setData([], [])
            self.add_line.setData([], [])
            print("Click to add polygon points. Right-click to finish.")
        elif mode == 'seed':
            self.buttons['add_seed'].setEnabled(False)
            print("Click to add seed location...")
        else:
            print(f"Click to add {mode}.")

    def _start_removing_mode(self, mode):
        """Start removing mode for specified shape type."""
        self._reset_all_modes()
        self.removing_modes[mode] = True
        self.main_view.setCursor(QtCore.Qt.CursorShape.CrossCursor)
        
        if mode == 'poly':
            self.poly_points = []
            self.sub_scatter.setData([], [])
            self.sub_line.setData([], [])
            print("Click to add polygon points. Right-click to finish.")
        else:
            print(f"Click to remove {mode}.")

    def _reset_all_modes(self):
        """Reset all drawing and removing modes."""
        for mode in self.drawing_modes:
            self.drawing_modes[mode] = False
        for mode in self.removing_modes:
            self.removing_modes[mode] = False

    def _finish_mode(self):
        """Finish current drawing/removing mode."""
        self._reset_all_modes()
        self.main_view.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self._clear_redo_stack()

    def _mouse_clicked(self, event):
        """Handle mouse clicks for drawing shapes."""
        if self.drawing_modes['poly'] or self.removing_modes['poly']:
            self._handle_polygon_click(event)
        elif self.drawing_modes['seed']:
            self._handle_seed_click(event)
        elif any(self.drawing_modes.values()) or any(self.removing_modes.values()):
            self._handle_shape_click(event)

    def _handle_polygon_click(self, event):
        """Handle polygon drawing clicks."""
        is_adding = self.drawing_modes['poly']
        scatter = self.add_scatter if is_adding else self.sub_scatter
        line = self.add_line if is_adding else self.sub_line
        
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            if self.main_view.sceneBoundingRect().contains(pos):
                mouse_point = self.main_view.mapSceneToView(pos)
                self.poly_points.append([mouse_point.x(), mouse_point.y()])
                scatter.setData([p[0] for p in self.poly_points], [p[1] for p in self.poly_points])
                if len(self.poly_points) > 1:
                    line.setData([p[0] for p in self.poly_points], [p[1] for p in self.poly_points])
                    
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self._finish_polygon_drawing(is_adding)

    def _handle_seed_click(self, event):
        """Handle seed location clicks."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            start_point = self.main_view.mapSceneToView(pos)
            
            x = math.floor(start_point.x() - self.subset_size / 2)
            y = math.floor(start_point.y() - self.subset_size / 2)
            
            seed_roi = pg.RectROI(
                [x, y], [self.subset_size, self.subset_size],
                pen=pg.mkPen('b', width=3),
                hoverPen=pg.mkPen('y', width=3),
                handlePen='#0000',
                handleHoverPen='#0000'
            )
            
            # Remove all handles to make it non-interactive
            for handle in seed_roi.getHandles():
                seed_roi.removeHandle(handle)
                
            self.main_view.addItem(seed_roi)
            self.seed_roi = seed_roi
            print(f"Seed initially added at location: [{x}, {self.width-y}]")
            self._finish_mode()

    def _handle_shape_click(self, event):
        """Handle rectangle and circle drawing clicks."""
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return

        pos = event.scenePos()
        start_point = self.main_view.mapSceneToView(pos)
        
        # Determine shape type and add/remove mode
        shape_type = None
        is_adding = True
        
        for mode in ['rect', 'circle']:
            if self.drawing_modes[mode]:
                shape_type = mode
                is_adding = True
                break
            elif self.removing_modes[mode]:
                shape_type = mode
                is_adding = False
                break

        if shape_type:
            roi = self._create_shape_roi(shape_type, start_point, is_adding)
            self._add_roi_to_scene(roi, is_adding)
            self._finish_mode()

    def _create_shape_roi(self, shape_type, start_point, is_adding):
        """Create ROI object for rectangle or circle."""
        pen = pg.mkPen('g', width=4) if is_adding else pg.mkPen('r', width=4)
        hover_pen = pg.mkPen('b', width=4)
        handle_pen = pg.mkPen('b', width=4)
        
        if shape_type == 'rect':
            roi = pg.RectROI(
                start_point, [self.height/6, self.width/6],
                pen=pen, hoverPen=hover_pen, handlePen=handle_pen, handleHoverPen=hover_pen
            )
            roi.addScaleHandle([1, 0], [0.0, 1.0])
            roi.addScaleHandle([0, 1], [1.0, 0.0])
            roi.addScaleHandle([0, 0], [1.0, 1.0])
            roi.addTranslateHandle([0.5, 0.5])
            
        elif shape_type == 'circle':
            x = start_point.x() - self.width / 10
            y = start_point.y() - self.width / 10
            roi = pg.CircleROI(
                [x, y], radius=self.width/10,
                pen=pen, hoverPen=hover_pen, handlePen=handle_pen, handleHoverPen=hover_pen
            )
            roi.addTranslateHandle([0.5, 0.5])
        
        # Style handles
        for handle in roi.getHandles():
            handle.radius = 10
            handle.buildPath()
            handle.update()
            
        return roi

    def _add_roi_to_scene(self, roi, is_adding):
        """Add ROI to scene and lists."""
        self.roi_list.append(roi)
        self.add_list.append(is_adding)
        self.main_view.addItem(roi)
        roi.sigRegionChanged.connect(self._redraw_fill_layer)
        self._redraw_fill_layer()
        self._update_button_states()

    def _finish_polygon_drawing(self, is_adding):
        """Finish polygon drawing."""
        if len(self.poly_points) >= 3:
            pen = pg.mkPen('g', width=4) if is_adding else pg.mkPen('r', width=4)
            hover_pen = pg.mkPen('b', width=4)
            handle_pen = pg.mkPen('b', width=4)
            
            roi = pg.PolyLineROI(
                self.poly_points, closed=True,
                pen=pen, hoverPen=hover_pen, handlePen=handle_pen, handleHoverPen=hover_pen
            )
            
            for handle in roi.getHandles():
                handle.radius = 10
                handle.buildPath()
                handle.update()
                
            self._add_roi_to_scene(roi, is_adding)
            print("Polygon added.")
        else:
            print("Need at least 3 points.")

        # Clean up
        self.poly_points = []
        scatter = self.add_scatter if is_adding else self.sub_scatter
        line = self.add_line if is_adding else self.sub_line
        scatter.setData([], [])
        line.setData([], [])
        self._finish_mode()

    def _redraw_fill_layer(self):
        """Redraw the fill layer based on current ROIs."""
        if not self.roi_list:
            self.fill_array.fill(0)
            self.temp_mask.fill(False)
            self.fill_layer.setImage(self.fill_array)
            return

        self.temp_mask.fill(False)

        for roi, is_adding in zip(self.roi_list, self.add_list):
            if isinstance(roi, pg.RectROI):
                self._apply_rect_mask(roi, is_adding)
            elif isinstance(roi, pg.CircleROI):
                self._apply_circle_mask(roi, is_adding)
            elif isinstance(roi, pg.PolyLineROI):
                self._apply_poly_mask(roi, is_adding)

        # Update fill array
        self.fill_array[:, :, 0] = 0
        self.fill_array[:, :, 1] = 255
        self.fill_array[:, :, 2] = 0
        self.fill_array[:, :, 3] = self.temp_mask * 80
        self.fill_layer.setImage(self.fill_array)

    def _apply_rect_mask(self, roi, is_adding):
        """Apply rectangle mask to temp_mask."""
        pos = roi.pos()
        size = roi.size()
        x, y = int(pos[1]), int(pos[0])
        w, h = int(size[1]), int(size[0])
        
        # Clamp to image bounds
        x = max(0, min(x, self.width))
        y = max(0, min(y, self.height))
        w = max(0, min(w, self.width - x))
        h = max(0, min(h, self.height - y))
        
        if w > 0 and h > 0:
            self.temp_mask[y:y+h, x:x+w] = is_adding

    def _apply_circle_mask(self, roi, is_adding):
        """Apply circle mask to temp_mask."""
        pos = roi.pos()
        size = roi.size()
        cx, cy = pos[1] + size[1]/2, pos[0] + size[0]/2
        rx, ry = size[1]/2, size[0]/2
        
        y_coords, x_coords = np.ogrid[:self.height, :self.width]
        circle_mask = ((x_coords - cx)/rx)**2 + ((y_coords - cy)/ry)**2 <= 1
        
        if is_adding:
            self.temp_mask |= circle_mask
        else:
            self.temp_mask &= ~circle_mask

    def _apply_poly_mask(self, roi, is_adding):
        """Apply polygon mask to temp_mask."""
        points = roi.getState()['points']
        pos = roi.pos()
        
        if len(points) >= 3:
            vertices = np.array([(p[1]+pos[1], p[0]+pos[0]) for p in points])
            path = mplPath(vertices)
            
            x_min, x_max = int(np.floor(vertices[:, 0].min())), int(np.ceil(vertices[:, 0].max()))
            y_min, y_max = int(np.floor(vertices[:, 1].min())), int(np.ceil(vertices[:, 1].max()))
            
            # Clamp to image bounds
            x_min = max(0, x_min)
            x_max = min(self.width, x_max)
            y_min = max(0, y_min)
            y_max = min(self.height, y_max)
            
            if x_max > x_min and y_max > y_min:
                xx, yy = np.meshgrid(np.arange(x_min, x_max), np.arange(y_min, y_max))
                points_grid = np.column_stack((xx.ravel(), yy.ravel()))
                inside = path.contains_points(points_grid)
                inside_2d = inside.reshape(y_max - y_min, x_max - x_min)
                
                if is_adding:
                    self.temp_mask[y_min:y_max, x_min:x_max] |= inside_2d
                else:
                    self.temp_mask[y_min:y_max, x_min:x_max] &= ~inside_2d

    def _update_button_states(self):
        """Update the enabled state of undo and redo buttons."""
        self.buttons['undo_prev'].setEnabled(len(self.roi_list) > 0)
        self.buttons['redo_prev'].setEnabled(len(self.undo_list) > 0)

    def _clear_redo_stack(self):
        """Clear the redo stack when new shapes are added."""
        self.undo_list = []
        self._update_button_states()

    def _undo_last(self):
        """Undo the last ROI operation."""
        if self.roi_list:
            roi = self.roi_list.pop()
            add_flag = self.add_list.pop()
            self.main_view.removeItem(roi)
            self.undo_list.append((roi, add_flag))
            self._redraw_fill_layer()
            self._update_button_states()

    def _redo_last(self):
        """Redo the last undone ROI operation."""
        if self.undo_list:
            roi, add_flag = self.undo_list.pop()
            self.roi_list.append(roi)
            self.add_list.append(add_flag)
            self.main_view.addItem(roi)
            roi.sigRegionChanged.connect(self._redraw_fill_layer)
            self._redraw_fill_layer()
            self._update_button_states()

    def _save_interactive_roi(self):
        """Save the current ROI to a YAML file. This only works with the interactive GUI."""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self.main_window, 'Save ROI', 'roi_interactive.yaml', filter='YAML Files (*.yaml)')

        if filename:

            # Ensure extension is added if user doesn't include it
            if filename and not filename.endswith('.yaml'):
                filename += '.yaml'

            print("Saving to file:", filename)
            serialized = [
                self._get_roi_data(roi, add) 
                for roi, add in zip(self.roi_list, self.add_list)
            ]

            # add ROI to serialized data
            if hasattr(self, 'seed_roi'):
                self._finalize_selection()
                seed_data = {
                    'type': 'SeedROI',
                    'pos': [self.seed[0], self.seed[1]],
                    'size': [self.subset_size, self.subset_size],
                    'add': True
                }
                serialized.append(seed_data)

            with open(filename, 'w') as f:
                yaml.dump(serialized, f, sort_keys=False)

    def _open_interactive_roi(self):
        """Open ROI from a YAML file. This only works with the interactive GUI."""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main_window, 'Open ROI', filter='YAML Files (*.yaml)'
        )
        if filename:
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)

            # Clear existing ROIs
            for roi in self.roi_list:
                self.main_view.removeItem(roi)
            self.roi_list = []
            self.add_list = []

            self.seed_roi = None  # Clear existing seed

            for entry in data:
                if entry.get('type') == 'SeedROI':
                    # Restore the seed ROI
                    x, y = entry['pos']
                    y = self.width-y
                    size = entry.get('size', [10, 10])  # fallback default
                    self.seed_roi = pg.RectROI(
                        [x, y], size,
                        pen=pg.mkPen('b', width=3),
                        hoverPen=pg.mkPen('y', width=3),
                        handlePen='#0000',
                        handleHoverPen='#0000'
                    )
                    self.main_view.addItem(self.seed_roi)

                else:
                    # Restore standard ROI
                    roi = self._create_roi_from_data(entry)
                    self.roi_list.append(roi)
                    self.add_list.append(entry['add'])
                    self.main_view.addItem(roi)
                    roi.sigRegionChanged.connect(self._redraw_fill_layer)

            self._redraw_fill_layer()
            self._update_button_states()
            
    def _create_roi_from_data(self, entry):
        """Create ROI object from saved data."""
        roi_type = entry['type']
        is_adding = entry['add']
        
        pen = pg.mkPen('g', width=4) if is_adding else pg.mkPen('r', width=4)
        hover_pen = pg.mkPen('b', width=4)
        handle_pen = pg.mkPen('b', width=4)
        
        if roi_type == 'RectROI':
            roi = pg.RectROI(entry['pos'], entry['size'], pen=pen, 
                             hoverPen=hover_pen, handlePen=handle_pen,
                             handleHoverPen=hover_pen)

            roi.addScaleHandle([1, 0], [0.0, 1.0])
            roi.addScaleHandle([0, 1], [1.0, 0.0])
            roi.addScaleHandle([0, 0], [1.0, 1.0])
            roi.addTranslateHandle([0.5, 0.5])

        elif roi_type == 'CircleROI':
            roi = pg.CircleROI(entry['pos'], entry['size'], pen=pen, 
                               hoverPen=hover_pen, handlePen=handle_pen, 
                               handleHoverPen=hover_pen)
            roi.addTranslateHandle([0.5, 0.5])

        elif roi_type == 'PolyLineROI':
            points = [QtCore.QPointF(p[0], p[1]) for p in entry['points']]
            roi = pg.PolyLineROI(points, closed=True,pen=pen, 
                                 hoverPen=hover_pen, handlePen=handle_pen,
                                 handleHoverPen=hover_pen)

        else:
            raise TypeError(f"Unsupported ROI type: {roi_type}")

        #update handle sizes
        for handle in roi.getHandles():
            handle.radius = 10
            handle.buildPath()
            handle.update()
            
        return roi

    def _finish(self):
        """Finish ROI selection and close the GUI, with a check for empty seed."""

        self._finalize_selection()

        if not self.seed:
            reply = QtWidgets.QMessageBox.question(
                self.main_window,
                "Exit Confirmation",
                "No Seed location has been selected for reliability guided DIC. Are you sure you want to continue?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                return

        self.main_window.close()
        pg.QtWidgets.QApplication.quit()

    def _finalize_selection(self):
        """Process the final mask and seed location."""
        self.mask = np.flipud(self.temp_mask.T)

        if hasattr(self, 'seed_roi'):
            pos = self.seed_roi.pos()
            x = int(np.floor(pos.x()))
            y = int(np.floor(self.width - pos.y()))
            self.seed = [x, y]

            if not self.mask[y, x]:
                raise ValueError(f"Seed location [{x}, {y}] is not within the mask")
            print(f"Final seed location: [{x}, {y}]")

    def _get_roi_data(self, roi_element, add: bool):
        """Extract data from ROI element for serialization."""
        if isinstance(roi_element, pg.RectROI):
            return {
                'type': 'RectROI',
                'pos': [float(roi_element.pos().x()), float(roi_element.pos().y())],
                'size': [float(roi_element.size().x()), float(roi_element.size().y())],
                'add': bool(add)
            }
        elif isinstance(roi_element, pg.CircleROI):
            return {
                'type': 'CircleROI',
                'pos': [float(roi_element.pos().x()), float(roi_element.pos().y())],
                'size': [float(roi_element.size().x()), float(roi_element.size().y())],
                'add': bool(add)
            }
        elif isinstance(roi_element, pg.PolyLineROI):
            handle_pos = roi_element.getLocalHandlePositions()
            points = [[float(p[1].x()), float(p[1].y())] for p in handle_pos]
            return {
                'type': 'PolyLineROI',
                'points': points,
                'add': bool(add)
            }
        else:
            raise TypeError(f"Unsupported ROI type: {type(roi_element)}")
    

    def reset_mask(self):
        """
        Completely resets the roi mask to 0s.
        """
        self.mask[:] = False;



    def rect_boundary(self, left: int, right: int, top: int, bottom: int) -> None:
        """
        Defines a central rectangular region of interest (ROI) excluding
        surrounding pixels defined by input arguments"
        
        Parameters
        ----------
            left (int): Number of px to exclude from left edge.
            right (int): Number of px to exclude from the right edge.
            top (int): Number of px to exclude from the top edge.
            bottom (int): Number of px to exclude from the bottom edge.
        """
        self.reset_mask()
        self.mask[bottom:(self.ref_image.shape[0]-top), left:(self.ref_image.shape[1])-right] = 255
        self.__roi_selected = True

    def rect_region(self, x: int, y: int, size_x: int, size_y: int ) -> None:

            top    = max(0, y)
            bottom = min(self.ref_image.shape[0],y+size_y)
            left   = max(0, x)
            right  = min(self.ref_image.shape[1],x+size_x)

            # Apply the mask in the subset region
            self.mask[top:bottom, left:right] = 255
            self.__roi_selected = True




    def save_image(self, filename: str | Path) -> None:
        """
        Save the ROI overlayed over the reference image in .tiff image format.

        Parameters
        ----------
        filename : str or pathlib.Path
            Filename of image

        Raises
        ------
        ValueError
            If no ROI has been selected
        """
        if not self.__roi_selected:
            raise ValueError("No ROI selected with \'interactive_selection\', \'rect_boundary\', \'read_array\' or \'rect_region\'. ")

        overlay = self.ref_image.copy()
        overlay[self.mask] = (0, 255, 0)
        result = cv2.addWeighted(self.ref_image, 0.6, overlay, 0.4, 0)
        cv2.imwrite(str(filename), result)




    def save_array(self, filename: str | Path, binary: bool=False) -> None:
        """
        Save the ROI mask as a numpy binary or text file.

        Parameters
        ----------
        filename : str or pathlib.Path
            filename given to saved ROI mask
        binary : bool
            If True, saves from as a .npy binary file. 
            If False, saves to a space delimited text file.

        Raises
        ------
        ValueError
            If no ROI has been selected.
        """
        if not self.__roi_selected:
            raise ValueError("No ROI selected with \'interactive_selection\', \'rect_boundary\', \'read_array\' or \'rect_region\'. ")
        
        if binary:
            np.save(filename, self.mask)
        else:
            np.savetxt(filename, self.mask, fmt='%d', delimiter=' ')


    def read_array(self, filename: str | Path, binary: bool = False) -> None:
        """
        Load the ROI mask from a binary or text file and store it in `self.mask`.

        Parameters
        ----------
        filename : str or pathlib.Path
            Path to the file to load.
        binary : bool
            If True, loads from a .npy binary file. If False, loads from a text file.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        ValueError
            If the loaded data is not a valid mask.
        """

        if not os.path.exists(filename):
            raise FileNotFoundError(f"File '{filename}' does not exist.")

        if binary:
            self.mask = np.load(filename)
        else:
            self.mask = np.loadtxt(filename, dtype=bool, delimiter=' ')

        # Optional: check if the loaded data is a proper binary mask (0s and 1s)
        if not np.isin(self.mask, [0, 1]).all():
            raise ValueError("Loaded ROI mask contains values other than 0 and 1.")

        self.__roi_selected = True


    def save_yaml(self,  filename: str | Path) -> None:
        """
        Save the current ROI to a YAML file. This only works with the after having run the interactive GUI.

        Parameters
        ----------
        filename : str or pathlib.Path
            Filename of the YAML file to save the ROI data.

        Raises
        ------
        ValueError
            If no ROI has been selected.
        """

        if filename:

            # Ensure extension is added if user doesn't include it
            if filename and not filename.endswith('.yaml'):
                filename += '.yaml'

            print("Saving to file:", filename)
            serialized = [
                self._get_roi_data(roi, add) 
                for roi, add in zip(self.roi_list, self.add_list)
            ]

            # add ROI to serialized data
            if hasattr(self, 'seed_roi'):
                self._finalize_selection()
                seed_data = {
                    'type': 'SeedROI',
                    'pos': [self.seed[0], self.seed[1]],
                    'size': [self.subset_size, self.subset_size],
                    'add': True
                }
                serialized.append(seed_data)

            with open(filename, 'w') as f:
                yaml.dump(serialized, f, sort_keys=False)

    def read_yaml(self, filename: str | Path) -> None:
        """
        Load the ROI from a YAML file and restore the state of the GUI.
        This method will clear existing ROIs and restore the state from the YAML file.

        Parameters
        ----------
        filename : str or pathlib.Path
            Path to the YAML file containing the ROI data.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        ValueError
            If the loaded data is not a valid ROI format.
        """

        # need to create a temp qapplication so I can import the ROI.
        self.__roi_selected = True
        
        # Initialize GUI
        self._setup_gui()
        self._setup_graphics()
        self._connect_signals()

        if filename:
            with open(filename, 'r') as f:
                data = yaml.safe_load(f)

            self.roi_list = []
            self.add_list = []

            self.seed_roi = None  # Clear existing seed

            for entry in data:
                if entry.get('type') == 'SeedROI':
                    # Restore the seed ROI
                    x, y = entry['pos']
                    y = self.width-y
                    size = entry.get('size', [10, 10])  # fallback default
                    self.seed_roi = pg.RectROI(
                        [x, y], size,
                        pen=pg.mkPen('b', width=3),
                        hoverPen=pg.mkPen('y', width=3),
                        handlePen='#0000',
                        handleHoverPen='#0000'
                    )
                    self.main_view.addItem(self.seed_roi)

                else:
                    # Restore standard ROI
                    roi = self._create_roi_from_data(entry)
                    self.roi_list.append(roi)
                    self.add_list.append(entry['add'])
                    self.main_view.addItem(roi)
                    roi.sigRegionChanged.connect(self._redraw_fill_layer)

            self._redraw_fill_layer()
            self._update_button_states()
            self._finalize_selection()



    def show_image(self) -> None:
        """
        Displays the current mask in grayscale.

        Raises
        ------
            ValueError: If no ROI is selected.
        """

        # Convert grayscale image to 3-channel if needed
        if self.ref_image.ndim == 2:
            ref_image_color = cv2.cvtColor(self.ref_image.astype(np.uint8), cv2.COLOR_GRAY2BGR)
        else:
            ref_image_color = self.ref_image

        # Create a green mask image
        if self.ref_image.ndim == 3:
            green_mask = np.zeros_like(self.ref_image)
        elif self.ref_image.ndim == 2:
            h, w = self.ref_image.shape
            green_mask = np.zeros((h, w, 3), dtype=self.ref_image.dtype)
        else:
            raise ValueError(f"Unsupported image shape: {self.ref_image.shape}")

        # Apply the green mask
        green_mask[self.mask, :] = [0, 255, 0]

        # Blend the original image and the green mask
        blended = ref_image_color.astype(float) * 0.7 + green_mask.astype(float) * 0.3
        blended = blended.astype(np.uint8)

        # Display using Matplotlib
        import matplotlib.pyplot as plt
        plt.figure()
        plt.imshow(blended)
        plt.axis('off')
        plt.tight_layout()
        plt.show()


class CustomMainWindow(QtWidgets.QWidget):
    def __init__(self, dic_obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dic_obj = dic_obj
        
    def closeEvent(self, event):
        if self.dic_obj:
            # Force finalization before checking seed
            self.dic_obj._finalize_selection()
            
            if not self.dic_obj.seed:
                reply = QtWidgets.QMessageBox.question(
                    self,
                    "Exit Confirmation",
                    "No Seed location has been selected for reliability guided DIC. Are you sure you want to continue?",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.No
                )
                if reply == QtWidgets.QMessageBox.StandardButton.No:
                    event.ignore()
                    return
        event.accept()
