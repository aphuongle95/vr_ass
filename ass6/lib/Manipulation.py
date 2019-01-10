#!/usr/bin/python

### import guacamole libraries ###
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.daemon

### import python libraries ###
import math
import sys


class ManipulationManager(avango.script.Script):

    ## input fields
    sf_toggle_button = avango.SFBool()

    ## constructor
    def __init__(self):
        self.super(ManipulationManager).__init__()


    def my_constructor(self,
        SCENEGRAPH = None,
        NAVIGATION_NODE = None,
        HEAD_NODE = None,
        POINTER_INPUT = None,
        ):


        ### variables ###
        self.active_manipulation_technique = None
        self.active_manipulation_technique_index = None
        self.sf_toggle_button.connect_from(POINTER_INPUT.sf_toggle_button)


        ## init manipulation techniques
        self.ray = Ray()
        self.ray.my_constructor(SCENEGRAPH, NAVIGATION_NODE, POINTER_INPUT)


        self.depthRay = DepthRay()
        self.depthRay.my_constructor(SCENEGRAPH, NAVIGATION_NODE, POINTER_INPUT)


        self.goGo = GoGo()
        self.goGo.my_constructor(SCENEGRAPH, NAVIGATION_NODE, HEAD_NODE, POINTER_INPUT)


        self.virtualHand = VirtualHand()
        self.virtualHand.my_constructor(SCENEGRAPH, NAVIGATION_NODE, POINTER_INPUT)


        ### set initial states ###
        self.set_manipulation_technique(1) # switch to virtual-ray manipulation technique



    ### functions ###
    def set_manipulation_technique(self, INT):
        # possibly disable prior technique
        if self.active_manipulation_technique is not None:
            self.active_manipulation_technique.enable(False)

        # enable new technique
        if INT == 0: # ray
            print("switch to Ray technique")
            self.active_manipulation_technique = self.ray

        elif INT == 1: # depth ray
            print("switch to Depth-Ray technique")
            self.active_manipulation_technique = self.depthRay

        elif INT == 2: # go-go
            print("switch to Go-Go technique")
            self.active_manipulation_technique = self.goGo

        elif INT == 3: # HOMER
            print("switch to Virtual-Hand (PRISM) technique")
            self.active_manipulation_technique = self.virtualHand

        self.active_manipulation_technique_index = INT
        self.active_manipulation_technique.enable(True)


    ### callback functions ###
    @field_has_changed(sf_toggle_button)
    def sf_toggle_button_changed(self):
        if self.sf_toggle_button.value == True: # key is pressed
            next_index = (self.active_manipulation_technique_index + 1) % 4
            self.set_manipulation_technique(next_index) # switch to Ray manipulation technique



