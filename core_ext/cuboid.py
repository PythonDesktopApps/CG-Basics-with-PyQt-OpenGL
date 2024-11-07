primitive_restart_index = -1

class Cuboid:

    @staticmethod
    def make_cuboid_fast_vertices(width:float, height:float, depth:float, color:list[float]):

        half_of_width: float = width/2
        half_of_height: float = height/2
        half_of_depth: float = depth/2

        # Definition of positions of vertices for a cuboid
        p0 = [-half_of_width, +half_of_height, +half_of_depth] # 0 front
        p1 = [-half_of_width, -half_of_height, +half_of_depth] # 1
        p2 = [+half_of_width, +half_of_height, +half_of_depth] # 2
        p3 = [+half_of_width, -half_of_height, +half_of_depth] # 3
        p4 = [-half_of_width, +half_of_height, -half_of_depth] # 4 back
        p5 = [-half_of_width, -half_of_height, -half_of_depth] # 5
        p6 = [+half_of_width, +half_of_height, -half_of_depth] # 6
        p7 = [+half_of_width, -half_of_height, -half_of_depth] # 7

        c = color

        # Cuboid vertices to be drawn as triangle stripes
        # Interlaces with color information
        vertices = [
                # front surface
                p0[0], p0[1], p0[2],  # position
                c[0],  c[1],  c[2],   # color
                p1[0], p1[1], p1[2],  # position
                c[0],  c[1],  c[2],   # color
                p2[0], p2[1], p2[2],  # position
                c[0],  c[1],  c[2],   # color
                p3[0], p3[1], p3[2],  # position
                c[0],  c[1],  c[2],   # color
                p4[0], p4[1], p4[2],  # position
                c[0],  c[1],  c[2],   # color
                p5[0], p5[1], p5[2],  # position
                c[0],  c[1],  c[2],   # color
                p6[0], p6[1], p6[2],  # position
                c[0],  c[1],  c[2],   # color
                p7[0], p7[1], p7[2],  # position
                c[0],  c[1],  c[2],   # color
        ]
        return vertices
    
    @staticmethod
    def make_cuboid_fast_indices_for_triangle_strip():

        # Indices to reference the number of the box vertices
        # defined in makeFastBoxVertices()
        indices = [
                0, 1, 2, 3, # front side
                7,             # right side, bottom front part
                1, 5,          # bottom side
                0, 4,          # left side
                2, 6,          # top side
                7,             # right side, top back part
                4, 5]          # back side

        return indices
