config = {
    "dynamics_type": "diff_drive",
    "dynamics_params": {
        "wheel_r": 0.098,  # Wheel radius
        "wheel_b": 0.262,  # Wheel base
        "vmin": -0.5,      # Minimum linear velocity
        "vmax": 2.0,       # Maximum linear velocity
        "wmin": -2.0,      # Minimum angular velocity
        "wmax": 2.0,       # Maximum angular velocity
    },
    "polygon": (
        (0.252, 0.252, -0.252, -0.252),  # x coordinates of the polygon vertices
        (-0.2165, 0.2165, 0.2165, -0.2165)  # y coordinates of the polygon vertices
    ),
}