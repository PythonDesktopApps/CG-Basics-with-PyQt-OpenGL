# https://github.com/dimitrsh/Python-OpenGL-Triangle-Example/blob/master/triangle_test.py
# this is easier than using the same array for vertex pos and colors
import time
import sys
from pathlib import Path

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
from core.attribute import Attribute

class GLWidget(qgl.QGLWidget):

    def __init__(self, main_window=None, *__args):
        fmt = Utils.is_macos_intel()

        if fmt:
            super().__init__(fmt, main_window, *__args)
        else:
            super().__init__(main_window, *__args)

        self.parent = main_window
        # self.setMinimumSize(800, 800)
        self.setMouseTracking(True)

    def initializeGL(self):
        # print gl info
        Utils.print_system_info()

        self.gl_settings()

        # Initialize program #
        vs_code = """
        // User defined in variables
        // Position and color of vertex
        in vec3 vPosition;
        in vec3 vColor;
        
        // Color of the vertex
        out vec4 color;
        
        void main(void) {
            // Calculation of the model-view-perspective transform
            gl_Position = vec4(vPosition.x, vPosition.y, vPosition.z, 1.0);
            // The color information is forwarded in homogeneous coordinates
            color = vec4(vColor, 1.0);
        }
        """

        fs_code = """
        // User defined in variable
        // Color from previous pipeline stage
        // Matches the out variable name of the vertex shader
        in vec4 color;
        // User defined out variable, fragment color
        out vec4 FragColor;

        void main (void)
        {
            // The input fragment color is forwarded
            // to the next pipeline stage
            FragColor = color;
        }
        """

        self.program_ref = Utils.initialize_program(vs_code, fs_code)
        # Render settings (optional) #
        # on Mac, only 1px line is allowed
        GL.glLineWidth(1)
        # Set up vertex array object #
        vao_ref = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao_ref)

        # Set up vertex attribute #
        vertices = [[-0.5, 0.5, 0.0],    # 0 position
                [ 0.0, -0.5, 0.0],   # 1 position
                [ 0.5,  0.5, 0.0]]   # 2 position
        
        colors = [[ 0.0, 0.68, 0.85],  # 0 color
                [ 0.0, 0.68, 0.85],  # 1 color
                [ 0.0, 0.68, 0.85]]  # 2 color
        

        self.vertex_count = len(vertices)

        self.buffer_ref = GL.glGenBuffers(2)

        # convert to numpy array - for convenience
        vertex_data = np.array(vertices).astype(np.float32)
        color_data = np.array(colors).astype(np.float32)

        # upload _data to GPU
        # Select first buffer for vertices
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer_ref[0])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data.ravel(), GL.GL_STATIC_DRAW)
        
        # associate the 'position' variable in the shader to the data above
        pos_ref = GL.glGetAttribLocation(self.program_ref, 'vPosition')
        # Specify how data will be read from the currently bound buffer into the specified variable
        # 3 since we are using vec3 to represent each vertex
        # since we separate vertices and colors, there's no offset now to the vertex_data
        GL.glVertexAttribPointer(pos_ref, 3, GL.GL_FLOAT, False, 0, None)
        # Indicate that data will be streamed to this variable
        GL.glEnableVertexAttribArray(pos_ref)

        # upload _data to GPU
        # Select second buffer for vertices
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer_ref[1])
        GL.glBufferData(GL.GL_ARRAY_BUFFER, color_data.nbytes, color_data.ravel(), GL.GL_STATIC_DRAW)
        
        # associate the 'position' variable in the shader to the data above
        color_ref = GL.glGetAttribLocation(self.program_ref, 'vColor')
        # Specify how data will be read from the currently bound buffer into the specified variable
        # 3 since we are using vec3 to represent each vertex
        # since we separate vertices and colors, there's no offset now to the color_data
        GL.glVertexAttribPointer(color_ref, 3, GL.GL_FLOAT, False, 0, None)
        # Indicate that data will be streamed to this variable
        GL.glEnableVertexAttribArray(color_ref)

    def paintGL(self):
        self.clear()
        GL.glUseProgram(self.program_ref)
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
