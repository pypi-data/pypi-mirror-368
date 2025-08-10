import trimesh
from gpx2mesh.mesh.medal import shape_mesh_into_medal
from gpx2mesh.mesh.elevation import elevation_to_mesh
from gpx2mesh.mesh.track import add_gpx_track_to_terrain


def generate_mesh(
    elevation_array,
    track_points,
    width=40.0,
    depth=5.0,
    base_thickness=1.0,
    track_height=0.5,
    track_width=1.0,
    debug=False,
) -> trimesh.Trimesh:
    terrain_mesh = elevation_to_mesh(elevation_array, width, depth, base_thickness)

    track_mesh = add_gpx_track_to_terrain(
        elevation_array,
        track_points,
        width,
        depth,
        track_height,
        track_width,
        debug,
    )
    mesh = trimesh.util.concatenate([terrain_mesh, track_mesh])

    mesh = shape_mesh_into_medal(mesh)

    return mesh