class ManipulationTechnique(avango.script.Script):

    ## input fields
    sf_button = avango.SFBool()

    ## constructor
    def __init__(self):
        self.super(ManipulationTechnique).__init__()


    def my_constructor(self,
        SCENEGRAPH = None,
        NAVIGATION_NODE = None,
        POINTER_INPUT = None,
        ):


        ### external references ###
        self.SCENEGRAPH = SCENEGRAPH
        self.POINTER_INPUT = POINTER_INPUT


        ### variables ###
        self.enable_flag = False

        self.selected_node = None
        self.dragged_node = None
        self.dragging_offset_mat = avango.gua.make_identity_mat()

        self.mf_pick_result = []
        self.pick_result = None # chosen pick result
        self.white_list = []
        self.black_list = ["invisible"]

        #self.pick_options = avango.gua.PickingOptions.PICK_ONLY_FIRST_OBJECT \
        #                    | avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE \
        #                    | avango.gua.PickingOptions.GET_POSITIONS \
        #                    | avango.gua.PickingOptions.GET_NORMALS \
        #                    | avango.gua.PickingOptions.GET_WORLD_POSITIONS \
        #                    | avango.gua.PickingOptions.GET_WORLD_NORMALS

        self.pick_options = avango.gua.PickingOptions.PICK_ONLY_FIRST_FACE \
                            | avango.gua.PickingOptions.GET_POSITIONS \
                            | avango.gua.PickingOptions.GET_NORMALS \
                            | avango.gua.PickingOptions.GET_WORLD_POSITIONS \
                            | avango.gua.PickingOptions.GET_WORLD_NORMALS



        ### resources ###

        ## init nodes
        self.pointer_node = avango.gua.nodes.TransformNode(Name = "pointer_node")
        self.pointer_node.Tags.value = ["invisible"]
        NAVIGATION_NODE.Children.value.append(self.pointer_node)


        self.ray = avango.gua.nodes.Ray() # required for trimesh intersection

        ## init field connections
        self.sf_button.connect_from(self.POINTER_INPUT.sf_button0)
        self.pointer_node.Transform.connect_from(self.POINTER_INPUT.sf_pointer_mat)

        self.always_evaluate(True) # change global evaluation policy


    ### functions ###
    def enable(self, BOOL):
        self.enable_flag = BOOL

        if self.enable_flag == True:
            self.pointer_node.Tags.value = [] # set tool visible
        else:
            self.stop_dragging() # possibly stop active dragging process

            self.pointer_node.Tags.value = ["invisible"] # set tool invisible


    def start_dragging(self, NODE):
        self.dragged_node = NODE
        self.dragging_offset_mat = avango.gua.make_inverse_mat(self.pointer_node.WorldTransform.value) * self.dragged_node.WorldTransform.value # object transformation in pointer coordinate system


    def stop_dragging(self):
        self.dragged_node = None
        self.dragging_offset_mat = avango.gua.make_identity_mat()


    def dragging(self):
        if self.dragged_node is not None: # object to drag
            _new_mat = self.pointer_node.WorldTransform.value * self.dragging_offset_mat # new object position in world coodinates
            _new_mat = avango.gua.make_inverse_mat(self.dragged_node.Parent.value.WorldTransform.value) * _new_mat # transform new object matrix from global to local space

            self.dragged_node.Transform.value = _new_mat


    def get_roll_angle(self, MAT4):
        _dir_vec = avango.gua.make_rot_mat(MAT4.get_rotate()) * avango.gua.Vec3(0.0,0.0,-1.0)
        _dir_vec = avango.gua.Vec3(_dir_vec.x, _dir_vec.y, _dir_vec.z) # cast to Vec3

        _ref_side_vec = avango.gua.Vec3(1.0,0.0,0.0)

        _up_vec = _dir_vec.cross(_ref_side_vec)
        _up_vec.normalize()
        _ref_side_vec = _up_vec.cross(_dir_vec)
        _ref_side_vec.normalize()

        _side_vec = avango.gua.make_rot_mat(MAT4.get_rotate()) * avango.gua.Vec3(1.0,0.0,0.0)
        _side_vec = avango.gua.Vec3(_side_vec.x, _side_vec.y, _side_vec.z) # cast to Vec3
        #print(_ref_side_vec, _side_vec)

        _axis = _ref_side_vec.cross(_side_vec)
        _axis.normalize()

        _angle = math.degrees(math.acos(min(max(_ref_side_vec.dot(_side_vec), -1.0), 1.0)))
        #print(_angle)

        if _side_vec.y > 0.0: # simulate rotation direction
            _angle *= -1.0

        return _angle



    def update_intersection(self, PICK_MAT = avango.gua.make_identity_mat(), PICK_LENGTH = 1.0):
        # update ray parameters
        self.ray.Origin.value = PICK_MAT.get_translate()

        _vec = avango.gua.make_rot_mat(PICK_MAT.get_rotate_scale_corrected()) * avango.gua.Vec3(0.0,0.0,-1.0) #?
        _vec = avango.gua.Vec3(_vec.x,_vec.y,_vec.z) #?

        self.ray.Direction.value = _vec * PICK_LENGTH

        ## trimesh intersection
        self.mf_pick_result = self.SCENEGRAPH.ray_test(self.ray, self.pick_options, self.white_list, self.black_list)



    def selection(self):
        if len(self.mf_pick_result.value) > 0: # intersection found
            self.pick_result = self.mf_pick_result.value[0] # get first pick result

        else: # nothing hit
            self.pick_result = None


        ## disable previous node highlighting
        if self.selected_node is not None:
            for _child_node in self.selected_node.Children.value:
                if _child_node.get_type() == 'av::gua::TriMeshNode':
                    _child_node.Material.value.set_uniform("enable_color_override", False)


        if self.pick_result is not None: # something was hit
            self.selected_node = self.pick_result.Object.value # get intersected geometry node
            self.selected_node = self.selected_node.Parent.value # take the parent node of the geomtry node (the whole object)

        else:
            self.selected_node = None


        ## enable node highlighting
        if self.selected_node is not None:
            for _child_node in self.selected_node.Children.value:
                if _child_node.get_type() == 'av::gua::TriMeshNode':
                    _child_node.Material.value.set_uniform("enable_color_override", True)
                    _child_node.Material.value.set_uniform("override_color", avango.gua.Vec4(1.0,0.0,0.0,0.3)) # 30% color override



    ### callback functions ###

    @field_has_changed(sf_button)
    def sf_button_changed(self):
        if self.sf_button.value == True: # button pressed
            if self.selected_node is not None:
                self.start_dragging(self.selected_node)

        else: # button released
            self.stop_dragging()


    def evaluate(self): # evaluated every frame
        raise NotImplementedError("To be implemented by a subclass.")



