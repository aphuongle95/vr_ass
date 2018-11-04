#!/usr/bin/python3

### import guacamole libraries
import avango
import avango.gua

### import application libraries
from lib.SimpleViewingSetup import *
from lib.SolarSystem import SolarSystem
from lib.Device import *
from lib.Navigation import SteeringNavigation
from lib.Utilities import *

### global variables ###
#NAVIGATION_MODE = "Spacemouse"
NAVIGATION_MODE = "Keyboard"


def start():

    ## init scenegraph
    scenegraph = avango.gua.nodes.SceneGraph(Name = "scenegraph")

    ## init solar system
    solarSystem = SolarSystem()
    solarSystem.my_constructor(scenegraph.Root.value)

    ## init navigation technique
    navigation = SteeringNavigation()
    navigation.set_start_transformation(avango.gua.make_trans_mat(0.0,0.1,0.3)) # move camera to initial position

    if NAVIGATION_MODE == "Spacemouse":
        deviceInput = NewSpacemouseInput()
        deviceInput.my_constructor("gua-device-spacemouse")

        navigation.my_constructor(deviceInput.mf_dof, 0.1, 1.0) # connect navigation with spacemouse input

    elif NAVIGATION_MODE == "Keyboard":
        deviceInput = KeyboardInput()
        deviceInput.my_constructor("gua-device-keyboard")

        navigation.my_constructor(deviceInput.mf_dof) # connect navigation with keyboard input

    else:
        print("Error: NAVIGATION_MODE " + NAVIGATION_MODE + " is not known.")
        return

    print_graph(scenegraph.Root.value)

    ## init viewing setup
    viewingSetup = SimpleViewingSetup(scenegraph, "mono")
    viewingSetup.connect_navigation_matrix(navigation.sf_nav_mat)
    navigation.set_rotation_center_offset(viewingSetup.get_head_position())

    viewingSetup.run(locals(), globals())


if __name__ == '__main__':
    start()
