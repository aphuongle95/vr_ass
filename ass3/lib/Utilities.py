#!/usr/bin/python3

# import python libraries
import math


### helper functions ###

## print the subgraph under a given node to the console
def print_graph(root_node):
  stack = [(root_node, 0)]
  while stack:
    node, level = stack.pop()
    print("│   " * level + "├── {0} <{1}>".format(
      node.Name.value, node.__class__.__name__))
    stack.extend(
      [(child, level + 1) for child in reversed(node.Children.value)])


## print all fields of a field container to the console
def print_fields(node, print_values = False):
  for i in range(node.get_num_fields()):
    field = node.get_field(i)
    print("→ {0} <{1}>".format(field._get_name(), field.__class__.__name__))
    if print_values:
      print("  with value '{0}'".format(field.value))



## Converts a rotation matrix to the Euler angles head, pitch and roll.
# @param MATRIX The rotation matrix to be converted.
def get_euler_angles(MATRIX):

    quat = MATRIX.get_rotate()
    qx = quat.x
    qy = quat.y
    qz = quat.z
    qw = quat.w

    sqx = qx * qx
    sqy = qy * qy
    sqz = qz * qz
    sqw = qw * qw
    
    unit = sqx + sqy + sqz + sqw # if normalised is one, otherwise is correction factor
    test = (qx * qy) + (qz * qw)

    if test > 1:
        head = 0.0
        roll = 0.0
        pitch = 0.0

    if test > (0.49999 * unit): # singularity at north pole
        head = 2.0 * math.atan2(qx,qw)
        roll = math.pi/2.0
        pitch = 0.0
    elif test < (-0.49999 * unit): # singularity at south pole
        head = -2.0 * math.atan2(qx,qw)
        roll = math.pi/-2.0
        pitch = 0.0
    else:
        #print("euler", 2.0 * test)
        head = math.atan2(2.0 * qy * qw - 2.0 * qx * qz, 1.0 - 2.0 * sqy - 2.0 * sqz)
        roll = math.asin(2.0 * test)
        pitch = math.atan2(2.0 * qx * qw - 2.0 * qy * qz, 1.0 - 2.0 * sqx - 2.0 * sqz)

    if head < 0.0:
        head += 2.0 * math.pi

    if pitch < 0:
        pitch += 2 * math.pi
    
    if roll < 0:
        roll += 2 * math.pi
       
    head = math.degrees(head)
    if head > 180.0:
        head = -(360.0 - head)

    pitch = math.degrees(pitch)
    if pitch > 180.0:
        pitch = -(360.0 - pitch)

    roll = math.degrees(roll)
    if roll > 180.0:
        roll = -(360.0 - roll)

    return head, pitch, roll
    