class Ray(ManipulationTechnique):

    ## constructor
    def __init__(self):
        self.super(Ray).__init__()


    def my_constructor(self,
        SCENEGRAPH = None,
        NAVIGATION_NODE = None,
        POINTER_INPUT = None,
        ):

        ManipulationTechnique.my_constructor(self, SCENEGRAPH, NAVIGATION_NODE, POINTER_INPUT) # call base-class constructor


        ### parameters ###
        self.ray_length = 2.5 # in meter
        self.ray_thickness = 0.01 # in meter

        self.intersection_point_size = 0.03 # in meter


        ### resources ###
        _loader = avango.gua.nodes.TriMeshLoader()

        self.ray_geometry = _loader.create_geometry_from_file("ray_geometry", "data/objects/cylinder.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.ray_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.0,0.0,self.ray_length * -0.5) * \
            avango.gua.make_scale_mat(self.ray_thickness, self.ray_thickness, self.ray_length)
        self.ray_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0,0.0,0.0,1.0))
        self.pointer_node.Children.value.append(self.ray_geometry)


        self.intersection_geometry = _loader.create_geometry_from_file("intersection_geometry", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.intersection_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0,0.0,0.0,1.0))
        SCENEGRAPH.Root.value.Children.value.append(self.intersection_geometry)


        ### set initial states ###
        self.enable(False)



    ### functions ###
    def enable(self, BOOL): # extend respective base-class function
        ManipulationTechnique.enable(self, BOOL) # call base-class function

        if self.enable_flag == False:
            self.intersection_geometry.Tags.value = ["invisible"] # set intersection point invisible


    def update_ray_visualization(self, PICK_WORLD_POS = None, PICK_DISTANCE = 0.0):
        if PICK_WORLD_POS is None: # nothing hit
            # set ray to default length
            self.ray_geometry.Transform.value = \
                avango.gua.make_trans_mat(0.0,0.0,self.ray_length * -0.5) * \
                avango.gua.make_scale_mat(self.ray_thickness, self.ray_thickness, self.ray_length)

            self.intersection_geometry.Tags.value = ["invisible"] # set intersection point invisible

        else: # something hit
            # update ray length and intersection point
            self.ray_geometry.Transform.value = \
                avango.gua.make_trans_mat(0.0,0.0,PICK_DISTANCE * -0.5) * \
                avango.gua.make_scale_mat(self.ray_thickness, self.ray_thickness, PICK_DISTANCE)

            self.intersection_geometry.Tags.value = [] # set intersection point visible
            self.intersection_geometry.Transform.value = avango.gua.make_trans_mat(PICK_WORLD_POS) * avango.gua.make_scale_mat(self.intersection_point_size)


    ### callback functions ###
    def evaluate(self): # implement respective base-class function
        if self.enable_flag == False:
            return


        ## calc ray intersection
        ManipulationTechnique.update_intersection(self, PICK_MAT = self.pointer_node.WorldTransform.value, PICK_LENGTH = self.ray_length) # call base-class function

        ## update object selection
        ManipulationTechnique.selection(self) # call base-class function

        ## update visualizations
        if self.pick_result is None:
            self.update_ray_visualization() # apply default ray visualization
        else:
            _node = self.pick_result.Object.value # get intersected geometry node

            _pick_pos = self.pick_result.Position.value # pick position in object coordinate system
            _pick_world_pos = self.pick_result.WorldPosition.value # pick position in world coordinate system

            _distance = self.pick_result.Distance.value * self.ray_length # pick distance in ray coordinate system

            #print(_node, _pick_pos, _pick_world_pos, _distance)

            self.update_ray_visualization(PICK_WORLD_POS = _pick_world_pos, PICK_DISTANCE = _distance)


        ## possibly perform object dragging
        ManipulationTechnique.dragging(self) # call base-class function



