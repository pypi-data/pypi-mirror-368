""" 
Tadqeeq - Image Annotator Tool
An interactive image annotation tool for efficient labeling.
Developed by Mohamed Behery @ RTR Software Development (2025-04-27).
Licensed under the MIT License.
"""

import numpy as np
from PyQt5.QtGui import QPixmap, QImage
from collections import deque
from itertools import combinations
import os

class EmptyDatasetError(FileNotFoundError):
    def __init__(self, message=''):
        super().__init__(message)

def compute_segment_areas(labelled_segment_masks):
    """
    Compute the pixel area of each individual mask in a stack of labelled segment masks.
    
    This function calculates the area (in terms of pixel count) for each segment in 
    a stack of labelled segment masks, where each mask represents a segment with a 
    specific label. The mask values are assumed to be labelled with integer values, 
    and 255 is considered as background or empty pixels.
    
    Args:
        labelled_segment_masks (np.ndarray): A 3D numpy array where each slice (along 
                                              the first axis) represents a binary mask 
                                              of a segment. The masks have pixel values 
                                              for the segmented regions, with 255 as background.
    
    Returns:
        np.ndarray: A 1D numpy array where each element represents the area (number of 
                    pixels) of the corresponding segment in the stack of labelled segment masks.
    
    Example:
        labelled_segment_masks = np.array([[[255, 0, 255], [0, 0, 255]], [[0, 0, 255], [255, 0, 0]]])
        areas = compute_segment_areas(labelled_segment_masks)
        # areas will contain the total pixel area of each segment
    """
    binary_segment_masks = np.empty_like(labelled_segment_masks)
    labelled_portions = labelled_segment_masks != 255
    binary_segment_masks[labelled_portions] = 1
    binary_segment_masks[~labelled_portions] = 0
    areas = np.sum(binary_segment_masks, axis=(1,2))
    return areas

def rgba_array_to_pixmap(rgba_array):
    """
    Convert a 4-channel RGBA numpy array to a QPixmap.
    
    This function takes a numpy array with RGBA values (4 channels) and converts it to a 
    QPixmap, which is a format suitable for use in Qt-based GUI applications.
    
    Args:
        rgba_array (np.ndarray): A 3D numpy array with shape (height, width, 4), 
                                  where the third dimension represents the RGBA channels.
    
    Returns:
        QPixmap: A QPixmap object created from the input RGBA array.
    
    Example:
        rgba_array = np.random.randint(0, 255, (100, 100, 4), dtype=np.uint8)
        pixmap = Helper.rgba_array_to_pixmap(rgba_array)
        # 'pixmap' can now be used in a Qt GUI for rendering
    """
    height, width = rgba_array.shape[:2]
    image = QImage(rgba_array.data, width, height, 4 * width, QImage.Format_RGBA8888)
    drawing = QPixmap.fromImage(image)
    return drawing

def apply_lut_replacement(segment_mask:np.ndarray, label_index:np.uint8):
    """
    Apply a label replacement to a segment mask using a lookup table (LUT).
    
    This function replaces the values in the `segment_mask` array based on a lookup table 
    where each value in the mask corresponds to a label index. The segment mask is updated
    to reflect the new label using the provided `label_index`.
    
    Args:
        segment_mask (np.ndarray): A 2D array representing a segment mask with integer values 
                                   that represent different segments or regions.
        label_index (np.uint8): The label index to replace the corresponding values in the 
                                `segment_mask` with.
    
    Returns:
        np.ndarray: A new mask where the values have been replaced by the corresponding label 
                    index using the lookup table.
    
    Example:
        segment_mask = np.array([[0, 1], [1, 0]])
        label_index = 5
        labelled_mask = Helper.apply_lut_replacement(segment_mask, label_index)
        # labelled_mask will contain the label_index (5) where applicable based on the LUT
    """
    lookup_table = np.uint8([255, label_index])
    labelled_mask = lookup_table[segment_mask]
    return labelled_mask

