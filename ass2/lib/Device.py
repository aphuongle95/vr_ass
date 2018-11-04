#!/usr/bin/python3

### import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.daemon


class MultiDofInput(avango.script.Script):

    ## output fields
    mf_dof = avango.MFFloat()
    mf_dof.value = [0.0,0.0,0.0,0.0,0.0,0.0,0.0] # init 7 channels

  
    ### functions
    def filter_channel(self, VALUE, OFFSET, MIN, MAX, NEG_THRESHOLD, POS_THRESHOLD):
        VALUE = VALUE - OFFSET
        MIN = MIN - OFFSET
        MAX = MAX - OFFSET

        if VALUE > 0:
            _pos = MAX * POS_THRESHOLD * 0.01

            if VALUE > _pos: # above positive threshold
                VALUE = min( (VALUE - _pos) / (MAX - _pos), 1.0) # normalize interval
            else: # below positive threshold
                VALUE = 0

        elif VALUE < 0:
            _neg = MIN * NEG_THRESHOLD * 0.01

            if VALUE < _neg:
                VALUE = max( (VALUE - _neg) / abs(MIN - _neg), -1.0)
            else: # above negative threshold
                VALUE = 0
          
        return VALUE


class NewSpacemouseInput(MultiDofInput):
 
    def my_constructor(self, DEVICE_STATION):
        ## init device sensors
        self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.device_sensor.Station.value = DEVICE_STATION

        ## init callback triggers
        self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)


    ### callback functions ###    
    def frame_callback(self): # evaluated every frame   
        x = self.device_sensor.Value0.value
        y = self.device_sensor.Value1.value * -1.0
        z = self.device_sensor.Value2.value
        rx = self.device_sensor.Value3.value
        ry = self.device_sensor.Value4.value * -1.0
        rz = self.device_sensor.Value5.value
        
        if x != 0.0:
            x = self.filter_channel(x, 0.0, -350.0, 350.0, 3, 3)
        
        if y != 0.0:
            y = self.filter_channel(y, 0.0, -350.0, 350.0, 3, 3)
          
        if z != 0.0:
            z = self.filter_channel(z, 0.0, -350.0, 350.0, 3, 3)
            
        if rx != 0.0:
            rx = self.filter_channel(rx, 0.0, -350.0, 350.0, 8, 8)
         
        if ry != 0.0:
            ry = self.filter_channel(ry, 0.0, -350.0, 350.0, 8, 8)
        
        if rz != 0.0:
            rz = self.filter_channel(rz, 0.0, -350.0, 350.0, 8, 8)
         
        self.mf_dof.value = [x,y,z,rx,ry,rz,0.0] # propagate input via field connection


class KeyboardInput(MultiDofInput):
   
    def my_constructor(self, DEVICE_STATION):
        ## init device sensors
        self.device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.device_sensor.Station.value = DEVICE_STATION

        ## init callback triggers
        self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)

        
    ### callback functions ###
    def frame_callback(self): # evaluated every frame  
        x = 0.0
        y = 0.0
        z = 0.0
        rx = 0.0
        ry = 0.0
        rz = 0.0

        ## handle button input
        if self.device_sensor.Button0.value == True: # w
            z = -1.0

        if self.device_sensor.Button1.value == True: # a
            x = -1.0

        if self.device_sensor.Button2.value == True: # s
            z = 1.0

        if self.device_sensor.Button3.value == True: # d
            x = 1.0

        if self.device_sensor.Button4.value == True: # arrow left
            ry = 1.0

        if self.device_sensor.Button5.value == True: # arrow right
            ry = -1.0

        if self.device_sensor.Button6.value == True: # arrow up
            rx = -1.0

        if self.device_sensor.Button7.value == True: # arrow down
            rx = 1.0

        if self.device_sensor.Button8.value == True: # q
            rz = 1.0

        if self.device_sensor.Button9.value == True: # e
            rz = -1.0

        if self.device_sensor.Button10.value == True: # page up
            y = 1.0

        if self.device_sensor.Button11.value == True: # page down
            y = -1.0

       
        ## scale input
        trans_factor = 0.15
        rot_factor = 0.75
        
        x *= trans_factor
        y *= trans_factor
        z *= trans_factor
        rx *= rot_factor
        ry *= rot_factor
        rz *= rot_factor

        self.mf_dof.value = [x,y,z,rx,ry,rz,0.0] # propagate input via field connection

