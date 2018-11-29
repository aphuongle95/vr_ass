#!/usr/bin/python

#### import guacamole libraries
import avango
import avango.gua 
import avango.script
from avango.script import field_has_changed
import avango.daemon

### import application libraries
from lib.Device import MouseInput, BlueSpacemouseInput

   
class ManipulationManager(avango.script.Script):

    ### input fields
    sf_key_1 = avango.SFBool()
    sf_key_2 = avango.SFBool()
    sf_key_3 = avango.SFBool()
    sf_key_4 = avango.SFBool()
    sf_key_5 = avango.SFBool()
    sf_key_6 = avango.SFBool()            

    sf_hand_mat = avango.gua.SFMatrix4()
    sf_dragging_trigger = avango.SFBool()


    # constructor
    def __init__(self):
        self.super(ManipulationManager).__init__()
    

    def my_constructor(self,
        PARENT_NODE = None,
        SCENE_ROOT = None,
        TARGET_LIST = [],
        ):
        

        ### external references ###        
        self.SCENE_ROOT = SCENE_ROOT
        self.TARGET_LIST = TARGET_LIST


        ### variables ###
        self.dragged_objects_list = []
        self.lf_hand_mat = avango.gua.make_identity_mat() # last frame hand matrix

        
        ## init hand geometry
        _loader = avango.gua.nodes.TriMeshLoader() # init trimesh loader to load external meshes
        
        self.hand_geometry = _loader.create_geometry_from_file("hand_geometry", "data/objects/hand.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.hand_geometry.Transform.value = \
            avango.gua.make_rot_mat(45.0,1,0,0) * \
            avango.gua.make_rot_mat(180.0,0,1,0) * \
            avango.gua.make_scale_mat(0.06)
        self.hand_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(1.0, 0.86, 0.54, 1.0))
        self.hand_geometry.Material.value.set_uniform("Emissivity", 0.9)
        self.hand_geometry.Material.value.set_uniform("Metalness", 0.1)  
        
        self.hand_transform = avango.gua.nodes.TransformNode(Name = "hand_transform")
        self.hand_transform.Children.value = [self.hand_geometry]
        PARENT_NODE.Children.value.append(self.hand_transform)
        self.hand_transform.Transform.connect_from(self.sf_hand_mat)
        

        ### init sub-classes ###
        
        ## init inputs
        self.mouseInput = MouseInput()
        self.mouseInput.my_constructor("gua-device-mouse")

        self.spacemouseInput = BlueSpacemouseInput()
        self.spacemouseInput.my_constructor("gua-device-spacemouse")
        

        ## init manipulation techniques
        self.IPCManipulation = IsotonicPositionControlManipulation()
        self.IPCManipulation.my_constructor(self.mouseInput.mf_dof, self.mouseInput.mf_buttons)

        self.EPCManipulation = ElasticPositionControlManipulation()
        self.EPCManipulation.my_constructor(self.spacemouseInput.mf_dof, self.spacemouseInput.mf_buttons)

        self.IRCManipulation = IsotonicRateControlManipulation()
        self.IRCManipulation.my_constructor(self.mouseInput.mf_dof, self.mouseInput.mf_buttons)

        self.ERCManipulation = ElasticRateControlManipulation()
        self.ERCManipulation.my_constructor(self.spacemouseInput.mf_dof, self.spacemouseInput.mf_buttons)

        self.IACManipulation = IsotonicAccelerationControlManipulation()
        self.IACManipulation.my_constructor(self.mouseInput.mf_dof, self.mouseInput.mf_buttons)

        self.EACManipulation = ElasticAccelerationControlManipulation()
        self.EACManipulation.my_constructor(self.spacemouseInput.mf_dof, self.spacemouseInput.mf_buttons)


        ## init keyboard sensor for system control
        self.keyboard_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.keyboard_sensor.Station.value = "gua-device-keyboard0"

        self.sf_key_1.connect_from(self.keyboard_sensor.Button16) # key 1
        self.sf_key_2.connect_from(self.keyboard_sensor.Button17) # key 2
        self.sf_key_3.connect_from(self.keyboard_sensor.Button18) # key 3
        self.sf_key_4.connect_from(self.keyboard_sensor.Button19) # key 4
        self.sf_key_5.connect_from(self.keyboard_sensor.Button20) # key 5
        self.sf_key_6.connect_from(self.keyboard_sensor.Button21) # key 6


        ### set initial states ###
        self.set_manipulation_technique(1) # switch to isotonic position control


    ### functions ###
    def set_manipulation_technique(self, INT):
        self.manipulation_technique = INT

        # disable prior manipulation technique
        self.IPCManipulation.enable_manipulation(False)
        self.EPCManipulation.enable_manipulation(False)
        self.IRCManipulation.enable_manipulation(False)
        self.ERCManipulation.enable_manipulation(False)
        self.IACManipulation.enable_manipulation(False)      
        self.EACManipulation.enable_manipulation(False)
        
        # remove existing field connections    
        self.sf_hand_mat.disconnect()
        self.sf_dragging_trigger.disconnect()
        
        if self.manipulation_technique == 1: # isotonic position control     
            self.IPCManipulation.enable_manipulation(True)

            # init field connections      
            self.sf_hand_mat.connect_from(self.IPCManipulation.sf_mat)
            self.sf_dragging_trigger.connect_from(self.IPCManipulation.sf_action_trigger)
        
        elif self.manipulation_technique == 2: # elastic position control        
            self.EPCManipulation.enable_manipulation(True)

            # init field connections
            self.sf_hand_mat.connect_from(self.EPCManipulation.sf_mat)
            self.sf_dragging_trigger.connect_from(self.EPCManipulation.sf_action_trigger)            
        
        elif self.manipulation_technique == 3: # isotonic rate control        
            self.IRCManipulation.enable_manipulation(True)
        
            # init field connections
            self.sf_hand_mat.connect_from(self.IRCManipulation.sf_mat)
            self.sf_dragging_trigger.connect_from(self.IRCManipulation.sf_action_trigger)
        
        elif self.manipulation_technique == 4: # elastic rate control
            self.ERCManipulation.enable_manipulation(True)

            # init field connections      
            self.sf_hand_mat.connect_from(self.ERCManipulation.sf_mat)
            self.sf_dragging_trigger.connect_from(self.ERCManipulation.sf_action_trigger)
        
        elif self.manipulation_technique == 5: # isotonic acceleration control
            self.IACManipulation.enable_manipulation(True)

            # init field connections      
            self.sf_hand_mat.connect_from(self.IACManipulation.sf_mat)
            self.sf_dragging_trigger.connect_from(self.IACManipulation.sf_action_trigger)

        elif self.manipulation_technique == 6: # elastic acceleration control        
            self.EACManipulation.enable_manipulation(True)

            # init field connections      
            self.sf_hand_mat.connect_from(self.EACManipulation.sf_mat)
            self.sf_dragging_trigger.connect_from(self.EACManipulation.sf_action_trigger)


    ##########################
    ### Exercise 4.2
    ##########################

    ## This function is called when the dragging button 
    ## (e.g. mouse button for isotonic input) is pressed down
    def start_dragging(self):
        _hand_mat = self.hand_transform.WorldTransform.value

        for _node in self.TARGET_LIST:
            if self.is_highlight_material(_node.CurrentColor.value) == True: # a monkey node in close proximity
                _node.CurrentColor.value = avango.gua.Vec4(1.0, 0.0, 0.0, 1.0)
                _node.Material.value.set_uniform("Color", _node.CurrentColor.value) # switch to dragging material
                self.dragged_objects_list.append(_node) # add node for dragging
          
                ## TODO: add code if necessary


    ## This function is called while the dragging button
    ## (e.g. mouse button for isotonic input) is pressed
    def object_dragging(self):
        pass
        ## TODO: add code if necessary

  

    ## This function is called when the dragging button
    ## (e.g. mouse button for isotonic input) is released
    def stop_dragging(self):  
        ## handle all dragged objects
        for _node in self.dragged_objects_list:      
            _node.CurrentColor.value = avango.gua.Vec4(0.0, 1.0, 0.0, 1.0)
            _node.Material.value.set_uniform("Color", _node.CurrentColor.value) # switch to highlight material
    
        self.dragged_objects_list = [] # clear list

        ## TODO: add code if necessary

 
    ########################## End of Exercise 4.2


    def update_dragging_candidates(self):
        _hand_pos = self.hand_transform.WorldTransform.value.get_translate()
    
        for _node in self.TARGET_LIST:
            _pos = _node.Transform.value.get_translate() # a monkey position

            _dist = (_hand_pos - _pos).length() # hand-object distance
            _color = _node.CurrentColor.value

            ## toggle object highlight
            if _dist < 0.025 and self.is_default_material(_color) == True:
                _node.CurrentColor.value = avango.gua.Vec4(0.0, 1.0, 0.0, 1.0)
                _node.Material.value.set_uniform("Color", _node.CurrentColor.value) # switch to highlight material

            elif _dist > 0.03 and self.is_highlight_material(_color) == True:
                _node.CurrentColor.value = avango.gua.Vec4(1.0, 1.0, 1.0, 1.0)
                _node.Material.value.set_uniform("Color", _node.CurrentColor.value) # switch to default material


    def is_default_material(self, VEC4):
        return VEC4.x == 1.0 and VEC4.y == 1.0 and VEC4.z == 1.0 and VEC4.w == 1.0


    def is_highlight_material(self, VEC4):
        return VEC4.x == 0.0 and VEC4.y == 1.0 and VEC4.z == 0.0 and VEC4.w == 1.0


    def is_dragging_material(self, VEC4):
        return VEC4.x == 1.0 and VEC4.y == 0.0 and VEC4.z == 0.0 and VEC4.w == 1.0
      
    
    ### callback functions ###

    @field_has_changed(sf_key_1)
    def sf_key_1_changed(self):
        if self.sf_key_1.value == True: # key is pressed
            self.set_manipulation_technique(1) # switch to isotonic position control
           

    @field_has_changed(sf_key_2)
    def sf_key_2_changed(self):
        if self.sf_key_2.value == True: # key is pressed
            self.set_manipulation_technique(2) # switch to elastic position control


    @field_has_changed(sf_key_3)
    def sf_key_3_changed(self):
        if self.sf_key_3.value == True: # key is pressed
            self.set_manipulation_technique(3) # switch to isotonic rate control


    @field_has_changed(sf_key_4)
    def sf_key_4_changed(self):
        if self.sf_key_4.value == True: # key is pressed
            self.set_manipulation_technique(4) # switch to elastic rate control
      

    @field_has_changed(sf_key_5)
    def sf_key_5_changed(self):
        if self.sf_key_5.value == True: # key is pressed
            self.set_manipulation_technique(5) # switch to isotonic acceleration control


    @field_has_changed(sf_key_6)
    def sf_key_6_changed(self):
        if self.sf_key_6.value == True: # key is pressed
            self.set_manipulation_technique(6) # switch to elastic acceleration control


    @field_has_changed(sf_dragging_trigger)
    def sf_dragging_trigger_changed(self):
        if self.sf_dragging_trigger.value == True:
            self.start_dragging()  
        else:
            self.stop_dragging()
     

    def evaluate(self): # evaluated every frame if any input field has changed (incl. dependency evaluation)
        self.update_dragging_candidates()

        self.object_dragging() # possibly drag object with hand input


        ## print covered distance and hand velocity as debug output
        _distance = (self.sf_hand_mat.value.get_translate() - self.lf_hand_mat.get_translate()).length()
        _velocity = _distance * 60.0 # application loop runs with 60Hz

        ## print speeds per frame and second for testing
        #print(round(_distance, 3), "m/frame  ", round(_velocity, 2), "m/s")
        
        self.lf_hand_mat = self.sf_hand_mat.value
        



