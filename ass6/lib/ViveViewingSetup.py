# import avango-guacamole libraries
import avango
import avango.daemon
import avango.gua
import avango.vive

# import python libraries
import builtins
import time


class ViveViewingSetup:
    def __init__(
        self,
        PARENT_NODE,
        SCENEGRAPH = None,
        BLACK_LIST = []
    ):
        ## parameter quards
        if SCENEGRAPH is None:
            print("ERROR: scenegraph instance missing")
            quit()

        self.SCENEGRAPH = SCENEGRAPH
        self.black_list = BLACK_LIST

        ### parameters ###
        self.printout_intervall = 1.0 # in seconds

        ### variables ###
        self.sav_time = time.clock()

        ### resources ###
        ## init window
        self.window = avango.vive.nodes.ViveWindow()

        # notice, that the oculus screen transforms and translations are
        # automatically computed by the oculus. do not try to enter them
        # yourself, or you will most likely get a wrong result due to influence
        # of the lenses

        #accessible fields:
        #    SensorOrientation ##head pose (rotation and translation)
        #    Resolution ##window resolution
        #    EyeResolution ##recommended eye resolution (behaves strange so far)
        #    LeftScreenSize  ## size of left screen in meters
        #    RightScreenSize ## size of right screen in meters
        #    LeftScreenTranslation  ## translation of left screen in meters
        #    RightScreenTranslation ## translation of right screen in meters
        #    EyeDistance ## distance between both eyes in meters. for SDKs < v0.6, this is fixed to 0.064

        self.window.Size.value = self.window.Resolution.value
        self.window.EnableVsync.value = False
        self.window.EnableFullscreen.value = False
        avango.gua.register_window(self.window.Title.value, self.window)

        ## init viewer
        self.viewer = avango.gua.nodes.Viewer()
        self.viewer.SceneGraphs.value = [self.SCENEGRAPH]
        self.viewer.Windows.value = [self.window]
        self.viewer.DesiredFPS.value = 2000.0 # in Hz

        # Triggers framewise evaluation of respective callback method
        self.frame_trigger = avango.script.nodes.Update(Callback = self.frame_callback, Active = True)


        ## init head node
        self.hmd_service = avango.daemon.DeviceService()
        self.hmd_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = self.hmd_service)
        self.hmd_sensor.Station.value = "vive-sensor-0"

        self.head_node = avango.gua.nodes.TransformNode(Name = "head_node")
        PARENT_NODE.Children.value.append(self.head_node)
        self.head_node.Transform.connect_from(self.hmd_sensor.Matrix)

        # this connection leads to image tearing - that's why the local daemon above is used
        #self.head_node.Transform.connect_from(self.window.SensorOrientation)


        ## init screen nodes
        self.left_screen_node = avango.gua.nodes.ScreenNode(
            Name="left_screen_node",
            Width=self.window.LeftScreenSize.value.x,
            Height=self.window.LeftScreenSize.value.y,
            Transform=avango.gua.make_trans_mat(self.window.LeftScreenTranslation.value))
        self.head_node.Children.value.append(self.left_screen_node)

        self.right_screen_node = avango.gua.nodes.ScreenNode(
            Name="right_screen_node",
            Width=self.window.RightScreenSize.value.x,
            Height=self.window.RightScreenSize.value.y,
            Transform=avango.gua.make_trans_mat(self.window.RightScreenTranslation.value))
        self.head_node.Children.value.append(self.right_screen_node)


        ## init camera node
        self.camera_node = avango.gua.nodes.CameraNode(
            Name = "camera_node",
            LeftScreenPath = self.left_screen_node.Path.value,
            RightScreenPath = self.right_screen_node.Path.value,
            SceneGraph = self.SCENEGRAPH.Name.value,
            Resolution = self.window.Resolution.value,
            OutputWindowName = self.window.Title.value,
            EyeDistance = self.window.EyeDistance.value,
            EnableStereo = True,
            BlackList = self.black_list,
            FarClip = 1500)
        self.head_node.Children.value.append(self.camera_node)


        ## init passes & render pipeline description
        self.resolve_pass = avango.gua.nodes.ResolvePassDescription()
        self.resolve_pass.EnableSSAO.value = False
        self.resolve_pass.SSAOIntensity.value = 2.5
        self.resolve_pass.SSAOFalloff.value = 2.0
        self.resolve_pass.SSAORadius.value = 1.0
        self.resolve_pass.EnvironmentLightingColor.value = avango.gua.Color(0.2, 0.2, 0.2)
        self.resolve_pass.ToneMappingMode.value = avango.gua.ToneMappingMode.UNCHARTED
        self.resolve_pass.Exposure.value = 1.0

        self.resolve_pass.BackgroundMode.value = avango.gua.BackgroundMode.SKYMAP_TEXTURE
        self.resolve_pass.BackgroundColor.value = avango.gua.Color(0.2, 0.2, 0.2)
        self.resolve_pass.BackgroundTexture.value = "data/textures/skymap.png"

        self.pipeline_description = avango.gua.nodes.PipelineDescription(Passes = [])
        self.pipeline_description.Passes.value.append(avango.gua.nodes.TriMeshPassDescription())
        self.pipeline_description.Passes.value.append(avango.gua.nodes.LightVisibilityPassDescription())
        self.pipeline_description.Passes.value.append(self.resolve_pass)
        self.pipeline_description.Passes.value.append(avango.gua.nodes.SSAAPassDescription())
        self.camera_node.PipelineDescription.value = self.pipeline_description


    def set_eye_distance(self, FLOAT):
        self.camera_node.EyeDistance.value = FLOAT


    def run(self, LOCALS, GLOBALS):
        self.viewer.run()


    def list_variabels(self):
        self.shell.list_variables()


    ### callback functions ###
    def frame_callback(self):
        if time.clock() - self.sav_time > self.printout_intervall:
            self.sav_time = time.clock()
            print("FPS", self.viewer.ApplicationFPS.value, self.window.RenderingFPS.value)