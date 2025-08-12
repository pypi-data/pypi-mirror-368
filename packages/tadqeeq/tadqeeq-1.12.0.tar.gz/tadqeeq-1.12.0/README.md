# Tadqeeq – Image Annotator Tool

An interactive image annotation tool built with **PyQt5**, designed for efficient labeling of **segmentation masks** and **bounding boxes**.

> Developed by **Mohamed Behery** @ RTR Software Development - An "Orbits" Subsidiary
> 📅 April 30, 2025
> 🪪 Licensed under the MIT License

---

## 🚀 Widget Features

- ✅ **Minimalist Interactive Design**
- 🖌️ **Scroll through label classes / Adjust pen size** with the mouse wheel
- 🎨 **Supports segmentation masks (.png)** and **bounding boxes (.txt)**
- 🧠 **Dynamic label color generation** (HSV-based)
- 💬 **Floating labels** showing hovered and selected classes
- 💾 **Auto-save** and **manual save** (Ctrl+S)
- 🧽 **Flood-fill segmentation** with a postprocessing stage of **binary hole filling**
- 🚫 **Right-click erase mode** and **double-click to clear all**

## 🚀 CLI Features

- ✅ **Minimalist Design**
- 🎨 **Navigate through images** using A and D.

---

## 📦 Installation

### Option 1: Install via pip

```bash
pip install tadqeeq
```

### Option 2: Run from source

```bash
git clone https://github.com/orbits-it/tadqeeq.git
cd tadqeeq
pip install -r requirements.txt
```

---

## 🛠️ Usage

### Import in your code:

```python
from tadqeeq.widgets import ImageAnnotator
```
```python
from tadqeeq.implementations import ImageAnnotatorWindow
```

### Run CLI tool from command line (if installed via pip):

```bash
tadqeeq [--void_background] [--verbose] [--autosave] [--use_bounding_boxes] --images <images_directory_path> --classes <class_names_filepath> [--bounding-boxes <bounding_boxes_directory_path>] [--semantic-segments <semantic_segments_directory_path>]
```

**Notes:**
>1. Use A and D to navigate through images.</br>
>2. At least one of --bounding-boxes or --semantic-segments must be provided.
>3. The annotation files could either be:</br>
>>a) PNG for **semantic segmentation masks** with class-labeled pixels on a white background.</br>
>>b) txt for **YOLO-style bounding boxes** formatted as: `label_index x_offset y_offset width height`.</br>
>4. <class_names_filepath> is a txt file containing a list of a class names used in annotating.</br>
>5. Tool Behavior in Segmentation:</br>
>>- If `void_background` is False:</br>
>>>- Increments all label values by 1, turning background (255) into 0 and shifting segment labels to start from 1.</br>
>>- If `void_background` is True:</br>
>>>- Leaves label values unchanged (255 remains as void).</br>
>>- Detects boundaries between segments and sets those boundary pixels to 255 (void label).

---

## 🧭 Controls

| Action                                     | Mouse / Key                      |
| ------------------------------------------ | -------------------------------- |
| Toggle erase mode                          | Right-click                      |
| Draw / Erase                               | Left-click / Drag                |
| Mark Bounding Box / Semantic Segment       | Double left-click (drawing mode) |
| Clear all                                  | Double right-click               |
| Toggle slider mode                         | Wheel-click                      |
| Slide through label classes / Brush widths | Scroll wheel                     |
| Save manually                              | Ctrl + S                         |
| Reveal annotated segment's label name      | Move cursor over annotation      |
| Navigate between images                    | A / D (keyboard)                 |

---

## 📁 Project Structure

```plaintext
root/
├── tadqeeq/
|   ├── __init__.py         # Entry point for importing
|   ├── widgets.py          # Contains ImageAnnotator class
|   ├── utils.py            # Helper methods (flood fill, bounding box logic)
|   |
|   ├── implementations.py  # Provides a complete, minimal working example of how to integrate the ImageAnnotator 
│   │                       # within an annotation pipeline. These implementation objects are intended to be 
│   │                       # used as-is and should not be modified directly in other applications.
|   |
|   └── cli.py              # Entry point for a full annotation solution utilizing the code in `implementations.py`
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
└── requirements.txt
```

---

## 🧑‍💻 Contributing

[Repository](https://github.com/orbits-it/tadqeeq.git)

Pull requests are welcome!  
If you add features (e.g. COCO export, brush tools, batch processing), please document them in the README.

---

## 📄 License

This project is licensed under the **MIT License**.  
See [LICENSE](https://github.com/orbits-it/tadqeeq/blob/main/LICENSE) for the full license text.

---

## 💡 Acknowledgements

🎉 Built for computer vision practitioners needing fast, mouse-based labeling with clean overlays and autosave logic.

🌟 Special thanks to **PyQt5** for providing the powerful and flexible GUI toolkit that made the development of this interactive image annotator possible.

---

## 🔗 Related Resources

- [PyQt5 Docs](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [NumPy](https://numpy.org/)
- [scikit-image](https://scikit-image.org/)
- [SciPy](https://scipy.org/)