class DepthRay(ManipulationTechnique):

    ## constructor
    def __init__(self):
        self.super(DepthRay).__init__()


    def my_constructor(self,
        SCENEGRAPH = None,
        NAVIGATION_NODE = None,
        POINTER_INPUT = None,
        ):

        ManipulationTechnique.my_constructor(self, SCENEGRAPH, NAVIGATION_NODE, POINTER_INPUT) # call base-class constructor


        ### parameters ###
        self.ray_length = 2.5 # in meter
        self.ray_thickness = 0.01 # in meter
        self.depth_marker_size = 0.03
        self.marker_point_size = 0.03 # in meter
        self.marker_distance = 0
        self.selected_nodes = []
        self.intersect_results = []

        ### resources ###

        ## To-Do: init (geometry) nodes here
        _loader = avango.gua.nodes.TriMeshLoader()

        self.ray_geometry = _loader.create_geometry_from_file("ray_geometry", "data/objects/cylinder.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.ray_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.0,0.0,self.ray_length * -0.5) * \
            avango.gua.make_scale_mat(self.ray_thickness, self.ray_thickness, self.ray_length)
        self.ray_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(0.0,1.0,0.0,1.0))
        self.pointer_node.Children.value.append(self.ray_geometry)

        # self.intersection_geometry = _loader.create_geometry_from_file("intersection_geometry", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)
        # self.intersection_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0,0.0,0.0,1.0))
        # SCENEGRAPH.Root.value.Children.value.append(self.intersection_geometry)

        # maker_geometry
        self.maker_geometry = _loader.create_geometry_from_file("intersection_geometry", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.maker_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.0,0.0,0) * \
            avango.gua.make_scale_mat(self.marker_point_size)
        self.maker_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(0.0,0.0,1.0,1.0))
        self.pointer_node.Children.value.append(self.maker_geometry)

        ### set initial states ###
        self.enable(False)


    ### callback functions ###
    def evaluate(self): # implement respective base-class function
        if self.enable_flag == False:
            return
        roll_angle = ManipulationTechnique.get_roll_angle(self, self.pointer_node.Transform.value)
        roll_angle += 180
        self.marker_distance = roll_angle / 360 * self.ray_length * 0.5
        ## To-Do: implement depth ray technique here
        self.maker_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.0,0.0, self.marker_distance * -1.0) * \
            avango.gua.make_scale_mat(self.marker_point_size)

        ## calc ray intersection
        ManipulationTechnique.update_intersection(self, PICK_MAT = self.pointer_node.WorldTransform.value, PICK_LENGTH = self.ray_length) # call base-class function

        ## update object selection
        self.selection() # call base-class function

        ## possibly perform object dragging
        ManipulationTechnique.dragging(self) # call base-class function

    def selection(self):
        if len(self.mf_pick_result.value) > 0: # intersection found
            closet_distance = self.ray_length
            pick_index = 0
            self.intersect_results = []

            # find the closet object to the marker
            for i in range(len(self.mf_pick_result.value)):
                pick_result = self.mf_pick_result.value[i]
                pick_distance = pick_result.Distance.value * self.ray_length
                pick_marker_distance = abs(pick_distance - self.marker_distance)
                if pick_marker_distance < closet_distance:
                    closet_distance = pick_marker_distance
                    self.pick_result = pick_result
                    pick_index = i
                #print("pick_distance", pick_distance)
                #print("marker_distance", self.marker_distance)

            # save objects intersected to a list
            for i in range(len(self.mf_pick_result.value)):
                if i != pick_index:
                    self.intersect_results.append(self.mf_pick_result.value[i])

        else: # nothing hit
            self.pick_result = None

        ## disable previous nodes highlighting
        if len(self.selected_nodes) > 0:
            for selected_node in self.selected_nodes:
                for _child_node in selected_node.Children.value:
                    if _child_node.get_type() == 'av::gua::TriMeshNode':
                        _child_node.Material.value.set_uniform("enable_color_override", False)
        self.selected_nodes = []

        # hightlight picked object
        if self.pick_result is not None:
            self.hightlight(self.pick_result,"red")

        # highlight intersected objects
        if len(self.intersect_results) > 0:
            for intersect_result in self.intersect_results:
                self.hightlight(intersect_result,"green")

    def hightlight(self, hightlight_node, color):
        #print("highlighting", color)
        selected_node = hightlight_node.Object.value # get intersected geometry node
        selected_node = selected_node.Parent.value # take the parent node of the geomtry node (the whole object)
        ## enable node highlighting
        for _child_node in selected_node.Children.value:
            if _child_node.get_type() == 'av::gua::TriMeshNode':
                _child_node.Material.value.set_uniform("enable_color_override", True)
                if color == "red":
                    _child_node.Material.value.set_uniform("override_color", avango.gua.Vec4(1.0,0.0,0.0,0.3)) # 30% color override
                if color == "green":
                    _child_node.Material.value.set_uniform("override_color", avango.gua.Vec4(0.0,1.0,0.0,0.3))
        self.selected_nodes.append(selected_node)

