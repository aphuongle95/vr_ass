#!/usr/bin/python3

### import guacamole libraries ###
import avango
import avango.gua
from avango.script import field_has_changed
import avango.daemon

### import framework libraries ###
from lib.SolarObject import SolarObject
import lib.SolarParameters as SP


class SolarSystem(avango.script.Script):

    ## input fields
    sf_key0 = avango.SFFloat()
    sf_key1 = avango.SFFloat()

    ## output_fields
    sf_time_scale_factor = avango.SFFloat()
    sf_time_scale_factor.value = 1.0


    ### constructor
    def __init__(self):
        self.super(SolarSystem).__init__() # call base-class constructor

        ## init device sensor
        self.keyboard_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.keyboard_sensor.Station.value = "gua-device-keyboard"

        self.sf_key0.connect_from(self.keyboard_sensor.Button12)
        self.sf_key1.connect_from(self.keyboard_sensor.Button13)


    def my_constructor(self, PARENT_NODE):

        # init Sun
        self.sun = SolarObject(
            NAME = "sun",
            TEXTURE_PATH = SP.SUN_TEXTURE,
            PARENT_NODE = PARENT_NODE,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.SUN_DIAMETER,
            ORBIT_RADIUS = 0.0,
            ORBIT_INCLINATION = 0.0,
            ORBIT_DURATION = 0.0,
            ROTATION_INCLINATION = 0.0,
            ROTATION_DURATION = 0.0,
            )

        # init lightsource (only for sun)
        self.sun_light = avango.gua.nodes.LightNode(Name = "sun_light", Type = avango.gua.LightType.POINT)
        self.sun_light.Color.value = avango.gua.Color(1.0, 1.0, 1.0)
        self.sun_light.Brightness.value = 25.0
        self.sun_light.Falloff.value = 0.2
        self.sun_light.EnableShadows.value = True
        self.sun_light.ShadowMapSize.value = 2048
        self.sun_light.Transform.value = avango.gua.make_scale_mat(50.0) # light volume defined by scale
        self.sun_light.ShadowNearClippingInSunDirection.value = 0.1 / 50.0
        self.sun.get_orbit_node().Children.value.append(self.sun_light)


        ## TODO: init planets and moons below here
        self.earth = SolarObject(
            NAME = "earth",
            TEXTURE_PATH = SP.EARTH_TEXTURE,
            PARENT_NODE = self.sun.orbit_inclination_node, #node parent for planets is orbi_inclination_node whose parent is root node
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.EARTH_DIAMETER,
            ORBIT_RADIUS = SP.EARTH_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.EARTH_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.EARTH_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.EARTH_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.EARTH_ROTATION_DURATION,
            )

        self.moon = SolarObject(
            NAME = "moon",
            TEXTURE_PATH = SP.EARTH_MOON_TEXTURE,
            PARENT_NODE = self.earth.orbit_radius_node, #node parent for moon is orbit_radius_node whose parent is orbit_inclination_node
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.EARTH_MOON_DIAMETER,
            ORBIT_RADIUS = SP.EARTH_MOON_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.EARTH_MOON_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.EARTH_MOON_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.EARTH_MOON_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.EARTH_MOON_ROTATION_DURATION,
            )
        self.mercury = SolarObject(
            NAME = "mercury",
            TEXTURE_PATH = SP.MERCURY_TEXTURE,
            PARENT_NODE = self.sun.orbit_inclination_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.MERCURY_DIAMETER,
            ORBIT_RADIUS = SP.MERCURY_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.MERCURY_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.MERCURY_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.MERCURY_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.MERCURY_ROTATION_DURATION,
            )
        self.venus = SolarObject(
            NAME = "venus",
            TEXTURE_PATH = SP.VENUS_TEXTURE,
            PARENT_NODE = self.sun.orbit_inclination_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.VENUS_DIAMETER,
            ORBIT_RADIUS = SP.VENUS_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.VENUS_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.VENUS_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.VENUS_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.VENUS_ROTATION_DURATION,
            )
        self.mars = SolarObject(
            NAME = "mars",
            TEXTURE_PATH = SP.MARS_TEXTURE,
            PARENT_NODE = self.sun.orbit_inclination_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.MARS_DIAMETER,
            ORBIT_RADIUS = SP.MARS_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.MARS_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.MARS_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.MARS_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.MARS_ROTATION_DURATION,
            )
        self.jupiter = SolarObject(
            NAME = "jupiter",
            TEXTURE_PATH = SP.JUPITER_TEXTURE,
            PARENT_NODE = self.sun.orbit_inclination_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.JUPITER_DIAMETER,
            ORBIT_RADIUS = SP.JUPITER_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.JUPITER_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.JUPITER_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.JUPITER_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.JUPITER_ROTATION_DURATION,
            )

        self.jupiter_moon1 = SolarObject(
            NAME = "jupiter_moon1",
            TEXTURE_PATH = SP.JUPITER_MOON1_TEXTURE,
            PARENT_NODE = self.jupiter.orbit_radius_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.JUPITER_MOON1_DIAMETER,
            ORBIT_RADIUS = SP.JUPITER_MOON1_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.JUPITER_MOON1_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.JUPITER_MOON1_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.JUPITER_MOON1_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.JUPITER_MOON1_ROTATION_DURATION,
            )
        self.jupiter_moon2 = SolarObject(
            NAME = "jupiter_moon2",
            TEXTURE_PATH = SP.JUPITER_MOON2_TEXTURE,
            PARENT_NODE = self.jupiter.orbit_radius_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.JUPITER_MOON2_DIAMETER,
            ORBIT_RADIUS = SP.JUPITER_MOON2_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.JUPITER_MOON2_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.JUPITER_MOON2_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.JUPITER_MOON2_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.JUPITER_MOON2_ROTATION_DURATION,
            )
        self.jupiter_moon3 = SolarObject(
            NAME = "jupiter_moon3",
            TEXTURE_PATH = SP.JUPITER_MOON3_TEXTURE,
            PARENT_NODE = self.jupiter.orbit_radius_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.JUPITER_MOON3_DIAMETER,
            ORBIT_RADIUS = SP.JUPITER_MOON3_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.JUPITER_MOON3_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.JUPITER_MOON3_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.JUPITER_MOON3_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.JUPITER_MOON3_ROTATION_DURATION,
            )
        self.saturn = SolarObject(
            NAME = "saturn",
            TEXTURE_PATH = SP.SATURN_TEXTURE,
            PARENT_NODE = self.sun.orbit_inclination_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.SATURN_DIAMETER,
            ORBIT_RADIUS = SP.SATURN_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.SATURN_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.SATURN_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.SATURN_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.SATURN_ROTATION_DURATION,
            )
        self.uranus = SolarObject(
            NAME = "uranus",
            TEXTURE_PATH = SP.URANUS_TEXTURE,
            PARENT_NODE = self.sun.orbit_inclination_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.URANUS_DIAMETER,
            ORBIT_RADIUS = SP.URANUS_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.URANUS_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.URANUS_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.URANUS_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.URANUS_ROTATION_DURATION,
            )
        self.neptune = SolarObject(
            NAME = "neptune",
            TEXTURE_PATH = SP.NEPTUNE_TEXTURE,
            PARENT_NODE = self.sun.orbit_inclination_node,
            SF_TIME_SCALE = self.sf_time_scale_factor,
            DIAMETER = SP.NEPTUNE_DIAMETER,
            ORBIT_RADIUS = SP.NEPTUNE_ORBIT_RADIUS,
            ORBIT_INCLINATION = SP.NEPTUNE_ORBIT_INCLINATION,
            ORBIT_DURATION = SP.NEPTUNE_ORBIT_DURATION,
            ROTATION_INCLINATION = SP.NEPTUNE_ROTATION_INCLINATION,
            ROTATION_DURATION = SP.NEPTUNE_ROTATION_DURATION,
            )




    ### callback functions ###
    @field_has_changed(sf_key0)
    def sf_key0_changed(self):
        if self.sf_key0.value == True: # button pressed
            _new_factor = self.sf_time_scale_factor.value * 1.5 # increase factor to 150%

            self.set_time_scale_factor(_new_factor)

    @field_has_changed(sf_key1)
    def sf_key1_changed(self):
        if self.sf_key1.value == True: # button pressed
            _new_factor = self.sf_time_scale_factor.value * 0.5 # decrease factor to 50%

            self.set_time_scale_factor(_new_factor)


    ### functions ###
    def set_time_scale_factor(self, FLOAT):
        self.sf_time_scale_factor.value = min(10000.0, max(1.0, FLOAT)) # clamp value to reasonable intervall
