import carla
import random
import functools


def print_vehicle_location(vehicle):
    vehicle_location = vehicle.get_location()
    print(vehicle_location)


def print_vehicle_location_callback(vehicle, world_snapshot):
    vehicle_location = vehicle.get_location()
    print(vehicle_location)


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

# town 1
# spectator.set_transform(carla.Transform(carla.Location(x=160, y=150, z=300), carla.Rotation(pitch=-90)))

# town 2
# spectator.set_transform(carla.Transform(carla.Location(x=130, y=150, z=300), carla.Rotation(pitch=-90)))

# town 3
spectator.set_transform(carla.Transform(carla.Location(x=40, y=0, z=200), carla.Rotation(pitch=-90)))

# town 4
# spectator.set_transform(carla.Transform(carla.Location(x=60, y=0, z=800), carla.Rotation(pitch=-90)))

# town 5
# spectator.set_transform(carla.Transform(carla.Location(x=-25, y=0, z=400), carla.Rotation(pitch=-90)))

# Now we need to give an initial transform to the vehicle.
transform = carla.Transform(carla.Location(x=0, y=20, z=10), carla.Rotation(yaw=-45.0))

# So let's tell the world to spawn the vehicle.
vehicle = world.spawn_actor(bp, transform)

# Every 1 second, print the coordinates of the vehicle in the world.
# The function world.on_tick requires a carla.WorldSnapshot as argument, which can be retrieved from wait_for_tick().
# world_snapshot = world.wait_for_tick()
# world.on_tick(print_vehicle_location_callback)


print('Done.')
