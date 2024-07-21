#Problems to fix:
#issue 1
#Last rescaling issue: portion of image visible changes when resizing and changing aspect ratios
#ie. image should not scale, but view should expand.

import os, sys
from PyQt6.QtWidgets import *#QApplication, QMainWindow, QWidget, QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPixmap, QColor, QPen, QBrush, QTransform
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, QTimer


zoom_step = 1.2 # Amount by which image will zoom on scrolling
zoom_scale = 1 #  Scale of image to display on screen
zoom_level = 0 #  How zoomed in/out the image is
image_index = 0

app = QApplication(sys.argv)
window = QMainWindow()
centralwidget = QWidget(window)
layout = QVBoxLayout(centralwidget)
view = QGraphicsView()
scene = QGraphicsScene()

# pixmap = QPixmap('images/pixel.png')
# pixmap = QPixmap('images/DOG.jpg')
pixmap = QPixmap('images/largeimage.jpg')
# pixmap = QPixmap('images/transparent.png')

image = scene.addPixmap(pixmap)
image_ratio = pixmap.width()/pixmap.height()
#centerImage()  # Add this line

window.setWindowTitle("Window Title")
window.setGeometry(300, 50, 500, 500) #app init x, y, w, h
window.setCentralWidget(centralwidget)

layout.setContentsMargins(50,50,50,50)
layout.addWidget(view)

view.setStyleSheet("background-color: green")
view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
view.setScene(scene)

def keyPressEvent(event):
    global image_index, image
    # print(event.key())
    if   event.key() == Qt.Key.Key_Escape: app.quit()
    elif event.key() == Qt.Key.Key_F11: 
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        window.showNormal() if window.isFullScreen() else window.showFullScreen()
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    elif event.key() == Qt.Key.Key_Control :
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
    event.accept()

def keyReleaseEvent(event):
    if event.key() == Qt.Key.Key_Control : 
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

def wheelEvent(event):
    global zoom_scale, zoom_level, pixmap
    if event.angleDelta().x() + event.angleDelta().y() > 0:
        view.scale(zoom_step, zoom_step)
        # zoom_scale *= zoom_step
        zoom_level += 1 #if (pixmap.height()*zoom_scale) > view.height() or (pixmap.width() *zoom_scale)> view.width() else zoom_level + 1
    elif zoom_level > -99:
        view.scale(1/zoom_step, 1/zoom_step)
        # zoom_scale /= zoom_step
        zoom_level -= 1
    updateSceneRect()
    # print(round(zoom_scale, 3), zoom_level)
    event.accept()

def resizeEvent(event = None):
    ## FIX ERROR CROPS SMALL PIECE
    global image_ratio, zoom_scale, zoom_level, scene, resize_timer

    center_before = view.mapToScene(view.viewport().rect().center())
    print(center_before)
    view_ratio = view.width()/view.height()
    widthratio = view.width()/(pixmap.width()*zoom_scale)
    heightratio = view.height()/(pixmap.height()*zoom_scale)
    if view_ratio < image_ratio:
        zoom_scale *= widthratio
        view.scale(widthratio, widthratio)  #remove for issue 1 fix
    else:
        zoom_scale *= heightratio 
        view.scale(heightratio, heightratio) #remove for issue 1 fix
    updateSceneRect()

def updateSceneRect():
    global scene, image

    viewport_rect = view.mapToScene(view.viewport().geometry()).boundingRect()

    top_distance = -1 * viewport_rect.top()
    left_distance = -1 * viewport_rect.left()
    bottom_distance = viewport_rect.bottom()-pixmap.height()
    right_distance = viewport_rect.right()-pixmap.width()
        
    # Create a new QRectF with the desired coordinates

    rect = QRectF()

    rect.setTop(    viewport_rect.top()     - pixmap.height()    - bottom_distance)
    rect.setLeft(   viewport_rect.left()    - pixmap.width()     - right_distance)
    rect.setBottom( viewport_rect.bottom()  + pixmap.height()    + top_distance)
    rect.setRight(  viewport_rect.right()   + pixmap.width()     + left_distance)
    
    scene.setSceneRect(rect)

    #Draw border for debug
    for item in scene.items():
        if isinstance(item, QGraphicsRectItem):
            scene.removeItem(item)
    drawSceneBorder()
#debug
def resetSceneRect():
    global scene, image
    print("Reset", image.sceneBoundingRect())
    scene.setSceneRect(image.sceneBoundingRect())
    drawSceneBorder()
#debug
def drawSceneBorder():
    global scene
    rect = scene.sceneRect()
    border_color = QColor(0, 0, 0)  # Red
    fill_color = QColor(255, 100, 0, 100)  
    scene.addRect(rect, QPen(border_color, 20), QBrush(fill_color))

view.wheelEvent = wheelEvent
window.keyPressEvent = keyPressEvent
window.keyReleaseEvent = keyReleaseEvent
window.resizeEvent = resizeEvent

window.showNormal()
window.resizeEvent()

sys.exit(app.exec())

#Switch Image
#pixmap = QPixmap('newimage')
#scene.removeItem(image)
#image = scene.addPixmap(pixmap)
#resizeEvent()

# def updateImage(image_index: int):
    # print("UPDATE IMAGE")
    # global image, pixmap
    # pixmap = QPixmap(os.listdir('Images')[image_index])
    # scene.removeItem(image)
    # image = scene.addPixmap(pixmap)
    # centerImage()  # Add this line
    # resizeEvent()