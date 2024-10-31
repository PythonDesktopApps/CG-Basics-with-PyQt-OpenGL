import time
import sys
from pathlib import Path
import ctypes

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
        // Position and color of vertex
        layout (location = 0) in vec3 vPosition;
        layout (location = 1) in vec3 vColor;
        
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
        // Color from previous pipeline stage
        // Matches the out variable name of the vertex shader
        in vec4 color;
        // fragment color
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
        vertices = [[-0.5,  0.5,  0.0],    # 0 position
                 [0.0,  0.68,  0.85],  # 0 color
                 [0.0, -0.5,   0.0],   # 1 position
                 [0.0,  0.68,  0.85],  # 1 color
                 [0.5,  0.5,   0.0],   # 2 position
                 [0.0,  0.68,  0.85]  # 2 color
        ]

        self.buffer_ref = GL.glGenBuffers(1)

        # convert to numpy array - for convenience
        data = np.array(vertices).astype(np.float32)

        # upload _data to GPU
        # Select buffer used by the following functions
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer_ref)
        # Store data in currently bound buffer
        # We multiply the 18 numbers by 32 since each is float32 to get the total bits
        # then divide by 8 since 1 byte = 8 bits
        # size_in_bytes = int(data.size * 32/8) or 72 bytes
        # easier way is to use data.nbytes
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes, data.ravel(), GL.GL_STATIC_DRAW)
        
        stride = int(6*32/8) # 6 values with 32 bits each, divide 8 to get bytes
        color_offset = int(3*32/8) # the first 3 values are to be skipped since they are for position
        buffer_offset = ctypes.c_void_p

        # Specify how data will be read from the currently bound buffer into the specified variable
        # 3 since we are using vec3 to represent each vertex
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, stride, buffer_offset(0))
        GL.glEnableVertexAttribArray(0)
        # Indicate that data will be streamed to this variable

        # Specify how data will be read from the currently bound buffer into the specified variable
        # 3 since we are using vec3 to represent each vertex
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, False, stride, buffer_offset(color_offset))
        GL.glEnableVertexAttribArray(1)
        # Indicate that data will be streamed to this variable

    def paintGL(self):
        self.clear()
        GL.glUseProgram(self.program_ref)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3) # 3 for 3 vertex pos

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
