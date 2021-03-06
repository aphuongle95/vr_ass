#!/usr/bin/python

### import guacamole libraries ###
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.daemon
import matplotlib.pyplot as plt

### import python libraries ###
import math
import sys
import time

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

        # TODO??? is this correct
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
        self.intersection_point_size = 0.35 # in meter
        self.gogo_threshold = 0.1 # in meter

        # self.plot_transfer_function(c_min, c_max, self.linear_para, self.noniso_para)

        ### resources ###

        # TODO??? quadratic transfer function above threshold? max and min value in virtual world?
        # TODO maybe some initial offset for hand transform
        ## To-Do: init (geometry) nodes here
        ## init hand geometry
        _loader = avango.gua.nodes.TriMeshLoader() # init trimesh loader to load external meshes

        self.hand_geometry = _loader.create_geometry_from_file("hand_geometry", "data/objects/hand.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.hand_scale_mat = \
            avango.gua.make_rot_mat(90.0,1,0,0) * \
            avango.gua.make_scale_mat(0.6)
            # avango.gua.make_trans_mat(0,0,-0.5) * \
        self.hand_geometry.Transform.value = \
            self.hand_scale_mat
        # self.hand_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0, 0.86, 0.54, 1.0))
        self.hand_geometry.Material.value.set_uniform("Emissivity", 0.9)
        self.hand_geometry.Material.value.set_uniform("Metalness", 0.1)
        self.pointer_node.Children.value.append(self.hand_geometry)

        ### set initial states ###
        self.enable(False)

    def set_hightlight(self, selected_node, is_highlight):
        ## disable previous node highlighting
        if(is_highlight):
            if selected_node.get_type() == 'av::gua::TriMeshNode':
                    selected_node.Material.value.set_uniform("enable_color_override", True)
                    selected_node.Material.value.set_uniform("override_color", avango.gua.Vec4(1.0, 0.86, 0.54, 1.0))
        else:
            if selected_node.get_type() == 'av::gua::TriMeshNode':
                    selected_node.Material.value.set_uniform("enable_color_override", False)


    ### callback functions ###
    def evaluate(self): # implement respective base-class function
        if self.enable_flag == False:
            return

        ## To-Do: implement Go-Go technique here
        # get pointer node translation
        pointer_trans = self.pointer_node.Transform.value.get_translate()
        head_trans = self.HEAD_NODE.Transform.value.get_translate()
        pointer_head_trans = pointer_trans-head_trans
        R_r = pointer_head_trans

        # calculate translation for hand object
        R_rx = R_r[0]
        R_ry = R_r[1]
        R_rz = R_r[2]
        (R_vx,is_amp1) = self.transfer_function(R_rx)
        # no y-direction amplification
        (R_vz,is_amp2) = self.transfer_function(R_rz)
        is_amp = True if is_amp1 and is_amp2 else False

        self.set_hightlight(self.hand_geometry, is_amp)
        # update the transform value
        # take node that hand_geometry is child of pointer node
        self.hand_geometry.Transform.value = \
            avango.gua.make_trans_mat(R_vx-R_rx, 0, R_vz-R_rz) * \
            self.hand_scale_mat

    def plot_transfer_function(self, x0, x1, linear_para, noniso_para):
        x_data = [x*0.5 for x in range(int(x0), int(x1))]
        y_data = [self.transfer_function(x, linear_para, noniso_para) for x in x_data]
        plt.scatter(x_data, y_data)
        plt.show()

    def transfer_function(self, x):
        x1 = abs(x)
        d = self.gogo_threshold
        if(x1<d):
            #linear
            return (x, False)
        else:
            #non-iso
            k = 5
            x2 = x1 + k * (x1-d) * (x1-d)
            x2 = -x2 if x<0 else x2
            return (x2, True)



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
        self.ball_point_size = 0.007

        self.min_vel = 0.01 / 60.0 # in meter/sec
        self.sc_vel = 0.15 / 60.0 # in meter/sec
        self.max_vel = 0.25 / 60.0 # in meter/sec
        self.last_time = time.time()
        self.last_pointer_translation = self.pointer_node.Transform.value.get_translate()

        ### resources ###

        ## To-Do: init (geometry) nodes here
        _loader = avango.gua.nodes.TriMeshLoader() # init trimesh loader to load external meshes

        # hand geometry
        self.hand_geometry = _loader.create_geometry_from_file("hand_geometry", "data/objects/hand.obj", avango.gua.LoaderFlags.DEFAULTS)

        self.hand_scale_mat = \
            avango.gua.make_scale_mat(0.5)

        self.hand_geometry.Transform.value = \
            self.hand_scale_mat
        self.hand_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0, 0.86, 0.54, 1.0))

        self.pointer_node.Children.value.append(self.hand_geometry)

        # ball geometry
        self.ball_geometry = _loader.create_geometry_from_file("intersection_geometry", "data/objects/sphere.obj", avango.gua.LoaderFlags.DEFAULTS)

        self.ball_geometry.Transform.value = \
            avango.gua.make_scale_mat(self.ball_point_size)

        self.ball_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0,0.0,0.0,1.0))
        self.pointer_node.Children.value.append(self.ball_geometry)

        ### set initial states ###
        self.enable(False)

    def transfer_function(self, ball_speed, ball_distance, ball_coordinate, hand_coordinate):
        # return the new virtual hand's coordinate
        v = abs(ball_speed)
        T_h = ball_distance
        # T_o is the translation distance of manipulated object
        mins = self.min_vel
        sc = self.sc_vel
        maxs = self.max_vel
        offset = 1.7

        print("v",v)
        print("T_h",T_h)
        print("hand_coordinate")
        print("ball_coordinate")
        print()

        if(v<=mins):
            print("v<=mins")
            # no movement due to unintended motion
            return hand_coordinate
        else:
            # calculate k = C/D Ratio
            if(v<=sc):
                print("v<=sc")
                # small movement in virtual world
                k = (v-sc)*(offset-1)/(mins-sc) + 1
                T_o = 1/k * T_h
                print("T_o",T_o)
                return hand_coordinate + T_o
            elif(v<=maxs):
                print("v<=maxs")
                # 1 to 1 movement in virtual world
                k = 1
                T_o = T_h
                print("T_o",T_o)
                return hand_coordinate + T_o
            else:
                print("v>maxs")
                # align virtual hand with real hand
                return ball_coordinate

    ### callback functions ###
    def evaluate(self): # implement respective base-class function
        if self.enable_flag == False:
            return

        # time
        t = time.time()
        dt = t - self.last_time
        self.last_time = t

        ## To-Do: implement Virtual Hand (with PRISM filter) technique here

        # get pointers and hand translation

        # get translation of pointer and hand object
        pointer_trans = self.pointer_node.WorldTransform.value.get_translate()
        hand_trans = self.hand_geometry.WorldTransform.value.get_translate()
        x1 = hand_trans[0]
        y1 = hand_trans[1]
        z1 = hand_trans[2]

        # loop through x, y, z and calculate new x, y, z for hand using transfer_function
        hand_trans2 = []

        for i in range(3):
            # coordinate, distance and velocity
            x = pointer_trans[i]
            d = x - self.last_pointer_translation[i]
            v = d / dt
            h = hand_trans[i]

            # calculate new translation using transfer_function
            hand_trans2.append(self.transfer_function(ball_speed = v,
                                                 ball_distance = d,
                                                 ball_coordinate = x,
                                                 hand_coordinate = h))

        # update last_pointer_translation for next evaluation
        self.last_pointer_translation = pointer_trans

        # update the transform value
        # take node that hand_geometry is child of pointer node
        x = pointer_trans[0]
        y = pointer_trans[1]
        z = pointer_trans[2]
        # print("pointer: ",x,y,z)
        x2 = hand_trans2[0]
        y2 = hand_trans2[1]
        z2 = hand_trans2[2]
        # print("hand: ", x2,y2,z2)

        self.hand_geometry.WorldTransform.value = \
            avango.gua.make_trans_mat(x2-x, y2-y, z2-z) * \
            self.pointer_node.WorldTransform.value * \
            self.hand_scale_mat
