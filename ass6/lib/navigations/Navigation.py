#!/usr/bin/python

## @file
# Contains base class Navigation.

### import avango-guacamole libraries
import avango
import avango.gua
from avango.script import field_has_changed

### import framework libraries
# ...

### import python libraries
import time


class NavigationScript(avango.script.Script):

    ### input fields ###
    mf_dof = avango.MFFloat()

    ### output fields ###
    sf_nav_mat = avango.gua.SFMatrix4()
    sf_nav_mat.value = avango.gua.make_identity_mat()

    ### Default constructor.
    def __init__(self):
        self.super(NavigationScript).__init__()
        self.CLASS = None

    def my_constructor(self, CLASS):
        # references
        self.CLASS = CLASS
        

## Base class. Not to be instantiated.
class Navigation:

    ### static class variables ###
    number_of_instances = 0

    ## Base constructor.
    def __init__(self, NAME = "", MATRIX = avango.gua.make_identity_mat()):

        self.id = Navigation.number_of_instances
        Navigation.number_of_instances += 1

        ### parameters ###
        self.name = NAME
        self.home_nav_mat = MATRIX

        ### resources ###
        self.bc_script = NavigationScript()
        self.bc_script.my_constructor(self)

        ### set initial states ###
        self.set_nav_mat(MATRIX)


    ### functions ##
    def get_nav_mat(self):
        return self.bc_script.sf_nav_mat.value


    def get_nav_mat_field(self):
        return self.bc_script.sf_nav_mat
        

    def set_nav_mat(self, MATRIX):
        self.bc_script.sf_nav_mat.value = MATRIX