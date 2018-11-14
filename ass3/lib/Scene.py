#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua


class Scene:

    ## constructor
    def __init__(self,
        PARENT_NODE = None,
        ):

        ### variables ###
        self.box_list = []

        ## init scene light
        self.light_node = avango.gua.nodes.LightNode(Name = "scene_light", Type = avango.gua.LightType.POINT)
        self.light_node.Color.value = avango.gua.Color(1.0, 1.0, 0.95)
        self.light_node.Brightness.value = 15.0
        self.light_node.Falloff.value = 1.0 # exponent
        self.light_node.EnableShadows.value = True
        self.light_node.ShadowMapSize.value = 1024
        self.light_node.Transform.value = \
            avango.gua.make_trans_mat(0.0, 0.5, 0.0) * \
            avango.gua.make_rot_mat(-90.0, 1, 0, 0) * \
            avango.gua.make_scale_mat(1.0)
        self.light_node.ShadowNearClippingInSunDirection.value = 0.1
        PARENT_NODE.Children.value.append(self.light_node)


        ## init scene geometries
        _loader = avango.gua.nodes.TriMeshLoader() # get trimesh loader to load external meshes

        ## init ground
        self.ground_geometry = _loader.create_geometry_from_file("ground_geometry", "data/objects/cube.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.ground_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.0, -0.105, 0.0) * \
            avango.gua.make_scale_mat(0.5, 0.01, 0.5)
        self.ground_geometry.Material.value.set_uniform("ColorMap", "data/textures/ground/bricks_diffuse.jpg")
        self.ground_geometry.Material.value.set_uniform("NormalMap", "data/textures/ground/bricks_normal.jpg")
        PARENT_NODE.Children.value.append(self.ground_geometry)
        

        ## init box0
        self.box0_geometry = _loader.create_geometry_from_file("box0_geometry", "data/objects/cube.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.box0_geometry.Transform.value = \
            avango.gua.make_trans_mat(-0.15, -0.05, 0.0) * \
            avango.gua.make_scale_mat(0.1)
        self.box0_geometry.Material.value.set_uniform("ColorMap", "data/textures/box1/wood_diffuse.jpg")
        self.box0_geometry.Material.value.set_uniform("NormalMap", "data/textures/box1/wood_normal.jpg")
        PARENT_NODE.Children.value.append(self.box0_geometry)
        self.box_list.append(self.box0_geometry)
        

        ## init box1
        self.box1_geometry = _loader.create_geometry_from_file("box1_geometry", "data/objects/cube.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.box1_geometry.Transform.value = \
            avango.gua.make_trans_mat(-0.15, 0.025, 0.0) * \
            avango.gua.make_scale_mat(0.05)
        self.box1_geometry.Material.value.set_uniform("ColorMap", "data/textures/box1/wood_diffuse.jpg")
        self.box1_geometry.Material.value.set_uniform("NormalMap", "data/textures/box1/wood_normal.jpg")
        PARENT_NODE.Children.value.append(self.box1_geometry)
        self.box_list.append(self.box1_geometry)


        ## init box2
        self.box2_geometry = _loader.create_geometry_from_file("box2_geometry", "data/objects/cube.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.box2_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.12, -0.075, 0.0) * \
            avango.gua.make_scale_mat(0.05)
        self.box2_geometry.Material.value.set_uniform("ColorMap", "data/textures/box2/diffuse.jpg")
        self.box2_geometry.Material.value.set_uniform("NormalMap", "data/textures/box2/normal.jpg")
        self.box2_geometry.Material.value.set_uniform("RoughnessMap", "data/textures/box2/roughness.jpg")
        PARENT_NODE.Children.value.append(self.box2_geometry)
        self.box_list.append(self.box2_geometry)


        ## init box3
        self.box3_geometry = _loader.create_geometry_from_file("box2_geometry", "data/objects/cube.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.box3_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.13, -0.025, 0.0) * \
            avango.gua.make_scale_mat(0.05)
        self.box3_geometry.Material.value.set_uniform("ColorMap", "data/textures/box2/diffuse.jpg")
        self.box3_geometry.Material.value.set_uniform("NormalMap", "data/textures/box2/normal.jpg")
        self.box3_geometry.Material.value.set_uniform("RoughnessMap", "data/textures/box2/roughness.jpg")
        PARENT_NODE.Children.value.append(self.box3_geometry)
        self.box_list.append(self.box3_geometry)

    
