#!/usr/bin/python3

### import guacamole libraries
import avango
import avango.gua


class OrbitVisualization:

    ### constructor
    def __init__(self,
        PARENT_NODE = None,
        ORBIT_RADIUS = 1.0,
        ):

        if PARENT_NODE is None: # guard
            print("ERROR: missing parameters")            
            return

        ### parameters ###
        self.number_of_segments = 100
        self.screenspace_linewidth = 5 # in pixel
        self.color = avango.gua.Color(1.0,1.0,1.0)
        
        ## init geometry
        _loader = avango.gua.nodes.LineStripLoader()

        self.linestrip_node = _loader.create_empty_geometry(PARENT_NODE.Name.value + "_orbit_visualization", PARENT_NODE.Name.value + "_orbit_visualization.lob")
        PARENT_NODE.Children.value.append(self.linestrip_node)
        self.linestrip_node.RenderVolumetric.value = False
        #self.linestrip_node.RenderAsPoints.value = True
        self.linestrip_node.ScreenSpaceLineWidth.value = self.screenspace_linewidth
        self.linestrip_node.ShadowMode.value = avango.gua._gua.ShadowMode.OFF # disable for shadow-pass

        self.linestrip_node.start_vertex_list()

        # enqueue vertices
        for _i in range(self.number_of_segments+1):
            _pos = avango.gua.make_rot_mat(_i * (360.0 / self.number_of_segments), 0.0, 1.0, 0.0) * avango.gua.Vec3(ORBIT_RADIUS, 0.0, 0.0) # transform vector with rotation matrix
            self.linestrip_node.enqueue_vertex(_pos.x, _pos.y, _pos.z, self.color.r, self.color.g, self.color.b, 0.001)
        
        self.linestrip_node.end_vertex_list()
            
