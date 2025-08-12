"""
Tadqeeq - Image Annotator Tool
An interactive image annotation tool for efficient labeling.
Developed by Mohamed Behery @ RTR Software Development (2025-04-27).
Licensed under the MIT License.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tadqeeq",
    version="1.12.0",
    author="Mohamed Behery",
    author_email="mohamed.i.behery@proton.me",
    description="An interactive PyQt5 image annotation tool for segmentation masks and bounding boxes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/orbits-it/tadqeeq",
    packages=find_packages(include=["tadqeeq", "tadqeeq.*"]),
    package_dir={"": "."},
    include_package_data=True,
    install_requires=[
        "imageio==2.37.0",
        "lazy_loader==0.4",
        "networkx==3.4.2",
        "numpy==2.2.5",
        "packaging==25.0",
        "pillow==11.2.1",
        "PyQt5>=5.15.0,<6.0",
        "PyQt5-Qt5>=5.15.0,<6.0",
        "PyQt5_sip>=12.17,<13.0",
        "scikit-image==0.25.2",
        "scipy==1.15.2",
        "tifffile==2025.3.30",
    ],
    extras_require={
        "dev": [
            "build",
            "twine",
            "wheel",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "tadqeeq=tadqeeq.cli:main",
        ],
    },
)