class Manipulation(avango.script.Script):

    ### input fields
    mf_dof = avango.MFFloat()
    mf_dof.value = [0.0,0.0,0.0,0.0,0.0,0.0,0.0] # init 7 channels

    mf_buttons = avango.MFBool()
    mf_buttons.value = [False,False] # init 2 channels


    ### output_fields
    sf_mat = avango.gua.SFMatrix4()
    sf_mat.value = avango.gua.make_identity_mat()

    sf_action_trigger = avango.SFBool()
    

    ### constructor
    def __init__(self):
        self.super(Manipulation).__init__()

        ### variables ###
        self.type = ""
        self.enable_flag = False

    
    ### callback functions ###
    def evaluate(self): # evaluated every frame if any input field has changed  
        if self.enable_flag == True:
            self.manipulate()


    @field_has_changed(mf_buttons)
    def mf_buttons_changed(self):
        if self.enable_flag == True:
            _left_button = self.mf_buttons.value[0]
            _right_button = self.mf_buttons.value[1]

            self.sf_action_trigger.value = _left_button ^ _right_button # button left XOR button right

        
    ### functions ###
    def enable_manipulation(self, FLAG):   
        self.enable_flag = FLAG
    
        if self.enable_flag == True:
            print(self.type + " enabled")
    
            self.reset()
      
   
    def manipulate(self):
        raise NotImplementedError("To be implemented by a subclass.")


    def reset(self):
        raise NotImplementedError("To be implemented by a subclass.")
    
    
    def clamp_matrix(self, MATRIX):    
        # clamp translation to certain range (within screen space)
        _x_range = 0.3 # in meter
        _y_range = 0.15 # in meter
        _z_range = 0.15 # in meter    

        MATRIX.set_element(0,3, min(_x_range, max(-_x_range, MATRIX.get_element(0,3)))) # clamp x-axis
        MATRIX.set_element(1,3, min(_y_range, max(-_y_range, MATRIX.get_element(1,3)))) # clamp y-axis
        MATRIX.set_element(2,3, min(_z_range, max(-_z_range, MATRIX.get_element(2,3)))) # clamp z-axis
         
        return MATRIX



