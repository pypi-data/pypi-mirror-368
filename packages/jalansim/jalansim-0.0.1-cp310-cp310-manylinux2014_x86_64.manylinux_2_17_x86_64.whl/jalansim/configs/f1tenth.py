config = {
    "dynamics_type": "bicycle_dynamics",
    "dynamics_params": {
        "a": 0.15875, # distance CoG → front axle
        "b": 0.17145, # distance CoG → rear axle
        "h": 0.074,   # CoG height
        "m": 3.74,    # kg
        "I_z": 0.04712, # kg·m²
        "mu": 1.0489, # friction coefficient
        "C_Sf": 4.718, # front cornering stiffness
        "C_Sr": 5.4562, # rear cornering stiffness
        "delta_min": -0.4189, # min steering angle
        "delta_max": 0.4189,  # max steering angle
        "delta_dot_min": -3.2, # min steering rate
        "delta_dot_max": 3.2,  # max steering rate
        "acc_min": -5.0,       # min acceleration
        "acc_max": 3.0,        # max acceleration
        # "v_min": 0.0,          # min velocity
        # "v_max": 3.0           # max velocity
    },
    "polygon": (
        (0.29, 0.29, -0.29, -0.29),  # x coordinates
        (-0.155, 0.155, 0.155, -0.155)  # y coordinates
    ),
}