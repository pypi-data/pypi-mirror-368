""" 
Tadqeeq - Image Annotator Tool
An interactive image annotation tool for efficient labeling.
Developed by Mohamed Behery @ RTR Software Development (2025-04-27).
Licensed under the MIT License.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QShortcut
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QKeySequence, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
import numpy as np
import os
from functools import reduce
from collections.abc import Iterable
from skimage.io import imsave
from skimage.transform import resize
from skimage.feature import canny
from scipy.ndimage import binary_fill_holes

from tadqeeq.utils import compute_segment_areas, rgba_array_to_pixmap, \
                  apply_lut_replacement, detect_overlapping_boxes_to_clean, \
                  mask_to_bounding_box, pixmap_to_rgba_array, \
                  locate_all_pixels_via_floodfill
                  
from warnings import filterwarnings
filterwarnings('ignore', category=UserWarning, message='.*low contrast image.*')

class ImageAnnotator(QWidget):
    
    """
    Interactive PyQt5 widget for image annotation using bounding boxes and segmentation masks.

    This tool supports real-time annotation, erasing, label switching, and autosave features. It can load both
    bounding boxes (from `.txt`) and semantic segmentation masks (from `.npy`) and allows switching between them.
    Users can draw with varying pen sizes, adjust transparency, and display floating label overlays.

    Parameters:
        image_filepath (str): Path to the input image file.
        bounding_boxes_filepath (str): Path to the file for loading/saving bounding box annotations.
        semantic_segments_filepath (str): Path to the file for loading/saving semantic segment masks.
        void_background (bool): Whether to treat background as a void region (labelled 255) or a regular label.
        autosave (bool): If True, saves annotations automatically after each edit.
        key_sequence_to_save (str): Keyboard shortcut to trigger manual save (default is "Ctrl+S").
        minimum_pen_width (int): Minimum width of the drawing pen in pixels.
        minimum_font_size (int): Minimum font size used in floating label displays.
        hsv_offsets (tuple): HSV color offsets (H, S, V) for generating distinct label colors.
        opacity (float): Opacity (0–1) for overlaying segmentation masks.
        label_slider_sensitivity (float): Sensitivity factor for scrolling through label indices.
        label_color_pairs (int): Number of label-color pairs to generate or expect.
        pen_width_slider_sensitivity (float): Sensitivity of scrolling input for changing pen width.
        maximum_pen_width_multiplier (float): Maximum multiplier for pen width scaling.
        floating_label_display_offsets (tuple): Offset (x, y) for floating label position relative to cursor.
        bounding_box_side_length_thresholds (tuple): Min and max allowable side lengths for bounding boxes.
        overlap_vs_smallest_area_threshold (float): Overlap ratio (vs smallest area) above which a box is suppressed.
        overlap_vs_union_area_threshold (float): Overlap ratio (vs union area) above which a box is suppressed.
        corner_label_attached_to_bounding_box (bool): Whether to attach label text to bounding box corners.
        verbose (bool): If True, enables verbose logging output for debugging and interaction feedback.
    """
    
    __RESIZE_DELAY = 200
    
    def __init__(self, 
                 image_filepath, 
                 bounding_boxes_filepath,
                 semantic_segments_filepath,
                 void_background=False,
                 autosave=True,
                 key_sequence_to_save='Ctrl+S',
                 minimum_pen_width=4,
                 minimum_font_size=16,
                 hsv_offsets=(0,255,200), 
                 opacity=0.5,
                 label_slider_sensitivity=0.30,
                 label_color_pairs=32,
                 pen_width_slider_sensitivity=0.05,
                 maximum_pen_width_multiplier=4.0,
                 floating_label_display_offsets=(15,30),
                 bounding_box_side_length_thresholds=(25,2000),
                 overlap_vs_smallest_area_threshold=0.95,
                 overlap_vs_union_area_threshold=0.95,
                 corner_label_attached_to_bounding_box=True,
                 verbose=True):
        
        def configure_verbosity():
            self.__verbose = verbose
            self.__previous_message = ''
        
        def disable_maximize_button():
            nonlocal self
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        
        def configure_resize_scheduler():
            nonlocal self
            self.__resize_scheduler = QTimer(self)
            self.__resize_scheduler.setSingleShot(True)
            self.__resize_scheduler.timeout.connect(self.__resize_user_interface_update_routine)
            self.__resize_flag = False
            
        def configure_saving_parameters():
            nonlocal self, key_sequence_to_save, autosave
            key_sequence_to_save = QKeySequence(key_sequence_to_save)
            self.__key_sequence_to_save = QShortcut(key_sequence_to_save, self)
            self.__key_sequence_to_save.activated.connect(self.save)
            self.__autosave = autosave
            
        def configure_displays():
            nonlocal self
            self.__image_display = QLabel(self)
            self.__label_to_annotate_display = QLabel('Label: N/A', self)
            self.__label_annotated_display = QLabel('Label: N/A', self)
            self.__minimum_widget_size_set = False
            self.floating_label_display_offsets = floating_label_display_offsets
            self.__label_index_hovered_over = -1
            
        def initialize_annotation_pen():
            nonlocal self, minimum_pen_width
            self.__annotation_pen = QPen(Qt.black, minimum_pen_width, Qt.SolidLine)
            self.last_pen_position = None
            self.__erasing = False
        
        def configure_annotation_parameters():
            nonlocal self, minimum_pen_width, minimum_font_size, hsv_offsets, opacity
            self.__minimum_pen_width = minimum_pen_width
            self.__label_font_size = minimum_font_size
            self.__hsv_offsets = hsv_offsets
            self.__opacity = opacity
            self.__void_background = void_background
            
        def configure_bounding_boxes():
            self.__bounding_box_side_length_thresholds = bounding_box_side_length_thresholds
            self.__overlap_vs_smallest_area_threshold = overlap_vs_smallest_area_threshold
            self.__overlap_vs_union_area_threshold = overlap_vs_union_area_threshold
            self.__corner_label_attached_to_bounding_box = corner_label_attached_to_bounding_box
        
        def initialize_sliders():
            self.__label_slider_enabled = True
            self.__pen_width_slider_sensitivity = pen_width_slider_sensitivity
            self.maximum_pen_width_multiplier = maximum_pen_width_multiplier
            self.pen_width_multiplier_accumulator = 0.0
            self.__label_slider_sensitivity = label_slider_sensitivity
            self.label_color_pairs = label_color_pairs
            self.label_index_accumulator = 0.0
        
        def load_image_annotation_pair():
            if not(bool(semantic_segments_filepath) or bool(bounding_boxes_filepath)):
                raise ValueError('At least one annotation filepath is to be provided, either `semantic_segments_filepath` or `bounding_boxes_filepath`, or both.')
            self.image_filepath = image_filepath
            self.bounding_boxes_filepath = bounding_boxes_filepath
            self.semantic_segments_filepath = semantic_segments_filepath
            
        def enable_mouse_tracking():
            self.setMouseTracking(True)
            self.__image_display.setMouseTracking(True)
            self.__label_to_annotate_display.setMouseTracking(True)
            self.__label_annotated_display.setMouseTracking(True)
            
        super().__init__()
        
        configure_verbosity()
        disable_maximize_button()
        configure_resize_scheduler()
        configure_saving_parameters()
        configure_displays()
        initialize_annotation_pen()
        configure_annotation_parameters()
        configure_bounding_boxes()
        initialize_sliders()
        load_image_annotation_pair()
        enable_mouse_tracking()
    
    @property
    def use_bounding_boxes(self):
        """
        Check if bounding box annotations are currently enabled.
        
        Returns:
            bool: True if bounding boxes are in use, False otherwise.
        
        Note: 
            `hasattr` is used to make sure no NameError occurs when checking this condition before the variable exists
        """
        return hasattr(self, f'_{self.__class__.__name__}__use_bounding_boxes') and self.__use_bounding_boxes
    
    @property
    def use_semantic_segments(self):
        """
        Check if semantic segmentation annotations are currently enabled.
        
        Returns:
            bool: True if semantic segments are in use, False otherwise.
            
        Note: 
            `hasattr` is used to make sure no NameError occurs when checking this condition before the variable exists
        """
        return hasattr(self, f'_{self.__class__.__name__}__use_semantic_segments') and self.__use_semantic_segments
    
    @property
    def bounding_boxes_filepath(self):
        """
        Get the file path used for bounding box annotations.
        
        Returns:
            str: Path to the bounding box annotation file.
        """
        return self.__bounding_boxes_filepath
    
    @bounding_boxes_filepath.setter
    def bounding_boxes_filepath(self, value:str):
        """
        Set the file path for bounding box annotations and load data from it.
        
        If the file is missing or empty, a fresh annotation state is initialized.
        
        Args:
            value (str): Path to the bounding box annotation file (TXT format assumed).
        """
        self.__bounding_boxes_filepath = value
        self.__use_bounding_boxes = bool(value)
        try:
            with open(value) as file:
                lines = file.readlines()
            table = [line.strip().split() for line in lines if line.strip()]
            assert len(table) > 0, 'Empty annotations file...'
            self.__bounding_boxes = np.int32(table)
        except (FileNotFoundError, AssertionError):
            self.log('No annotations existing, starting afresh...')
            self.__clear_annotations()
        finally:
            self.__annotate_user_interface_update_routine()
    
    @property
    def semantic_segments_filepath(self):
        """
        Get the file path used for semantic segmentation annotations.
        
        Returns:
            str: Path to the segmentation mask image file.
        """
        return self.__semantic_segments_filepath
    
    @semantic_segments_filepath.setter
    def semantic_segments_filepath(self, value:str):
        """
        Set the file path for semantic segmentation annotations and load the segment masks.
        
        If the corresponding .npy file is missing or empty, a fresh annotation state is initialized.
        
        Args:
            value (str): Path to the segmentation mask image file (PNG format assumed).
        """
        self.__semantic_segments_filepath = value
        self.__use_semantic_segments = bool(value)
        try:
            self.__path_to_labelled_segment_masks = os.path.splitext(value)[0] + '.npy'
            self.labelled_segment_masks = np.load(self.__path_to_labelled_segment_masks)
            assert self.labelled_segment_masks.size > 0, 'Empty annotations file...'
        except (FileNotFoundError, AssertionError):
            self.log('No annotations existing, starting afresh...')
            self.__clear_annotations()
        finally:
            self.__annotate_user_interface_update_routine()
        
    @property
    def void_background(self):
        """
        Indicates whether the background is treated as a void class (labelled 255) or as a regular one (labelled 0).
        
        Returns:
            bool: True if background is considered void (label 255), otherwise False.
        """
        return self.__void_background
        
    @property
    def RESIZE_DELAY(cls):
        """
        Delay (in milliseconds) before triggering a resize update routine.
        
        Returns:
            int: Time delay used to debounce resize events.
        """
        return cls.__RESIZE_DELAY
        
    @property
    def last_pen_position(self):
        """
        Get the most recent pen position used for drawing.
        
        Returns:
            QPoint: The last recorded pen position.
        """
        return self.__last_pen_position
    
    @last_pen_position.setter
    def last_pen_position(self, value:QPoint):
        """
        Set the last pen position and update the corresponding cursor position 
        in original image coordinates.
        
        Args:
            value (QPoint): Latest cursor position in the widget's coordinate space.
        """
        self.__last_pen_position = value
        self.__update_yx_cursor_within_original_image(value)
        
    @property
    def maximum_pen_width_multiplier(self):
        """
        Get the maximum allowed multiplier for pen width scaling.
        
        Returns:
            float: Maximum multiplier used to scale pen width.
        """
        return self.__maximum_pen_width_multiplier
    
    @maximum_pen_width_multiplier.setter
    def maximum_pen_width_multiplier(self, value):
        """
        Set the maximum allowed multiplier for pen width scaling.
        
        Args:
            value (float): The maximum scaling factor for pen width.
        """
        self.__maximum_pen_width_multiplier = value
    
    @property
    def verbose(self):
        """
        Get the current verbosity setting.
        
        Returns:
            bool: True if verbose logging is enabled, False otherwise.
        """
        return self.__verbose
        
    @property
    def erasing(self):
        """
        Check whether the erasing mode is currently active.
        
        Returns:
            bool: True if erasing is enabled, False otherwise.
        """
        return self.__erasing
    
    @property
    def floating_label_display_offsets(self):
        """
        Get the current (x, y) pixel offsets for floating label display.
        
        Returns:
            tuple: Offset values used to position floating labels relative to the cursor.
        """
        return self.__floating_label_display_offsets
    
    @floating_label_display_offsets.setter
    def floating_label_display_offsets(self, value):
        """
        Set the (x, y) pixel offsets for floating label placement.
        
        Enables or disables floating labels based on whether the given value is truthy or falsey.
        
        Args:
            value (tuple|NoneType): Pixel offset used to position floating labels relative to the cursor.
        """
        self.__floating_label_display_offsets = value
        self.__is_floating_label = bool(self.__floating_label_display_offsets)
    
    @property
    def image_filepath(self):
        """
        Get the path to the currently loaded image.
        
        Returns:
            str: Filepath of the image being annotated.
        """
        return self.__image_filepath
    
    @image_filepath.setter
    def image_filepath(self, value:str):
        """
        Set the path to the image and initialize the image display and drawing overlay.
        
        Args:
            value (str): Path to the image file.
        """
        self.__image_filepath = value
        self.image = QPixmap(value)
        self.initialize_overlay('drawing')
        
    @property
    def label_index_to_annotate(self):
        """
        Get the index of the currently selected label for annotation.
    
        Returns:
            int: Index of the active label used for drawing.
        """
        return self.__label_index_to_annotate
    
    @label_index_to_annotate.setter
    def label_index_to_annotate(self, value:int):
        """
        Set the index of the label to be used for annotation.
        
        Updates the current label index, the corresponding label string,
        and the pen color used for annotation to match the selected label.
        
        Args:
            value (int): The index of the label to activate for annotation.
        """
        self.__label_index_to_annotate = value
        self.__label_to_annotate = self.labels[value]
        self.__label_to_annotate_color = self.label_colors[value]
        
    @property
    def label_to_annotate_color(self):
        """
        Get the color associated with the currently selected annotation label.
        
        Returns:
            QColor: The color used to draw or highlight the active label.
        """
        """Returns the label color currently selected for annotation."""
        return self.__label_to_annotate_color
        
    @property
    def label_to_annotate(self):
        """
        Get the label currently selected for annotation.
        
        Returns:
            str: The active label name used for annotating objects.
        """
        return self.__label_to_annotate
        
    @property
    def is_floating_label(self):
        """
        Indicates whether floating label display mode is enabled.
        
        Returns:
            bool: True if floating label mode is active, False otherwise.
        """
        return self.__is_floating_label
    
    @property
    def label_color_pairs(self):
        """
        Get all label and color pairs.
        
        Returns:
            dict: Collection of label-color pairs used for annotation.
        """
        return self.__label_color_pairs
    
    @label_color_pairs.setter
    def label_color_pairs(self, value):
        """
        Set the label-color pairs and update internal label and color mappings accordingly.
        
        This setter accepts different input types to configure the label-color mappings:
        
        - If `value` is a dictionary, it directly sets `__label_color_pairs` and updates
          `__labels`, `__label_colors`, and `__n_labels` accordingly.
        - If `value` is an iterable (e.g., a list of labels), it converts the labels into a list
          and generates corresponding colors automatically.
        - If `value` is an integer, it generates sequential numeric labels from 0 to `value - 1`
          and assigns unique colors to each.
        - If `value` is none of the above, a `ValueError` is raised.
        
        Args:
            value (dict, Iterable, int): 
                - Dictionary of label-color pairs (label: color), or
                - Iterable of labels (for which colors will be generated), or
                - Integer specifying the number of labels to generate with numeric labels.
        
        Raises:
            ValueError: If `value` is neither a dictionary, an iterable, nor an integer.
        """
        try:
            self.__label_color_pairs = dict(value)
            self.__labels = list(self.__label_color_pairs.keys())
            self.__label_colors = list(self.__label_color_pairs.values())
            self.__n_labels = len(self.__labels)
        except (ValueError, TypeError):
            if isinstance(value, Iterable):
                self.labels = list(value)
            elif type(value) is int:
                self.labels = list(range(value))
            else:
                raise ValueError('`labels` should either be `Iterable` or `int`.')
                
    @property
    def labels(self):
        """
        Get the list of annotation labels.
        
        Returns:
            list: The current list of labels used for annotation.
        """
        return self.__labels
    
    @labels.setter
    def labels(self, value:list):
        """
        Set the list of labels and generate corresponding colors for each label.
        
        This setter:
        - Assigns the provided list of labels to the internal `__labels` attribute.
        - Updates the number of labels (`__n_labels`) based on the list length.
        - Generates a unique color for each label using an HSV-based color model.
        - Maps each label to its corresponding color in `__label_color_pairs`.
        
        Args:
            value (list): List of labels to set.
        
        Notes:
            - Colors are generated using a hue, saturation, and value (HSV) scheme
              based on the label index and predefined HSV offsets.
            - Generated colors are stored in `__label_colors` and paired with labels
              in `__label_color_pairs`.
        """
        def color_from_label_index(index):
            hsv_bin_sizes = (255 - np.array(self.__hsv_offsets)) // self.__n_labels
            h, s, v = map(lambda a, b: a * index + b, hsv_bin_sizes, self.__hsv_offsets)
            return QColor.fromHsv(h, s, v)
        
        self.__labels = value
        self.__n_labels = len(value)
        self.__label_colors = [color_from_label_index(index) for index in range(self.__n_labels)]
        self.__label_color_pairs = dict(zip(self.__labels, self.__label_colors))
    
    @property
    def label_colors(self):
        """
        Get the list of colors assigned to each label.
        
        Returns:
            list(QColor): Colors corresponding to each label.
        """
        return self.__label_colors
    
    @property
    def n_labels(self):
        """
        Get the total number of labels.
        
        Returns:
            int: Number of labels currently defined.
        """
        return self.__n_labels
    
    @property
    def corner_label_attached_to_bounding_box(self):
        """
        Check whether the corner label is attached to the bounding box.
        
        Returns:
            bool: True if the corner label is attached, False otherwise.
        """
        return self.__corner_label_attached_to_bounding_box
        
    @property
    def image(self):
        """
        Get the currently loaded image.
        
        Returns:
            QPixmap: The current image used for annotation.
        """
        return self.__image
    
    @image.setter
    def image(self, value:QPixmap):
        """
        Set the image to be annotated and adjust internal parameters accordingly.
        
        This setter:
        - Assigns the provided QPixmap to the internal `__image` attribute.
        - Records the original image dimensions (height and width) in `__original_array_shape`.
        - If the provided QPixmap is null (e.g., no image loaded), creates a blank white image
          matching the widget size to ensure a valid image is set.
        - Calculates the scaling factor based on the widget’s width relative to the image width.
        - Scales the image to fit the widget size while preserving aspect ratio, using smooth transformation.
        - Resizes the widget to the scaled image size.
        
        Args:
            value (QPixmap): The new image to set.
        """
        self.__image = value
        self.__original_array_shape = [value.height(), value.width()]
        if value.isNull():
            blank_image = QPixmap(self.size())
            blank_image.fill(Qt.white)
            self.__image = blank_image
        self.__scale_factor = self.width() / self.image.width()
        self.__image = value.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.resize(self.__image.size())
    
    @property
    def annotation_overlay(self):
        """
        Get the current annotation overlay.
        
        Returns:
            QPixmap: The current annotation overlay pixmap.
        """
        return self.__annotation_overlay
    
    @annotation_overlay.setter
    def annotation_overlay(self, value:QPixmap):
        """
        Set the annotation overlay with the provided QPixmap, resizing and aligning it to the current image size.
        
        This setter:
        - Initializes the internal `__annotation_overlay` as a transparent QPixmap matching the image size.
        - Uses a QPainter to draw the given `value` QPixmap onto the transparent overlay at position (0, 0).
        - Ensures that the annotation overlay is correctly aligned and sized with respect to the image.
        
        Args:
            value (QPixmap): The QPixmap to set as the annotation overlay.
            
        Notes:
            - The annotation overlay is reset to a transparent layer each time this setter is called.
            - QPainter is used to composite the provided pixmap onto the transparent overlay.
        """
        self.initialize_overlay('annotation')
        painter = QPainter(self.__annotation_overlay)
        painter.drawPixmap(0, 0, QPixmap(value))
        painter.end()
        
    @property
    def bounding_boxes(self):    
        """
        Get the bounding boxes used for annotation.
    
        Returns:
            list or dict: The current bounding boxes defining annotated regions.
        """
        return self.__bounding_boxes
    
    @property
    def labelled_segment_masks(self):
        """
        Get the labelled segment masks for annotations.
        
        Returns:
            list or array: Masks where each segment is labeled for annotation purposes.
        """
        return self.__labelled_segment_masks
    
    @labelled_segment_masks.setter
    def labelled_segment_masks(self, value:np.ndarray):
        """
        Set the labelled segment masks and update the combined overlay.
        
        - Sorts masks by ascending area to prioritize smaller segments.
        - Synchronizes bounding boxes if active.
        - Recomputes the combined overall segment mask.
        
        Args:
            value (np.ndarray): A 3D array of shape (N, H, W), where each slice is a labelled mask.
        """
        segment_areas = (value != 255).sum(axis=(1,2))
        sorted_area_indices = np.argsort(segment_areas)
        self.__labelled_segment_masks = value[sorted_area_indices]
        if self.use_bounding_boxes and self.__bounding_boxes.size:
            self.__bounding_boxes = self.__bounding_boxes[sorted_area_indices]
        self.__overall_segment_mask = self.__combine_labelled_segment_masks()
    
    @property
    def overall_segment_mask(self):
        """
        Get the combined segment mask that merges all labelled segment masks.
        
        Returns:
            np.ndarray: The overall combined segment mask.
        """
        return self.__overall_segment_mask
    
    @property
    def label_index_accumulator(self):
        """
        Get the floating-point accumulator used for smooth label scrolling.
        
        Returns:
            float: The current value of the label index accumulator.
        """
        return self.__label_index_accumulator
    
    @label_index_accumulator.setter
    def label_index_accumulator(self, value:float):
        """
        Set the label index accumulator and update the active label index for annotation.
        
        This setter:
        - Wraps the floating-point accumulator value modulo the total number of labels,
          ensuring it stays within valid bounds.
        - Computes the integer label index to annotate, with safeguards against floating-point
          rounding errors (e.g., ensuring values like 31.999999 map correctly to 31).
        - If label slider mode is enabled, logs the current accumulator value along with
          the active label index and label name.
        
        Args:
            value (float): New accumulator value, can be fractional to enable smooth scrolling or adjustments.
        """
        self.__label_index_accumulator = value % self.n_labels
        self.label_index_to_annotate = int(value % self.n_labels) % self.n_labels # To avoid quantization error issues when flooring (e.g. 31.99999999999 gives 32 not 31)
        if self.__label_slider_enabled: # Not to depend on the order of initialization
            self.log(f'Label Slider: {self.__label_index_accumulator:.2f}: {self.label_index_to_annotate + 1}/{self.n_labels}, {self.label_to_annotate}')
      
    @property
    def pen_width_multiplier_accumulator(self):
        """
        Get the floating-point accumulator used for pen width adjustments.
        
        Returns:
            float: The current value of the pen width multiplier accumulator.
        """
        return self.__pen_width_multiplier_accumulator
    
    @pen_width_multiplier_accumulator.setter
    def pen_width_multiplier_accumulator(self, value:float):
        """
        Set the floating-point accumulator for pen width adjustments and update the pen width multiplier.
        
        This setter:
        - Clamps the input value between 0.0 and 1.0.
        - Calculates the pen width multiplier as a scaled value between 1 and the maximum allowed multiplier.
        - Logs the updated pen width multiplier if label slider mode is not enabled.
        
        Args:
            value (float): The new pen width multiplier accumulator, expected in the range [0.0, 1.0].
        """
        self.__pen_width_multiplier_accumulator = 0.0 if value < 0.0 else 1.0 if value > 1.0 else value
        self.pen_width_multiplier = 1 + self.__pen_width_multiplier_accumulator * (self.maximum_pen_width_multiplier - 1)
        if not self.__label_slider_enabled: # Not to depend on the order of initialization
            self.log(f'Pen Width Slider: {self.pen_width_multiplier:.2f}')
        
    @property
    def pen_width_multiplier(self):
        """
        Get the current pen width multiplier.
        
        Returns:
            float: The current multiplier applied to the pen width.
        """
        return self.__pen_width_multiplier
    
    @pen_width_multiplier.setter
    def pen_width_multiplier(self, value:float):
        """
        Set the pen width multiplier and update the pen size accordingly.
        
        Args:
            value (float): The new pen width multiplier.
        """
        self.__pen_width_multiplier = value
        self.__resize_pen()
        
    def save(self):
        """
        Save the current annotations to disk.
        
        Behavior:
        - If bounding boxes are used:
            - Saves annotations as a plain text `.txt` file.
            - Each line corresponds to one bounding box, formatted as space-separated values.
        - If semantic segmentation masks are used:
            - Saves the raw labelled segment masks as a `.npy` file.
            - Processes the overall segment mask with label shifting and void boundary tracing
              via `Helper.postprocess_overall_segment_mask_for_saving()`.
            - Saves the processed mask as a `.png` image.
        
        Notes:
        - The save directory is created automatically if it does not exist.
        - The postprocessing ensures label 0 is reserved for the void/background if `void_background` is False,
          and properly traces segment boundaries.
        
        Raises:
            OSError: If saving fails due to file permission or filesystem errors.
        """
        if self.use_bounding_boxes:
            os.makedirs(os.path.dirname(self.bounding_boxes_filepath), exist_ok=True)
            lines = [' '.join(row)+'\n' for row in self.bounding_boxes.astype(str)]
            with open(self.bounding_boxes_filepath, 'w') as file:
                file.writelines(lines)
            self.log(f'Annotations saved to "{self.bounding_boxes_filepath}"')
                
        if self.use_semantic_segments:
            os.makedirs(os.path.dirname(self.semantic_segments_filepath), exist_ok=True)
            np.save(self.__path_to_labelled_segment_masks, self.labelled_segment_masks)
            overall_segment_mask_to_save = self.postprocess_overall_segment_mask_for_saving()
            imsave(self.semantic_segments_filepath, overall_segment_mask_to_save)
            self.log(f'Annotations saved to "{self.semantic_segments_filepath}"')
            
    
    def log(self, message:str):
        """
        Print a log message to the console if verbose mode is enabled.
        
        This method:
        - Clears the previous message from the console by overwriting it with spaces.
        - Prints the new message in place (using carriage return to overwrite the same line).
        - Updates the stored previous message to the current one for next overwrite.
        
        Args:
            message (str): The message to print.
        """
        if self.__verbose:
            print(' ' * len(self.__previous_message), end='\r')
            print(message, end='\r')
            self.__previous_message = message
        
    def __combine_labelled_segment_masks(self):
        """
        Merge all labelled segment masks into a single composite mask.
        
        Behavior:
        - Defines a helper `merge()` function that overlays one mask onto another by copying all
          labelled pixels (non-255) from the first mask onto the second mask at the same locations.
          This prioritizes earlier masks in the sequence.
        - Applies `reduce(merge, masks)` to combine all segment masks into one.
        - Converts the combined mask to `uint8`.
        - If no masks are present, returns an array filled with 255 (void label) matching the original image shape.
        - Note: The method assumes that label value 255 represents void/unlabeled areas.
        
        Returns:
            np.ndarray: A uint8 numpy array representing the combined labelled segment mask, where
                        each pixel's value corresponds to the label or 255 for void.
        """
        def merge(mask_a, mask_b):
            annotated_portion_in_mask_a = mask_a != 255
            annotated_indices_in_mask_a = np.where(annotated_portion_in_mask_a)
            mask_b[annotated_indices_in_mask_a] = mask_a[annotated_indices_in_mask_a]
            return mask_b
        
        if self.labelled_segment_masks.size:
            masks = self.labelled_segment_masks.copy()
            combined_masks = reduce(merge, masks).astype('uint8')
            return combined_masks
        return np.zeros(self.__original_array_shape, 'uint8') + 255
    
    def __resize_user_interface_update_routine(self):
        """
        Handle window resize events by rescaling images and updating all related annotation layers.
        
        This routine performs the following steps:
        - Reloads and rescales the main image to fit the new window size.
        - Retraces existing annotations to align with the resized image.
        - Updates the drawing and pen tracer overlays to maintain correct appearance.
        - Combines all layers and refreshes the displayed image.
        - Updates label display elements to reflect the resized interface.
        - Adjusts the pen size proportionally to the new scale.
        - Resets the internal resize flag to indicate completion.
        """
        self.__reload_image()
        self.__retrace_annotations()
        self.__update_drawing_overlay()
        self.__update_pen_tracer_overlay()
        self.__combine_layers_and_update_image_display()
        self.__update_label_displays()
        self.__resize_pen()
        self.__resize_flag = False
        
    def __annotate_user_interface_update_routine(self):
        """
        Update the user interface to reflect changes in annotations.
        
        This routine:
        - Retraces existing annotations to ensure they are up to date.
        - Combines annotation layers and updates the displayed image accordingly.
        - Refreshes the contents of label display elements to match the current annotation state.
        """
        self.__retrace_annotations()
        self.__combine_layers_and_update_image_display()
        self.__update_contents_of_label_displays()
        
    def __reload_image(self):
        """
        Reload the current image from the stored image file path.
        
        This method refreshes the image by reassigning the `image_filepath` property,
        triggering any associated loading and processing logic.
        """
        self.image_filepath = self.image_filepath
        
    def __retrace_annotations(self):
        """
        Redraw annotations on the overlay based on the current annotation mode.
        
        Behavior:
        - Clears the current annotation overlay.
        - If using bounding boxes (and not semantic segments), retraces bounding boxes.
        - Otherwise, retraces semantic segment annotations.
        """
        self.annotation_overlay = None
        if self.use_bounding_boxes and not self.use_semantic_segments:
            self.__trace_bounding_boxes()
        else:
            self.__trace_segments()
            
    def __trace_bounding_boxes(self):
        """
        Draw bounding boxes and optionally corner labels on the annotation overlay.
        
        Behavior:
        - Initializes QPainter with the current annotation overlay.
        - Sets pen and brush styles based on the annotation pen properties.
        - Adjusts pen width relative to the minimum pen width for consistent scaling.
        - If `corner_label_attached_to_bounding_box` is True:
            - Sets the font size scaled by the current image scale factor.
            - Draws a filled rectangle near the bounding box corner displaying the label text.
            - Uses label color as background and white for the text for contrast.
        - For each bounding box:
            - Extracts the label index and bounding box dimensions.
            - Scales the bounding box coordinates according to the current scale factor.
            - Draws the bounding box rectangle with the corresponding label color.
            - Optionally draws the label text box in the top-left corner of the bounding box.
        """
        painter, pen, brush = QPainter(self.annotation_overlay), QPen(self.__annotation_pen), QBrush(Qt.Dense7Pattern)
        pen.setWidthF(self.__annotation_pen.widthF() / self.__minimum_pen_width)
        if self.corner_label_attached_to_bounding_box:
            font_size = int(self.__label_font_size * self.__scale_factor)
            font = QFont('Arial', font_size)
            painter.setFont(font)
        
        for bounding_box in self.bounding_boxes:
            label_index, dimensions = bounding_box[0], bounding_box[1:]
            dimensions = np.int32(dimensions * self.__scale_factor)
            color = self.label_colors[label_index]
            pen.setColor(color); brush.setColor(color)
            painter.setPen(pen); painter.setBrush(brush)
            painter.drawRect(QRect(*dimensions))
            if self.corner_label_attached_to_bounding_box:
                x_offset, y_offset = dimensions[:2]
                text = f'Label: {self.labels[label_index]}'
                font_metrics = painter.fontMetrics()
                text_width, text_height = round(font_metrics.horizontalAdvance(text) * 1.2), font_metrics.height()
                text_box = QRect(x_offset, y_offset, text_width, text_height)
                painter.fillRect(text_box, self.label_colors[label_index])
                pen.setColor(Qt.white); painter.setPen(pen)
                x_text, y_text = [x_offset, y_offset] + np.int32([0.08 * text_width, 0.77 * text_height])
                painter.drawText(x_text, y_text, text)
    
    def __trace_segments(self):
        """
        Render the semantic segmentation overlay using label colors and opacity.
    
        - Prepares an RGBA lookup table based on label colors and global opacity.
        - Resizes the overall segment mask to match the current widget dimensions.
        - Maps each pixel in the mask to its RGBA color using the lookup table.
        - Converts the resulting RGBA image to a QPixmap and stores it as the annotation overlay.
        """
        def prepare_rgba_lookup_table():
            alpha = int(self.__opacity * 255)
            get_rgb_channels = lambda color: [color.red(), color.green(), color.blue()]
            lookup_table = np.zeros([256, 4], 'uint8')
            lookup_table_modification = np.uint8([get_rgb_channels(color) + [alpha] for color in self.label_colors])
            lookup_table[:self.n_labels] += lookup_table_modification
            return lookup_table
        
        current_array_shape = self.height(), self.width()
        scaled_overall_segment_mask = resize(self.overall_segment_mask, current_array_shape, 0)
        lookup_table = prepare_rgba_lookup_table()
        rgba_array = lookup_table[scaled_overall_segment_mask]
        self.annotation_overlay = rgba_array_to_pixmap(rgba_array)
    
    def __combine_layers_and_update_image_display(self):
        """
        Composite the image with annotation, drawing, and pen tracer overlays, then update the display.
        
        - Stacks the base image with the annotation overlay (segmentation or boxes).
        - Includes the drawing overlay and pen tracer if they exist.
        - Updates the QLabel display with the final composited image.
        """
        compound_layer = QPixmap(self.image)
        painter = QPainter(compound_layer)
        painter.drawPixmap(0, 0, self.annotation_overlay)
        if hasattr(self, f'_{self.__class__.__name__}__drawing_overlay'):
            painter.drawPixmap(0, 0, self.drawing_overlay)
        if hasattr(self, f'_{self.__class__.__name__}__pen_tracer_overlay'):
            painter.drawPixmap(0, 0, self.pen_tracer_overlay)
        painter.end()
        self.__image_display.setPixmap(compound_layer)
        
    @property
    def drawing_overlay(self):
        """
        Get the overlay layer used for live drawing annotations.
        
        Returns:
            QPixmap: The current drawing overlay.
        """
        return self.__drawing_overlay
        
    @property
    def pen_tracer_overlay(self):
        """
        Get the overlay that visually traces the pen cursor during interaction.
        
        Returns:
            QPixmap: The pen tracer overlay used for previewing pen position and size.
        """
        return self.__pen_tracer_overlay
        
    def __get_mask_for_annotations_hovered_over(self):
        
        """
        Compute a boolean mask indicating which annotations are currently hovered over by the cursor.
        
        - For bounding boxes enabled (and not semantic segments): checks if the cursor lies within each box.
        - For segment masks: checks if the cursor overlaps with any non-background pixel in the masks.
        - Chooses logic based on whether bounding boxes or semantic segments are in use.
        
        Returns:
            np.ndarray: A boolean array where True indicates the annotation is under the cursor.
        
        Notes:
            - The method returns a boolean array where `True` indicates that the annotation is hovered over, and `False` otherwise.
            - If no annotations are present or the cursor is not hovering over any annotation, the returned mask will be all `False`.
        """
        annotation_hover_mask_shape = self.bounding_boxes.shape[0] if self.use_bounding_boxes and not self.use_semantic_segments else self.labelled_segment_masks.shape[0]
        annotation_hover_mask = np.zeros(annotation_hover_mask_shape, bool)
        annotations_exist = bool(annotation_hover_mask.size)
        if annotations_exist:
            y_cursor, x_cursor = self.__yx_cursor_within_original_image
            if self.use_bounding_boxes and not self.use_semantic_segments:
                for index, (_, x_offset, y_offset, width, height) in enumerate(self.bounding_boxes):
                    annotation_hover_mask[index] = \
                        y_offset <= y_cursor <= y_offset + height and \
                        x_offset <= x_cursor <= x_offset + width
            else:
                annotation_hover_mask = self.labelled_segment_masks[:, y_cursor, x_cursor] != 255
        return annotation_hover_mask
    
    def __get_mask_for_smallest_annotation_hovered_over(self):
        """
        Identify the smallest annotation currently hovered over by the cursor.
        
        - If only one annotation is hovered, returns that directly.
        - For multiple hovered annotations:
            - Computes area of each bounding box (if semantic segments are not enabled) or segment.
            - Selects the one with the smallest area.
            - Returns a boolean mask selecting only that annotation.
        
        Returns:
            np.ndarray: A boolean mask where only the smallest hovered annotation is marked True.
            
        Notes:
            - The method compares annotations based on their area and returns a mask for the smallest one.
            - If no valid annotation is found under the cursor, it returns an empty mask.
        """
        annotation_hover_mask = self.__get_mask_for_annotations_hovered_over()
        if annotation_hover_mask.sum() < 2:
            return annotation_hover_mask
        annotations = self.bounding_boxes if self.use_bounding_boxes and not self.use_semantic_segments else self.labelled_segment_masks
        annotations_to_inspect = annotations[annotation_hover_mask]
        if self.use_bounding_boxes and not self.use_semantic_segments:
            areas = np.prod(annotations_to_inspect[:,-2:], axis=1)
        else:
            areas = compute_segment_areas(annotations_to_inspect)
        index_of_interest = np.argmin(areas)
        smallest_annotation_hover_mask = (annotations == annotations_to_inspect[index_of_interest]).all(axis=1 if self.use_bounding_boxes and not self.use_semantic_segments else (1,2))
        return smallest_annotation_hover_mask
    
    def __drop_smallest_annotation_hovered_over(self):
        """
        Remove the smallest annotation currently under the cursor.
        
        - Uses the smallest hovered annotation mask to identify the target.
        - Removes it from either the bounding box list or segmentation mask array, or both.
        - Skips removal if no hovered annotation is found.
        
        Returns:
            bool: True if an annotation was removed, False otherwise.
            
        Notes:
            - The method checks for the smallest annotation under the cursor and removes it based on the current configuration (bounding boxes or segment masks or both).
            - The method returns `True` if an annotation was removed, and `False` if no annotation was found or removed.
        """
        smallest_annotation_hover_mask = self.__get_mask_for_smallest_annotation_hovered_over()
        if smallest_annotation_hover_mask.any():
            if self.use_bounding_boxes:
                self.__bounding_boxes = self.bounding_boxes[~smallest_annotation_hover_mask]
            if self.use_semantic_segments:
                self.labelled_segment_masks = self.labelled_segment_masks[~smallest_annotation_hover_mask]
            return True
        return False
    
    def __get_label_index_hovered_over(self):
        """
        Get the label index of the smallest annotation currently under the cursor.
        
        - For bounding boxes are enabled (and not semantic segments): returns the label index of the hovered box.
        - For segments: returns the label index of the hovered mask (excluding background 255).
        - Returns -1 if no annotation is hovered.
        
        Returns:
            int: Index of the hovered label, or -1 if none is detected.
        """
        smallest_annotation_hover_mask = self.__get_mask_for_smallest_annotation_hovered_over()
        if smallest_annotation_hover_mask.any():
            if self.use_bounding_boxes and not self.use_semantic_segments:
                smallest_annotation_hovered_over = self.bounding_boxes[smallest_annotation_hover_mask].squeeze()
                return smallest_annotation_hovered_over[0]
            else:
                smallest_annotation_hovered_over = self.labelled_segment_masks[smallest_annotation_hover_mask].squeeze()
                annotated_portion = smallest_annotation_hovered_over != 255
                return np.unique(smallest_annotation_hovered_over[annotated_portion])[0]
        return -1
    
    def __clear_annotations(self):
        """
        Remove all current annotations from the scene.
        
        - Clears bounding boxes if enabled.
        - Clears semantic segment masks if enabled.
        """
        if self.use_bounding_boxes:
            self.__bounding_boxes = np.empty([0, 5], 'int32')
            
        if self.use_semantic_segments:
            self.labelled_segment_masks = np.empty([0] + self.__original_array_shape, 'int32')
        
    def __draw(self, current_position:QPoint, mode:str):
        """
        Draw a point or line on the drawing overlay at the specified position.
        
        - In 'point' mode, draws a dot at the given position.
        - In 'line' mode, draws a line from the last recorded pen position.
        - If erasing mode is active, draws with transparency to clear annotations.
        
        Args:
            current_position (QPoint): The current cursor position on the widget.
            mode (str): Drawing mode, either 'point' or 'line'.
        
        Raises:
            ValueError: If mode is not 'point' or 'line'.
        """
        if mode not in {'point', 'line'}:
            raise ValueError("The argument `mode` can either take the value of 'point' or 'line'.")
        
        painter = QPainter(self.drawing_overlay)
        if self.erasing:
            self.__annotation_pen.setColor(Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
        else:
            self.__annotation_pen.setColor(self.label_to_annotate_color)
        painter.setPen(self.__annotation_pen)
        
        if mode == 'point' or self.__last_pen_position is None:
            painter.drawPoint(current_position)
        else:
            painter.drawLine(self.__last_pen_position, current_position)
        painter.end()
        
    def __configure_label_display(self, label_display:QLabel, label_index:int, hovering:bool):
        """
        Configure the QLabel to show the current label text and background color.
        
        - If label_index is invalid (< 0) or erasing mode is active without hovering,
          sets the label text to 'N/A' and background to transparent.
        - Otherwise, sets the label text and background color according to the label index.
        - Aligns the label text padding based on the maximum label length for consistent display.
        
        Args:
            label_display (QLabel): The QLabel widget to update.
            label_index (int): The index of the label to display.
            hovering (bool): Whether the user is hovering over the label.
        """
        if label_index < 0 or (self.erasing and not hovering):
            text = 'N/A'
            background_color = 'transparent'
        else:
            text = self.labels[label_index]
            background_color = self.label_colors[label_index].name()
        maximum_text_length = max(map(len, self.labels + ['N/A']))
        label_display.setText(f'Label: {text:<{maximum_text_length}}')
        label_display.setStyleSheet(f'background: {background_color}; border: 1px solid black; padding: 2px;')
        
    def __update_positions_of_label_displays(self):
        """
        Update the screen positions of the floating label display widgets.
        
        - If there is a recorded last pen position and floating labels are enabled,
          positions the label displays near the pen cursor with predefined offsets.
        - Otherwise, positions the labels at the top-right corner of the widget,
          aligning them vertically stacked.
        - Moves both `__label_to_annotate_display` and `__label_annotated_display`
          widgets to their calculated coordinates.
        """
        if self.__last_pen_position and self.is_floating_label:
            x_offset = self.__last_pen_position.x() + self.__floating_label_display_offsets[0]
            y_offset = self.__last_pen_position.y() + self.__floating_label_display_offsets[1]
        else:
            x_offset = self.width() - max(self.__label_to_annotate_display.width(), self.__label_annotated_display.width())
            y_offset = 0
        self.__label_to_annotate_display.move(x_offset, y_offset)
        self.__label_annotated_display.move(x_offset, y_offset + self.__label_to_annotate_display.height())
        
    def __update_contents_of_label_displays(self):
        """
        Update the text and appearance of label display widgets.
        
        - Determines the label index currently hovered over by the cursor.
        - Configures the label-to-annotate display using the active label index.
        - Configures the annotated label display using the hovered label index.
        - On first update, synchronizes the widths of both label displays for consistent UI appearance.
        
        Notes:
            This method ensures that label displays show the correct label text and styling 
            based on user interaction (hover and active annotation label).
        """
        self.__label_index_hovered_over = self.__get_label_index_hovered_over()
        self.__configure_label_display(self.__label_to_annotate_display, self.label_index_to_annotate, False)
        self.__configure_label_display(self.__label_annotated_display, self.__label_index_hovered_over, True)
        
        self.__label_to_annotate_display.adjustSize()
        self.__label_annotated_display.adjustSize()
        
        font_metrics = QFontMetrics(self.__label_to_annotate_display.font())
        text_to_annotate_width = font_metrics.horizontalAdvance(self.__label_to_annotate_display.text())
        text_annotated_width = font_metrics.horizontalAdvance(self.__label_annotated_display.text())
        common_text_width = max(text_to_annotate_width, text_annotated_width)
        common_text_height = font_metrics.height()
        margins = self.__label_to_annotate_display.contentsMargins()
        common_text_width += (margins.left() + margins.right()) * 2
        common_text_height += (margins.top() + margins.bottom()) * 1
        
        self.__label_to_annotate_display.setFixedSize(common_text_width, common_text_height)
        self.__label_annotated_display.setFixedSize(common_text_width, common_text_height)
            
    def __update_label_displays(self):
        """
        Refresh label display positions and contents.
        
        - Updates the position of label display widgets relative to the current pen position or widget size.
        - Updates the displayed text and styling of label widgets to reflect current annotation and hover states.
        
        This method ensures the label UI is kept in sync with user interaction and layout changes.
        """
        self.__update_positions_of_label_displays()
        self.__update_contents_of_label_displays()
            
    def __reconfigure_label_annotated_display(self):
        """
        Update the annotated label display based on the current hover state.
        
        - Retrieves the label index currently hovered over by the user.
        - Configures the annotated label display widget with the hovered label's text and color.
        
        This ensures that the label display dynamically reflects user interaction.
        """
        self.__label_index_hovered_over = self.__get_label_index_hovered_over()
        self.__configure_label_display(self.__label_annotated_display, self.__label_index_hovered_over, True)
    
    def __resize_pen(self):
        """
        Adjust the annotation pen width dynamically based on the widget's current width.
        
        - Computes the ratio of the current widget width to its minimum width.
        - Scales the pen width by this ratio, the minimum pen width, and the current pen width multiplier.
        - Updates the internal annotation pen's width accordingly for consistent drawing thickness.
        
        This method ensures the pen thickness scales appropriately during window resizing or zooming.
        """
        widget_minimum_width = self.minimumWidth()
        if widget_minimum_width:
            ratio = self.width() / widget_minimum_width
            self.__annotation_pen.setWidthF(ratio * self.__minimum_pen_width * self.pen_width_multiplier)
    
    def resizeEvent(self, event):
        """
        Handle the widget resize event.
        
        - Sets a flag indicating that a resize is currently occurring to omit the possibility of IndexError if the cursor hovers outside the image (QPixmap) awaiting to be resized.
        - If the minimum widget size hasn't been set yet, sets it to the current size to prevent shrinking below this size.
        - Resizes the internal image display widget to match the new size.
        - Starts a timer (`__resize_scheduler`) to delay handling of the resize, allowing batch processing after resizing is complete.
        - Accepts the event to mark it as handled.
        
        Args:
            event (QResizeEvent): The resize event containing size change information.
        """
        self.__resize_flag = True
        if not self.__minimum_widget_size_set:
            self.setMinimumSize(self.size())
            self.__minimum_widget_size_set = True
        self.__image_display.resize(self.size())
        self.__resize_scheduler.start(self.RESIZE_DELAY)
        event.accept()
    
    def wheelEvent(self, event):
        """
        Handle mouse wheel scrolling to adjust label selection or pen width.
        
        - If currently in erasing mode and the label slider is enabled, disables the label slider.
        - Reads the vertical scroll delta from the event.
        - If the label slider is enabled:
            - Adjusts the label index accumulator by a fixed sensitivity step in the scroll direction.
        - Otherwise:
            - Adjusts the pen width multiplier accumulator similarly.
        - Updates the pen tracer overlay and refreshes the combined image display.
        - Updates the label display contents to reflect changes.
        
        Args:
            event (QWheelEvent): The wheel event with scrolling information.
        """
        if self.erasing and self.__label_slider_enabled:
                self.__label_slider_enabled = False
        delta = event.angleDelta().y()
        if self.__label_slider_enabled:
            delta = self.__label_slider_sensitivity * np.sign(delta)
            self.label_index_accumulator += delta
        else:
            delta = self.__pen_width_slider_sensitivity * np.sign(delta)
            self.pen_width_multiplier_accumulator += delta
        self.__update_pen_tracer_overlay()
        self.__combine_layers_and_update_image_display()
        self.__update_contents_of_label_displays()
    
    def mousePressEvent(self, event):
        """
        Handle mouse button press events for annotation and mode toggling.
        
        Behavior:
        - Updates the cursor position relative to the original image coordinates.
        - Left-click:
            - If erasing mode is active, attempts to remove the smallest annotation under the cursor,
              retraces annotations, and updates the label display. Optionally autosaves changes.
            - Draws a point at the cursor position on the drawing overlay.
            - Refreshes the combined image display.
        - Right-click:
            - Toggles erasing mode on/off.
            - Enables label slider mode.
            - Updates pen tracer overlay and combined image display.
            - Updates label display contents.
        - Middle-click:
            - Toggles label slider mode on/off.
            - Updates pen tracer overlay and combined image display.
        
        Args:
            event (QMouseEvent): The mouse press event containing button and position info.
        """
        self.__update_yx_cursor_within_original_image(event.pos())
        if event.button() == Qt.LeftButton:
            if self.erasing:
                updated = self.__drop_smallest_annotation_hovered_over()
                self.__retrace_annotations()
                if updated:
                    self.__reconfigure_label_annotated_display()
                    if self.__autosave:
                        self.save()
            self.__draw(event.pos(), 'point')
            self.__combine_layers_and_update_image_display()
        elif event.button() == Qt.RightButton:
            self.__erasing ^= True
            self.__label_slider_enabled = True
            self.__update_pen_tracer_overlay()
            self.__combine_layers_and_update_image_display()
            self.__update_contents_of_label_displays()
        elif event.button() == Qt.MiddleButton:
            self.__label_slider_enabled ^= True
            self.__update_pen_tracer_overlay()
            self.__combine_layers_and_update_image_display()
            
    def __update_drawing_overlay(self):
        """
        Update the drawing overlay by scaling it to match the current image size.
        
        Behavior:
        - If the drawing overlay already exists, it is scaled to the image size while maintaining aspect ratio,
          using fast transformation for performance.
        - If the drawing overlay does not exist, it is initialized fresh.
        
        Notes:
        - Uses a class-private attribute check to determine overlay existence.
        """
        if hasattr(self, f'_{self.__class__.__name__}__drawing_overlay'):
            self.__drawing_overlay = self.drawing_overlay.scaled(self.image.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
        else:
            self.initialize_overlay('drawing')
            
    def __update_pen_tracer_overlay(self):
        """
        Update the pen tracer overlay to show the current pen position and size.
    
        Behavior:
        - If no last pen position is recorded, the method returns early.
        - Initializes the 'pen_tracer' overlay as a transparent QPixmap matching the image size.
        - Creates a QPainter on the pen tracer overlay.
        - Sets the pen color:
            - Black if label slider is enabled or erasing mode is active.
            - Otherwise, uses the color of the current label to annotate.
        - Calculates an ellipse size based on the annotation pen width, scaled by pen width multiplier and UI scale factor.
        - Draws an ellipse centered at the last pen position with the computed width.
        - Ends the QPainter.
    
        Notes:
        - The ellipse visually indicates the pen tip size and position on the annotation widget.
        """
        if self.__last_pen_position is None:
            return
        self.initialize_overlay('pen_tracer')
        painter = QPainter(self.pen_tracer_overlay)
        if self.__label_slider_enabled or self.__erasing:
            pen = QPen(Qt.black, 1)
        else:
            pen = QPen(self.label_colors[self.label_index_to_annotate], 1)
        painter.setPen(pen)
        pen_width = self.__annotation_pen.widthF()
        width = pen_width - 6 * self.pen_width_multiplier * self.__scale_factor
        painter.drawEllipse(self.__last_pen_position, width, width)
        painter.end()
        
    def initialize_overlay(self, overlay_name:str):
        """
        Initialize a transparent QPixmap overlay for annotation layers.
        
        Args:
            overlay_name (str): The name of the overlay to initialize. 
                Must be one of: 'drawing', 'annotation', or 'pen_tracer'.
        
        Raises:
            ValueError: If `overlay_name` is not one of the allowed strings.
        
        Behavior:
            - Creates a new QPixmap matching the current image size.
            - Fills the QPixmap with a transparent background.
            - Assigns it to a private attribute named `__{overlay_name}_overlay`.
        """
        if overlay_name not in {'drawing', 'annotation', 'pen_tracer'}:
            raise ValueError("`overlay_name` should either be 'drawing', 'annotation', or 'pen_tracer'")
        attribute_name = f'_{self.__class__.__name__}__{overlay_name}_overlay'
        self.__dict__[attribute_name] = QPixmap(self.image.size())
        self.__dict__[attribute_name].fill(Qt.transparent)
        
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events for drawing and erasing annotations.
        
        Behavior:
        - If the widget is currently resizing (`__resize_flag`), ignores the event.
        - Updates the cursor position relative to the original image.
        - If the left mouse button is pressed:
            - Draws a line from the last pen position to the current position.
            - If in erasing mode, attempts to remove the smallest annotation hovered over,
              retraces annotations, and autosaves if enabled.
        - If the left button is not pressed, updates the label display contents.
        - Updates the last pen position to the current position.
        - Updates the pen tracer overlay.
        - Combines all layers and refreshes the image display.
        - Updates the positions of the label display widgets.
        
        Args:
            event (QMouseEvent): The mouse move event containing position and button state.
        
        Note: It is very necessary to apply this routine while the application is not resizing. Otherwise, an IndexError 
        exception could later occur due to the cursor (`self.__yx_cursor_within_original_image`) being mapped to outside 
        the bounds of the original image.
        """
        if self.__resize_flag:
            return
        current_pen_position = event.pos()
        self.__update_yx_cursor_within_original_image(current_pen_position)
        if event.buttons() & Qt.LeftButton:
            self.__draw(current_pen_position, 'line')
            if self.erasing:
                updated = self.__drop_smallest_annotation_hovered_over()
                if updated:
                    self.__retrace_annotations()
                    if self.__autosave:
                        self.save()
        else:
            self.__update_contents_of_label_displays()
        self.last_pen_position = current_pen_position
        self.__update_pen_tracer_overlay()
        self.__combine_layers_and_update_image_display()
        self.__update_positions_of_label_displays()
        
    def __update_yx_cursor_within_original_image(self, position:QPoint):
        """
        Update the cursor coordinates relative to the original image resolution.
        
        Behavior:
        - Converts the given widget position (QPoint) to image coordinates by scaling down
          according to the current scale factor.
        - Stores the result as a tuple (y, x) to match image coordinate conventions.
        - If position is None, resets cursor coordinates to (0, 0).
        
        Args:
            position (QPoint | None): The current cursor position on the widget, or None.
        """
        if position is None:
            self.__yx_cursor_within_original_image = (0, 0)
        else:
            self.__yx_cursor_within_original_image = (np.array([position.y(), position.x()]) / self.__scale_factor).astype(int)
        
    def mouseDoubleClickEvent(self, event):
        """
        Handle double-click mouse events for annotation clearing or adding new annotations.
        
        Behavior:
        - Right double-click:
            - Prompts the user with a warning dialog to confirm clearing all annotations.
            - If confirmed, clears all annotations and resets erasing mode.
        - Left double-click (when not erasing):
            - Performs a flood fill from the clicked position on the drawing overlay to find connected annotated pixels.
            - If using bounding boxes:
                - Converts the flood-filled mask to a bounding box, scales it to original image coordinates.
                - Adds the new bounding box if it passes size thresholds.
                - Cleans up overlapping bounding boxes based on configured thresholds.
            - If using semantic segmentation:
                - Resizes the flood-filled mask to original image size.
                - Applies hole filling and label replacement to create a labelled segment mask.
                - Prepends the new segment mask to the existing labelled masks.
        - After any update:
            - Clears the drawing overlay.
            - Updates the annotation UI.
            - Autosaves if enabled.
        
        Args:
            event (QMouseEvent): The double-click mouse event.
        """
        updated = False
        if event.button() == Qt.RightButton:
            response = QMessageBox.warning(self, 'Clear Drawing?', 'You are about to clear your annotations for this image!', QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if response == QMessageBox.Ok:
                self.__clear_annotations()
                self.__erasing = False
                updated = True
        elif event.button() == Qt.LeftButton and not self.erasing:
            yx_root = event.y(), event.x()
            rgba_array = pixmap_to_rgba_array(self.drawing_overlay)
            rgb_array = rgba_array[:,:,:-1]
            traversed_pixels_mask = locate_all_pixels_via_floodfill(rgb_array, yx_root)
            if self.use_bounding_boxes:
                bounding_box = mask_to_bounding_box(traversed_pixels_mask)
                x_offset, y_offset, width, height = (bounding_box / self.__scale_factor).astype('int32').tolist()
                minimum_side_length, maximum_side_length = min(width, height), max(width, height)
                lower_side_length_bound, upper_side_length_bound = self.__bounding_box_side_length_thresholds
                if (lower_side_length_bound <= minimum_side_length and maximum_side_length <= upper_side_length_bound) or self.use_semantic_segments:
                    self.__bounding_boxes = np.concatenate([
                        self.bounding_boxes,
                        np.array([self.label_index_to_annotate, x_offset, y_offset, width, height])[np.newaxis, ...]
                    ])
                if not self.use_semantic_segments:
                    boxes_to_remove_mask = detect_overlapping_boxes_to_clean(self.bounding_boxes, self.__overlap_vs_smallest_area_threshold, self.__overlap_vs_union_area_threshold)
                    self.__bounding_boxes = self.bounding_boxes[~boxes_to_remove_mask]
            if self.use_semantic_segments:
                segment_mask = resize(traversed_pixels_mask, self.__original_array_shape, 0)
                segment_mask = binary_fill_holes(segment_mask).astype(int)
                labelled_segment_mask = apply_lut_replacement(segment_mask, self.label_index_to_annotate)
                self.labelled_segment_masks = np.concatenate([labelled_segment_mask[np.newaxis, ...], self.labelled_segment_masks])
            updated = True
        if updated:
            self.drawing_overlay.fill(Qt.transparent)
            self.__annotate_user_interface_update_routine()
            if self.__autosave:
                self.save()
                
    def trace_bounds_around_segments(self):
        """
        Detects 1-pixel-wide boundaries around segments using Canny edge detection.
    
        Behavior:
        - Applies the Canny edge detector with low and high thresholds set to 0 and 1, respectively.
        - Operates on `self.overall_segment_mask` (a 2D `uint8` array).
        - Identifies the boundary pixels between segmented regions.
        - Returns the indices of the detected boundary pixels.
    
        Returns:
            tuple(np.ndarray): A tuple (row_indices, col_indices) representing the coordinates
                                 of the boundary pixels.
        """
        overall_mask = self.overall_segment_mask.copy()
        bound_indices = np.where(canny(overall_mask, low_threshold=0, high_threshold=1))
        return bound_indices
                
    def postprocess_overall_segment_mask_for_saving(self):
        """
        Prepares the overall segmentation mask for saving by applying label shifting and boundary tracing.
        
        Behavior:
        - If `void_background` is False:
            - Increments all label values by 1, turning background (255) into 0 and shifting segment labels.
        - If `void_background` is True:
            - Leaves label values unchanged (255 remains as void).
        - Detects boundaries between segments and sets those boundary pixels to 255 (void label).
        
        Returns:
            np.ndarray: The final segmentation mask array with boundaries marked and label values adjusted,
                        suitable for saving as a PNG.
        """
        overall_segment_mask_to_save = self.overall_segment_mask + (not self.void_background)
        bound_indices = self.trace_bounds_around_segments()
        overall_segment_mask_to_save[bound_indices] = 255
        return overall_segment_mask_to_save