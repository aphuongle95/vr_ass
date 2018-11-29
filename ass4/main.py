#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua


### import application libraries
from lib.SimpleViewingSetup import SimpleViewingSetup
from lib.Scene import Scene
from lib.Device import KeyboardInput
from lib.Navigation import SteeringNavigation
from lib.Manipulation import ManipulationManager


def start():

    ## create scenegraph
    scenegraph = avango.gua.nodes.SceneGraph(Name = "scenegraph")

    ## init scene
    scene = Scene(PARENT_NODE = scenegraph.Root.value)


    ## init navigation technique
    keyboardInput = KeyboardInput()
    keyboardInput.my_constructor("gua-device-keyboard0")

    steeringNavigation = SteeringNavigation()
    steeringNavigation.my_constructor(keyboardInput.mf_dof, keyboardInput.mf_buttons) # connect steering navigation with keyboard input


    ## init viewing setup
    viewingSetup = SimpleViewingSetup(SCENEGRAPH = scenegraph, STEREO_MODE = "mono")
    #viewingSetup = SimpleViewingSetup(SCENEGRAPH = scenegraph, STEREO_MODE = "anaglyph")
    viewingSetup.connect_navigation_matrix(steeringNavigation.sf_nav_mat)
    steeringNavigation.set_rotation_center_offset(viewingSetup.get_head_position())


    ## init manipulation techniques    
    manipulation_manager = ManipulationManager()
    manipulation_manager.my_constructor(PARENT_NODE = viewingSetup.navigation_node, SCENE_ROOT = scenegraph.Root.value, TARGET_LIST = scene.target_list)


    print_graph(scenegraph.Root.value)

    ## start application/render loop
    viewingSetup.run(locals(), globals())



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

## print all fields of a fieldcontainer to the console
def print_fields(node, print_values = False):
  for i in range(node.get_num_fields()):
    field = node.get_field(i)
    print("→ {0} <{1}>".format(field._get_name(), field.__class__.__name__))
    if print_values:
      print("  with value '{0}'".format(field.value))


if __name__ == '__main__':
  start()

