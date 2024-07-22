#Problems to fix:
#issue 1 (minor issues)
#Last rescaling issue: portion of image visible changes when resizing and changing aspect ratios
#ie. image should not scale, but view should expand.

import os, sys
from PyQt6.QtWidgets import *#QApplication, QMainWindow, QWidget, QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPixmap, QColor, QPen, QBrush, QPainter
from PyQt6.QtCore import Qt, QRectF


zoom_step = 1.2 # Amount by which image will zoom on scrolling
zoom_scale = 1 #  Scale of image to display on screen
zoom_level = 0 #  How zoomed in/out the image is
image_index = 0

app = QApplication([])
window = QMainWindow()
centralwidget = QWidget(window)
layout = QVBoxLayout(centralwidget)
view = QGraphicsView()
scene = QGraphicsScene()

# pixmap = QPixmap('images/pixel.png')
pixmap = QPixmap('images/DOG.jpg')
# pixmap = QPixmap('images/largeimage.jpg')
# pixmap = QPixmap('images/transparent.png')

image = scene.addPixmap(pixmap)
image_ratio = pixmap.width()/pixmap.height()

window.setWindowTitle("Window Title")
window.setGeometry(300, 50, 500, 500) #app init x, y, w, h
window.setCentralWidget(centralwidget)

layout.setContentsMargins(0,0,0,0) #L, U, R, D
layout.addWidget(view)

view.setStyleSheet("background-color: green")
view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
view.setScene(scene)

def keyPressEvent(event):
    if event.key() == Qt.Key.Key_Escape:
        app.quit()
    elif event.key() == Qt.Key.Key_F11:
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        window.showNormal() if window.isFullScreen() else window.showFullScreen()
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    elif event.key() == Qt.Key.Key_Control:
        view.setDragMode(QGraphicsView.DragMode.NoDrag)
    elif event.key() == Qt.Key.Key_Space:
        resetSceneRect()
    event.accept()

def keyReleaseEvent(event):
    if event.key() == Qt.Key.Key_Control:
        view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
    event.accept()

def wheelEvent(event):
    global zoom_level
    if event.angleDelta().x() + event.angleDelta().y() > 0:
        view.scale(zoom_step, zoom_step)
        zoom_level += 1
    elif zoom_level > -5:
        view.scale(1/zoom_step, 1/zoom_step)
        zoom_level -= 1
    updateSceneRect()
    event.accept()

def resizeEvent(event = None):
    ## FIX ERROR CROPS SMALL PIECE
    global image_ratio, zoom_scale
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
    global scene

    viewport_rect = view.mapToScene(view.viewport().geometry()).boundingRect()

    rect = QRectF()

    rect.setTop(    viewport_rect.top()    - viewport_rect.bottom()                )
    rect.setLeft(   viewport_rect.left()   - viewport_rect.right()                 )
    rect.setBottom( viewport_rect.bottom() - viewport_rect.top()  + pixmap.height())
    rect.setRight(  viewport_rect.right()  - viewport_rect.left() + pixmap.width() )
    
    scene.setSceneRect(rect)

    #Draw border for debug
    for item in scene.items():
        if isinstance(item, QGraphicsRectItem):
            scene.removeItem(item)
    drawSceneBorder()
#debug
def resetSceneRect():
    global scene, image
    scene.setSceneRect(image.sceneBoundingRect())
    drawSceneBorder()
#debug
def drawSceneBorder():
    global scene
    rect = scene.sceneRect()
    border_color = QColor(0, 0, 0)  # Red
    fill_color = QColor(255, 100, 0, 100)  
    #scene.addRect(rect, QPen(border_color, 20), QBrush(fill_color))

startpos = None

current_rect_item = None

def mousePressEvent(event):
    global startpos, current_rect_item
    if Qt.KeyboardModifier.ControlModifier in event.modifiers():
        startpos = view.mapToScene(event.pos())
        # Create initial rectangle
        rect = QRectF(startpos, startpos)
        current_rect_item = scene.addRect(rect, QPen(QColor(0, 0, 0)), QBrush(QColor(255, 0, 0, 50)))
    else:
        view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        QGraphicsView.mousePressEvent(view, event)

def mouseMoveEvent(event):
    global current_rect_item, startpos
    if current_rect_item and startpos:
        current_pos = view.mapToScene(event.pos())
        rect = QRectF(startpos, current_pos).normalized()
        current_rect_item.setRect(rect)
    else:
        QGraphicsView.mouseMoveEvent(view, event)

def mouseReleaseEvent(event):
    global current_rect_item, startpos
    if current_rect_item:
        current_rect_item = None
    startpos = None
    view.setDragMode(QGraphicsView.DragMode.NoDrag)
    QGraphicsView.mouseReleaseEvent(view, event)



view.wheelEvent = wheelEvent
window.keyPressEvent = keyPressEvent
window.keyReleaseEvent = keyReleaseEvent
window.resizeEvent = resizeEvent

view.mousePressEvent = mousePressEvent
view.mouseMoveEvent = mouseMoveEvent
view.mouseReleaseEvent = mouseReleaseEvent

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

# for attribute in dir(event):
#         if not attribute.startswith('__'):
#             print(attribute)