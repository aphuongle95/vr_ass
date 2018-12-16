#!/usr/bin/python

## @file
# Contains class ViveNavigation.

### import avango-guacamole libraries
import avango
import avango.gua
import avango.script

### import framework libraries
from lib.navigations.Navigation import Navigation

### import python libraries
import math
import time
import builtins


class ViveNavigationScript(avango.script.Script):

  ### input fields ###
  sf_user_tracking_mat = avango.gua.SFMatrix4()
  sf_forward_mat = avango.gua.SFMatrix4()
  sf_throttle = avango.SFFloat() # between zero and one


  ### Default constructor.
  def __init__(self):
    self.super(ViveNavigationScript).__init__()
    self.max_speed = 13.88 # meters per second
    self.lf_time = time.time()
    self.CLASS = None


  def my_constructor(self, CLASS):
    self.CLASS = CLASS
    self.always_evaluate(True)


  ### callbacks ###
  def evaluate(self):
    elapsed = time.time()-self.lf_time

    forward_yaw = self.get_yaw(self.sf_forward_mat.value) * 180.0/math.pi
    rot_mat = avango.gua.make_rot_mat(forward_yaw, 0, 1, 0)
    
    speed_input = self.sf_throttle.value * self.max_speed
    trans_input = avango.gua.Vec3(0.0, 0.0, -speed_input * elapsed)
    rotated_trans_input = rot_mat * trans_input

    self.CLASS.map_movement_input(rotated_trans_input.x, 
                                  rotated_trans_input.y, 
                                  rotated_trans_input.z)

    self.lf_time = time.time()

  def get_yaw(self, MATRIX):
    # compute the current yaw angle of the given matrix
    forward_mat = MATRIX * avango.gua.make_trans_mat(0.0, 0.0, -1.0)
    mat_trans = MATRIX.get_translate()
    forward_trans = forward_mat.get_translate()
    diff_translate_without_y = avango.gua.Vec3(forward_trans.x-mat_trans.x, 
                                                                       0.0,
                                                forward_trans.z-mat_trans.z)
    diff_translate_without_y.normalize()
    yaw = math.atan2(-1.0, 0.0) - math.atan2(diff_translate_without_y.z, diff_translate_without_y.x)
    return yaw
          


class ViveNavigation(Navigation):

  ### constructor
  def __init__(self
              , MATRIX = avango.gua.make_identity_mat()
              ):
         
    # call base class constructor
    Navigation.__init__(self, MATRIX = MATRIX)

    ## init script
    self.script = ViveNavigationScript()
    self.script.my_constructor(self)


  ### functions ###
  def assign_input(self, SF_USER_TRACKING_MAT, SF_FORWARD_MAT, SF_THROTTLE):
    self.script.sf_user_tracking_mat.connect_from(SF_USER_TRACKING_MAT)
    self.script.sf_forward_mat.connect_from(SF_FORWARD_MAT)
    self.script.sf_throttle.connect_from(SF_THROTTLE)


  def get_forward_mat(self):
    return self.script.sf_forward_mat.value

 
  def map_movement_input(self, X, Y, Z):
    _trans_vec = avango.gua.Vec3(X, Y, Z)
    _trans_input = _trans_vec.length()
    
    if _trans_input < 0.01:
      return

    _ref_rot_mat = avango.gua.make_rot_mat(avango.gua.make_identity_mat().get_rotate_scale_corrected())

    if _trans_input != 0.0: # transfer function for translation            
      _trans_vec = _ref_rot_mat * _trans_vec # transform into reference orientation (e.g. input device orientation)
      _trans_vec = avango.gua.Vec3(_trans_vec.x, _trans_vec.y, _trans_vec.z)

    _nav_mat = Navigation.get_nav_mat(self)

    # map input
    _nav_mat = _nav_mat * avango.gua.make_trans_mat(_trans_vec) 
    Navigation.set_nav_mat(self, _nav_mat)