def detect_overlapping_boxes_to_clean(bounding_boxes:np.ndarray, overlap_vs_smallest_area_threshold:float, overlap_vs_union_area_threshold:float):
    """
    Identify bounding boxes that significantly overlap and should be removed.
    
    This function checks pairs of bounding boxes for significant overlap based on two criteria:
    - The overlap area compared to the smallest box area.
    - The overlap area compared to the union of both box areas.
    
    Bounding boxes that exceed either of the specified thresholds are considered for removal.
    The function returns a mask indicating which bounding boxes should be removed based on 
    the overlap criteria.
    
    Args:
        bounding_boxes (np.ndarray): A 2D array where each row represents a bounding box with 
                                      5 elements: [label_index, x_min, y_min, width, height].
        overlap_vs_smallest_area_threshold (float): The threshold for the ratio of overlap area 
                                                     to the smallest box area, above which the overlap 
                                                     is considered significant.
        overlap_vs_union_area_threshold (float): The threshold for the ratio of overlap area to the 
                                                  union of both box areas, above which the overlap is 
                                                  considered significant.
    
    Returns:
        np.ndarray: A boolean mask array indicating which bounding boxes should be removed. 
                    `True` means the corresponding bounding box is to be removed.
    
    Example:
        bounding_boxes = np.array([[0, 10, 10, 50, 50], [0, 20, 20, 50, 50], [1, 100, 100, 50, 50]])
        mask = Helper.detect_overlapping_boxes_to_clean(bounding_boxes, 0.5, 0.5)
        # mask will indicate which bounding boxes have significant overlap and should be removed
    """
    assert bounding_boxes.shape[1] == 5, '`bounding_boxes` arguments each should contain 5 columns.'
    box_pairs = combinations(bounding_boxes, 2)
    boxes_to_remove_mask = np.zeros(bounding_boxes.shape[0], bool)
    for box_a, box_b in box_pairs:
        overlap_area = compute_overlap_area(box_a[1:], box_b[1:])
        box_a_area, box_b_area = np.prod(box_a[-2:]), np.prod(box_b[-2:])
        overlap_vs_smallest_area = overlap_area / min(box_a_area, box_b_area)
        overlap_vs_union_area = overlap_area / (box_a_area + box_b_area - overlap_area)
        overlap_exceeds_threshold = (overlap_vs_smallest_area > overlap_vs_smallest_area_threshold) or (overlap_vs_union_area > overlap_vs_union_area_threshold)
        if overlap_exceeds_threshold:
            same_label = box_a[0] == box_b[0]
            if same_label:
                to_remove = box_a if box_b_area < box_a_area else box_b
            else:
                to_remove = box_a if box_a_area < box_b_area else box_b
            boxes_to_remove_mask |= np.all(bounding_boxes == to_remove, axis=1)
    return boxes_to_remove_mask

def compute_overlap_area(box_a:np.ndarray, box_b:np.ndarray):
    """
    Compute the intersection area between two bounding boxes.
    
    This function takes in two bounding boxes, each defined by four coordinates 
    (x_minimum, y_minimum, x_maximum, y_maximum), and computes the area of overlap 
    between them. The function assumes that the bounding boxes are axis-aligned.
    
    Args:
        box_a (np.ndarray): The first bounding box, an array with 4 elements 
                             representing (x_minimum, y_minimum, x_maximum, y_maximum).
        box_b (np.ndarray): The second bounding box, also an array with 4 elements 
                             representing (x_minimum, y_minimum, x_maximum, y_maximum).
    
    Returns:
        float: The area of intersection between the two bounding boxes. If there is no overlap, 
               the result will be 0.
    
    Raises:
        AssertionError: If either `box_a` or `box_b` does not have exactly 4 elements.
    
    Example:
        box_a = np.array([1, 1, 4, 4])
        box_b = np.array([2, 2, 5, 5])
        overlap_area = compute_overlap_area(box_a, box_b)
    """
    assert box_a.size == box_b.size == 4, '`box_a` and `box_b` arguments each should only contain 4 elements.'
    (x_minimum_a, y_minimum_a), x_maximum_a, y_maximum_a = box_a[:2], sum(box_a[::2]), sum(box_a[1::2])
    (x_minimum_b, y_minimum_b), x_maximum_b, y_maximum_b = box_b[:2], sum(box_b[::2]), sum(box_b[1::2])
    x_minimum, y_minimum = max(x_minimum_a, x_minimum_b), max(y_minimum_a, y_minimum_b)
    x_maximum, y_maximum = min(x_maximum_a, x_maximum_b), min(y_maximum_a, y_maximum_b)
    return max(0, x_maximum - x_minimum) * max(0, y_maximum - y_minimum)

def mask_to_bounding_box(traversed_pixels_mask):
    """
    Convert a binary mask to a bounding box (x, y, width, height).
    
    This function takes a binary mask, where traversed pixels are non-zero (usually `True` 
    or `1`), and computes the smallest axis-aligned bounding box that can contain all of 
    the non-zero pixels.
    
    Args:
        traversed_pixels_mask (np.ndarray): A binary mask array where non-zero elements 
                                             represent the "traversed" or relevant pixels.
    
    Returns:
        np.ndarray: An array representing the bounding box, in the format 
                    [x_minimum, y_minimum, width, height].
    
    Example:
        mask = np.array([[0, 1, 0], [1, 1, 0], [0, 0, 0]])
        bounding_box = mask_to_bounding_box(mask)
    """
    xy_pixels = np.column_stack(np.where(traversed_pixels_mask)[::-1]).squeeze()
    (x_minimum, y_minimum), (x_maximum, y_maximum) = xy_pixels.min(axis=0), xy_pixels.max(axis=0)
    bounding_box = np.array([x_minimum, y_minimum, x_maximum - x_minimum, y_maximum - y_minimum])
    return bounding_box

