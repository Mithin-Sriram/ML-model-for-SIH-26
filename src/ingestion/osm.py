from pyrosm import OSM
from pathlib import Path


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Input OSM file
OSM_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "osm"
    / "southern-zone-260916.osm.pbf"
)

# Output directory
OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "intermediate"
    / "extracted_features"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_osm_features():
    print("Loading OSM file...")

    osm = OSM(str(OSM_FILE))

    print("Extracting industrial areas...")

    industrial = osm.get_data_by_custom_criteria(
        custom_filter={"landuse": ["industrial"]},
        filter_type="keep",
        keep_nodes=False,
        keep_ways=True,
        keep_relations=True,
    )

    print("Extracting power plants...")

    power_plants = osm.get_data_by_custom_criteria(
        custom_filter={"power": ["plant"]},
        filter_type="keep",
        keep_nodes=True,
        keep_ways=True,
        keep_relations=True,
    )

    print("Extracting quarries...")

    quarries = osm.get_data_by_custom_criteria(
        custom_filter={"landuse": ["quarry"]},
        filter_type="keep",
        keep_nodes=False,
        keep_ways=True,
        keep_relations=True,
    )

    print("Saving industrial areas...")

    industrial.to_file(
        OUTPUT_DIR / "industrial_areas.geojson",
        driver="GeoJSON",
    )

    print("Saving power plants...")

    power_plants.to_file(
        OUTPUT_DIR / "power_plants.geojson",
        driver="GeoJSON",
    )

    print("Saving quarries...")

    quarries.to_file(
        OUTPUT_DIR / "quarries.geojson",
        driver="GeoJSON",
    )

    print("\nOSM extraction completed successfully!")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    extract_osm_features()