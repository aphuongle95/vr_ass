#!/usr/bin/python3

### import guacamole libraries ###
import avango
import avango.gua
import math

### import framework libraries ###
from lib.OrbitVisualization import OrbitVisualization


class SolarObject:

    ### constructor ###
    def __init__(self,
        NAME = "",
        TEXTURE_PATH = "",
        PARENT_NODE = None,
        SF_TIME_SCALE = None,
        DIAMETER = 1.0,
        ORBIT_RADIUS = 1.0,
        ORBIT_INCLINATION = 0.0, # in degrees
        ORBIT_DURATION = 0.0,
        ROTATION_INCLINATION = 0.0, # in degrees
        ROTATION_DURATION = 0.0
        ):

        if PARENT_NODE is None: # guard
            print("ERROR: missing parameters")
            return


        ### parameters ###
        self.sf_time_scale_factor = SF_TIME_SCALE

        self.diameter = DIAMETER
        self.orbit_radius = ORBIT_RADIUS
        self.rotation_inclination = ROTATION_INCLINATION
        self.orbit_inclination = ORBIT_INCLINATION
        if  ORBIT_DURATION == 0:
            self.orbit_velocity = ORBIT_DURATION
        else:
            self.orbit_velocity =  ORBIT_RADIUS / ORBIT_DURATION

        if  ROTATION_DURATION == 0:
            self.rotation_velocity = ROTATION_DURATION
        else:
            self.rotation_velocity = 1 / ROTATION_DURATION


        ### resources ###
        # init geometries of solar object
        _loader = avango.gua.nodes.TriMeshLoader() # init trimesh loader to load external meshes

        self.object_geometry = _loader.create_geometry_from_file(NAME + "_geometry", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.object_geometry.Transform.value = avango.gua.make_scale_mat(self.diameter)
        self.object_geometry.Material.value.set_uniform("ColorMap", TEXTURE_PATH)
        self.object_geometry.Material.value.set_uniform("Roughness", 0.2)
        self.object_geometry.Material.value.EnableBackfaceCulling.value = False

        if NAME == "sun":
            self.object_geometry.Material.value.set_uniform("Emissivity", 1.0)


        self.axis_red_geometry = _loader.create_geometry_from_file("axis_red", "data/objects/cylinder.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.axis_red_geometry.Transform.value = avango.gua.make_scale_mat(0.001,self.diameter*2.5,0.001)
        self.axis_red_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0, 0.0, 0.0, 1.0))
        self.axis_red_geometry.Material.value.set_uniform("Emissivity", 1.0) # no shading
        self.axis_red_geometry.ShadowMode.value = avango.gua.ShadowMode.OFF # geometry does not cast shadows

        self.axis_green_geometry = _loader.create_geometry_from_file("axis_green", "data/objects/cylinder.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.axis_green_geometry.Transform.value = avango.gua.make_scale_mat(0.001,self.diameter*2.5,0.001)
        self.axis_green_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(0.0, 1.0, 0.0, 1.0))
        self.axis_green_geometry.Material.value.set_uniform("Emissivity", 1.0) # no shading
        self.axis_green_geometry.ShadowMode.value = avango.gua.ShadowMode.OFF # geometry does not cast shadows



        # init transformation nodes for specific solar object aspects
        self.orbit_radius_node = avango.gua.nodes.TransformNode(Name = NAME + "_orbit_radius_node")
        self.rotation_inclination_node = avango.gua.nodes.TransformNode(Name = NAME + "_rotation_inclination_node")

        self.orbit_radius_node.Children.value = [self.rotation_inclination_node, self.axis_red_geometry]
        #declare child, red axis denote tangent line to planet orbis surface, rotation_inclination_node only affect planet rotate around itself, not affect the moon
        self.orbit_radius_node.Transform.value = avango.gua.make_trans_mat(self.orbit_radius, 0.0, 0.0)


        ## TODO: create further scenegraph nodes below here
        # add scenegraph node orbis_inclination_node
        self.orbit_inclination_node = avango.gua.nodes.TransformNode(Name = NAME + "_orbit_inclination_node")
        self.orbit_inclination_node.Children.value = [self.orbit_radius_node]
        self.orbit_inclination_node.Transform.value = avango.gua.make_rot_mat(self.orbit_inclination, 0.0, 0.0 , 1.0)
        PARENT_NODE.Children.value.append(self.orbit_inclination_node)
        #child of root node

        self.rotation_inclination_node.Children.value = [self.object_geometry, self.axis_green_geometry]
        self.rotation_inclination_node.Transform.value = avango.gua.make_rot_mat(self.rotation_inclination, 0.0, 0.0 , 1.0)


        ## TODO: create orbit visualization below here
        self.orbis_visualize = OrbitVisualization(
            PARENT_NODE = self.orbit_inclination_node,
            ORBIT_RADIUS = self.orbit_radius
        )


        # Triggers framewise evaluation of respective callback method
        self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)


    ### functions ###
    def get_orbit_node(self):
        return self.orbit_radius_node


    def update_orbit(self):
        self.orbit_radius_node.Transform.value = \
            avango.gua.make_rot_mat(self.orbit_velocity * self.sf_time_scale_factor.value, 0.0, 1.0, 0.0) * \
            self.orbit_radius_node.Transform.value


    def update_rotation(self):
        pass
        ## TODO: fill this function with code
        self.rotation_inclination_node.Transform.value = \
              self.rotation_inclination_node.Transform.value * avango.gua.make_rot_mat(self.rotation_velocity * self.sf_time_scale_factor.value, 0.0, 1.0, 0.0)



    ### callback functions ###
    def frame_callback(self): # evaluated once per frame
        self.update_orbit()
        self.update_rotation()
