import time
import sys
from pathlib import Path
import platform as pl

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
        is_macos_intel = (pl.platform() == 'Darwin' and pl.machine() == 'x86_64')
        is_windows = pl.platform() == 'Windows'

        if is_macos_intel:
            fmt = qgl.QGLFormat()
            fmt.setVersion(4, 1)
            # note that if you set CompatibilityProfile in mac, you will not be able to use version 4.1
            fmt.setProfile(qgl.QGLFormat.CoreProfile)
            fmt.setSampleBuffers(True)
            super().__init__(fmt, main_window, *__args)
        elif is_windows:
            super().__init__(main_window, *__args)
        else:
            raise NotImplementedError('App not supported in your platform.')

        self.parent = main_window
        # self.setMinimumSize(800, 800)
        self.setMouseTracking(True)

    def initializeGL(self):
        # print gl info
        Utils.print_system_info()

        self.gl_settings()

        # Initialize program #
        vs_code = """
            layout (location = 0) in vec3 position;
            void main()
            {
                gl_Position = vec4(position.x, position.y, position.z, 1.0);
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
        # Render settings (optional) #
        # on Mac, only 1px line is allowed
        GL.glLineWidth(1)
        # Set up vertex array object #
        vao_ref = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao_ref)
        # Set up vertex attribute #
        position_data = [[ 0.8,  0.0,  0.0],
                         [ 0.4,  0.6,  0.0],
                         [-0.4,  0.6,  0.0],
                         [-0.8,  0.0,  0.0],
                         [-0.4, -0.6,  0.0],
                         [ 0.4, -0.6,  0.0]]

        self.vertex_count = len(position_data)

        self.buffer_ref = GL.glGenBuffers(1)

        # convert to numpy array - for convenience
        data = np.array(position_data).astype(np.float32)

        # upload _data to GPU
        # Select buffer used by the following functions
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffer_ref)
        # Store data in currently bound buffer
        # We multiply the 18 numbers by 32 since each is float32 to get the total bits
        # then divide by 8 since 1 byte = 8 bits
        # size_in_bytes = int(data.size * 32/8) or 72 bytes
        # easier way is to use data.nbytes
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes, data.ravel(), GL.GL_STATIC_DRAW)
        
        # instead of getting the 'position' attribute location, we can also pre-assigned the ref to it
        # we can enable it here or after
        # GL.glEnableVertexAttribArray(0)
        # Specify how data will be read from the currently bound buffer into the specified variable
        # 3 since we are using vec3 to represent each vertex
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, False, 0, None)
        # Indicate that data will be streamed to this variable
        GL.glEnableVertexAttribArray(0);

    def paintGL(self):
        self.clear()
        GL.glUseProgram(self.program_ref)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, self.vertex_count)
        
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
