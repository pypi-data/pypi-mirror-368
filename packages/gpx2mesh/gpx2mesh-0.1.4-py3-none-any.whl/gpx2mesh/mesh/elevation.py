import numpy as np
import trimesh


def elevation_to_mesh(
    elevation_array,
    width=40.0,
    target_depth=5.0,
    base_thickness=1.0,
):
    # Get dimensions
    rows, cols = elevation_array.shape

    # Calculate scaling factors to fit target dimensions
    x_scale = width / (cols - 1)  # Scale to fit target width
    y_scale = width / (rows - 1)  # Scale to fit target height

    # Normalize elevation data to fit target depth
    elevation_min = elevation_array.min()
    elevation_max = elevation_array.max()
    elevation_range = elevation_max - elevation_min

    if elevation_range > 0:
        # Scale elevations to fit within target_depth
        normalized_elevation = (elevation_array - elevation_min) / elevation_range
        scaled_elevation = normalized_elevation * target_depth
    else:
        # Handle flat terrain case
        scaled_elevation = np.zeros_like(elevation_array)

    # Create coordinate grids with scaled dimensions
    x = np.arange(cols) * x_scale
    y = np.arange(rows) * y_scale
    X, Y = np.meshgrid(x, y)

    # Create vertices for the top surface
    top_vertices = np.column_stack(
        [X.flatten(), Y.flatten(), scaled_elevation.flatten()]
    )

    # Create vertices for the bottom surface (base)
    base_z = -base_thickness  # Base extends below the lowest elevation
    bottom_vertices = np.column_stack(
        [X.flatten(), Y.flatten(), np.full(X.size, base_z)]
    )

    # Combine all vertices
    vertices = np.vstack([top_vertices, bottom_vertices])

    # Create faces for the top surface
    top_faces = []
    for i in range(rows - 1):
        for j in range(cols - 1):
            # Current quad vertices (top surface)
            v1 = i * cols + j
            v2 = i * cols + (j + 1)
            v3 = (i + 1) * cols + j
            v4 = (i + 1) * cols + (j + 1)

            # Create two triangles for each quad
            top_faces.extend(
                [
                    [v1, v2, v3],  # First triangle
                    [v2, v4, v3],  # Second triangle
                ]
            )

    # Create faces for the bottom surface (flipped normals)
    bottom_faces = []
    offset = len(top_vertices)  # Offset for bottom vertices
    for i in range(rows - 1):
        for j in range(cols - 1):
            # Current quad vertices (bottom surface)
            v1 = offset + i * cols + j
            v2 = offset + i * cols + (j + 1)
            v3 = offset + (i + 1) * cols + j
            v4 = offset + (i + 1) * cols + (j + 1)

            # Create two triangles (flipped winding order)
            bottom_faces.extend(
                [
                    [v1, v3, v2],  # First triangle
                    [v2, v3, v4],  # Second triangle
                ]
            )

    # Create side faces to connect top and bottom
    side_faces = []

    # Front and back edges
    for j in range(cols - 1):
        # Front edge (y=0)
        top_front_1 = j
        top_front_2 = j + 1
        bottom_front_1 = offset + j
        bottom_front_2 = offset + j + 1

        side_faces.extend(
            [
                [top_front_1, bottom_front_1, top_front_2],
                [top_front_2, bottom_front_1, bottom_front_2],
            ]
        )

        # Back edge (y=max)
        back_row = (rows - 1) * cols
        top_back_1 = back_row + j
        top_back_2 = back_row + j + 1
        bottom_back_1 = offset + back_row + j
        bottom_back_2 = offset + back_row + j + 1

        side_faces.extend(
            [
                [top_back_1, top_back_2, bottom_back_1],
                [top_back_2, bottom_back_2, bottom_back_1],
            ]
        )

    # Left and right edges
    for i in range(rows - 1):
        # Left edge (x=0)
        top_left_1 = i * cols
        top_left_2 = (i + 1) * cols
        bottom_left_1 = offset + i * cols
        bottom_left_2 = offset + (i + 1) * cols

        side_faces.extend(
            [
                [top_left_1, top_left_2, bottom_left_1],
                [top_left_2, bottom_left_2, bottom_left_1],
            ]
        )

        # Right edge (x=max)
        top_right_1 = i * cols + (cols - 1)
        top_right_2 = (i + 1) * cols + (cols - 1)
        bottom_right_1 = offset + i * cols + (cols - 1)
        bottom_right_2 = offset + (i + 1) * cols + (cols - 1)

        side_faces.extend(
            [
                [top_right_1, bottom_right_1, top_right_2],
                [top_right_2, bottom_right_1, bottom_right_2],
            ]
        )

    # Combine all faces
    all_faces = np.array(top_faces + bottom_faces + side_faces)

    # Create the mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=all_faces)

    # Ensure the mesh is watertight and has correct normals
    mesh.remove_duplicate_faces()
    mesh.remove_unreferenced_vertices()
    mesh.fix_normals()

    # Reflection around y axis to flip north/south orientation, without changing its center
    center = mesh.centroid
    translate_to_origin = trimesh.transformations.translation_matrix(-center)
    reflect = np.array(
        [
            [1, 0, 0, 0],  # keep x
            [0, -1, 0, 0],  # flip y
            [0, 0, 1, 0],  # keep z
            [0, 0, 0, 1],
        ]
    )
    translate_back = trimesh.transformations.translation_matrix(center)
    transforms = translate_back @ reflect @ translate_to_origin
    mesh.apply_transform(transforms)

    return mesh
