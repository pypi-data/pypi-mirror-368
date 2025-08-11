from setuptools import setup, find_packages

setup(
    name="luminescent",  # Your package name
    version="1.0.48",  # Your package version
    description="A description of your package",
    author="Paul Shen",
    author_email="pxshen@alumni.stanford.edu",
    packages=find_packages(),  # Automatically find your package(s)
    install_requires=[
        "gdsfactory",
        "pymeshfix",
        "electromagneticpython",
        "sortedcontainers",
        "scikit-rf",
        "opencv-python",
        "femwell",
        "rasterio",
        "rtree",
    ],
)
# cd C:\Users\pxshe\OneDrive\Desktop\beans\Luminescent.jl\luminescent
# cd luminescent
# python -m build
# twine upload dist/*

# pip install gdsfactory pillow pymeshfix electromagneticpython sortedcontainers scikit-rf
#
