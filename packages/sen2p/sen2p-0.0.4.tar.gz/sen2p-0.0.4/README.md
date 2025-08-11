# sen2p

`sen2p` is a lightweight Python library to download Sentinel-2 imagery from Microsoft Planetary Computer.

## 🌍 Features

- 🔍 Search Sentinel-2 data by date and location (point or shapefile)
- 🛰️ Download multiple bands and/or selected bands
- 🗂️ Stack and preprocess bands into a single image
- 🐍 Easy to integrate with geospatial workflows

## 📦 Installation

```bash
pip install sen2p
```

## Usage

### Using a Point Location [lon, lat]
```python
from sen2p import download

location = [172.1, -43.5]

results = download(
    start_date="2023-06-01",
    end_date="2023-06-10",
    location=location,
    bands=["B02", "B03", "B04"],
    output_dir="test_outputs",        
)

for r in results:
    print("Downloaded:", r)
```
### Using a bounding box
```python
from sen2p import download

bbox = [172.0, -43.6, 172.5, -43.3]

results = download(
    start_date="2023-06-01",
    end_date="2023-06-10",
    location=bbox,
    bands=["B02", "B03", "B04"],
    output_dir="test_outputs",        
)
```

### Using a Polygon Shapefile
```python
from sen2p import download

# Path to your shapefile
shapefile_path = "Site.shp"  # Update with your actual shapefile path

# Call the function
results = download(
    start_date="2023-06-01",
    end_date="2023-06-30",
    location=shapefile_path,
    bands=["B02", "B03", "B04"],
    output_dir="test_output",       
)
```
### Show metadata
```python
from sen2p import show_meta
show_meta("S2B_..._merged.tif")
```
## 🔖 License

This project is licensed under the MIT License.