import trimesh


def shape_mesh_into_medal(terrain: trimesh.Trimesh):
    # Get the bounds of the mesh
    bounds = terrain.bounds

    # Calculate the size of the square (assuming it's roughly square)
    x_size = bounds[1][0] - bounds[0][0]  # max_x - min_x
    y_size = bounds[1][1] - bounds[0][1]  # max_y - min_y

    # Use the larger dimension as the square size
    square_size = max(x_size, y_size)

    # Circle radius is half the square size (diameter = square_size)
    radius = square_size / 2

    # Find the center of the mesh
    center_x = (bounds[1][0] + bounds[0][0]) / 2
    center_y = (bounds[1][1] + bounds[0][1]) / 2

    # Method 1: Using boolean intersection with a cylinder
    # Create a cylinder that spans the full height of the mesh
    z_min = bounds[0][2]
    z_max = bounds[1][2]
    cylinder_height = z_max - z_min + 1  # Add some margin

    # Create cylinder mesh
    cylinder = trimesh.creation.cylinder(
        radius=radius,
        height=cylinder_height,
        transform=trimesh.transformations.translation_matrix(
            [center_x, center_y, (z_min + z_max) / 2]
        ),
    )

    terrain = terrain.intersection(cylinder)

    ring = trimesh.creation.annulus(
        r_min=radius, r_max=radius + 2, height=5, sections=100
    )
    dz = terrain.bounds[0][2] - ring.bounds[0][2]
    ring = ring.apply_transform(
        trimesh.transformations.translation_matrix([center_x, center_y, dz])
    )

    mesh = trimesh.util.concatenate([terrain, ring])

    hook = trimesh.creation.annulus(r_min=3, r_max=4.5, height=2.5, sections=100)

    hook = hook.apply_transform(
        trimesh.transformations.translation_matrix(
            [
                terrain.bounds[1][0] / 2 - hook.centroid[0],
                terrain.bounds[1][1] + 1.5 - hook.centroid[1],
                terrain.bounds[0][2] - hook.bounds[0][2],
            ]
        )
    )
    return trimesh.util.concatenate([mesh, hook])
