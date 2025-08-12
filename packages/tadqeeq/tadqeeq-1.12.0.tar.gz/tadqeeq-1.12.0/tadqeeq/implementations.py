""" 
Tadqeeq - Image Annotator Tool
An interactive image annotation tool for efficient labeling.
Developed by Mohamed Behery @ RTR Software Development (2025-04-27).
Licensed under the MIT License.
"""

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer
import os
from collections.abc import Iterable
from tadqeeq.widgets import ImageAnnotator
from tadqeeq.utils import get_pixmap_compatible_image_filepaths, EmptyDatasetError

class ImageAnnotatorWindow(QMainWindow):
    """
    A main application window for navigating and annotating a sequence of images using the ImageAnnotator widget.
    
    This window supports:
    - Image navigation via key bindings.
    - Automatic loading of bounding boxes and semantic segments (if paths are provided).
    - Autosizing to match the size of the annotator widget.
    - Managed overlay updates and autosave support.
    
    Args:
        images_directory_path (str): Directory containing image files to annotate.
        bounding_boxes_directory_path (str): Directory containing bounding box annotations (optional).
        semantic_segments_directory_path (str): Directory containing semantic segmentation masks (optional).
        image_navigation_keys (list): List of two Qt key codes to navigate images (default: [Qt.Key_A, Qt.Key_D]).
        **image_annotator_kwargs: Additional keyword arguments passed to the ImageAnnotator.
    """
    def __init__(self,
                 parent,
                 images_directory_path,
                 bounding_boxes_directory_path,
                 semantic_segments_directory_path,
                 image_navigation_keys=[Qt.Key_A, Qt.Key_D],
                 **image_annotator_kwargs):
        
        def initialize_image_filepaths():
            self.images_directory_path = images_directory_path
            
        def initialize_annotation_filepaths():
            self.bounding_boxes_directory_path = bounding_boxes_directory_path
            self.semantic_segments_directory_path = semantic_segments_directory_path
            
        def initialize_image_annotator_widget():
            self.__image_annotator_kwargs = image_annotator_kwargs
            self.image_index = 0
            self.__resize_user_interface_update_routine()
        
        def disable_maximize_button():
            self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        
        def configure_resize_scheduler():
            self.__resize_scheduler = QTimer(self)
            self.__resize_scheduler.setSingleShot(True)
            self.__resize_scheduler.timeout.connect(self.__resize_user_interface_update_routine)
        
        super().__init__(parent)
        
        initialize_image_filepaths()
        initialize_annotation_filepaths()
        initialize_image_annotator_widget()
        
        disable_maximize_button()
        configure_resize_scheduler()
        
        self.image_navigation_keys = image_navigation_keys
        
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setCentralWidget(self.__image_annotator)
        self.move_to_center_of_parent()
        
    def move_to_center_of_parent(self):
        parent = self.parent()
        if parent:
            parent_center = parent.frameGeometry().center()
        else:
            parent_center = QDesktopWidget().availableGeometry().center()
        frame = self.frameGeometry()
        frame.moveCenter(parent_center)
        self.move(frame.topLeft())
        
    @property
    def images_directory_path(self):
        """
        Get the directory path where the images are stored.
        
        Returns:
            str: Absolute path to the directory containing input images.
        """
        return self.__images_directory_path
    
    @images_directory_path.setter
    def images_directory_path(self, value:str):
        """
        Set the directory path where the images are stored.
        
        - Validates that the provided path is a directory.
        - Updates the list of image filepaths using Helper utility.
        
        Args:
            value (str): New directory path to be set.
        
        Raises:
            ValueError: If the provided path is not a valid directory.
        """
        if not os.path.isdir(value):
            raise ValueError(f'The directory "{value}" does not exist.')
        self.__images_directory_path = value
        self.__image_filepaths = get_pixmap_compatible_image_filepaths(value)
        if len(self.__image_filepaths) == 0:
            raise EmptyDatasetError(f'The folder "{value}" has no compatible image files.')
        
    @property
    def bounding_boxes_directory_path(self):
        """
        Get the directory path where bounding box annotation files are stored.
        
        Returns:
            str: Path to the bounding boxes directory.
        """
        return self.__bounding_boxes_directory_path
    
    @bounding_boxes_directory_path.setter
    def bounding_boxes_directory_path(self, value:str):
        """
        Set the directory path for bounding box annotation files and compute filepaths
        corresponding to each image in the dataset.
        
        Args:
            value (str): Path to the directory containing bounding box `.txt` files.
        """
        self.__bounding_boxes_directory_path = value
        os.makedirs(value, exist_ok=True)
        if value:
            self.__bounding_boxes_filepaths = list(
                map(lambda x: self.__image_filepath_to_annotation_filepath(x, value, '.txt'), self.image_filepaths)
            )
            
    @property
    def semantic_segments_directory_path(self):
        """
        Get the directory path where semantic segmentation mask files are stored.
        
        Returns:
            str: The path to the semantic segments directory.
        """
        return self.__semantic_segments_directory_path
    
    @semantic_segments_directory_path.setter
    def semantic_segments_directory_path(self, value:str):
        """
        Set the directory path where semantic segmentation mask files are stored,
        and generate corresponding file paths for each image.
        
        Args:
            value (str): The path to the semantic segments directory.
        """
        self.__semantic_segments_directory_path = value
        os.makedirs(value, exist_ok=True)
        if value:
            self.__semantic_segments_filepaths = list(
                map(lambda x: self.__image_filepath_to_annotation_filepath(x, value, '.png'), self.image_filepaths)
            )
    
    @staticmethod
    def __image_filepath_to_annotation_filepath(image_filepath, annotations_directory_path, annotation_file_extension):
        """
        Convert an image filepath to its corresponding annotation filepath.
        
        Supports generating paths for both bounding box (.txt) and semantic segment (.png) annotations.
        
        Args:
            image_filepath (str): The original image filepath.
            annotations_directory_path (str): The directory where annotations are stored.
            annotation_file_extension (str): The annotation file extension (either '.txt' or '.png').
        
        Returns:
            str: The corresponding annotation filepath.
        
        Raises:
            ValueError: If the extension is not '.txt' or '.png'.
        """
        if annotation_file_extension not in {'.txt', '.png'}:
            raise ValueError("`annotation_file_extension` parameter can only be either '.txt' or '.png'")
        filename = os.path.basename(image_filepath)
        annotation_filename = os.path.splitext(filename)[0] + annotation_file_extension
        annotation_filepath = os.path.join(annotations_directory_path, annotation_filename)
        return annotation_filepath
    
    @property
    def image_filepaths(self):
        """
        Get the list of filepaths for the images being annotated.
        
        Returns:
            list(str): List of full filepaths to image files.
        """
        return self.__image_filepaths
    
    @property
    def semantic_segments_filepaths(self):
        """
        Get the list of filepaths for semantic segmentation mask files.
    
        Returns:
            list(str): List of full filepaths to semantic segment mask files.
        """
        return self.__semantic_segments_filepaths
    
    @property
    def bounding_boxes_filepaths(self):
        """
        Get the list of filepaths for the bounding box annotation files.
        
        Returns:
            list(str): List of full filepaths to bounding box annotation files.
        """
        return self.__bounding_boxes_filepaths
    
    @property
    def image_navigation_keys(self):
        """
        Get the list of keys used for navigating between images.
        
        Returns:
            list: A list of 2 keys (e.g., Qt key constants) that control image navigation.
        """
        return self.__image_navigation_keys
    
    @image_navigation_keys.setter
    def image_navigation_keys(self, value:Iterable):
        """
        Set the keys used for navigating between images.
        
        Args:
            value (Iterable): An iterable containing exactly two items representing navigation keys.
        
        Raises:
            ValueError: If the iterable does not contain exactly two items.
        """
        if len(value) != 2:
            raise ValueError('`image_navigation_keys` should be an `Iterable` of two items.')
        self.__image_navigation_keys = list(value)
    
    def keyPressEvent(self, event):
        """
        Handle key press events to navigate between images.
        
        - Pressing the first navigation key moves to the previous image if not at the first.
        - Pressing the second navigation key moves to the next image if not at the last.
        
        Args:
            event (QKeyEvent): The key press event triggered by user input.
        """
        if event.key() == self.image_navigation_keys[0] and self.image_index > 0:
            self.image_index -= 1
        elif event.key() == self.image_navigation_keys[1] and self.image_index < len(self.image_filepaths) - 1:
            self.image_index += 1
    
    @property
    def image_index(self):
        """
        Get the current index of the image being displayed.
        
        Returns:
            int: The current image index.
        """
        return self.__image_index
    
    @image_index.setter
    def image_index(self, value:int):
        """
        Set the current image index and update associated filepaths and annotator.
        
        Args:
            value (int): The new image index to set.
        
        Side Effects:
            - Updates the current image filepath based on the new index.
            - Updates the current bounding boxes and semantic segments filepaths if they exist.
            - Calls the internal method to update the image annotator accordingly.
        """
        self.__image_index = value
        self.current_image_filepath = self.image_filepaths[value]
        if hasattr(self, f'_{self.__class__.__name__}__bounding_boxes_filepaths'):
            self.__current_bounding_boxes_filepath = self.bounding_boxes_filepaths[value]
        if hasattr(self, f'_{self.__class__.__name__}__semantic_segments_filepaths'):
            self.__current_semantic_segments_filepath = self.semantic_segments_filepaths[value]
        self.__update_image_annotator()
    
    def __update_image_annotator(self):
        """
        Update or initialize the internal ImageAnnotator instance with current filepaths.
        
        - If the ImageAnnotator instance already exists, update its filepaths.
        - Otherwise, create a new ImageAnnotator with the current image, bounding boxes, and semantic segments filepaths.
        """
        if hasattr(self, f'_{self.__class__.__name__}__image_annotator'):
            self.__image_annotator.image_filepath = self.current_image_filepath
            self.__image_annotator.bounding_boxes_filepath = self.current_bounding_boxes_filepath
            self.__image_annotator.semantic_segments_filepath = self.current_semantic_segments_filepath
        else:
            self.__image_annotator = ImageAnnotator(
                self.current_image_filepath, 
                self.current_bounding_boxes_filepath,
                self.current_semantic_segments_filepath, 
                **self.__image_annotator_kwargs
            )
    
    @property
    def current_image_filepath(self):
        """
        Get the current image filepath being annotated.
        
        Returns:
            str: Filepath of the current image.
        """
        return self.__current_image_filepath
    
    @current_image_filepath.setter
    def current_image_filepath(self, value:str):
        self.__current_image_filepath = value
        self.setWindowTitle(f'Tadqeeq - Image Annotator\t\t|\t{os.path.basename(value)}')
    
    @property
    def current_bounding_boxes_filepath(self):
        """
        Get the current bounding boxes annotation filepath.
        
        Returns:
            str: Filepath of the current bounding boxes annotation.
        """
        return self.__current_bounding_boxes_filepath
    
    @property
    def current_semantic_segments_filepath(self):
        """
        Get the current semantic segments annotation filepath.
        
        Returns:
            str: Filepath of the current semantic segments annotation.
        """
        return self.__current_semantic_segments_filepath
    
    def resizeEvent(self, event):
        """
        Handle the widget resize event by starting the resize scheduler
        with a delay defined in the image annotator.
        
        Args:
            event (QResizeEvent): The resize event.
        """
        self.__resize_scheduler.start(
            self.__image_annotator.RESIZE_DELAY
        )
        
    def __resize_user_interface_update_routine(self):
        """
        Resize the user interface widget to match the size of the image annotator widget.
        """
        self.resize(self.__image_annotator.size())
        
    def closeEvent(self, event):
        self.destroy()
        parent = self.parent()
        if parent and parent.isHidden():
            parent.show()
        event.accept()
            