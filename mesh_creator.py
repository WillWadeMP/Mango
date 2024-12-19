import json
import bpy
import os

def create_building_meshes(data):
    """
    Creates Blender meshes for buildings from GeoJSON data, organized
    into district folders.

    Args:
    data (dict): The GeoJSON data as a Python dictionary.
    """

    # Create the main output directory if it doesn't exist
    if not os.path.exists("mesh/buildings"):
        os.makedirs("mesh/buildings")

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

    # Determine district for each building and create mesh
    for i, building in enumerate(buildings):
        centroid = building.centroid
        for district_name, district_polygon in districts.items():
            if district_polygon.contains(centroid):
                # Create district folder if it doesn't exist
                district_folder = os.path.join("mesh/buildings", district_name)
                if not os.path.exists(district_folder):
                    os.makedirs(district_folder)

                # Create a new mesh and object
                mesh = bpy.data.meshes.new(f"Building_{i}")
                obj = bpy.data.objects.new(f"Building_{i}", mesh)

                # Add the object to the scene
                bpy.context.collection.objects.link(obj)

                # Create vertices and faces
                verts = [tuple(coord) + (0,) for coord in building_coords[0]]  # z=0 for ground level
                faces = [list(range(len(verts)))]  # Single face for the base

                # Add top vertices
                verts += [tuple(coord) + (1,) for coord in building_coords[0]]  # z=1 for top

                # Add side faces
                num_base_verts = len(building_coords[0])
                for j in range(num_base_verts):
                    faces.append([j, (j + 1) % num_base_verts, num_base_verts + (j + 1) % num_base_verts, num_base_verts + j])

                # Update mesh with vertices and faces
                mesh.from_pydata(verts, [], faces)
                mesh.update()

                # Export the building mesh to the district folder
                filepath = os.path.join(district_folder, f"Building_{i}.obj")
                bpy.ops.export_scene.obj(filepath=filepath, use_selection=True, use_materials=False)

                # Remove the object and mesh from the scene
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(mesh)

                break  # Move to the next building once district is found

if __name__ == "__main__":
    with open('greenbark_field.json', 'r') as f:
        data = json.load(f)

    create_building_meshes(data)