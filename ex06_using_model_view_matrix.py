# https://github.com/dimitrsh/Python-OpenGL-Triangle-Example/blob/master/triangle_test.py
# this is easier than using the same array for vertex pos and colors
import time
import sys
from pathlib import Path
import math

import numpy as np
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import PyQt5.QtOpenGL as qgl

from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot

import OpenGL.GL as GL

package_dir = str(Path(__file__).resolve().parents[1])
print("parent dir: ", package_dir)
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from core.utils import Utils
from core.uniform import Uniform
from core.matrix import Matrix

class GLWidget(qgl.QGLWidget):

    def __init__(self, main_window=None, *__args):
        # commennt for now, focus first on refactoring the actual code
        fmt = qgl.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(qgl.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super().__init__(fmt, main_window, *__args)

        self.parent = main_window
        # self.setMinimumSize(800, 800)
        self.setMouseTracking(True)

    def initializeGL(self):
        # print gl info
        Utils.print_system_info()

        self.gl_settings()

        # Initialize program #
        vs_code = """
            in vec3 position;
            uniform mat4 projectionMatrix;
            uniform mat4 modelMatrix;
            void main()
            {
                gl_Position = projectionMatrix * modelMatrix * vec4(position, 1.0);
            }
        """
        fs_code = """
            out vec4 fragColor;
            void main()
            {
                fragColor = vec4(1.0, 1.0, 0.0, 1.0);
            }
        """
        self.program_ref = Utils.initialize_program(vs_code, fs_code)

        # VAO - like container for VBOs
        vao_ref = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao_ref)

        # Set up vertex attribute #
        vertices = [[0.0,   0.2,  0.0],    # 0 position
                [0.1,  -0.2,  0.0],   # 1 position
                [-0.1, -0.2,  0.0]]   # 2 position
        
        self.vertex_count = len(vertices)

        self.buffer_ref = GL.glGenBuffers(1)

        # convert to numpy array - for convenience
        vertex_data = np.array(vertices).astype(np.float32)

        # upload _data to GPU
        # Select first buffer for vertices
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer_ref)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data.ravel(), GL.GL_STATIC_DRAW)
        
        # associate the 'position' variable in the shader to the data above
        pos_ref = GL.glGetAttribLocation(self.program_ref, 'position')
        # Specify how data will be read from the currently bound buffer into the specified variable
        # 3 since we are using vec3 to represent each vertex
        GL.glVertexAttribPointer(pos_ref, 3, GL.GL_FLOAT, False, 0, None)
        # Indicate that data will be streamed to this variable
        GL.glEnableVertexAttribArray(pos_ref)

        ### Set up model matrix
        # move -1 units i z direction (z is direction to screen)
        self.m_matrix = np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, -1],
             [0, 0, 0, 1]]
        ).astype(float)

        self.m_matrix_ref = GL.glGetUniformLocation(self.program_ref, 'modelMatrix')
        # GL.glUniformMatrix4fv(self.m_matrix_ref, 1, GL.GL_TRUE, self.m_matrix)

        far, near = 1000, 0.1
        aspect_ratio = 1
        # convert to radians
        a = 60 * math.pi / 180.0
        d = 1.0 / math.tan(a / 2)
        b = (far + near) / (near - far)
        c = 2 * far * near / (near - far)
        self.p_matrix = np.array(
            [[d / aspect_ratio, 0, 0, 0],
             [0, d, 0, 0],
             [0, 0, b, c],
             [0, 0, -1, 0]]
        ).astype(float)
    
        self.p_matrix_ref = GL.glGetUniformLocation(self.program_ref, 'projectionMatrix')
        # GL.glUniformMatrix4fv(self.p_matrix_ref, 1, GL.GL_TRUE, self.p_matrix)

        self.move_speed = 0.5
        # rotation speed, radians per second
        self.turn_speed = 90 * (math.pi / 180)
    
    def paintGL(self):
        self.clear()
        GL.glUseProgram(self.program_ref)

        # the use of uniforms only works in the paintGL
        GL.glUniformMatrix4fv(self.m_matrix_ref, 1, GL.GL_TRUE, self.m_matrix)
        GL.glUniformMatrix4fv(self.p_matrix_ref, 1, GL.GL_TRUE, self.p_matrix)
        # we can now use vertex_count attribute instead of hardcoding it
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertex_count)
        
    # def resizeGL(self, w, h):
    #     pass

    def gl_settings(self):
        # self.qglClearColor(qtg.QColor(255, 255, 255))
        GL.glClearColor(255, 255, 255, 1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        # the shapes are basically behind the white background
        # if you enabled face culling, they will not show
        # GL.glEnable(GL.GL_CULL_FACE)
        
    def clear(self):
        # Clearing the screen (color like Qt window)
        # GL.glClearColor(0.94117647058, 0.94117647058, 0.94117647058, 1.0)
        # color it white for better visibility
        GL.glClearColor(255, 255, 255, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

class MainWindow(qtw.QMainWindow):

    def __init__(self, *args):
        super().__init__(*args)
        self.scaling = self.devicePixelRatioF()

        loadUi("resources/Tsugite.ui", self)
        self.setupUi()

        self.title = "PyOpenGL Framework"
        self.setWindowTitle(self.title)
        self.setWindowIcon(qtg.QIcon("resources/tsugite_icon.png"))

        self.glWidget = GLWidget(self)

        self.hly_gl.addWidget(self.glWidget)

        self.statusBar = qtw.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(
            "To open and close the joint: PRESS 'Open/close joint' button or DOUBLE-CLICK anywhere inside the window.")

        # timer = qtc.QTimer(self)
        # timer.setInterval(20)  # period, in milliseconds
        # timer.timeout.connect(self.glWidget.updateGL)
        # timer.start()

    def setupUi(self):
        pass
    
    @pyqtSlot()
    def open_close_joint(self):
        pass
    
    def keyPressEvent(self, e):
        pass
        # if e.key() == qtc.Qt.Key_Shift:
        #     self.glWidget.joint_type.mesh.select.shift = True
    
# deal with dpi
qtw.QApplication.setAttribute(qtc.Qt.AA_EnableHighDpiScaling, True)     # enable high dpi scaling
qtw.QApplication.setAttribute(qtc.Qt.AA_UseHighDpiPixmaps, True)        # use high dpi icons

app = qtw.QApplication(sys.argv)

window = MainWindow()
window.show()
sys.exit(app.exec_())
