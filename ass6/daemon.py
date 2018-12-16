#!/usr/bin/python

import avango.daemon
import os


### functions ###
    
## Initializes AR Track
def init_art_tracking_wall():

    # create instance of DTrack
    _dtrack = avango.daemon.DTrack()
    _dtrack.port = "5000" # ART port

    _dtrack.stations[10] = avango.daemon.Station('tracking-glasses-1') # 3D-TV (Mitsubishi) wired shutter glasses
    _dtrack.stations[2] = avango.daemon.Station('tracking-glasses-2') # small powerwall polarization glasses
    _dtrack.stations[5] = avango.daemon.Station('tracking-glasses-4') # ASUS 3D mirror display

    _dtrack.stations[27] = avango.daemon.Station('tracking-pointer-1') # HAS pointer
    _dtrack.stations[18] = avango.daemon.Station('tracking-pointer-2') # Gyromouse pointer
    _dtrack.stations[21] = avango.daemon.Station('tracking-pointer-3') # 2.4G pointer (green)    
    _dtrack.stations[11] = avango.daemon.Station('tracking-pointer-4') # MOSART pointer (red)
   

    device_list.append(_dtrack)
    print("ART Tracking@Powerwall started")



def init_art_tracking_3DTV():

    # create instance of DTrack
    _dtrack = avango.daemon.DTrack()
    _dtrack.port = "5010" # ART port

    _dtrack.stations[1] = avango.daemon.Station('tracking-glasses-3') # Samsung 3D-TV wired shutter glasses
    _dtrack.stations[2] = avango.daemon.Station('tracking-pointer-3') # 2.4F Mouse Pointer

    device_list.append(_dtrack)
    print("ART Tracking @3DTV started")

    
def init_keyboard():

    _string = get_event_string(1, "Cherry GmbH")
    
    if _string is None:
        _string = get_event_string(1, "HID 046a:0011")
    
    if _string is None:
        _string = get_event_string(1, "MOSART Semi. 2.4G Keyboard Mouse")
    
    if _string is None:
        _string = get_event_string(1, "Logitech USB Keyboard")
    
    if _string is None:
        _string = get_event_string(1, "Logitech USB Keyboard")
    
    if _string is None:
        _string = get_event_string(1, "DELL Dell QuietKey Keyboard")

    if _string is not None:
        _keyboard = avango.daemon.HIDInput()
        _keyboard.station = avango.daemon.Station('gua-device-keyboard')
        _keyboard.device = _string

        _keyboard.buttons[0] = "EV_KEY::KEY_W"
        _keyboard.buttons[1] = "EV_KEY::KEY_A"
        _keyboard.buttons[2] = "EV_KEY::KEY_S"
        _keyboard.buttons[3] = "EV_KEY::KEY_D"
        _keyboard.buttons[4] = "EV_KEY::KEY_LEFT"
        _keyboard.buttons[5] = "EV_KEY::KEY_RIGHT"
        _keyboard.buttons[6] = "EV_KEY::KEY_UP"
        _keyboard.buttons[7] = "EV_KEY::KEY_DOWN"
        _keyboard.buttons[8] = "EV_KEY::KEY_Q"
        _keyboard.buttons[9] = "EV_KEY::KEY_E"
        _keyboard.buttons[10] = "EV_KEY::KEY_PAGEUP"
        _keyboard.buttons[11] = "EV_KEY::KEY_PAGEDOWN"
        _keyboard.buttons[12] = "EV_KEY::KEY_KPPLUS"
        _keyboard.buttons[13] = "EV_KEY::KEY_KPMINUS"
        _keyboard.buttons[14] = "EV_KEY::KEY_SPACE"
        _keyboard.buttons[15] = "EV_KEY::KEY_LEFTCTRL"
        _keyboard.buttons[16] = "EV_KEY::KEY_1"
        _keyboard.buttons[17] = "EV_KEY::KEY_2"
        _keyboard.buttons[18] = "EV_KEY::KEY_3"
        _keyboard.buttons[19] = "EV_KEY::KEY_4"
               

        device_list.append(_keyboard)
        print("Keyboard started at:", _string)

        return

    print("Keyboard NOT found!")



