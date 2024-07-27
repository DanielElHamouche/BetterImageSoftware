#Problems to fix:
#issue 1 (minor issues)
#Last rescaling issue: portion of image visible changes when resizing and changing aspect ratios
#ie. image should not scale, but view should expand.


#issue 2
#allow crop from 0,0

#issue 3
#make zoom limits, ie range of zoom_level dependent on image size. ie not pixel count

#Issue 4
# fulscreening and not moving mouse results in zooming to incorrect area

from PyQt6.QtWidgets import *#QApplication, QMainWindow, QWidget, QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPixmap, QColor, QPen, QBrush, QImage
from PyQt6.QtCore import Qt, QRectF, QPointF
import os, sys
import cv2


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

filepath = 'images/DOG.jpg'
# filepath = 'images/pixel.png'
# filepath = 'images/largeimage.jpg'

cv2image = cv2.imread(filepath)
pixmap = QPixmap(filepath)
image = scene.addPixmap(pixmap)
image_ratio = pixmap.width()/pixmap.height()


window.setWindowTitle("Window Title")
window.setGeometry(300, 50, 500, 500) #app init x, y, w, h
window.setCentralWidget(centralwidget)

layout.setContentsMargins(0,0,0,0) #L, U, R, D
layout.addWidget(view)

view.setStyleSheet("background-color: gray")
view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
view.setDragMode(QGraphicsView.DragMode.NoDrag)
view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
view.setScene(scene)

def keyPressEvent(event):
    global current_rect_item, cv2image, scene, image
    if event.key() == Qt.Key.Key_Escape:
        app.quit()
    elif event.key() == Qt.Key.Key_F11:
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        window.showNormal() if window.isFullScreen() else window.showFullScreen()
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
    elif event.key() == Qt.Key.Key_Control:
        if view.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            view.setDragMode(QGraphicsView.DragMode.NoDrag)
    elif event.key() == Qt.Key.Key_Space:
        if current_rect_item:
            rect = current_rect_item.rect()
            print(rect.x(), rect.y(), rect.x() + rect.width(), rect.y()+rect.height())
            
            y_start = max(0, int(rect.y()))
            y_end = min(cv2image.shape[0], int(rect.y() + rect.height()))
            x_start = max(0, int(rect.x()))
            x_end = min(cv2image.shape[1], int(rect.x() + rect.width()))

            imagecrop = cv2image[y_start:y_end, x_start:x_end]
            pixmap = cv2_to_pixmap(imagecrop)
            scene.removeItem(image)
            image = scene.addPixmap(pixmap)
            resizeEvent()
            
    event.accept()

def cv2_to_pixmap(cv2_image):
    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    
    # Get the shape of the image
    height, width, _ = rgb_image.shape
    
    # Create QImage from numpy array
    bytes_per_line = 3 * width
    q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
    
    # Convert QImage to QPixmap
    pixmap = QPixmap.fromImage(q_image)
    
    return pixmap


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

start_x, start_y = None, None

current_rect_item = None

def mousePressEvent(event):
    global start_x, start_y, current_rect_item
    if Qt.KeyboardModifier.ControlModifier in event.modifiers():
        current_rect_item = None
        for item in scene.items():
            if isinstance(item, QGraphicsRectItem):
                scene.removeItem(item)
        startpos = view.mapToScene(event.pos())
        start_x, start_y = round(startpos.x()), round(startpos.y())
        print(start_x, start_y)
        #print(startpos, "before")
        #print(round(startpos.x()), round(startpos.y()), "ROUND")
        #print(type(round(startpos.x())), type(round(startpos.y())), "ROUND")
        #startpos = QPointF(round(x), round(y))
        #startpos = QPointF(0.0, 0.0)
        print(startpos, "after")
        #print('SIR', QPointF(0, 0))
        # Create initial rectangle
        rect = QRectF(start_x, start_y, 0, 0)
        current_rect_item = scene.addRect(rect, 
                                  QPen(QColor(0, 0, 0), .1, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin), 
                                  QBrush(QColor(255, 0, 0, 50)))
    else:
        pass
        view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        QGraphicsView.mousePressEvent(view, event)

def mouseMoveEvent(event):
    global current_rect_item, start_x, start_y
    if current_rect_item and not start_x == None:
        current_pos = view.mapToScene(event.pos())
        end_x, end_y = round(current_pos.x()), round(current_pos.y())
        #current_pos = QPointF(round(current_pos.x()), round(current_pos.y()))
        rect = QRectF(start_x, start_y, end_x - start_x, end_y - start_y)
        current_rect_item.setRect(rect)
    else:
        QGraphicsView.mouseMoveEvent(view, event)

def mouseReleaseEvent(event):
    global current_rect_item, start_x, start_y
    start_x, start_y = None, None
    view.setDragMode(QGraphicsView.DragMode.NoDrag)
    QGraphicsView.mouseReleaseEvent(view, event)



view.wheelEvent = wheelEvent
window.keyPressEvent = keyPressEvent
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