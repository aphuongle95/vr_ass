#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

### import python libraries
# ...
   
class SteeringNavigation(avango.script.Script):

    ### fields ###

    ## input fields
    mf_dof = avango.MFFloat()
    mf_dof.value = [0.0,0.0,0.0,0.0,0.0,0.0,0.0] # init 7 channels

    ## output fields
    sf_nav_mat = avango.gua.SFMatrix4()
    sf_nav_mat.value = avango.gua.make_identity_mat()

    
    ### constructor
    def __init__(self):
        self.super(SteeringNavigation).__init__() # call base-class constructor

        ### parameters ###
        self.rot_center_offset = avango.gua.Vec3(0.0,0.0,0.0)

        self.translation_factor = 1.0
        self.rotation_factor = 1.0        


    def my_constructor(self, MF_DOF, MF_BUTTONS, TRANSLATION_FACTOR = 1.0, ROTATION_FACTOR = 1.0):
        self.mf_dof.connect_from(MF_DOF)
        
        self.translation_factor = TRANSLATION_FACTOR
        self.rotation_factor = ROTATION_FACTOR

    
    ### callback functions ###
    @field_has_changed(mf_dof)
    def mf_dof_changed(self):
        ## handle translation input
        _x = self.mf_dof.value[0]
        _y = self.mf_dof.value[1]
        _z = self.mf_dof.value[2]

        _trans_vec = avango.gua.Vec3(_x, _y, _z) * self.translation_factor
        _trans_input = _trans_vec.length()

        #print(_trans_input)
         
        if _trans_input > 0.0:
            ## transfer-function for translation
            _factor = pow(min(_trans_input,1.0), 2)

            _trans_vec.normalize()
            _trans_vec *= _factor


        ## handle rotation input
        _rx = self.mf_dof.value[3]
        _ry = self.mf_dof.value[4]
        _rz = self.mf_dof.value[5]

        _rot_vec = avango.gua.Vec3(_rx, _ry, _rz) * self.rotation_factor
        _rot_input = _rot_vec.length()

        if _rot_input > 0.0:
            ## transfer-function for rotation
            _factor = pow(_rot_input, 2)

            _rot_vec.normalize()
            _rot_vec *= _factor

             
        if _trans_input or _rot_input > 0.0:
            ## accumulate input
            self.sf_nav_mat.value = \
                self.sf_nav_mat.value * \
                avango.gua.make_trans_mat(_trans_vec) * \
                avango.gua.make_trans_mat(self.rot_center_offset) * \
                avango.gua.make_rot_mat(_rot_vec.y,0,1,0) * \
                avango.gua.make_rot_mat(_rot_vec.x,1,0,0) * \
                avango.gua.make_rot_mat(_rot_vec.z,0,0,1) * \
                avango.gua.make_trans_mat(self.rot_center_offset * -1)

        

    ### functions ###
    def set_start_transformation(self, MAT4):
        self.sf_nav_mat.value = MAT4

  
    def set_rotation_center_offset(self, VEC3): 
        self.rot_center_offset = VEC3

