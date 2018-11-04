#!/usr/bin/python3

### import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed


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
        self.translation_factor = 1.0
        self.rotation_factor = 1.0        


    def my_constructor(self, MF_DOF, TRANSLATION_FACTOR = 1.0, ROTATION_FACTOR = 1.0):
        self.mf_dof.connect_from(MF_DOF)
        
        self.translation_factor = TRANSLATION_FACTOR
        self.rotation_factor = ROTATION_FACTOR

    
    ### callback functions ###
    @field_has_changed(mf_dof)
    def mf_dof_changed(self):                
        ## handle translation input
        x = self.mf_dof.value[0]
        y = self.mf_dof.value[1]
        z = self.mf_dof.value[2]

        trans_vec = avango.gua.Vec3(x, y, z) * self.translation_factor
        trans_input = trans_vec.length()

        if trans_input > 0.0:
            ## transfer-function for translation
            factor = pow(min(trans_input,1.0), 2)
            trans_vec.normalize()
            trans_vec *= factor


        ## handle rotation input
        rx = self.mf_dof.value[3]
        ry = self.mf_dof.value[4]
        rz = self.mf_dof.value[5]

        rot_vec = avango.gua.Vec3(rx, ry, rz) * self.rotation_factor
        rot_input = rot_vec.length()

        if rot_input > 0.0:
            ## transfer-function for rotation
            factor = pow(rot_input, 2)
            rot_vec.normalize()
            rot_vec *= factor

             
        if trans_input or rot_input > 0.0:
            ## accumulate input
            self.sf_nav_mat.value = \
                self.sf_nav_mat.value * \
                avango.gua.make_trans_mat(trans_vec) * \
                avango.gua.make_rot_mat(rot_vec.y,0,1,0) * \
                avango.gua.make_rot_mat(rot_vec.x,1,0,0) * \
                avango.gua.make_rot_mat(rot_vec.z,0,0,1)
        

    ### functions ###
    def set_start_transformation(self, MAT4):
        self.sf_nav_mat.value = MAT4

  
    def set_rotation_center_offset(self, VEC3): 
        self.rot_center_offset = VEC3

