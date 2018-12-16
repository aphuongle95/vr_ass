#!/usr/bin/python3

## import avango-guacamole libraries
import avango
import avango.daemon

## import python libraries
import os

device_list = []

def init_hmd_tracking(SERVER_IP, PORT):
    hmd = avango.daemon.HMDTrack()
    for i in range(7):
        hmd.stations[i] = avango.daemon.Station('vive-sensor-' + str(i))

    hmd.server = SERVER_IP
    hmd.port = PORT

    device_list.append(hmd)
    print("HMD started!")


if __name__ == '__main__':
    init_hmd_tracking("141.54.147.27", "7770")
    avango.daemon.run(device_list)
