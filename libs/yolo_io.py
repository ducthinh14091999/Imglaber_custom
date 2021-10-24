#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs
from libs.constants import DEFAULT_ENCODING

TXT_EXT = '.txt'
ENCODE_METHOD = DEFAULT_ENCODING

class YOLOWriter:

    def __init__(self, foldername, filename, imgSize, databaseSrc='Unknown', localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.localImgPath = localImgPath
        self.verified = False

    def addBndBox(self, x1, y1, x2, y2, x3, y3, x4, y4, name, difficult):
        bndbox = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,'x3': x3, 'y3': y3, 'x4': x4, 'y4': y4}
        bndbox['name'] = name
        bndbox['difficult'] = difficult
        self.boxlist.append(bndbox)

    def BndBox2YoloLine(self, box, classList=[]):
        x1 = box['x1']
        x2 = box['x2']
        y1 = box['y1']
        y2 = box['y2']
        x3 = box['x3']
        x4 = box['x4']
        y3 = box['y3']
        y4 = box['y4']


        # xcen = float((xmin + xmax)) / 2 / self.imgSize[1]
        # ycen = float((ymin + ymax)) / 2 / self.imgSize[0]

        # w = float((xmax - xmin)) / self.imgSize[1]
        # h = float((ymax - ymin)) / self.imgSize[0]

        # PR387
        boxName = box['name']
        if boxName not in classList:
            classList.append(boxName)

        classIndex = classList.index(boxName)

        return boxName, x1,y1,x2,y2,x3,y3,x4,y4

    def save(self, classList=[], targetFile=None):

        out_file = None #Update yolo .txt
        out_class_file = None   #Update class list .txt

        if targetFile is None:
            out_file = open(
            self.filename + TXT_EXT, 'w', encoding=ENCODE_METHOD)
            classesFile = os.path.join(os.path.dirname(os.path.abspath(self.filename)), "classes.txt")
            out_class_file = open(classesFile, 'w',encoding='utf-8')

        else:
            out_file = codecs.open(targetFile, 'w', encoding=ENCODE_METHOD)
            classesFile = os.path.join(os.path.dirname(os.path.abspath(targetFile)), "classes.txt")
            out_class_file = open(classesFile, 'w',encoding='utf-8')


        for box in self.boxlist:
            classIndex, x1,y1,x2,y2,x3,y3,x4,y4 = self.BndBox2YoloLine(box, classList)
            # print (classIndex, xcen, ycen, w, h)
            out_file.write("%d*%d*%d*%d*%d*%d*%d*%d*%d\n" % (classIndex, x1,y1,x2,y2,x3,y3,x4,y4))

        # print (classList)
        # print (out_class_file)
        for c in classList:
            out_class_file.write(c+'\n')

        out_class_file.close()
        out_file.close()



class YoloReader:

    def __init__(self, filepath, image, classListPath=None):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.filepath = filepath

        if classListPath is None:
            dir_path = os.path.dirname(os.path.realpath(self.filepath))
            self.classListPath = os.path.join(dir_path, "classes.txt")
        else:
            self.classListPath = classListPath

        # print (filepath, self.classListPath)

        classesFile = open(self.classListPath, 'r',encoding='utf-8')
        self.classes = classesFile.read().strip('\n').split('\n')

        # print (self.classes)

        imgSize = [image.height(), image.width(),
                      1 if image.isGrayscale() else 3]

        self.imgSize = imgSize

        self.verified = False
        # try:
        self.parseYoloFormat()
        # except:
            # pass

    def getShapes(self):
        return self.shapes

    def addShape(self, label, x1, y1, x2, y2, x3, y3, x4, y4, difficult):

        points = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        self.shapes.append((label, points, None, None, difficult))

    def yoloLine2Shape(self,  text, x1,y1,x2,y2,x3,y3,x4,y4):
        label = text

        
        return label, x1, y1, x2, y2, x3, y3, x4, y4
    def parseYoloFormat(self):
        bndBoxFile = open(self.filepath, 'r',encoding='utf-8')
        for bndBox in bndBoxFile:
            # classIndex, xcen, ycen, w, h = bndBox.strip().split('*')
            text, x1,y1,x2,y2,x3,y3,x4,y4 = bndBox.strip().split('*')
            x1,y1,x2,y2,x3,y3,x4,y4= map(int,[x1,y1,x2,y2,x3,y3,x4,y4])
            # x1,y1,x2,y2,x3,y3,x4,y4 = 
            label, x1,y1,x2,y2,x3,y3,x4,y4 = self.yoloLine2Shape(text, x1,y1,x2,y2,x3,y3,x4,y4)

            # Caveat: difficult flag is discarded when saved as yolo format.
            self.addShape(label, x1, y1, x2, y2, x3, y3, x4, y4, False)
