# This was created by Nick Levine and is under this creative commons licence:
# http://creativecommons.org/licenses/by/3.0/
# Basically, you can do whatever you want so long as you accredit the author
# and include the license.


from dxfwrite import DXFEngine as dxf
import xml.etree.ElementTree as etree
import zipfile
import math


def findTag(elt, name):
    for child in elt:
        if child.tag == name:
            return child

def findTagChain(elt, names):
    if names:
        return findTagChain(findTag(elt, names[0]), names[1:])
    else:
        return elt

def findName(elt, name):
    for child in elt:
        if child.attrib['name'] == name:
            return child

def lineSegment(drawing, geometry):
    line = findTag(geometry, 'LineSegment').attrib
    drawing.add(dxf.line((line['StartX'], line['StartY']), (line['EndX'], line['EndY'])))

def circle(drawing, geometry):
    circle = findTag(geometry, 'Circle').attrib
    drawing.add(dxf.circle(circle['Radius'], (circle['CenterX'], circle['CenterY'])))

pi = math.pi

def arcOfCircle(drawing, geometry):
    arc = findTag(geometry, 'ArcOfCircle').attrib
    drawing.add(dxf.arc(arc['Radius'], (float(arc['CenterX']), float(arc['CenterY'])), float(arc['StartAngle'])*180/pi, float(arc['EndAngle'])*180/pi))

def convert(ifile, ofile):
    drawing = dxf.drawing(ofile)
    document = etree.parse(zipfile.ZipFile(ifile).open('Document.xml')).getroot()
    properties = findTagChain(document, ['ObjectData', 'Object', 'Properties'])
    geometryList = findTag(findName(properties, 'Geometry'), 'GeometryList')
    for geometry in geometryList:
        type = geometry.attrib['type'][len('Part::Geom'):]
        try:
            processor = {'LineSegment': lineSegment,
                         'Circle':      circle,
                         'ArcOfCircle': arcOfCircle,
                         }[type]
        except:
            print "Don't know how to process %s" % (type,)
        processor(drawing, geometry)
    drawing.save()
