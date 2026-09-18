from pyrosm import OSM
from pathlib import Path


# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

OSM_FILE = PROJECT_ROOT / "data" / "raw" / "osm" / "southern-zone-latest.osm.pbf"

OUTPUT_DIR = PROJECT_ROOT / "data" / "intermediate" / "extracted_features"
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

    # Save extracted data
    industrial.to_file(
        OUTPUT_DIR / "industrial_areas.geojson",
        driver="GeoJSON",
    )

    power_plants.to_file(
        OUTPUT_DIR / "power_plants.geojson",
        driver="GeoJSON",
    )

    quarries.to_file(
        OUTPUT_DIR / "quarries.geojson",
        driver="GeoJSON",
    )

    print("\nOSM extraction completed successfully.")
    print(f"Files saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    extract_osm_features()