def pixmap_to_rgba_array(drawing:QPixmap):
    """
    Convert a QPixmap to an RGBA numpy array.
    
    This function converts a `QPixmap` to an RGBA array. The resulting array contains the 
    RGBA values (Red, Green, Blue, Alpha) of each pixel in the image. The conversion ensures 
    that each pixel is represented by 4 channels.
    
    Args:
        drawing (QPixmap): The `QPixmap` object to be converted.
    
    Returns:
        np.ndarray: A numpy array of shape (height, width, 4) where each element represents 
                    an RGBA value in uint8 format.
    
    Example:
        pixmap = QPixmap("image.png")
        rgba_array = pixmap_to_rgba_array(pixmap)
        
    Notes:
        - This method uses `rgba_array.copy()` to ensure the image array is properly packed
          in memory after converting from a `QPixmap`. This resolves a subtle issue in PyQt5
          where lazily evaluated NumPy arrays can lead to clipped or partially rendered 
          images during display or processing.
    """
    image = drawing.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    height, width = image.height(), image.width()
    buffer = image.bits(); buffer.setsize(height * width * 4)
    rgba_array = np.frombuffer(buffer, 'uint8').reshape((height, width, 4))
    rgba_array = rgba_array.copy() # Prevents mempery optimization to the `rgba_array`
    return rgba_array

def locate_all_pixels_via_floodfill(rgb_array:np.ndarray, yx_root:tuple):
    """
    Perform a flood fill to find all pixels connected to a starting pixel with the same RGB color.
    
    This function performs a flood fill algorithm starting from the pixel specified by `yx_root` 
    (given in (y, x) coordinates) in the provided RGB image array. It identifies all neighboring 
    pixels that have the same RGB color as the starting pixel and returns a mask of the connected 
    region.
    
    Args:
        rgb_array (np.ndarray): The RGB image array with shape (height, width, 3), where each 
                                 pixel contains RGB values.
        yx_root (tuple): A tuple representing the (y, x) coordinates of the starting pixel for the 
                         flood fill. This pixel's color is used as the reference for the flood fill.
                         
    Returns:
        np.ndarray: A boolean mask (2D array) of the same height and width as `rgb_array`, where 
                    `True` values indicate the pixels that are connected to the starting pixel and 
                    have the same RGB color.
                    
    Example:
        rgb_image = np.array([[[255, 0, 0], [255, 0, 0]], [[0, 255, 0], [255, 0, 0]]])
        mask = locate_all_pixels_via_floodfill(rgb_image, (0, 0))
        # mask will be a boolean array with True for the connected red pixels
    """
    def get_valid_neighbors(yx_pixel):
        is_valid = lambda yx_neighbor: 0 <= yx_neighbor[0] < rgb_array.shape[0] and 0 <= yx_neighbor[1] < rgb_array.shape[1] and matching_pixels_mask[*yx_neighbor]
        yx_neighbors = yx_pixel + np.array([(-1,0), (1,0), (0,-1), (0,1)])
        return filter(is_valid, yx_neighbors)
    
    matching_pixels_mask = (rgb_array == rgb_array[*yx_root]).all(axis=2)
    traversed_pixels_mask = np.zeros(rgb_array.shape[:2], bool)
    traversal_candidates = deque([yx_root])
    while traversal_candidates:
        yx_candidate = traversal_candidates.pop()
        if traversed_pixels_mask[*yx_candidate]:
            continue
        traversal_candidates.extendleft(get_valid_neighbors(yx_candidate))
        traversed_pixels_mask[*yx_candidate] = True
    return traversed_pixels_mask

def get_pixmap_compatible_image_filepaths(images_directory_path):
    """
    Retrieves a list of image file paths from a directory that are compatible with QPixmap.
    
    This method filters all files in the specified directory and returns those that:
    - Are regular files (not directories).
    - Have extensions supported by QPixmap (e.g., .png, .jpg, .bmp, etc.).
    
    The extension check is case-insensitive to ensure compatibility with uppercase/lowercase file names.
    
    Parameters:
        images_directory_path (str): The path to the directory containing image files.
    
    Returns:
        list of str: A list of absolute file paths to valid image files compatible with QPixmap.
    
    Raises:
        FileNotFoundError: If the specified directory does not exist.
    
    Example:
        images = Helper.get_pixmap_compatible_image_filepaths("/path/to/images/")
        for image_path in images:
            pixmap = QPixmap(image_path)
    """
    valid_extensions = {
        '.png', '.jpg', '.jpeg', '.bmp', '.gif',
        '.ppm', '.pgm', '.pbm', '.xbm', '.xpm'
    }
    filepaths = [os.path.join(images_directory_path, filename) for filename in os.listdir(images_directory_path)]
    check_filepath = lambda filepath: os.path.isfile(filepath) and os.path.splitext(filepath)[-1].lower() in valid_extensions
    valid_filepaths = list(filter(check_filepath, filepaths))
    return valid_filepaths