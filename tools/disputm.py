#!/usr/bin/env python

import json

try:
    from PySide import QtCore, QtGui
except ImportError:
    print("[error] sudo apt-get install python-pyside")
    import sys; sys.exit(1)

try:
    import gladys
except ImportError:
    print("[error] install gladys [and setup PYTHONPATH]")
    import sys; sys.exit(1)

def draw_path(paintable, path, sx=1.0, sy=1.0):
    painter = QtGui.QPainter(paintable)
    painter.scale(sx, sy)
    painter.setPen(QtGui.QPen(QtCore.Qt.green, 4))
    # TODO draw path
    painter.drawPolyline(path)
    painter.setPen(QtGui.QPen(QtCore.Qt.red, 4))
    for num, point in enumerate(path):
        painter.drawText(point, "%i"%num)
    painter.end()

class ImageLabel(QtGui.QLabel):
    def __init__(self):
        QtGui.QLabel.__init__(self)
        self.path = QtGui.QPolygonF()
        self.scale = 1.0
    def set_image(self, image):
        self.image = image
        size = image.size() * self.scale
        self.setPixmap(QtGui.QPixmap.fromImage( image.scaled(size) ))
    def paint_path(self, path):
        self.path = QtGui.QPolygonF([ QtCore.QPointF(x, y) for x, y in path ])
        self.repaint()
    def paintEvent(self, event):
        QtGui.QLabel.paintEvent(self, event)
        draw_path(self, self.path, self.scale, self.scale)
    def set_scale(self, scale=1.0):
        self.scale = scale
        self.set_image(self.image)
        self.repaint()


class MainWindow(QtGui.QMainWindow):
    def __init__(self, argv):
        super(MainWindow, self).__init__()
        # image viewer
        self.image_label = ImageLabel()
        self.setCentralWidget(self.image_label)

        self.setWindowTitle("Eurasample")
        self.resize(200, 200)

        self.points_pix = []
        self.image_gdal = gladys.gdal(argv[1])
        self.image_disp = QtGui.QImage(argv[1])
        self.image_label.set_image(self.image_disp)

        print("===============================\n"
              "  Welcome to Display UTM !\n"
              "===============================\n\n"
              "Actions\n"
              "-------\n"
              " - Click     = select points\n"
              " - C         = clear points\n"
              " - Space     = get points UTM\n"
              " - Escape    = quit\n")

        # key bindings
        self._bindings = {}
        self.bind(QtCore.Qt.Key_Escape, self.close)
        self.bind(QtCore.Qt.Key_C,      self.clear_points)
        self.bind(QtCore.Qt.Key_Space,  self.get_utm_coord)
        self.bind(QtCore.Qt.Key_Q,      self.zoom_in)
        self.bind(QtCore.Qt.Key_A,      self.zoom_out)

    def zoom_in(self):
        self.image_label.set_scale(2.0)

    def zoom_out(self):
        self.image_label.set_scale(0.5)

    def point_pix2utm(self, point):
        return gladys.point_pix2utm(self.image_gdal, *point)

    def point_pix2custom(self, point):
        return gladys.point_pix2custom(self.image_gdal, *point)

    def get_utm_coord(self):
        utm_coordinates = []
        custom_coordinates = []
        for point in self.points_pix:
            utm    = self.point_pix2utm(point)
            custom = self.point_pix2custom(point)
            utm_coordinates.append(utm)
            custom_coordinates.append(custom)
            print("%s -> %s" % ( str(point), str(utm) ) )
        for x, y in custom_coordinates:
            print("%f %f" % (x, y) )
        self.display_path()
        self.save_custom(custom_coordinates)
        self.save_image()

    def save_image(self):
        image = self.image_disp.copy()
        path  = self.image_label.path
        draw_path(image, path)
        image.save('/tmp/path.png')

    def display_path(self):
        self.image_label.paint_path(self.points_pix)

    def save_custom(self, coord):
        with open('/tmp/path.txt', 'w') as f:
            for x, y in coord:
                f.write("goto %f %f\n" % (x, y) )

    def clear_points(self):
        self.points_pix = []
        print("clear points")

    def bind(self, key, func):
        self._bindings[key] = func

    # PySide.QtGui.QWidget.keyPressEvent(event)
    def keyPressEvent(self, event):
        if event.key() in self._bindings:
            self._bindings[event.key()]()

    # PySide.QtGui.QWidget.mousePressEvent(event)
    def mousePressEvent(self, event):
        pose = event.pos()
        point = [pose.x(), pose.y()]
        if self.points_pix and self.points_pix[-1] == point:
            return # skip double click
        self.points_pix.append(point)
        print("new point: %s" % str(point) )

def main(argv=[]):
    if len(argv) < 2:
        print("usage: %s geoimage"%argv[0])
        return 1
    app = QtGui.QApplication(argv)
    mww = MainWindow(argv)
    mww.show()
    return app.exec_()

if __name__ == '__main__':
    import sys
    sys.exit( main(sys.argv) )