class GoGo(ManipulationTechnique):

    ## constructor
    def __init__(self):
        self.super(GoGo).__init__()


    def my_constructor(self,
        SCENEGRAPH = None,
        NAVIGATION_NODE = None,
        HEAD_NODE = None,
        POINTER_INPUT = None,
        ):

        ManipulationTechnique.my_constructor(self, SCENEGRAPH, NAVIGATION_NODE, POINTER_INPUT) # call base class constructor


        ### external references ###
        self.HEAD_NODE = HEAD_NODE


        ### parameters ###
        self.intersection_point_size = 0.03 # in meter
        self.gogo_threshold = 0.35 # in meter

        self.half_arm = 0.35
        self.scene_length = 5

        # z reach :
        # for control
        c_min = 1.75
        c_max = 0.4
        # for display
        d_min = 0
        d_max = -5

        # for transfer function
        # linear :
        x_l0 = c_min
        x_l1 = c_min - self.half_arm
        self.z_threshold = x_l1
        y_l0 = d_min
        y_l1 = d_min - self.half_arm
        # non-isomophic
        x_n0 = c_min - self.half_arm
        x_n1 = c_max
        y_n0 = d_min - self.half_arm
        y_n1 = d_max
        self.linear_para = self.linear_transfer_function(x_l0,x_l1,y_l0,y_l1)
        self.noniso_para = self.nonisomorphic_function(x_n0,x_n1,y_n0,y_n1)
        ### resources ###

        ## To-Do: init (geometry) nodes here
        ## init hand geometry
        _loader = avango.gua.nodes.TriMeshLoader() # init trimesh loader to load external meshes

        self.hand_geometry = _loader.create_geometry_from_file("hand_geometry", "data/objects/hand.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.hand_rot_scale_mat = \
            avango.gua.make_rot_mat(90.0,1,0,0) * \
            avango.gua.make_scale_mat(0.6)
            # avango.gua.make_trans_mat(0,0,-0.5) * \
        self.hand_geometry.Transform.value = \
            self.hand_rot_scale_mat
        self.hand_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0, 0.86, 0.54, 1.0))
        self.hand_geometry.Material.value.set_uniform("Emissivity", 0.9)
        self.hand_geometry.Material.value.set_uniform("Metalness", 0.1)
        self.pointer_node.Children.value.append(self.hand_geometry)

        ### set initial states ###
        self.enable(False)



    ### callback functions ###
    def evaluate(self): # implement respective base-class function
        if self.enable_flag == False:
            return

        ## To-Do: implement Go-Go technique here
        # get pointer node translation
        trans = self.pointer_node.WorldTransform.value.get_translate()
        print(trans)

        x = trans[0] # + 0.07
        y = trans[1] # - 0.10
        z = trans[2] # - 0.35

        if(z>self.z_threshold):
            #linear
            (a,b) = self.linear_para
            z2 = a * z + b
        else:
            #non-iso
            (a,b,c) = self.noniso_para
            z2 = a * z * z + b * z + c
        self.hand_geometry.Transform.value = \
            avango.gua.make_inverse_mat(avango.gua.make_trans_mat(trans)) * \
            avango.gua.make_trans_mat(x, y, z2) * \
            self.hand_rot_scale_mat

    def linear_transfer_function(self, x0, y0, x1, y1):
        # linear transfer function looks like this: y = a*x + b
        # to calculate a,b
        # a = (y1 - y0) / (x1 - x0)
        # b = y0 - ax0
        a = (y1 - y0) / (x1 - x0)
        b = y0 - a*x0
        return (a,b)

    def nonisomorphic_function(self, x0, y0, x1, y1):
        # lets this function to be quadratic function: y = a*x*x + bx + c
        # to calculate a,b,c
        # first y = a * (x-x0)^2 + y0
        # a = (y1-y0)/(x1-x0)^2
        a = (y1-y0)/((x1-x0) * (x1-x0))
        b = -2 * a * x0
        c = a*x0*x0 + y0
        return (a,b,c)

class VirtualHand(ManipulationTechnique):

    ## constructor
    def __init__(self):
        self.super(ManipulationTechnique).__init__()


    def my_constructor(self,
        SCENEGRAPH = None,
        NAVIGATION_NODE = None,
        POINTER_INPUT = None
        ):

        ManipulationTechnique.my_constructor(self, SCENEGRAPH, NAVIGATION_NODE, POINTER_INPUT) # call base-class constructor


        ### parameters ###
        self.intersection_point_size = 0.03 # in meter

        self.min_vel = 0.01 / 60.0 # in meter/sec
        self.sc_vel = 0.15 / 60.0 # in meter/sec
        self.max_vel = 0.25 / 60.0 # in meter/sec


        ### resources ###

        ## To-Do: init (geometry) nodes here

        ### set initial states ###
        self.enable(False)


    ### callback functions ###
    def evaluate(self): # implement respective base-class function
        if self.enable_flag == False:
            return

        ## To-Do: implement Virtual Hand (with PRISM filter) technique here
