#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua

### import python libraries
import random


class Scene:

    ## constructor
    def __init__(self,
        PARENT_NODE = None,
        ):

        ### variables ###
        
        self.target_list = []
        

        ## init scene light
        self.light = avango.gua.nodes.LightNode(Name = "light")
        self.light.Color.value = avango.gua.Color(0.9, 0.9, 0.9)
        self.light.Falloff.value = 0.4 # exponent
        self.light.EnableShadows.value = True
        self.light.ShadowMapSize.value = 2048
        self.light.ShadowOffset.value = 0.001
        self.light.Transform.value = \
            avango.gua.make_trans_mat(0.0, 1.0, 0.0) * \
            avango.gua.make_scale_mat(2.0)
        self.light.ShadowNearClippingInSunDirection.value = 0.1 * (1.0 / 2.0)
        PARENT_NODE.Children.value.append(self.light)
        

        ## init scene geometries
        _loader = avango.gua.nodes.TriMeshLoader() # get trimesh loader to load external meshes

        # init ground plane
        self.ground_geometry = _loader.create_geometry_from_file("ground", "data/objects/plane.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.ground_geometry.Transform.value = avango.gua.make_trans_mat(0.0, -0.15, 0.0)
        self.ground_geometry.Material.value.set_uniform("ColorMap", "data/textures/ground/bricks_diffuse.jpg")
        self.ground_geometry.Material.value.set_uniform("NormalMap", "data/textures/ground/bricks_normal.jpg")
        PARENT_NODE.Children.value.append(self.ground_geometry)


        # init manipulation geometries
        _number = 15

        for _i in range(_number):
            _x_range = 280 # in mm
            _y_range = 130 # in mm

            _rand_pos_x = random.randrange(-_x_range, _x_range) * 0.001
            _rand_pos_y = random.randrange(-_y_range, _y_range) * 0.001
            _rand_pos_z = 0.0

            _rand_angle = random.randrange(-180,180)
            _rand_axis_x = random.randrange(0,100) * 0.01
            _rand_axis_y = random.randrange(0,100) * 0.01
            _rand_axis_z = random.randrange(0,100) * 0.01
               
            _geometry = _loader.create_geometry_from_file("monkey" + str(_i), "data/objects/monkey.obj", avango.gua.LoaderFlags.DEFAULTS)
            _geometry.Transform.value = \
                avango.gua.make_trans_mat(_rand_pos_x, _rand_pos_y, _rand_pos_z) * \
                avango.gua.make_rot_mat(_rand_angle,_rand_axis_x,_rand_axis_y,_rand_axis_z) * \
                avango.gua.make_scale_mat(0.022)

            _geometry.add_field(avango.gua.SFMatrix4(), "DraggingOffsetMatrix")
            _geometry.add_field(avango.gua.SFVec4(), "CurrentColor")
            _geometry.CurrentColor.value = avango.gua.Vec4(1.0, 1.0, 1.0, 1.0)
            _geometry.Material.value.set_uniform("Color", _geometry.CurrentColor.value)
            PARENT_NODE.Children.value.append(_geometry)

            self.target_list.append(_geometry) # append monkey to target list
    