def init_spacemouse():
    
    # search for new spacemouse (blue LED)
    _string = get_event_string(1, "3Dconnexion SpaceNavigator for Notebooks")

    if _string is None:
        _string = get_event_string(1, "3Dconnexion SpaceNavigator")
            
    if _string is not None: # new spacemouse was found
        _spacemouse = avango.daemon.HIDInput()
        _spacemouse.station = avango.daemon.Station('gua-device-spacemouse') # create a station to propagate the input events
        _spacemouse.device = _string
        _spacemouse.timeout = '14' # better !
        _spacemouse.norm_abs = 'True'

        # map incoming spacemouse events to station values
        _spacemouse.values[0] = "EV_REL::REL_X"   # trans X
        _spacemouse.values[1] = "EV_REL::REL_Z"   # trans Y
        _spacemouse.values[2] = "EV_REL::REL_Y"   # trans Z
        _spacemouse.values[3] = "EV_REL::REL_RX"  # rotate X
        _spacemouse.values[4] = "EV_REL::REL_RZ"  # rotate Y
        _spacemouse.values[5] = "EV_REL::REL_RY"  # rotate Z

        # buttons
        _spacemouse.buttons[0] = "EV_KEY::BTN_0" # left button
        _spacemouse.buttons[1] = "EV_KEY::BTN_1" # right button

        device_list.append(_spacemouse)
        print("New SpaceMouse started at:", _string)

        return


    print("SpaceMouse NOT found!")
    


def init_pointer1(): # HAS pointer
    _string = get_event_string(1, "HAS   HAS HS304")

    if _string is not None:
        _pointer = avango.daemon.HIDInput()
        _pointer.station = avango.daemon.Station("device-pointer-1") # create a station to propagate the input events
        _pointer.device = _string

        _pointer.buttons[0] = "EV_KEY::KEY_VOLUMEUP"

        device_list.append(_pointer)

        print("HAS Pointer started at:", _string)

        return

    print("HAS Pointer NOT found!")
    


def init_pointer2(): # Gyromouse
    _string = get_event_string(2, "Gyration Gyration RF Technology Receiver")

    if _string is not None:           
        _pointer = avango.daemon.HIDInput()
        _pointer.station = avango.daemon.Station("device-pointer-2") # create a station to propagate the input events
        _pointer.device = _string

        _pointer.buttons[0] = "EV_KEY::KEY_F14"

        device_list.append(_pointer)

        print("Gyromouse Pointer started at:", _string)

        return

    print("Gyromouse Pointer NOT found!")



def init_pointer3(): # 2.4G Mouse
    _string = get_event_string(1, "2.4G KB 2.4G Mouse")

    if _string is not None:           
        _pointer = avango.daemon.HIDInput()
        _pointer.station = avango.daemon.Station("device-pointer-3") # create a station to propagate the input events
        _pointer.device = _string

        _pointer.buttons[0] = "EV_KEY::KEY_ESC"

        device_list.append(_pointer)

        print("2.4G Pointer started at:", _string)

        return

    print("2.4G Pointer NOT found!")


def init_pointer4(): # MOSART pointer red
    _string = get_event_string(1, "MOSART Semi. Input Device")

    if _string is not None:           
        _pointer = avango.daemon.HIDInput()
        _pointer.station = avango.daemon.Station("device-pointer-4") # create a station to propagate the input events
        _pointer.device = _string

        _pointer.buttons[0] = "EV_KEY::KEY_PAGEUP"

        device_list.append(_pointer)

        print("MOSART Pointer started at:", _string)

        return

    print("MOSART Pointer NOT found!")



## Gets the event string of a given input device.
# @param STRING_NUM Integer saying which device occurence should be returned.
# @param DEVICE_NAME Name of the input device to find the event string for.
def get_event_string(STRING_NUM, DEVICE_NAME):

    # file containing all devices with additional information
    _device_file = os.popen("cat /proc/bus/input/devices").read()
    _device_file = _device_file.split("\n")
    
    DEVICE_NAME = '\"' + DEVICE_NAME + '\"'
    
    # lines in the file matching the device name
    _indices = []

    for _i, _line in enumerate(_device_file):
        if DEVICE_NAME in _line:
            _indices.append(_i)

    # if no device was found or the number is too high, return an empty string
    if len(_indices) == 0 or STRING_NUM > len(_indices):
        return None

    # else captue the event number X of one specific device and return /dev/input/eventX
    else:
        _event_string_start_index = _device_file[_indices[STRING_NUM-1]+4].find("event")
                
        return "/dev/input/" + _device_file[_indices[STRING_NUM-1]+4][_event_string_start_index:].split(" ")[0]






device_list = []

init_art_tracking_wall()
init_art_tracking_3DTV()
init_keyboard()
init_spacemouse()
init_pointer1()
init_pointer2()
init_pointer3()
init_pointer4()


avango.daemon.run(device_list)
