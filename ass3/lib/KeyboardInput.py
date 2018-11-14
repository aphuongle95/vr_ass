#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.daemon


# import python libraries
import time


################################
## KeyboardInput gets events from a connected keyboard and maps them to a movement vector for the avatar.
## Furthermore, it modifies this movement vector when a jump action is triggered by a keyboard event.
################################

class KeyboardInput(avango.script.Script):

    ## declaration of fields
    sf_time_in = avango.SFFloat()
    
    sf_fps_toggle_button = avango.SFBool()
    
    sf_rot_input0 = avango.SFFloat()
    sf_rot_input1 = avango.SFFloat()
    sf_rot_input2 = avango.SFFloat()    

    sf_max_fps = avango.SFFloat()
    sf_max_fps.value = 60.0 # initial value
        

    ## constructor
    def __init__(self):
        self.super(KeyboardInput).__init__()
   
        ## parameters
        self.rot_velocity = 45.0 # in degrees/sec
       

        ## init sensors                   
        self.timeSensor = avango.nodes.TimeSensor()

        self.keyboardSensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.keyboardSensor.Station.value = "gua-device-keyboard"

        ## init field connections
        self.sf_time_in.connect_from(self.timeSensor.Time)
        self.sf_fps_toggle_button.connect_from(self.keyboardSensor.Button14)
 

    ### callback functions ###
    @field_has_changed(sf_fps_toggle_button) # evaluated if this field has changed
    def sf_fps_toggle_button_changed(self):
    
        if self.sf_fps_toggle_button.value == True: # key pressed            
            if self.sf_max_fps.value == 60.0:
                self.sf_max_fps.value = 20.0 # set slow application/render framerate
                print("slow:", self.sf_max_fps.value, "FPS")
            else:
                self.sf_max_fps.value = 60.0 # set fast application/render framerate
                print("fast:", self.sf_max_fps.value, "FPS")


    def evaluate(self): # perform update when fields change (with dependency evaluation)

        # ToDo: calculate rotation input per frame that corresponds to given velocity (self.rot_velocity)
        _rot_input = 1.0

        # ToDo: adapt rotation input to varying frame rates
        # time.time() # absolute timestamp


        ## update rot_value0
        if self.keyboardSensor.Button4.value == True: # KEY_LEFT
            self.sf_rot_input0.value = _rot_input * -1.0

        elif self.keyboardSensor.Button5.value == True: # KEY_RIGHT
            self.sf_rot_input0.value = _rot_input

        else:
            if self.sf_rot_input0.value != 0.0:
                self.sf_rot_input0.value = 0.0

        ## update rot_value1
        if self.keyboardSensor.Button6.value == True: # KEY_UP
            self.sf_rot_input1.value = _rot_input * -1.0

        elif self.keyboardSensor.Button7.value == True: # KEY_DOWN
            self.sf_rot_input1.value = _rot_input
        
        else:
            if self.sf_rot_input1.value != 0.0:
                self.sf_rot_input1.value = 0.0

        ## update rot_value2
        if self.keyboardSensor.Button10.value == True: # KEY_PAGEUP
            self.sf_rot_input2.value = _rot_input * -1.0

        elif self.keyboardSensor.Button11.value == True: # KEY_PAGEDOWN
            self.sf_rot_input2.value = _rot_input
        
        else:
            if self.sf_rot_input2.value != 0.0:
                self.sf_rot_input2.value = 0.0
    
