import bpy
import math
import sys
import subprocess
import os
import pandas as pd

# this next little bit is because Blender uses a different python distro than conda
# so you either need this, or to change the Blender settings to point to conda
# and I was scared to do that
"""
except:
    python_exe = os.path.join(sys.prefix, 'bin', 'python3.10')
    # upgrade pip
    subprocess.call([python_exe, "-m", "ensurepip"])
    subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
    # install required packages
    subprocess.call([python_exe, "-m", "pip", "install", "pandas"])
"""


df = pd.read_csv("/Users/mattnicholson/Desktop/play61.csv", index_col=0)
df = df.assign(row_number=range(len(df)))


player_df = pd.read_csv("/Users/mattnicholson/Desktop/play61_players.csv", index_col=0)

# create parameters
cube_count = 10
location_offset = 3
frame_count = 300
fps = 50


# Clear existing objects
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Create a plane for the field
bpy.ops.mesh.primitive_plane_add(size=500, enter_editmode=False, align='WORLD', location=(0, 250, 0))
bpy.context.object.rotation_euler[2] = 0.785398

# Assign a material to the plane
material = bpy.data.materials.new(name="Grass")
bpy.context.object.data.materials.append(material)

# Set up the material
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Remove default nodes
for node in nodes:
    nodes.remove(node)

# Create a diffuse shader node
diffuse_node = nodes.new(type='ShaderNodeBsdfPrincipled')
diffuse_node.location = (0, 0)

# Create an image texture node
texture_node = nodes.new(type='ShaderNodeTexImage')
texture_node.location = (-200, 0)
texture_node.image = bpy.data.images.load('/Users/mattnicholson/Documents/RandomProjects/BlenderMessAround/grass.png')  

# Create a material output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

# Link nodes together
links.new(diffuse_node.outputs['BSDF'], output_node.inputs['Surface'])
links.new(texture_node.outputs['Color'], diffuse_node.inputs['Base Color'])

# Set the render engine to Cycles
bpy.context.scene.render.engine = 'CYCLES'


# Set up dome parameters
radius = 18
segments = 32
ring_count = 16

# Create the half dome
bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments, ring_count=ring_count, location=(0, 60.5, 0), scale=(1, 1, 0.1))

dome = bpy.context.object
dome.name = "HalfDome"

dirt_material = bpy.data.materials.new(name="DirtMaterial")
dirt_material.diffuse_color = (0.84375, 0.6171875, 0.47265625, 1.0) 
dome.data.materials.append(dirt_material)

white_material = bpy.data.materials.new(name="WhiteMaterial")
white_material.diffuse_color = (1.0, 1.0, 1.0, 1.0)  # White color

yellow_material = bpy.data.materials.new(name="YellowMaterial")
yellow_material.diffuse_color = (1.0, 0.83, 0, 1.0) 

black_material = bpy.data.materials.new(name="BlackMaterial")
black_material.diffuse_color = (0, 0, 0, 1.0) 

foul_line_length = 350 
foul_line_rotation = math.degrees(-45) 

# Create the foul lines
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=foul_line_length, location=(math.cos(math.pi/4) * foul_line_length / 2, math.cos(math.pi/4) * foul_line_length / 2, 0))
foul_line1 = bpy.context.object
foul_line1.name = "FoulLine1"
foul_line1.rotation_euler = (1.5708, 0, -0.78598)

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=foul_line_length, location=(- math.cos(math.pi/4) * foul_line_length / 2, math.cos(math.pi/4) * foul_line_length / 2, 0))
foul_line2 = bpy.context.object
foul_line2.name = "FoulLine2"
foul_line2.rotation_euler = (1.5708, 0, 0.78598)

# make foul poles
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=50, location=(math.cos(math.pi/4) * foul_line_length, math.cos(math.pi/4) * foul_line_length, 25))
foul_pole1 = bpy.context.object
foul_pole1.name = "RightFieldFoulPole"

bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=50, location=(- math.cos(math.pi/4) * foul_line_length, math.cos(math.pi/4) * foul_line_length, 25))
foul_pole2 = bpy.context.object
foul_pole2.name = "LeftFieldFoulPole" 

foul_pole1.data.materials.append(yellow_material)
foul_pole2.data.materials.append(yellow_material)



# first base
bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(math.cos(math.pi/4) * 90, math.cos(math.pi/4) * 90, 0), scale=(1, 1, 1))
first_base = bpy.context.object
first_base.name = "FirstBase"
first_base.rotation_euler = (0, 0, 0.78598)


# second base
bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 2 * math.cos(math.pi/4) * 90, 0), scale=(1, 1, 1))
second_base = bpy.context.object
second_base.name = "SecondBase"
second_base.rotation_euler = (0, 0, 0.78598)


# third base
bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(-math.cos(math.pi/4) * 90, math.cos(math.pi/4) * 90, 0), scale=(1, 1, 1))
third_base = bpy.context.object
third_base.name = "ThirdBase"
third_base.rotation_euler = (0, 0, 0.78598)


# Assign material to cylinder
foul_line1.data.materials.append(white_material)
foul_line2.data.materials.append(white_material)
first_base.data.materials.append(white_material)
second_base.data.materials.append(white_material)
third_base.data.materials.append(white_material)




# Set up the Blender scene
scene = bpy.context.scene
scene.frame_start = df['row_number'].min()
scene.frame_end = 300 # df['row_number'].max()

frame_count = 300 # df['row_number'].max() - df['row_number'].min()

# This should be the freq of the samples
bpy.context.scene.render.fps = 20

# the ball
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.5, location=(0, 60.5, 6))
ball_obj = bpy.context.active_object
ball_obj.data.materials.append(white_material)


# Create animation keyframes for the ball object
for _, row in df.iterrows():
    frame = int(row['row_number'])
    position = (row['ball_position_x'], row['ball_position_y'], row['ball_position_z'])
    
    # Set the position of the ball
    ball_obj.location = position
    ball_obj.keyframe_insert(data_path="location", frame=frame)


for pos in player_df["player_position"].unique():
    
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=5, align='WORLD', location=(0, 0, 2.5))
    player = bpy.context.active_object
    
    if pos in list(range(1, 10)):
        player.data.materials.append(yellow_material)
    else:
        player.data.materials.append(black_material)
        
    
    this_df = player_df[player_df["player_position"] == pos]
    this_df = this_df.assign(row_number=range(len(this_df)))
    
    for _, row in this_df.iterrows():
        frame = int(row['row_number'])
        position = (row['field_x'], row['field_y'], 2.5)
        
        # Set the position of the ball
        player.location = position
        player.keyframe_insert(data_path="location", frame=frame)
        
        
    


# bpy.ops.mesh.primitive_cube_add(size=10, location=(2, 0, 0))


# add a camera into the scene
bpy.ops.object.camera_add()
camera = bpy.context.active_object
camera.location.x = 100
camera.location.y = 70
camera.location.z = 10



bpy.ops.object.constraint_add(type="TRACK_TO")
bpy.context.object.constraints["Track To"].influence = 1
bpy.context.object.constraints["Track To"].target = ball_obj

