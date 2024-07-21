#Problems to fix
# Fix image movement and scaling when resizing app
# maintain image position/[relative scale] when fullscreening app (f11)
#fix image scrolling? Might not be necesarry

#change funcitonality of Holding CTRL while zooming to zoom the image and keep its position to where it is. instead of zooming into viewcenter.
import os, sys
from PyQt6.QtWidgets import *#QApplication, QMainWindow, QWidget, QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPixmap, QColor, QPen, QBrush, QTransform
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF

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
pixmap = QPixmap('images/DOG.jpg')
# pixmap = QPixmap('images/largeimage.jpg')
# pixmap = QPixmap('images/transparent.png')

window.setWindowTitle("Window Title")
window.setGeometry(300, 50, 500, 500) #app init x, y, w, h
window.setCentralWidget(centralwidget)

layout.setContentsMargins(0,0,0,0)
layout.addWidget(view)

view.setStyleSheet("background-color: green")
view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
#view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter) ?does anything
view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
view.setScene(scene)

def centerImage():
    global image, view
    view_rect = view.viewport().rect()
    view_center = view.mapToScene(view_rect.center())
    image_rect = image.sceneBoundingRect()
    image_center = image_rect.center()
    
    # Calculate the difference between the centers
    diff = view_center - image_center
    
    # Move the image by this difference
    image.setPos(image.pos() + diff + QPointF(1, 0)) #fix to only add offsett when needed
    
image = scene.addPixmap(pixmap)
image_ratio = pixmap.width()/pixmap.height()
centerImage()  # Add this line

def keyPressEvent(event):
    global image_index, image
    # print(event.key())
    if   event.key() == Qt.Key.Key_Escape: app.quit()
    elif event.key() == Qt.Key.Key_F11: 
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        window.showNormal() if window.isFullScreen() else window.showFullScreen()
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    elif event.key() == Qt.Key.Key_Right :
        image_index = (image_index + 1) % len(os.listdir('images'))
        # updateImage(image_index)
    elif event.key() == Qt.Key.Key_Left : 
        image_index = (image_index - 1) % len(os.listdir('images'))
        # updateImage(image_index)        
    elif event.key() == Qt.Key.Key_Space : updateSceneRect()
    elif event.key() == Qt.Key.Key_Control :
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
    elif event.key() == Qt.Key.Key_0 :
        print(view.mapFromScene(image.boundingRect().center()))
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
    global image_ratio, zoom_scale, zoom_level, scene

    view_ratio = view.width()/view.height()
    widthratio = view.width()/(pixmap.width()*zoom_scale)
    heightratio = view.height()/(pixmap.height()*zoom_scale)
    if view_ratio < image_ratio:
        zoom_scale *= widthratio
        view.scale(widthratio, widthratio)
    else:
        zoom_scale *= heightratio
        view.scale(heightratio, heightratio)
    updateSceneRect()
    centerImage()

    #elif zoom_level < 0: 
    #    if heightratio < 1 or widthratio < 1: zoom_level = 0
    #else:
    #    pass#print(widthratio, heightratio)

def updateSceneRect():
    global scene, image

    viewport_rect = view.mapToScene(view.viewport().geometry()).boundingRect()

    top_distance = -1 * viewport_rect.top()
    left_distance = -1 * viewport_rect.left()
    bottom_distance = viewport_rect.bottom()-pixmap.height()
    right_distance = viewport_rect.right()-pixmap.width()
        
    # Create a new QRectF with the desired coordinates

    rect = scene.sceneRect()
    rect.moveCenter(scene.sceneRect().center())
    # print("CENTER CHECK", scene.sceneRect().center())
    # print(viewport_rect)
    # print(rect)
    rect.setTop(    viewport_rect.top()     - pixmap.height()   * 1.5   - bottom_distance)
    rect.setLeft(   viewport_rect.left()    - pixmap.width()    * 1.5   - right_distance)
    rect.setBottom( viewport_rect.bottom()  + pixmap.height()   / 2     + top_distance)
    rect.setRight(  viewport_rect.right()   + pixmap.width()    / 2     + left_distance)
    
    scene.setSceneRect(rect)

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