### ISOTONIC DEVICE MAPPINGS ##

class IsotonicPositionControlManipulation(Manipulation):

    def my_constructor(self, MF_DOF, MF_BUTTONS):
        self.type = "isotonic-position-control"
    
        # init field connections
        self.mf_dof.connect_from(MF_DOF)
        self.mf_buttons.connect_from(MF_BUTTONS)


    ## implement respective base-class function
    def manipulate(self):
        _x = self.mf_dof.value[0]
        _y = self.mf_dof.value[1]
        _z = self.mf_dof.value[2]
          
        _x *= 0.1
        _y *= 0.1
        _z *= 0.1
       
        # accumulate input
        _new_mat = avango.gua.make_trans_mat(_x, _y, _z) * self.sf_mat.value

        # possibly clamp matrix (to screen space borders)
        _new_mat = self.clamp_matrix(_new_mat)

        self.sf_mat.value = _new_mat # apply new matrix to field
    

    ## implement respective base-class function    
    def reset(self):
        self.sf_mat.value = avango.gua.make_identity_mat() # snap hand back to screen center


##########################
### Exercise 4.3
##########################

class IsotonicRateControlManipulation(Manipulation):

    def my_constructor(self, MF_DOF, MF_BUTTONS):
        self.type = "isotonic-rate-control"
          
        # init field connections
        self.mf_dof.connect_from(MF_DOF)
        self.mf_buttons.connect_from(MF_BUTTONS)


    ## implement respective base-class function
    def manipulate(self):
        pass
        ## TODO: add code
    
    
    ## implement respective base-class function
    def reset(self):
        pass
        ## TODO: add code



