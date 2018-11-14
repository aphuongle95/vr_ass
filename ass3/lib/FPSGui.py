#!/usr/bin/python

## @file
# Contains base class FPSGui.

### import avango-guacamole libraries
import avango
import avango.gua
import avango.gua.gui

### import framework libraries
# ...

### import python libraries
import time


class FPSGui:

    ## constructor
    def __init__(self,
        PARENT_NODE = None,
        WINDOW = None,
        VIEWER = None,
        ):

        ### guard ###
        if PARENT_NODE is None or WINDOW is None: # guard
            print("ERROR: missing parameters")
            return

        ### external references ###
        self.WINDOW = WINDOW
        self.VIEWER = VIEWER

        ### parameters ###
        self.size = avango.gua.Vec2(512, 64) # in pixel

        ### variables ###
        self.time_sav = time.time()


        ### resources ###
        self.gui = avango.gua.gui.nodes.GuiResourceNode(
            TextureName = "fps_gui",
            URL = "asset://gua/data/html/fps_chart.html",
            Size = self.size
            )
        self.gui.Interactive.value = False # do not propagate events into gui
        
        
        self.quad = avango.gua.nodes.TexturedScreenSpaceQuadNode()
        self.quad.Name.value = "fps_quad_node"
        self.quad.Texture.value = "fps_gui"
        self.quad.Width.value = int(self.size.x)
        self.quad.Height.value = int(self.size.y)        
        #self.quad.Anchor.value = avango.gua.Vec2(1.0, -1.0) # lower right corner
        self.quad.Anchor.value = avango.gua.Vec2(1.0, 0.86) # upper right corner
        PARENT_NODE.Children.value.append(self.quad)


        ### trigger callbacks ###

        ## @var frame_trigger
        # Triggers framewise evaluation of respective callback method
        self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)
        

    ### callback functions ###
    def frame_callback(self):
        if (time.time() - self.time_sav) > 0.2: # print out every 0.2 sec
            _rnd_fps_str = "{:5.2f}".format(self.WINDOW.RenderingFPS.value)
            _app_fps_str = "{:5.2f}".format(self.VIEWER.ApplicationFPS.value)
                        
            self.gui.call_javascript("add_value_pair", [_rnd_fps_str, _app_fps_str])
        
            self.time_sav = time.time()
           
