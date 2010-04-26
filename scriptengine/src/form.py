from OCC.Display.SimpleGui import *
from OCC.BRepPrimAPI import *
from OCC.BRepBuilderAPI import *
from OCC.BRepAlgoAPI import *
from OCC.BRepOffsetAPI import *
import sys
from PyQt4 import QtGui, QtOpenGL
from OCC.Display.qtDisplay import qtViewer3d
from OpenGL.GL import *
from OCC.gp import *
from OCC.TopoDS import *
from OCC.GC import *
from OCC.Geom import *
import os
from scriptengine import *

class OCCWidget(qtViewer3d,QtOpenGL.QGLWidget):
    pass

class MainWindow(QtGui.QMainWindow):
    def __init__(self, args=None):
        QtGui.QMainWindow.__init__(self)
        self.centralWidget=CentralWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.InitViewer()
        self.setWindowIcon(QtGui.QIcon('caddd_icon.png'))
        self.setWindowTitle('CADDD - 3D Script Engine')
        self.resize(640, 480)

        new_action = QtGui.QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('Start new script')
        self.connect(new_action, QtCore.SIGNAL('triggered()'), self.newAction)

        open_action = QtGui.QAction('Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open script')
        self.connect(open_action, QtCore.SIGNAL('triggered()'), self.openAction)

        save_action = QtGui.QAction('Save As...', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save script')
        self.connect(save_action, QtCore.SIGNAL('triggered()'), self.saveAction)

        import_action = QtGui.QAction('Import...', self)
        import_action.setShortcut('Ctrl+I')
        import_action.setStatusTip('Import solid')
        self.connect(import_action, QtCore.SIGNAL('triggered()'), self.importAction)

        export_action = QtGui.QAction('Export...', self)
        export_action.setShortcut('Ctrl+E')
        export_action.setStatusTip('Export solid')
        self.connect(export_action, QtCore.SIGNAL('triggered()'), self.exportAction)

        exit = QtGui.QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.connect(exit, QtCore.SIGNAL('triggered()'),QtCore.SLOT('close()'))

        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(new_action)
        file.addAction(open_action)
        file.addAction(save_action)
        file.addAction(import_action)
        file.addAction(export_action)
        file.addAction(exit)

        samples = menubar.addMenu('&Samples')
        for filename in os.listdir("./samples"):
            if filename.lower().find(".ddd")>0:
                with open("./samples/"+filename, 'r') as f:
                    title=f.readline()
                    title=title[1:]
                    sample_action = QtGui.QAction(title, self)
                    self.connect(sample_action, QtCore.SIGNAL('triggered()'), lambda file="./samples/"+filename: self.sampleAction(file))
                    samples.addAction(sample_action)


    def sampleAction(self, filename):
        with open(filename, 'r') as f:
                self.centralWidget.textedit.setText(f.read())
                self.centralWidget.errorbox.setText("FILE LOADED")

    def newAction(self):
        self.centralWidget.textedit.setText("")
        self.centralWidget.executeScript()

    def openAction(self):
        filename=QtGui.QFileDialog.getOpenFileName(self, "Open Script","","All files (*.*);;Text files (*.txt);;CADDD files (*.ddd)","CADDD files (*.ddd)")
        if filename!='':
            with open(filename, 'r') as f:
                self.centralWidget.textedit.setText(f.read())
                self.centralWidget.errorbox.setText("FILE LOADED")
        else:
            self.centralWidget.errorbox.setText("NO FILE WAS SELECTED")

    def saveAction(self):
        filename=QtGui.QFileDialog.getSaveFileName(self, "Save Script","","All files (*.*);;Text files (*.txt);;CADDD files (*.ddd)","CADDD files (*.ddd)")
        if filename!='':
            with open(filename, 'w') as f:
                f.write(self.centralWidget.textedit.toPlainText ())
                self.centralWidget.errorbox.setText("FILE SAVED")
        else:
            self.centralWidget.errorbox.setText("NO FILENAME WAS SPECIFIED")

    def importAction(self):
        pass

    def exportAction(self):
        pass



class CentralWidget(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        generate = QtGui.QPushButton("Generate")
        self.connect(generate, QtCore.SIGNAL('clicked()'),self.executeScript)
        self.textedit = MyTextEdit()
        self.errorbox = QtGui.QTextEdit()
        self.errorbox.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.errorbox.setStyleSheet ( "background-color: lightgrey;")
        self.errorbox.setReadOnly(True)
        self.canva = OCCWidget(self)

        overall_layout = QtGui.QHBoxLayout(self)
        hbox = QtGui.QSplitter(QtCore.Qt.Horizontal)
        hbox.addWidget(self.canva)
        vbox = QtGui.QSplitter(QtCore.Qt.Vertical)
        vbox.addWidget(self.textedit)
        self.textedit.width
        vbox.addWidget(self.errorbox)
        vbox.addWidget(generate)
        hbox.addWidget(vbox)
        overall_layout.addWidget(hbox)
        self.setLayout(overall_layout)
        hbox.setStretchFactor(hbox.indexOf(self.canva), 6);
        hbox.setStretchFactor(hbox.indexOf(vbox), 1);
        vbox.setStretchFactor(vbox.indexOf(self.textedit), 4);
        vbox.setStretchFactor(vbox.indexOf(self.errorbox), 1);

    def InitViewer(self):
        #self.canva._display.Test()
        self.canva.InitDriver()
        self.canva._display.SetBackgroundImage("background.bmp")
        self.canva._display.EraseAll()

    def executeScript(self):
        self.canva._display.EraseAll()
        self.errorbox.setText("ATTEMPTING OPERATION")
        self.errorbox.repaint()
        try:
            ScriptEngine(self.canva._display,self.textedit.toPlainText().__str__()).run()
            self.errorbox.setText("OPERATION SUCCESSFUL")
        except:
            text = "AN ERROR HAS OCCURED\n\n"
            for line in sys.exc_info(): text+=(str(line)+"\n")
            self.errorbox.setText(text)


class MyTextEdit(QtGui.QTextEdit):
   def __init__(self, parent=None):
       QtGui.QTextEdit.__init__(self, parent)
       self.setAcceptRichText ( False )
       self.setWordWrapMode(QtGui.QTextOption.NoWrap)

   def keyPressEvent(self,  event):
       if self.textCursor().selectedText()!='':
           QtGui.QTextEdit.keyPressEvent(self,  event)
           return
       elif event.key() == QtCore.Qt.Key_Tab:
           self.insertPlainText("    ")
           return
       elif event.key() == QtCore.Qt.Key_Return:
           cursor = self.textCursor()
           cursor.movePosition(QtGui.QTextCursor.StartOfLine,QtGui.QTextCursor.KeepAnchor)
           text=cursor.selectedText()
           space_count=0
           for character in text:
               if character ==' ':
                   space_count=space_count+1
               else:
                   break
           space_count=(space_count/4)*4
           cursor.setPosition(cursor.anchor())
           cursor.clearSelection()
           spaces=''
           for i in range(space_count):
               spaces=spaces+' '
           cursor.insertText("\n"+spaces)
           return
       elif event.key() == QtCore.Qt.Key_Backspace:
           cursor = self.textCursor()
           cursor.movePosition(QtGui.QTextCursor.StartOfLine,QtGui.QTextCursor.KeepAnchor)
           text=cursor.selectedText()
           if text=='':
               QtGui.QTextEdit.keyPressEvent(self,  event)
           space_count=0
           for character in text:
               if character ==' ':
                   space_count=space_count+1
               else:
                   QtGui.QTextEdit.keyPressEvent(self,  event)
                   return
           space_count=((space_count-1)/4)*4
           spaces=''
           for i in range(space_count):
               spaces=spaces+' '
           cursor.insertText(spaces)
           return
       QtGui.QTextEdit.keyPressEvent(self,  event)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow(sys.argv)
    window.show()
    sys.exit(app.exec_())
