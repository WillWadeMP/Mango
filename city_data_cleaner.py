import json
from shapely.geometry import Polygon, Point

def find_building_districts(data):
    """
    Determines the district for each building in the GeoJSON data.

    Args:
    data (dict): The GeoJSON data as a Python dictionary.

    Returns:
    list: A list of dictionaries, where each dictionary represents a building
          and includes its coordinates and the district it belongs to.
    """

    # Extract district polygons and names
    districts = {}
    for feature in data['features']:
        if feature['id'] == 'districts':
            for geom in feature['geometries']:
                districts[geom['name']] = Polygon(geom['coordinates'][0])

    # Extract building polygons
    buildings = []
    for feature in data['features']:
        if feature['id'] == 'buildings':
            for building_coords in feature['coordinates']:
                buildings.append(Polygon(building_coords[0]))

    # Determine district for each building
    building_data = []
    for building in buildings:
        centroid = building.centroid
        for district_name, district_polygon in districts.items():
            if district_polygon.contains(centroid):
                building_data.append({
                    "coordinates": list(building.exterior.coords),
                    "district": district_name
                })
                break  # Move to the next building once district is found

    return building_data

if __name__ == "__main__":
    with open('greenbark_field.json', 'r') as f:
        data = json.load(f)

    building_districts = find_building_districts(data)

    with open('buildings_with_districts.json', 'w') as f:
        json.dump(building_districts, f, indent=4)