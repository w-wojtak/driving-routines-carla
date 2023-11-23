import time

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
x_lim, t_lim = 100, 100  # Limits for space and time. Space is set as [-x_lim, x_lim], time as [0, t_lim].
dx, dt = 0.05, 0.05  # Spatial and temporal discretization.
theta = 1  # Threshold for the activation function.

# Remaining parameters
tau_h = 20  # time constant of the threshold adaptation
h_0 = 0  # initial value of h-level

field_pars = [x_lim, t_lim, dx, dt, theta]

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

# So let's tell the world to spawn the vehicle.
if desired_blueprint:

    # Call the function to spawn the vehicle
    vehicle = carla_helpers.spawn_vehicle_with_color(world, desired_blueprint, initial_transform)

    # Set the route plan for the vehicle
    route_1 = grp.trace_route(destinations['HOME'], destinations['SCHOOL'])
    route_2 = grp.trace_route(destinations['SCHOOL'], destinations['WORK'])
    route_3 = grp.trace_route(destinations['WORK'], destinations['HOME'])

    # Combine the routes
    route = route_1 + route_2 + route_3

    # Draw the route on the map
    carla_helpers.draw_route_on_map(world, route, life_time=100.0)

    # Set the start time
    time_start = time.time()

    # Create the figure for u_field
    fig, ax = plt.subplots(figsize=(4, 3))

    for index, waypoint in enumerate(route):
        # Move the car to the current waypoint
        vehicle.set_transform(waypoint[0].transform)

        # Calculate the elapsed time
        elapsed_time = time.time() - time_start

        # Print the elapsed time
        # print(f"Elapsed time: {elapsed_time:.2f} seconds")

        # Check if the vehicle has arrived at any of the destinations
        for destination_name, destination_location in destinations.items():
            if carla_helpers.check_arrival(waypoint[0].transform.location, destination_location):
                print(f"You arrived at {destination_name}")
                # Set input_position based on the destination_name
                input_position = input_positions.get(destination_name, 0)
                # input_position_index = np.argmin(np.abs(x - input_position))
                print(f"Setting input_position to {input_position}")
                input_on = True
                break  # Exit the loop when the vehicle arrives at a destination
            else:
                input_on = False

        carla_helpers.draw_text_annotation(world, vehicle, life_time=0.03)

        # Update the field
        f = np.heaviside(u_field - theta, 1)
        f_hat = np.fft.fft(f)
        conv = dx * np.fft.ifftshift(np.real(np.fft.ifft(f_hat * w_hat)))
        h_u = h_u + dt / tau_h * f  # threshold adaptation
        if input_on and elapsed_time > 5:
            input = input_shape[0] * np.exp(-0.5 * (x - input_position) ** 2 / input_shape[1] ** 2)
            print(f"input on at {input_position}")
        else:
            input = 0

        u_field = u_field + dt * (-u_field + conv + input + h_u)

        # plot the field activity u_field for each 10th waypoint
        if index % 10 == 0:
            plot_activity_at_time_step(u_field, field_pars, elapsed_time, fig=fig)
            # clear the figure so that the next time step can be plotted
            plt.clf()

        # Sleep for a short duration
        time.sleep(0.001)

    # Additional iterations
    extra_iterations = 200
    for extra_iteration in range(extra_iterations):
        # Additional code for extra iterations, if needed
        elapsed_time = time.time() - time_start

        # Update the field (modify this part according to your needs)
        f = np.heaviside(u_field - theta, 1)
        f_hat = np.fft.fft(f)
        conv = dx * np.fft.ifftshift(np.real(np.fft.ifft(f_hat * w_hat)))
        h_u = h_u + dt / tau_h * f  # threshold adaptation

        if extra_iteration > 10:
            input = 0  # Set input to 0 for extra iterations

        u_field = u_field + dt * (-u_field + conv + input + h_u)

        # Plot the field activity for each 10th iteration
        if extra_iteration % 10 == 0:
            plot_activity_at_time_step(u_field, field_pars, elapsed_time, fig=fig)
            plt.clf()  # Clear the figure for the next time step

        if extra_iteration == extra_iterations - 1:
            # Save the figure on the last iteration
            plot_activity_at_time_step(u_field, field_pars, elapsed_time, fig=fig)
            fig.savefig('routine_memory.png')
            plt.clf()

        # Sleep for a short duration
        time.sleep(0.001)

    time.sleep(5)
    # vehicle.destroy()
    print("Route completed.")

    # # Save the figure to file
    # fig.savefig('routine_memory.png')

    elapsed_time_total = time.time() - time_start
    print(f"Total elapsed time: {elapsed_time_total:.2f} seconds")

else:
    print(f"Blueprint {desired_blueprint_key} not found.")
