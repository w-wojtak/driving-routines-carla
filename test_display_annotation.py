import carla
import random

# Connect to the client and retrieve the world object
client = carla.Client('localhost', 2000)
client.set_timeout(5.0)
world = client.get_world()

client.load_world('Town03')

# Retrieve the spectator object
spectator = world.get_spectator()

# Get the location and rotation of the spectator through its transform
transform = spectator.get_transform()

location = transform.location
rotation = transform.rotation

# The world contains the list blueprints that we can use for adding new
# actors into the simulation.
blueprint_library = world.get_blueprint_library()

# Now let's filter all the blueprints of type 'vehicle' and choose one
# at random.
bp = random.choice(blueprint_library.filter('vehicle'))

# Set the vehicle color to red
bp.set_attribute('color', '255,0,0')

# Set the spectator with the bird-eye view transform and zoom out
# town 3
spectator.set_transform(carla.Transform(carla.Location(x=40, y=0, z=200), carla.Rotation(pitch=-90)))

# Now we need to give an initial transform to the vehicle.
initial_transform = carla.Transform(carla.Location(x=0, y=20, z=0.1), carla.Rotation(yaw=-45.0))

# So let's tell the world to spawn the vehicle.
vehicle = world.spawn_actor(bp, initial_transform)

# Display a text annotation on the screen
text_offset = carla.Location(x=2, y=2)

while True:
    # Get the current location of the vehicle
    vehicle_location = vehicle.get_location()

    # Calculate the new text location based on the current vehicle location
    text_location = vehicle_location + text_offset

    # Draw the text annotation
    world.debug.draw_string(
        text_location,  # Position of the text
        "Hi, I'm a red car!",
        draw_shadow=False,
        color=carla.Color(r=0, g=0, b=255),  # Text color (blue)
        life_time=.1  # Display for a short duration (in seconds)
    )

    # Sleep for a short duration to control the update rate
    world.wait_for_tick(seconds=.1)

    # # Let's make the car drive to carla.Location(x=100, y=40, z=0.1)
    # # We can do this by setting the vehicle's target velocity
    # vehicle.set_target_velocity(carla.Vector3D(x=10, y=0, z=0))
    # # We can also set the vehicle's target location
    # vehicle.set_transform(carla.Transform(carla.Location(x=100, y=40, z=0.1), carla.Rotation(yaw=-45.0)))


