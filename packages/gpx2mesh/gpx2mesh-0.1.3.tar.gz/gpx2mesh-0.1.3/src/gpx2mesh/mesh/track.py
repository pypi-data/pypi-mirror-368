import numpy as np
import trimesh
from scipy.interpolate import RegularGridInterpolator
from matplotlib import pyplot as plt


def add_gpx_track_to_terrain(
    elevation_array,
    track_points,
    width=40.0,
    target_depth=5.0,
    track_height=0.5,
    track_width=1.0,
    debug=False,
):
    # Convert track into mesh coordinates
    track_mesh_coords = track_points * width

    if debug:
        plt.plot(track_mesh_coords[:, 0], track_mesh_coords[:, 1], "r")
        plt.imshow(elevation_array, extent=[0, width, 0, width])
        plt.colorbar()
        plt.savefig("debug.png")

    # Sample elevations along the track from the terrain
    track_elevations = sample_terrain_elevations(
        track_mesh_coords,
        elevation_array,
        width,
        target_depth,
    )

    # Create the track geometry
    track_mesh = create_track_mesh(
        track_mesh_coords, track_elevations, track_height, track_width
    )

    return track_mesh


def sample_terrain_elevations(
    track_coords,
    elevation_array,
    width,
    target_depth,
):
    """
    Sample elevation values along the track path.

    Returns elevations in the final mesh coordinate system.
    """
    rows, cols = elevation_array.shape

    # Create coordinate grids that match the mesh coordinate system
    x_grid = np.linspace(0, width, cols)
    y_grid = np.linspace(width, 0, rows)

    # Normalize and scale elevation data (same as terrain mesh)
    elevation_min = elevation_array.min()
    elevation_max = elevation_array.max()
    elevation_range = elevation_max - elevation_min

    if elevation_range > 0:
        normalized_elevation = (elevation_array - elevation_min) / elevation_range
        scaled_elevation = normalized_elevation * target_depth
    else:
        scaled_elevation = np.zeros_like(elevation_array)

    # Create interpolator
    # Note: elevation_array[0,0] corresponds to the "bottom-left" in mesh coordinates
    # We need to be careful about the Y-axis orientation
    interpolator = RegularGridInterpolator(
        (y_grid, x_grid),
        scaled_elevation,
        bounds_error=False,
        fill_value=0,
        method="linear",
    )

    # Sample elevations at track points
    # track_coords is in (x, y) format, interpolator expects (y, x)
    track_elevations = interpolator(track_coords[:, [1, 0]])

    print("Track elevation sampling:")
    print(f"  Terrain elevation range: {elevation_min:.2f} to {elevation_max:.2f}")
    print(f"  Scaled elevation range: 0.0 to {target_depth:.2f}")
    print(
        f"  Track elevation range: {track_elevations.min():.2f} to {track_elevations.max():.2f}"
    )

    return track_elevations


def create_track_mesh(track_coords, track_elevations, track_height, track_width):
    """
    Create a 3D mesh for the track path.

    The track is created as a ribbon/tube following the path.
    """
    if len(track_coords) < 2:
        print("Not enough points in track")
        return None

    # Remove consecutive duplicate points (with smaller tolerance for better precision)
    unique_indices = [0]  # Always keep first point
    for i in range(1, len(track_coords)):
        if not np.allclose(
            track_coords[i], track_coords[i - 1], atol=0.01
        ):  # Much smaller tolerance
            unique_indices.append(i)

    if len(unique_indices) < 2:
        print("Not enough unique points in track")
        return None

    track_coords = track_coords[unique_indices]
    track_elevations = track_elevations[unique_indices]

    print("Track mesh creation:")
    print(
        f"  Original points: {len(track_coords)}, After deduplication: {len(unique_indices)}"
    )
    print(f"  Track width: {track_width:.2f}, Track height: {track_height:.2f}")

    # Calculate track center line with elevated height
    track_z = track_elevations + track_height

    # Create track ribbon by adding width perpendicular to path direction
    vertices = []
    faces = []

    for i in range(len(track_coords)):
        x, y = track_coords[i]
        z = track_z[i]

        # Calculate direction vector for track width
        if i == 0:
            # First point: use direction to next point
            if len(track_coords) > 1:
                direction = track_coords[i + 1] - track_coords[i]
            else:
                direction = np.array([1, 0])
        elif i == len(track_coords) - 1:
            # Last point: use direction from previous point
            direction = track_coords[i] - track_coords[i - 1]
        else:
            # Middle points: use average direction for smoother curves
            dir1 = track_coords[i] - track_coords[i - 1]
            dir2 = track_coords[i + 1] - track_coords[i]
            direction = (dir1 + dir2) / 2

        # Normalize direction and get perpendicular
        direction_length = np.linalg.norm(direction)
        if direction_length > 1e-6:  # Avoid division by very small numbers
            direction = direction / direction_length
            perpendicular = np.array(
                [-direction[1], direction[0]]
            )  # 90-degree rotation
        else:
            perpendicular = np.array([1, 0])

        # Create track vertices (left and right edges)
        half_width = track_width / 2
        left_point = np.array([x, y]) + perpendicular * half_width
        right_point = np.array([x, y]) - perpendicular * half_width

        # Add vertices: top surface and bottom surface for each edge
        base_idx = len(vertices)
        vertices.extend(
            [
                [left_point[0], left_point[1], z],  # 0: Top left
                [right_point[0], right_point[1], z],  # 1: Top right
                [left_point[0], left_point[1], track_elevations[i]],  # 2: Bottom left
                [
                    right_point[0],
                    right_point[1],
                    track_elevations[i],
                ],  # 3: Bottom right
            ]
        )

        # Create faces connecting this segment to the previous one
        if i > 0:
            prev_base = base_idx - 4
            curr_base = base_idx

            # Top surface triangles (track surface)
            faces.extend(
                [
                    [prev_base, prev_base + 1, curr_base],  # Triangle 1
                    [prev_base + 1, curr_base + 1, curr_base],  # Triangle 2
                ]
            )

            # Bottom surface triangles (flipped normals)
            faces.extend(
                [
                    [prev_base + 2, curr_base + 2, prev_base + 3],
                    [prev_base + 3, curr_base + 2, curr_base + 3],
                ]
            )

            # Left side wall triangles
            faces.extend(
                [
                    [prev_base, curr_base, prev_base + 2],
                    [curr_base, curr_base + 2, prev_base + 2],
                ]
            )

            # Right side wall triangles
            faces.extend(
                [
                    [prev_base + 1, prev_base + 3, curr_base + 1],
                    [curr_base + 1, prev_base + 3, curr_base + 3],
                ]
            )

    # Create end caps to close the ribbon
    if len(vertices) >= 4:
        # Start cap
        faces.extend(
            [
                [0, 2, 1],  # Front face triangle 1
                [1, 2, 3],  # Front face triangle 2
            ]
        )

        # End cap
        end_base = len(vertices) - 4
        faces.extend(
            [
                [end_base, end_base + 1, end_base + 2],
                [end_base + 1, end_base + 3, end_base + 2],
            ]
        )

    if not vertices or not faces:
        return None

    print(f"  Created track mesh: {len(vertices)} vertices, {len(faces)} faces")

    track_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    track_mesh.fix_normals()

    return track_mesh
