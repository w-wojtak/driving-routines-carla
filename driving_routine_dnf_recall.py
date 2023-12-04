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

# Specify the file name you used for saving the array
file_name_field = "sequence_memory.npy"
# file_name_pars = "field_parameters.npy"

# Load the array from the file
saved_activity = np.load(file_name_field)

# For oscillatory kernel: a, b, alpha.
kernel_pars_wm = [1.5, 0.5, 0.8]

# For gaussian kernel: a_ex, s_ex, w_in.
kernel_pars_gauss = [2, 1, 0.0]

# Remaining parameters
h_d_init = -7.28
tau_h_dec = 20
h_wm = -1.0
c_wm = 6  # strength of inhibitory connections from u_wm to u_dec

destinations = {
    'HOME': carla.Location(x=25, y=130, z=0.5),
    'WORK': carla.Location(x=155, y=-140, z=9),
    'SCHOOL': carla.Location(x=-20, y=-140, z=0.5)
}

# Create a copy of the destinations dictionary
destinations_copy = destinations.copy()

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
# for recall
memory = saved_activity
u_dec = memory + h_d_init

u_wm = h_wm * np.ones(np.shape(x))

h_d = h_d_init

# kernels and ffts
w_hat_wm = np.fft.fft(kernel_osc(x, *kernel_pars_wm))
w_lat = np.fft.fft(kernel_gauss(x, *kernel_pars_gauss))

input_position = [-60, -30, 0]
indices_closest = [np.argmin(np.abs(x - target)) for target in input_position]

u_dec_prev = []

# ----------------------------------------------------------------

# Number of waypoints to add at the end of each route
# = time to stay at each location
t1 = 100
t2 = 500
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
    fig_memory_decision_wm, axes_memory_decision_wm = plt.subplots(1, 3, figsize=(14, 5))

    # Set message to empty string
    message_arrival = []
    message_decision = []

    # Set the time of day in minutes (420 -> 7AM)
    time_day = 420

    count = 1

    for index, waypoint in enumerate(route):

        # Move the car to the current waypoint
        vehicle.set_transform(waypoint[0].transform)

        time_day += .02

        # Check if the vehicle has arrived at any of the destinations
        for destination_name, destination_location in destinations.items():
            if carla_helpers.check_arrival(waypoint[0].transform.location, destination_location):
                if (len(previous_waypoints) > 2) and waypoint != previous_waypoints[-1]:
                    if destination_name in destinations_copy.keys():
                        print(f"You arrived at {destination_name}")
                        print(f"time= {time_day}")
                        message_arrival = f"You arrived at {destination_name}"
                        fig_memory_decision_wm, axes_memory_decision_wm = plot_memory_decision_wm(u_field, u_dec, u_wm,
                                                                                                  field_pars,
                                                                                                  time_day, message_arrival,
                                                                                                  message_decision,
                                                                                                  fig=fig_memory_decision_wm,
                                                                                                  axes=axes_memory_decision_wm)
                        time.sleep(2)
                        plt.clf()
                        del destinations_copy[destination_name]
                        message_arrival = []

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
        if input_on and time_day > 421:
            input = input_shape[0] * np.exp(-0.5 * (x - input_position) ** 2 / input_shape[1] ** 2)
            # print(f"input on at {input_position}")
        else:
            input = 0

        u_field = u_field + dt * (-u_field + conv + input + h_u)

        # === recall
        f_dec = np.heaviside(u_dec - theta, 1)
        f_hat_dec = np.fft.fft(f_dec)
        f_wm = np.heaviside(u_wm - 0.5, 1)
        f_hat_wm = np.fft.fft(f_wm)

        conv_dec = dx * np.fft.ifftshift(np.real(np.fft.ifft(f_hat_dec * w_lat)))
        conv_wm = dx * np.fft.ifftshift(np.real(np.fft.ifft(f_hat_wm * w_hat_wm)))

        h_d = h_d + dt / tau_h_dec  # threshold adaptation

        u_dec = u_dec + dt * (-u_dec + conv_dec + memory + h_d - c_wm * f_wm * u_wm)
        u_wm = u_wm + dt * (-u_wm + conv_wm + h_wm + f_dec * u_dec)

        # Check for theta crossings
        for k in indices_closest:
            if len(u_dec_prev) > 0 and u_dec[k] > theta and (u_dec_prev[k] < theta):
                print(f"recalled time {count}: {time_day:.1f}")
                closest_key = min(input_positions, key=lambda key: abs(input_positions[key] - x[np.argmax(u_dec)]))
                message_decision = f"You should be at {closest_key} in 10 minutes!"
                fig_memory_decision_wm, axes_memory_decision_wm = plot_memory_decision_wm(u_field, u_dec, u_wm,
                                                                                          field_pars,
                                                                                          time_day, message_arrival,
                                                                                          message_decision,
                                                                                          fig=fig_memory_decision_wm,
                                                                                          axes=axes_memory_decision_wm)
                plt.pause(2)
                plt.clf()
                count += 1
                message_decision = []

        # Store the current u_dec for the next iteration
        u_dec_prev = u_dec.copy()

        # plot the field activity u_field for each 10th waypoint
        if index % 10 == 0:
            fig_memory_decision_wm, axes_memory_decision_wm = plot_memory_decision_wm(u_field, u_dec, u_wm, field_pars,
                                                                                      time_day, message_arrival,
                                                                                      message_decision,
                                                                                      fig=fig_memory_decision_wm,
                                                                                      axes=axes_memory_decision_wm)
            plt.clf()

        # Sleep for a short duration
        time.sleep(0.0001)

        # Update the previous waypoints list
        previous_waypoints.append(waypoint)

        # Only keep the last 5 waypoints in the list to avoid excessive memory usage
        if len(previous_waypoints) > 4:
            previous_waypoints.pop(0)

    time.sleep(5)

    fig_memory_decision_wm, axes_memory_decision_wm = plot_memory_decision_wm(u_field, u_dec, u_wm, field_pars,
                                                                              time_day, message_arrival,
                                                                              message_decision,
                                                                              fig=fig_memory_decision_wm,
                                                                              axes=axes_memory_decision_wm)
    fig_memory_decision_wm.savefig('routine_memory_decision_wm.png')
    plt.clf()

    # vehicle.destroy()
    print("Route completed.")

    elapsed_time_total = time.time() - time_start
    print(f"Total elapsed time: {elapsed_time_total:.2f} seconds")

    # Specify the file name
    file_name_field = "sequence_memory.npy"

    # Save the array to the file
    np.save(file_name_field, u_field)

else:
    print(f"Blueprint {desired_blueprint_key} not found.")
