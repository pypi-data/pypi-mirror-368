from setuptools import setup, find_packages

# Optional: load README.md as the long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sen2p",
    version="0.0.4",
    description="Download Sentinel-2 data from Microsoft Planetary Computer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Thai Tran",
    author_email="ThaiTran@outlook.co.nz",  
    url="https://github.com/tnmthai/sen2p",  
    packages=find_packages(),
    install_requires=[
        "planetary-computer",
        "pystac-client",
        "rioxarray",
        "xarray",
        "tqdm",
        "geopandas", 
        "shapely"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
    ],
)
