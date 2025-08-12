""" 
Tadqeeq - Image Annotator Tool
An interactive image annotation tool for efficient labeling.
Developed by Mohamed Behery @ RTR Software Development (2025-04-27).
Licensed under the MIT License.
"""

from PyQt5.QtWidgets import QApplication
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
import os
from .implementations import ImageAnnotatorWindow

def main():
        
    parser = ArgumentParser(
        description='Tadqeeq Image Annotation Tool',
        usage="tadqeeq [--void_background] [--verbose] [--autosave] [--use_bounding_boxes]\n--images <images_directory_path>\n--classes <class_names_filepath>\n[--bounding-boxes <bounding_boxes_directory_path>] [--semantic-segments <semantic_segments_directory_path>]\nNote:\n\tAt least one of --bounding-boxes or --semantic-segments must be provided.",
        formatter_class=RawTextHelpFormatter
    )
    
    parser.add_argument('--images', required=True, help='Directory path for images')
    parser.add_argument('--classes', required=True, help='Text filepath for class names separated by newline characters')
    
    parser.add_argument('--semantic-segments', required=False, help='Directory path for semantic segmentation PNG files')
    parser.add_argument('--bounding-boxes', required=False, help='Directory path for bounding box TXT files')
    
    parser.add_argument('--void_background', action='store_true', help='Use void background')
    parser.add_argument('--autosave', action='store_true', help='Enable autosave')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode')
    
    args = parser.parse_args()
    
    if not args.semantic_segments and not args.bounding_boxes:
        print("Error: At least one of '--semantic-segments' or '--bounding-boxes' must be specified.")
        parser.print_help()
        sys.exit(1)
        
    if not os.path.isdir(args.images):
        print(f'Error: The directory "{args.images}" does not exist.')
        sys.exit(2)
        
    if not os.path.isfile(args.classes):
        print(f'Error: The file "{args.classes}" does not exist.')
        sys.exit(3)
    else:
        with open(args.classes) as file:
            class_names = [line.strip() for line in file.readlines() if line.strip()]
    
    app = QApplication(sys.argv)
    window = ImageAnnotatorWindow(
        images_directory_path=args.images, 
        bounding_boxes_directory_path=args.bounding_boxes,
        semantic_segments_directory_path=args.semantic_segments,
        label_color_pairs=class_names,
        void_background=args.void_background,
        autosave=args.autosave,
        verbose=args.verbose
    )
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()