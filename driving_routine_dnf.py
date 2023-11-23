import time
import datetime
import carla
import carla_helpers
import sys

sys.path.append(
    'C:/Users/weronika.wojtak/OneDrive - Centro de Computação Gráfica/Desktop/Work/Carla/WindowsNoEditor/PythonAPI/carla')  # tweak to where you put carla
from agents.navigation.global_route_planner import GlobalRoutePlanner

from src.plotting import *
from src.utils import *

destinations = {
    'HOME': carla.Location(x=25, y=130, z=0.5),
    'WORK': carla.Location(x=155, y=-140, z=9),
    'SCHOOL': carla.Location(x=-20, y=-140, z=0.5)
}

input_positions = {
    'HOME': -60,
    'WORK': -30,
    'SCHOOL': 0
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

#  DNF parameters ----------------------------------------------
# For oscillatory kernel: a, b, alpha.
kernel_pars = [1, 0.7, 0.9]

# Field parameters
x_lim = 100  # Limits for space, it is set as [-x_lim, x_lim].
dx, dt = 0.05, 0.05  # Spatial and temporal discretization.
theta = 1  # Threshold for the activation function.

# Remaining parameters
tau_h = 20  # time constant of the threshold adaptation
h_0 = 0  # initial value of h-level

field_pars = [x_lim, dx, dt, theta]

x = np.arange(-x_lim, x_lim + dx, dx)

u_0 = h_0 * np.ones(np.shape(x))
u_field = u_0
h_u = h_0 * np.ones(np.shape(x))

# kernel and its fft
w_hat = np.fft.fft(kernel_osc(x, *kernel_pars))

# Input parameters
input_shape = [10, 1.5]  # parameters of gaussian inputs: amplitude, sigma.

input_on = False

# ----------------------------------------------------------------

# Number of waypoints to add at the end of each route
# = time to stay at each location
t1 = 100
t2 = 1000
t3 = 300

# Keep track of the previous waypoints
previous_waypoints = []

# So let's tell the world to spawn the vehicle.
if desired_blueprint:

    # Call the function to spawn the vehicle
    vehicle = carla_helpers.spawn_vehicle_with_color(world, desired_blueprint, initial_transform)

    # Set the route plan for the vehicle
    route_1 = grp.trace_route(destinations['HOME'], destinations['SCHOOL'])
    route_2 = grp.trace_route(destinations['SCHOOL'], destinations['WORK'])
    route_3 = grp.trace_route(destinations['WORK'], destinations['HOME'])

    # Replicate the last waypoint for each route
    route_1 = carla_helpers.replicate_last_waypoint(route_1, t1)
    route_2 = carla_helpers.replicate_last_waypoint(route_2, t2)
    route_3 = carla_helpers.replicate_last_waypoint(route_3, t3)

    # Combine the routes
    route = route_1 + route_2 + route_3

    # Draw the route on the map
    carla_helpers.draw_route_on_map(world, route, life_time=150.0)

    # Set the start time
    time_start = time.time()

    # Create the figure for u_field
    fig, ax = plt.subplots(figsize=(4, 3))

    for index, waypoint in enumerate(route):
        # Move the car to the current waypoint
        vehicle.set_transform(waypoint[0].transform)

        # day onset time in minutes (420 -> 7AM)
        day_onset = 420

        # Calculate the elapsed time
        elapsed_time = time.time() - time_start + day_onset

        elapsed_time_minutes = elapsed_time

        # Format elapsed time as HH:MM
        elapsed_time_formatted = str(datetime.timedelta(minutes=elapsed_time_minutes))

        # Check if the vehicle has arrived at any of the destinations
        for destination_name, destination_location in destinations.items():
            if carla_helpers.check_arrival(waypoint[0].transform.location, destination_location):
                if (len(previous_waypoints) > 2) and waypoint != previous_waypoints[-1]:
                    print(f"You arrived at {destination_name}")
                # Set input_position based on the destination_name
                input_position = input_positions.get(destination_name, 0)
                input_on = True
                break  # Exit the loop when the vehicle arrives at a destination
            else:
                input_on = False

        # Check if the current waypoint is equal to the previous 4 waypoints
        if (len(previous_waypoints) > 2) and waypoint == previous_waypoints[-3]:
            input_on = False

        carla_helpers.draw_text_annotation(world, vehicle, life_time=0.03)

        # Update the field
        f = np.heaviside(u_field - theta, 1)
        f_hat = np.fft.fft(f)
        conv = dx * np.fft.ifftshift(np.real(np.fft.ifft(f_hat * w_hat)))
        h_u = h_u + dt / tau_h * f  # threshold adaptation
        if input_on and elapsed_time > (day_onset + 5):
            input = input_shape[0] * np.exp(-0.5 * (x - input_position) ** 2 / input_shape[1] ** 2)
            # print(f"input on at {input_position}")
        else:
            input = 0

        u_field = u_field + dt * (-u_field + conv + input + h_u)

        # plot the field activity u_field for each 10th waypoint
        if index % 10 == 0:
            plot_activity_at_time_step(u_field, field_pars, elapsed_time_formatted, fig=fig)
            # clear the figure so that the next time step can be plotted
            plt.clf()

        # Sleep for a short duration
        time.sleep(0.001)

        # Update the previous waypoints list
        previous_waypoints.append(waypoint)

        # Only keep the last 5 waypoints in the list to avoid excessive memory usage
        if len(previous_waypoints) > 4:
            previous_waypoints.pop(0)

    time.sleep(5)

    plot_activity_at_time_step(u_field, field_pars, elapsed_time_formatted, fig=fig)
    fig.savefig('routine_memory.png')
    plt.clf()

    # vehicle.destroy()
    print("Route completed.")

    elapsed_time_total = time.time() - time_start
    print(f"Total elapsed time: {elapsed_time_total:.2f} seconds")

else:
    print(f"Blueprint {desired_blueprint_key} not found.")
