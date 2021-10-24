# Copyright (c) 2016 Tzutalin
# Create by TzuTaLin <tzu.ta.lin@gmail.com>

try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PyQt4.QtGui import QImage

from base64 import b64encode, b64decode
from libs.pascal_voc_io import PascalVocWriter
from libs.yolo_io import YOLOWriter
from libs.pascal_voc_io import XML_EXT
from libs.create_ml_io import CreateMLWriter
from libs.create_ml_io import JSON_EXT
from enum import Enum
import os.path
import sys


class LabelFileFormat(Enum):
    PASCAL_VOC= 1
    YOLO = 2
    CREATE_ML = 3


class LabelFileError(Exception):
    pass


class LabelFile(object):
    # It might be changed as window creates. By default, using XML ext
    # suffix = '.lif'
    suffix = XML_EXT

    def __init__(self, filename=None):
        self.shapes = ()
        self.imagePath = None
        self.imageData = None
        self.verified = False

    def saveCreateMLFormat(self, filename, shapes, imagePath, imageData, classList, lineColor=None, fillColor=None, databaseSrc=None):
        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        outputFilePath = "/".join(filename.split("/")[:-1])
        outputFile = outputFilePath + "/" + imgFolderName + JSON_EXT

        image = QImage()
        image.load(imagePath)
        imageShape = [image.height(), image.width(),
                      1 if image.isGrayscale() else 3]
        writer = CreateMLWriter(imgFolderName, imgFileName,
                                imageShape, shapes, outputFile, localimgpath=imagePath)
        writer.verified = self.verified
        writer.write()


    def savePascalVocFormat(self, filename, shapes, imagePath, imageData,
                            lineColor=None, fillColor=None, databaseSrc=None):
        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        #imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        if isinstance(imageData, QImage):
            image = imageData
        else:
            image = QImage()
            image.load(imagePath)
        imageShape = [image.height(), image.width(),
                      1 if image.isGrayscale() else 3]
        writer = PascalVocWriter(imgFolderName, imgFileName,
                                 imageShape, localImgPath=imagePath)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            # Add Chris
            difficult = int(shape['difficult'])
            bndbox = LabelFile.convertPoints2BndBox(points)
            writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3],bndbox[4], bndbox[5], bndbox[6], bndbox[7], label, difficult)

        writer.save(targetFile=filename)
        return

    def saveYoloFormat(self, filename, shapes, imagePath, imageData, classList,
                            lineColor=None, fillColor=None, databaseSrc=None):
        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        #imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        if isinstance(imageData, QImage):
            image = imageData
        else:
            image = QImage()
            image.load(imagePath)
        imageShape = [image.height(), image.width(),
                      1 if image.isGrayscale() else 3]
        writer = YOLOWriter(imgFolderName, imgFileName,
                                 imageShape, localImgPath=imagePath)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            # Add Chris
            difficult = int(shape['difficult'])
            bndbox = LabelFile.convertPoints2BndBox(points)
            writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3],bndbox[4], bndbox[5], bndbox[6], bndbox[7], label, difficult)

        writer.save(targetFile=filename, classList=classList)
        return

    def toggleVerify(self):
        self.verified = not self.verified

    ''' ttf is disable
    def load(self, filename):
        import json
        with open(filename, 'rb') as f:
                data = json.load(f)
                imagePath = data['imagePath']
                imageData = b64decode(data['imageData'])
                lineColor = data['lineColor']
                fillColor = data['fillColor']
                shapes = ((s['label'], s['points'], s['line_color'], s['fill_color'])\
                        for s in data['shapes'])
                # Only replace data after everything is loaded.
                self.shapes = shapes
                self.imagePath = imagePath
                self.imageData = imageData
                self.lineColor = lineColor
                self.fillColor = fillColor

    def save(self, filename, shapes, imagePath, imageData, lineColor=None, fillColor=None):
        import json
        with open(filename, 'wb') as f:
                json.dump(dict(
                    shapes=shapes,
                    lineColor=lineColor, fillColor=fillColor,
                    imagePath=imagePath,
                    imageData=b64encode(imageData)),
                    f, ensure_ascii=True, indent=2)
    '''

    @staticmethod
    def isLabelFile(filename):
        fileSuffix = os.path.splitext(filename)[1].lower()
        return fileSuffix == LabelFile.suffix

    @staticmethod
    def convertPoints2BndBox(points):
        x1 = float('inf')
        y1 = float('inf')
        x2 = float('-inf')
        y2 = float('-inf')
        x3 = float('inf')
        y3 = float('inf')
        x4 = float('-inf')
        y4 = float('-inf')
        # for p in points:
        #     x = p[0]
        #     y = p[1]
        #     xmin = min(x, xmin)
        #     ymin = min(y, ymin)
        #     xmax = max(x, xmax)
        #     ymax = max(y, ymax)
        x1 = int(points[0][0])
        y1 = int(points[0][1])
        x2 = int(points[1][0])
        y2 = int(points[1][1])
        x3 = int(points[2][0])
        y3 = int(points[2][1])
        x4 = int(points[3][0])
        y4 = int(points[3][1])
        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        # if xmin < 1:
        #     xmin = 1

        # if ymin < 1:
        #     ymin = 1

        return (x1,y1,x2,y2,x3,y3,x4,y4)
