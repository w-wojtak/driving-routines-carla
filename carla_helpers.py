"""
carla_helpers.py

This module contains helper functions for working with the Carla simulator.

Functions:
    print_vehicle_location(vehicle, timestamp, print_interval):
        Print the location of a Carla vehicle at specified intervals.

    # Add more functions here if needed
"""
import time

import carla


def get_vehicle_blueprint_by_key(blueprint_library, key):
    """
    Get a vehicle blueprint from the blueprint library by its key.
    """
    for blueprint in blueprint_library:
        if blueprint.id == key:
            return blueprint
    return None


def print_vehicle_location(vehicle, timestamp, print_interval):
    current_time = timestamp.elapsed_seconds if timestamp else 0
    if hasattr(print_vehicle_location, 'last_print_time'):
        time_since_last_print = current_time - print_vehicle_location.last_print_time
        if time_since_last_print >= print_interval:
            vehicle_location = vehicle.get_location()
            print(vehicle_location)
            print_vehicle_location.last_print_time = current_time
    else:
        print_vehicle_location.last_print_time = current_time


def spawn_vehicle_with_color(world, blueprint, initial_transform, color='255,0,0'):
    """
    Spawn a vehicle with the specified blueprint, color, and initial transform.

    Parameters:
        - world: The Carla world object.
        - blueprint: The Carla vehicle blueprint.
        - initial_transform: The initial transform of the vehicle.
        - color: The color to set for the vehicle (default is '255,0,0' for red).
    """
    if blueprint:
        # Set the vehicle color
        blueprint.set_attribute('color', color)

        # Spawn the vehicle with the specified blueprint and initial transform
        vehicle = world.spawn_actor(blueprint, initial_transform)

        print(f"Spawned {blueprint.id} with color {color}.")
        return vehicle
    else:
        print(f"Blueprint not found or does not support setting color.")
        return None


def draw_route_on_map(world, route, waypoint_symbol='^', color=carla.Color(r=0, g=0, b=255), life_time=60.0):
    """
    Draw the route on the map with specified parameters.

    Parameters:
        - world: The Carla world object.
        - route: The route to be drawn.
        - waypoint_symbol: The symbol to be drawn at each waypoint (default is '^').
        - color: The color of the drawn symbols (default is blue).
        - life_time: The duration for which the symbols will be displayed (default is 60.0 seconds).
    """
    for waypoint in route:
        world.debug.draw_string(
            waypoint[0].transform.location,
            waypoint_symbol,
            draw_shadow=False,
            color=color,
            life_time=life_time,
            persistent_lines=True
        )


def move_car_along_route(world, vehicle, route, sleep_time=0.01, display_image=False):
    """
    Move the car along the specified route.

    Parameters:
        - vehicle: The Carla vehicle object.
        - route: The route to follow.
        - sleep_time: The time to sleep between movements (default is 0.1 seconds).
        - display_image: Whether to display the image during the movement (default is False).
    """
    for waypoint in route:
        # Move the car to the current waypoint
        vehicle.set_transform(waypoint[0].transform)

        # Display image if requested
        if display_image:
            # Assuming you have the 'camera_data' defined
            # cv2.imshow('Fake self-driving', camera_data['image'])
            # cv2.waitKey(50)
            pass
        else:
            pass

        draw_text_annotation(world, vehicle, sleep_time)

        # Sleep for a short duration
        time.sleep(sleep_time)

    # vehicle.destroy()
    print("Route completed.")


def add_text_annotations(world, locations):
    """
    Add text annotations at specified destinations on the map.

    Parameters:
        - world: The Carla world object.
        - destinations: A dictionary mapping location names to carla.Location objects.
    """
    for location_name, location in locations.items():
        world.debug.draw_string(
            location + carla.Location(x=2, y=0, z=1),  # Offset from the location
            location_name,
            draw_shadow=False,
            color=carla.Color(r=255, g=0, b=0),  # Red color
            life_time=100  # Display for a specified duration (in seconds)
        )


def draw_text_annotation(world, vehicle, life_time):
    """
    Draw a text annotation based on the vehicle location.

    Parameters:
        - world: The Carla world object.
        - vehicle: The Carla vehicle object.
        - text_offset: The offset for the text annotation.
        - life_time: Duration for which the text will be displayed (in seconds).
    """
    # Get the current location of the vehicle
    vehicle_location = vehicle.get_location()

    # Display a text annotation on the screen
    text_offset = carla.Location(x=2, y=2)

    # Calculate the new text location based on the current vehicle location
    text_location = vehicle_location + text_offset

    # Draw the text annotation
    world.debug.draw_string(
        text_location,  # Position of the text
        "I'm a red car!",
        draw_shadow=False,
        color=carla.Color(r=255, g=0, b=0),  # Text color (red)
        life_time=life_time  # Display for the specified duration
    )


def execute_route(grp, world, vehicle, start_location, end_location, sleep_time=2, display_image=False):
    """
    Execute a route from start_location to end_location for the vehicle.

    Parameters:
        - world: The Carla world object.
        - vehicle: The Carla vehicle object.
        - start_location: The starting location for the route.
        - end_location: The ending location for the route.
        - sleep_time: Duration for which the vehicle stays at the destination location (in seconds).
        - display_image: Whether to display images during the route execution.
    """
    # Set the route plan for the vehicle
    route = grp.trace_route(start_location, end_location)

    # Draw the route on the map
    draw_route_on_map(world, route)

    # Move the vehicle along the route
    move_car_along_route(world, vehicle, route, sleep_time=0.01, display_image=display_image)

    # Make the car stay at this location for x seconds
    time.sleep(sleep_time)