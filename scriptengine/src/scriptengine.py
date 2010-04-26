from OCC.Display.SimpleGui import *
from OCC.BRepPrimAPI import *
from OCC.BRepBuilderAPI import *
from OCC.BRepAlgoAPI import *
from OCC.BRepOffsetAPI import *
from OpenGL.GL import *
from OCC.gp import *
from OCC.TopoDS import *
from OCC.GC import *
from OCC.Geom import *
import math


class ScriptEngine():
    def __init__(self, display, text):
        self.display=display
        self.text=text
        self.shapes=[]

    def add(self, shape):
        self.shapes.append(shape)
        shape.display(self.display)

    def remove(self, arg):
        self.shapes.remove(arg)
        self.refresh()

    def refresh(self):
        self.display.EraseAll()
        for shape in self.shapes:
            shape.display(self.display)

    def clear(self):
        self.shapes=[]
        self.refresh()

    def run(self):
        Display=self
        exec(self.text)


class Point(gp_Pnt):
    pass

#ABSTRACT
class Segment():
    def edge(self):
        edge=BRepBuilderAPI_MakeEdge(self.seg.Value())
        return edge.Edge()

    def display(self, display):
        display.DisplayShape(self.edge())    


class Line(Segment):
    def __init__(self, p1, p2):
        self._p1=p1
        self._p2=p2
        self.seg=GC_MakeSegment(p1 , p2)
    
    def p1(self):
        return self._p1
    
    def p2(self):
        return self._p2


class Arc(Segment):
    def __init__(self, p1, p2, vec):
        self._p1=p1
        self._p2=p2
        self.seg=GC_MakeArcOfCircle(p1,gp_Vec(gp_Pnt(0,0,0),vec),p2)

    def p1(self):
        return self._p1
    
    def p2(self):
        return self._p2

#ABSTRACT
class Face():
    def face(self):
        face=BRepBuilderAPI_MakeFace(self.wire.Wire()).Face()
        return face

    def display(self, display):
        display.DisplayShape(self.face())

    def extrude(self,vec):
        shape=Solid()
        shape.solid = BRepPrimAPI_MakePrism(self.face() , gp_Vec(vec.X() , vec.Y() , vec.Z()))
        return shape

    def revolve(self,line,angle):
        _p1=line.p1()
        _p2=line.p2()
        shape=Solid()
        shape.solid = BRepPrimAPI_MakeRevol(self.face() ,gp_Ax1(_p1,gp_Dir(_p2.X()-_p1.X(),_p2.Y()-_p1.Y(),_p2.Z()-_p1.Z())),angle/180.*math.pi)
        return shape

class Profile(Face):
    def __init__(self, startPoint):
        self.wire=BRepBuilderAPI_MakeWire()
        self.point=startPoint
        self.startPoint=startPoint

    def addLine(self,p1):
        self.wire.Add(Line(self.point,p1).edge())
        self.point=p1

    def addArc(self,p1,vec):
        self.wire.Add(Arc(self.point,p1,vec).edge())
        self.point=p1

    def close(self):
        if not self.point.IsEqual(self.startPoint,0):
            self.wire.Add(Line(self.point,self.startPoint).edge())
            self.point=self.startPoint


class Circle(Face):
    def __init__(self, p1, onAxisP, R):
        seg=GC_MakeCircle(p1,onAxisP,R)
        edge=BRepBuilderAPI_MakeEdge(seg.Value())
        self.wire=BRepBuilderAPI_MakeWire()
        self.wire.Add(edge.Edge())

class Solid():

    def shape(self):
        return self.solid.Shape()

    def display(self, display):
        display.DisplayShape(self.shape())

    def cut(self, solid_to_cut):
        self.solid=BRepAlgoAPI_Cut(self.shape(),solid_to_cut.shape())

    def join(self, solid_to_join):
        self.solid=BRepAlgoAPI_Fuse(self.shape(),solid_to_join.shape())

    def intersect(self, solid_to_intersect):
        self.solid=BRepAlgoAPI_Common(self.shape(),solid_to_intersect.shape())

    def saveIGES(self, filename):
        filename=(filename.split("."))[0]
        from OCC.Utils.DataExchange.IGES import IGESExporter
        my_iges_exporter = IGESExporter(filename+".iges",format="5.3")
        my_iges_exporter.AddShape(self.shape())
        my_iges_exporter.WriteFile()

    def loadIGES(self, filename):
        from OCC.Utils.DataExchange.IGES import IGESImporter
        my_iges_importer = IGESImporter(filename)
        my_iges_importer.ReadFile()
        shapes=my_iges_importer.GetShapes()
        self.solid=BRepAlgoAPI_Fuse(shapes[0],shapes[0])
        for shape in shapes:
            self.solid=BRepAlgoAPI_Fuse(self.shape(),shape)

    def grow(self, offset):
        self.solid = BRepOffsetAPI_MakeOffsetShape (self.shape(), offset, 0)

class Box(Solid):
    def __init__(self, point1,point2):
        S=point1
        E=point2
        P1=S
        P2=Point(S.X(),E.Y(),S.Z())
        P3=Point(E.X(),E.Y(),S.Z())
        P4=Point(E.X(),S.Y(),S.Z())
        face = Profile(P1)
        face.addLine(P2)
        face.addLine(P3)
        face.addLine(P4)
        face.addLine(P1)
        self.solid = face.extrude(Point(0,0,E.Z()-S.Z()))
