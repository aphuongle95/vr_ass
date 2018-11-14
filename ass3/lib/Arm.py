#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua


class Arm:

    ### class variables ###

    # Number of Hinge instances that have already been created.
    number_of_instances = 0
    
  
    # constructor
    def __init__(self,
        PARENT_NODE = None,
        DIAMETER = 0.1, # in meter
        LENGTH = 0.1, # in meter
        ROT_OFFSET_MAT = avango.gua.make_identity_mat(), # the rotation offset relative to the parent coordinate system
        ):

        ## get unique id for this instance
        self.id = Arm.number_of_instances
        Arm.number_of_instances += 1


        ### resources ###
        
        self.arm_start_node = avango.gua.nodes.TransformNode(Name = "arm{0}_start_node".format(str(self.id)))
        self.arm_start_node.Transform.value = ROT_OFFSET_MAT
        PARENT_NODE.Children.value.append(self.arm_start_node)


        self.arm_end_node = avango.gua.nodes.TransformNode(Name = "arm{0}_end_node".format(str(self.id)))
        self.arm_end_node.Transform.value = avango.gua.make_trans_mat(0.0, LENGTH, 0.0)
        self.arm_start_node.Children.value.append(self.arm_end_node)


        _loader = avango.gua.nodes.TriMeshLoader() # get trimesh loader to load external tri-meshes

        self.arm_geometry = _loader.create_geometry_from_file("arm{0}_geometry".format(str(self.id)), "data/objects/cylinder.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.arm_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.0, LENGTH * 0.5, 0.0) * \
            avango.gua.make_scale_mat(DIAMETER, LENGTH, DIAMETER)
        self.arm_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(0.45,0.45,0.45,1.0))
        self.arm_start_node.Children.value.append(self.arm_geometry)
            
