import geopandas as gpd
from pathlib import Path

INPUT = Path("data/intermediate/extracted_features/oil_gas_refinery.geojson")
OUTPUT = Path("data/intermediate/extracted_features/oil_gas_refinery_clean.geojson")

gdf = gpd.read_file(INPUT)

keep_columns = [
    "name",
    "name:en",
    "man_made",
    "industrial",
    "landuse",
    "resource",
    "operator",
    "description",
    "geometry",
]

keep_columns = [col for col in keep_columns if col in gdf.columns]

gdf = gdf[keep_columns].copy()
gdf = gdf[gdf.geometry.notna()].copy()
gdf = gdf.to_crs("EPSG:4326")

gdf.to_file(OUTPUT, driver="GeoJSON")

print(f"Input records: {len(gdf)}")
print(f"Output: {OUTPUT}")

print("\nGeometry types:")
print(gdf.geometry.geom_type.value_counts())

print("\nSaved successfully.")
