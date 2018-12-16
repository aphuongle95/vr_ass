#!/usr/bin/python3

## import avango-guacamole libraries
import avango
import avango.gua


## import framework libraries
from lib.Manipulation import ManipulationManager
from lib.PointerInput import PointerInput
from lib.Scene import Scene
from lib.VivePlatform import VivePlatform
from lib.UdpReceiver import UdpReceiver

## import python libraries
import builtins


def start():
    scenegraph = avango.gua.nodes.SceneGraph(Name = "scenegraph")
    builtins.SCENEGRAPH = scenegraph

    # init scene
    scene = Scene(PARENT_NODE = scenegraph.Root.value)

    ## create viewing platform
    vive_platform = VivePlatform()
    vive_platform.my_constructor(PARENT_NODE = scenegraph.Root.value,
    	                         TRACKING_NAME_BASE = "vive-sensor")

    pointer_input = PointerInput()
    pointer_input.init_vive_pointer(TRACKING_NAME_BASE = "vive-sensor")

    ## create manipulation manager
    manipulation_manager = ManipulationManager()
    manipulation_manager.my_constructor(
    	SCENEGRAPH = scenegraph,
    	NAVIGATION_NODE = vive_platform.get_navigation_node(),
    	HEAD_NODE = vive_platform.get_head_node(),
    	POINTER_INPUT = pointer_input)

    ## create UdpReceiver to listen for incoming control commands
    udp_receiver = UdpReceiver('127.0.0.1', 7070, handle_message)

    # print complete scenegraph
    #print_graph(scenegraph.Root.value)

    # Start application/render loop
    vive_platform.run_viewer(locals(), globals())


def handle_message(MESSAGE):
    try:
        eval(MESSAGE)
    except:
        print("Error parsing command: " + MESSAGE)
        import sys
        print(sys.exc_info())


def print_graph(root_node):
  stack = [(root_node, 0)]
  while stack:
    node, level = stack.pop()
    print("│   " * level + "├── {0} <{1}>".format(
      node.Name.value, node.__class__.__name__))
    stack.extend(
      [(child, level + 1) for child in reversed(node.Children.value)])


if __name__ == '__main__':
    start()
