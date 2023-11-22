import carla

import carla_helpers

import sys

sys.path.append(
    'C:/Users/weronika.wojtak/OneDrive - Centro de Computação Gráfica/Desktop/Work/Carla/WindowsNoEditor/PythonAPI/carla')  # tweak to where you put carla
from agents.navigation.global_route_planner import GlobalRoutePlanner


destinations = {
    'HOME': carla.Location(x=25, y=130, z=0.5),
    'WORK': carla.Location(x=155, y=-140, z=9),
    'SCHOOL': carla.Location(x=-20, y=-140, z=0.5)
}

# Connect to the client and retrieve the world object
client = carla.Client('localhost', 2000)
client.set_timeout(5.0)
world = client.get_world()

# Get the map's spawn points
spawn_points = world.get_map().get_spawn_points()

# Load the desired map
client.load_world('Town03')

# Set the route planner
sampling_resolution = 1
grp = GlobalRoutePlanner(world.get_map(), sampling_resolution)

# Write the destinations on the map
carla_helpers.add_text_annotations(world, destinations)

# The world contains the list blueprints that we can use for adding new
# actors into the simulation.
blueprint_library = world.get_blueprint_library()

# Specify the key or ID of the desired vehicle blueprint
desired_blueprint_key = 'vehicle.tesla.model3'

# Get the specific vehicle blueprint by its key
desired_blueprint = carla_helpers.get_vehicle_blueprint_by_key(blueprint_library, desired_blueprint_key)

# Set the spectator with the bird-eye view transform and zoom out
spectator = world.get_spectator()
spectator.set_transform(carla.Transform(carla.Location(x=70, y=-10, z=250), carla.Rotation(pitch=-90)))

# Now we need to give an initial transform to the vehicle.
initial_transform = carla.Transform(destinations['HOME'], carla.Rotation(yaw=90.0))

# So let's tell the world to spawn the vehicle.
if desired_blueprint:

    # Call the function to spawn the vehicle
    vehicle = carla_helpers.spawn_vehicle_with_color(world, desired_blueprint, initial_transform)

    # Execute Route 1
    carla_helpers.execute_route(grp, world, vehicle, destinations, destinations['HOME'], destinations['SCHOOL'])

    # Execute Route 2
    carla_helpers.execute_route(grp, world, vehicle, destinations, destinations['SCHOOL'], destinations['WORK'])

    # Execute Route 3
    carla_helpers.execute_route(grp, world, vehicle, destinations, destinations['WORK'], destinations['SCHOOL'])

    # Execute Route 4
    carla_helpers.execute_route(grp, world, vehicle, destinations, destinations['SCHOOL'], destinations['HOME'])

else:
    print(f"Blueprint {desired_blueprint_key} not found.")




