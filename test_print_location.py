import carla
import random
import functools
import time

import carla_helpers


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
transform = carla.Transform(carla.Location(x=0, y=20, z=10), carla.Rotation(yaw=-45.0))

# So let's tell the world to spawn the vehicle.
vehicle = world.spawn_actor(bp, transform)

# Every x second, print the coordinates of the vehicle.

# Set up the on_tick callback with the desired print interval (e.g., 10 seconds)
print_interval = 2
world.on_tick(functools.partial(carla_helpers.print_vehicle_location, vehicle, print_interval=print_interval))

try:
    while True:
        # Do something else in your main loop if needed
        time.sleep(1)

except KeyboardInterrupt:
    pass
finally:
    # Destroy the actor when exiting
    vehicle.destroy()

print('Done.')
