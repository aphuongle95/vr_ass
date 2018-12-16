#!/usr/bin/python3

## import avango-guacamole libraries
import avango
import avango.gua
import avango.daemon
from avango.script import field_has_changed

## import framework libraries
from lib.navigations.ViveNavigation import ViveNavigation
from lib.ViveViewingSetup import ViveViewingSetup

## import python libraries
import builtins


class VivePlatform(avango.script.Script):

    sf_platform_mat = avango.gua.SFMatrix4()
    sf_platform_mat.value = avango.gua.make_identity_mat()


    def __init__(self):
        self.super(VivePlatform).__init__()
        self.viewing_setup = None


    def my_constructor(self, PARENT_NODE, TRACKING_NAME_BASE):
        self.hmd_service = avango.daemon.DeviceService()
        self.hmd_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = self.hmd_service)
        self.hmd_sensor.Station.value = TRACKING_NAME_BASE + "-0"
        self.controller1_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = self.hmd_service)
        self.controller1_sensor.Station.value = TRACKING_NAME_BASE + "-1"

        self.navigation_node = avango.gua.nodes.TransformNode(Name = "navigation")
        self.navigation_node.Transform.connect_from(self.sf_platform_mat)
        PARENT_NODE.Children.value.append(self.navigation_node)

        self.create_vive_models()

        self.viewing_setup = ViveViewingSetup(PARENT_NODE = self.navigation_node,
                                              SCENEGRAPH = builtins.SCENEGRAPH,
                                              BLACK_LIST = ['invisible'])
   
        self.navigation = ViveNavigation(MATRIX = avango.gua.make_identity_mat())
        self.navigation.assign_input(SF_USER_TRACKING_MAT = self.hmd_sensor.Matrix,
                                              SF_FORWARD_MAT = self.controller1_sensor.Matrix,
                                              SF_THROTTLE = self.controller1_sensor.Value3)
        self.sf_platform_mat.connect_from(self.navigation.get_nav_mat_field())


    def get_navigation_node(self):
        return self.navigation_node


    def get_head_node(self):
        return self.viewing_setup.head_node


    def create_vive_models(self):
        loader = avango.gua.nodes.TriMeshLoader()

        self.controller1 = loader.create_geometry_from_file(
            "controller1",
            "data/objects/vive_controller/vive_controller.obj",
            avango.gua.LoaderFlags.LOAD_MATERIALS)

        self.controller1.Material.value.set_uniform("Roughness", 0.8)
        self.controller1.Material.value.set_uniform("ColorMap", "data/objects/vive_controller/onepointfive_texture.png")
        self.controller1.ShadowMode.value = avango.gua.ShadowMode.OFF

        self.hmd_trans = avango.gua.nodes.TransformNode(Name="hmd_trans")
        self.hmd_trans.Transform.connect_from(self.hmd_sensor.Matrix)

        self.controller1_trans = avango.gua.nodes.TransformNode(Name="controller1_trans")
        self.controller1_trans.Transform.connect_from(self.controller1_sensor.Matrix)
        self.navigation_node.Children.value.append(self.controller1_trans)
        self.controller1_trans.Children.value.append(self.controller1)


    def run_viewer(self, LOCALS, GLOBALS):
        self.viewing_setup.run(LOCALS, GLOBALS)
