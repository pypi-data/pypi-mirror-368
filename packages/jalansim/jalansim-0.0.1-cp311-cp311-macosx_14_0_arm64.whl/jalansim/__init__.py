import os

force_cpu = os.getenv('USE_CUDA', '').lower() in ('0', 'false', 'no', 'off')

try:
    if force_cpu:
        raise ImportError("Forcing CPU backend due to environment variable.")
    import jalansim._core_cuda as _core
    print("Using CUDA backend for jalansim")
except ImportError:
    import jalansim._core_cpu as _core
    print("Using CPU backend for jalansim")

def make(vehicle_type, num_envs, dynamics_params=None, *, radius=None, width=None, length=None, polygon=None):
    """
    Factory function to create a BatchSim instance based on the dynamics and collision type.
    
    Args:
        vehicle_type (str): The type of vehicle for which to create a BatchSim instance.
    
    Returns:
        BatchSim: An instance of the appropriate BatchSim class.
    """
    default_models = ['jackal', 'f1tenth']
    if vehicle_type in default_models:
        if vehicle_type == 'jackal':
            from .configs.jackal import config
        elif vehicle_type == 'f1tenth':
            from .configs.f1tenth import config
        dynamics_type = config['dynamics_type']
        dynamics_params = config.get('dynamics_params', dynamics_params)
        polygon = config.get('polygon', polygon)
    else:
        dynamics_type = vehicle_type

    if radius is None and (width is None or length is None) and polygon is None:
        raise ValueError("Either 'radius', 'width' and 'length', or 'polygon' must be provided to define the vehicle shape.")
    if (radius is not None) + (width is not None or length is not None) + (polygon is not None) > 1:
        raise ValueError("Only one of 'radius', 'width' and 'length', or 'polygon' can be provided to define the vehicle shape.")
    shape_type = 'circle' if radius is not None else 'polygon'

    if shape_type == 'circle':
        collision = _core.collision.Circle()
        collision.set_radius(radius)
    elif shape_type == 'polygon':
        if polygon is None:
            if width is None or length is None:
                raise ValueError("If 'polygon' is not provided, both 'width' and 'length' must be provided to define the vehicle shape.")
            # Create a rectangle polygon based on width and length
            half_width = width / 2.0
            half_length = length / 2.0
            polygon = (
                (half_length, half_length, -half_length, -half_length),  # x coordinates
                (-half_width, half_width, half_width, -half_width)  # y coordinates
            )
        assert len(polygon) == 2, "Polygon must be a tuple of two lists (x_coords, y_coords)."
        assert len(polygon[0]) == len(polygon[1]), "Polygon x and y coordinates must have the same length."
        assert len(polygon[0]) >= 3, "Polygon must have at least 3 vertices."
        collision = _core.collision.Polygon()
        collision.set_polygon(polygon[0], polygon[1])

        
    
    if dynamics_type == 'diff_drive':
        dynamics = _core.dynamics.DiffDrive()
        if shape_type == 'circle':
            base = _core.DiffDriveCircleBatchSim
        else:
            base = _core.DiffDrivePolyBatchSim
    elif dynamics_type == 'bicycle':
        dynamics = _core.dynamics.Bicycle()
        if shape_type == 'circle':
            base = _core.BicycleCircleBatchSim
        else:
            base = _core.BicyclePolyBatchSim
    elif dynamics_type == 'bicycle_dynamics':
        dynamics = _core.dynamics.BicycleDynamics()
        if shape_type == 'circle':
            base = _core.BicycleDynCircleBatchSim
        else:
            base = _core.BicycleDynPolyBatchSim
    else:
        raise NotImplementedError(f"Vehicle type '{dynamics_type}' is not implemented.")

    # Initialize the dynamics parameters if provided
    if dynamics_params is not None:
        for key, value in dynamics_params.items():
            if hasattr(dynamics, key):
                setattr(dynamics, key, value)
            else:
                raise ValueError(f"Dynamics does not have attribute '{key}'.")

    class BatchSim(base):
        def __init__(self, num_envs):
            super().__init__(num_envs, dynamics, collision)
    
    return BatchSim(num_envs)

Map = _core.Map
MapCollection = _core.MapCollection

__all__ = ['make', 'Map', 'MapCollection']