class IsotonicAccelerationControlManipulation(Manipulation):

    def my_constructor(self, MF_DOF, MF_BUTTONS):
        self.type = "isotonic-acceleration-control"
      
        # init field connections
        self.mf_dof.connect_from(MF_DOF)
        self.mf_buttons.connect_from(MF_BUTTONS)


    ## implement respective base-class function
    def manipulate(self):
        pass
        ## TODO: add code


    ## implement respective base-class function
    def reset(self):
        pass
        ## TODO: add code

########################## End of Exercise 4.3
    

##########################
### Exercise 4.4
##########################

### ELASTIC DEVICE MAPPINGS ###

class ElasticPositionControlManipulation(Manipulation):

    def my_constructor(self, MF_DOF, MF_BUTTONS):
        self.type = "elastic-position-control"
    
        # init field connections
        self.mf_dof.connect_from(MF_DOF)
        self.mf_buttons.connect_from(MF_BUTTONS)


    ## implement respective base-class function
    def manipulate(self):
        pass
        # TODO: add code


    ## implement respective base-class function
    def reset(self):
        pass
        # TODO: add code


class ElasticRateControlManipulation(Manipulation):

    def my_constructor(self, MF_DOF, MF_BUTTONS):
        self.type = "elastic-rate-control"
      
        # init field connections
        self.mf_dof.connect_from(MF_DOF)
        self.mf_buttons.connect_from(MF_BUTTONS)


    ## implement respective base-class function
    def manipulate(self):
        pass
        # TODO: add code

         
    ## implement respective base-class function
    def reset(self):
        pass
        # TODO: add code


class ElasticAccelerationControlManipulation(Manipulation):

    def my_constructor(self, MF_DOF, MF_BUTTONS):
        self.type = "elastic-acceleration-control"

        # init field connections
        self.mf_dof.connect_from(MF_DOF)
        self.mf_buttons.connect_from(MF_BUTTONS)


    ## implement respective base-class function
    def manipulate(self): 
        pass
        # TODO: add code
             

    ## implement respective base-class function
    def reset(self):
        pass
        # TODO: add code
        
########################## End of Exercise 4.4