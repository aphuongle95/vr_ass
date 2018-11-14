#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua


### import application libraries
from lib.SimpleViewingSetup import *
from lib.Scene import Scene
from lib.Crane import Crane
from lib.Utilities import *


def start():

    ## create scenegraph
    scenegraph = avango.gua.nodes.SceneGraph(Name = "scenegraph")

    ## init viewing setup
    viewingSetup = SimpleViewingSetup(SCENEGRAPH = scenegraph, STEREO_MODE = "mono")
    #viewingSetup = SimpleViewingSetup(SCENEGRAPH = scenegraph, STEREO_MODE = "anaglyph")

    ## init scene
    scene = Scene(PARENT_NODE = scenegraph.Root.value)

    ## init crane
    crane = Crane(PARENT_NODE = scenegraph.Root.value, TARGET_LIST = scene.box_list)


    ## init field connections (dependency graph)
    viewingSetup.viewer.DesiredFPS.connect_from(crane.input.sf_max_fps) # change viewer FPS during runtime


    print_graph(scenegraph.Root.value)
    
    ## start application/render loop
    viewingSetup.run(locals(), globals())


if __name__ == '__main__':
  start()

