#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua
import avango.script


class PointerInput(avango.script.Script):

    ## input fields
    sf_button0 = avango.SFBool()
    sf_toggle_button = avango.SFBool()
    sf_pointer_mat = avango.gua.SFMatrix4()

    ## Default constructor.
    def __init__(self):
        self.super(PointerInput).__init__()


    def init_art_pointer(self, POINTER_TRACKING_STATION, TRACKING_TRANSMITTER_OFFSET, POINTER_DEVICE_STATION, KEYBOARD_STATION):
    
        ## init sensors
        self.pointer_tracking_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.pointer_tracking_sensor.Station.value = POINTER_TRACKING_STATION
        self.pointer_tracking_sensor.TransmitterOffset.value = TRACKING_TRANSMITTER_OFFSET
        self.pointer_tracking_sensor.ReceiverOffset.value = avango.gua.make_trans_mat(0.0,0.0,-0.1)
            
        self.pointer_device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.pointer_device_sensor.Station.value = POINTER_DEVICE_STATION
        
        self.keyboard_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.keyboard_sensor.Station.value = KEYBOARD_STATION
        
        ### init field connections
        self.sf_button0.connect_from(self.pointer_device_sensor.Button0)
        self.sf_toggle_button.connect_from(self.keyboard_sensor.Button16)
        self.sf_pointer_mat.connect_from(self.pointer_tracking_sensor.Matrix)
        

    def init_vive_pointer(self, TRACKING_NAME_BASE):

        ## init sensors
        self.hmd_service = avango.daemon.DeviceService()
        self.hmd_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = self.hmd_service)
        self.hmd_sensor.Station.value = TRACKING_NAME_BASE + "-0"
        self.controller1_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = self.hmd_service)
        self.controller1_sensor.Station.value = TRACKING_NAME_BASE + "-1"

        ### init field connections
        self.sf_button0.connect_from(self.controller1_sensor.Button4)
        self.sf_toggle_button.connect_from(self.controller1_sensor.Button2)
        self.sf_pointer_mat.connect_from(self.controller1_sensor.Matrix)