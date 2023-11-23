import time

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

    # Set the route plan for the vehicle
    route_1 = grp.trace_route(destinations['HOME'], destinations['SCHOOL'])
    route_2 = grp.trace_route(destinations['SCHOOL'], destinations['WORK'])
    route_3 = grp.trace_route(destinations['WORK'], destinations['SCHOOL'])
    route_4 = grp.trace_route(destinations['SCHOOL'], destinations['HOME'])

    # Combine the routes
    route = route_1 + route_2 + route_3 + route_4

    # Draw the route on the map
    carla_helpers.draw_route_on_map(world, route, life_time=100.0)

    # Set the start time
    time_start = time.time()

    for waypoint in route:
        # Move the car to the current waypoint
        vehicle.set_transform(waypoint[0].transform)

        # Calculate the elapsed time
        # elapsed_time = time.time() - time_start

        # Print the elapsed time
        # print(f"Elapsed time: {elapsed_time:.2f} seconds")

        # Check if the vehicle has arrived at any of the destinations
        for destination_name, destination_location in destinations.items():
            if carla_helpers.check_arrival(waypoint[0].transform.location, destination_location):
                print(f"You arrived at {destination_name}")

        carla_helpers.draw_text_annotation(world, vehicle, life_time=0.01)

        # Sleep for a short duration
        time.sleep(0.02)

    # vehicle.destroy()
    elapsed_time_total = time.time() - time_start
    print(f"Total elapsed time: {elapsed_time_total:.2f} seconds")

    print("Route completed.")

else:
    print(f"Blueprint {desired_blueprint_key} not found.")




