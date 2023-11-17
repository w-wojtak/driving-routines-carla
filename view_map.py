import carla

# Connect to the client and retrieve the world object
client = carla.Client('localhost', 2000)
world = client.get_world()

client.load_world('Town05')

# Retrieve the spectator object
spectator = world.get_spectator()

# Get the location and rotation of the spectator through its transform
transform = spectator.get_transform()

location = transform.location
rotation = transform.rotation

# Set the spectator with an empty transform
# spectator.set_transform(carla.Transform())
# This will set the spectator at the origin of the map, with 0 degrees
# pitch, yaw and roll - a good way to orient yourself in the map


# Set the spectator with the bird-eye view transform
# spectator.set_transform(carla.Transform(carla.Location(x=0, y=0, z=50), carla.Rotation(pitch=-90)))

# Zoom out the spectator

# town 1
# spectator.set_transform(carla.Transform(carla.Location(x=160, y=150, z=300), carla.Rotation(pitch=-90)))

# town 2
# spectator.set_transform(carla.Transform(carla.Location(x=130, y=150, z=300), carla.Rotation(pitch=-90)))

# town 3
# spectator.set_transform(carla.Transform(carla.Location(x=60, y=0, z=450), carla.Rotation(pitch=-90)))

# town 4
# spectator.set_transform(carla.Transform(carla.Location(x=60, y=0, z=800), carla.Rotation(pitch=-90)))

# town 5
spectator.set_transform(carla.Transform(carla.Location(x=-25, y=0, z=400), carla.Rotation(pitch=-90)))

# town 6
# spectator.set_transform(carla.Transform(carla.Location(x=60, y=0, z=450), carla.Rotation(pitch=-90)))


print('Done.')