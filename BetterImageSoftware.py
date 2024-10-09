from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Better Image Software")
        self.setGeometry(200, 50, 600, 500)

        self.centralWidget = CentralWidget()
        self.setCentralWidget(self.centralWidget)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.button_open_file = QAction("&Open File  (Ctrl + O)")
        self.button_open_file.triggered.connect(self.dialog_open_file)
        self.file_menu.addAction(self.button_open_file)

    def dialog_open_file(self):
        dialog = QFileDialog()
        file, _ = dialog.getOpenFileName(self, "Select an Image", filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file:
            self.centralWidget.view.setImage(file)

    def keyPressEvent(self, event: QKeyEvent | None):
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
        elif event.key() == Qt.Key.Key_F11:
            self.centralWidget.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
            window.showNormal() if window.isFullScreen() else window.showFullScreen()
            self.centralWidget.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_O:
            self.dialog_open_file()
        elif event.key() == Qt.Key.Key_1:
            if self.centralWidget.view.image:
                self.centralWidget.view.toggleCrop()
        elif event.key() == Qt.Key.Key_2:
            print(self.centralWidget.view.crop_selection.rect())
        return super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        self.centralWidget.view.scaleView(None)

class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.view = ImageViewer()
        layout.addWidget(self.view)
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)
        
class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.setStyleSheet("background-color: gray;")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.zoom_level = 1.0
        self.image, self.pixmap = None, None

        self.crop_overlay = None
        self.crop_selection = None
        self.is_cropping = False

    def setImage(self, path):
        self.is_cropping = False #?
        self.zoom_level = 1.0
        self.resetTransform()
        self.scene.clear()
        self.pixmap = QPixmap(path)
        self.image = self.scene.addPixmap(self.pixmap)
        self.scaleView(None)
        self.centerOn(self.pixmap.width()/2, self.pixmap.height()/2)
    
    def mousePressEvent(self, event):
        #self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        #super().mousePressEvent(event)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        # self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self.image:
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            #self.zoom_level *= factor
            self.scale(factor, factor)
            self.updateSceneRect()

    def scaleView(self, event):
        if self.image:
            width_scale  = self.width() / self.pixmap.width()
            height_scale = self.height() / self.pixmap.height()
            scale_factor = min(width_scale, height_scale) / self.zoom_level
            self.zoom_level *= scale_factor
            self.scale(scale_factor, scale_factor)
            self.updateSceneRect()
    
    def updateSceneRect(self):
        viewport_rect = self.mapToScene(self.viewport().geometry()).boundingRect()
        rect = QRectF()
        rect.setTop(    viewport_rect.top()    - viewport_rect.bottom()                     )
        rect.setLeft(   viewport_rect.left()   - viewport_rect.right()                      )
        rect.setBottom( viewport_rect.bottom() - viewport_rect.top()  + self.pixmap.height())
        rect.setRight(  viewport_rect.right()  - viewport_rect.left() + self.pixmap.width() )
        self.scene.setSceneRect(rect)

    def toggleCrop(self):
        if self.is_cropping:
            self.is_cropping = False
            self.scene.removeItem(self.crop_overlay)
            self.scene.removeItem(self.crop_selection)
        else:
            self.is_cropping = True
            self.crop_overlay = CropOverlay(self.scene)
            self.scene.addItem(self.crop_overlay)
            self.crop_selection = CropSelection(0, 0, self.pixmap.width(), self.pixmap.height(), self.crop_overlay)
            self.scene.addItem(self.crop_selection)
            self.crop_overlay.setCropSelection(self.crop_selection.rect())
            self.update()

class CropOverlay(QGraphicsItem):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.crop_selection = QRectF()
    
    def boundingRect(self):
            return self.scene.sceneRect()

    def paint(self, painter, option, widget):
        path = QPainterPath()
        path.addRect(self.scene.sceneRect())
        path.addRect(self.crop_selection)
        #path.setFillRule(Qt.FillRule.OddEvenFill)
        painter.setBrush(QColor(0, 0, 0, 128))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

    def setCropSelection(self, crop_selection):
        self.crop_selection = crop_selection
        self.update()

class CropSelection(QGraphicsRectItem):
    def __init__(self, x, y, width, height, crop_overlay):
        super().__init__(x, y, width, height)

        self.crop_overlay = crop_overlay
        self.setPen(QPen(Qt.GlobalColor.black, .5, join=Qt.PenJoinStyle.MiterJoin))
        self.setAcceptHoverEvents(True)
        
        self.handles = {}
        self.handlesize = 5
        self.updateHandles()
        self.start_pos = None

    def updateHandles(self):
        s = self.handlesize
        b = self.boundingRect()
        self.handles = {
            'tl': QRectF(b.left(), b.top(), s, s),
            'tr': QRectF(b.right() - s, b.top(), s, s),
            'bl': QRectF(b.left(), b.bottom() - s, s, s),
            'br': QRectF(b.right() - s, b.bottom() - s, s, s),
            'tm': QRectF(b.center().x() - s / 2, b.top(), s, s),
            'bm': QRectF(b.center().x() - s / 2, b.bottom() - s, s, s),
            'lm': QRectF(b.left(), b.center().y() - s / 2, s, s),
            'rm': QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        }

    def handleAt(self, point):
        for k, v in self.handles.items():
            if v.contains(point):
                return k
        return None
    
    def hoverMoveEvent(self, event): #Inefficient as check through each handle every tick
        handle = self.handleAt(event.pos())
        cursor = Qt.CursorShape.ArrowCursor
        if handle is not None:
            if handle in ['tl', 'br']:
                cursor = Qt.CursorShape.SizeFDiagCursor
            elif handle in ['tr', 'bl']:
                cursor = Qt.CursorShape.SizeBDiagCursor
            elif handle in ['tm', 'bm']:
                cursor = Qt.CursorShape.SizeVerCursor
            elif handle in ['lm', 'rm']:
                cursor = Qt.CursorShape.SizeHorCursor
        self.setCursor(cursor)
        # super().hoverMoveEvent(event)

    def interactiveResize(self, mouse_pos):
        offset = mouse_pos - self.start_pos
        rect = self.mouse_press_rect
        mode = self.resize_mode

        if mode == 'tl':
            rect = rect.adjusted(offset.x(), offset.y(), 0, 0)
        elif mode == 'tr':
            rect = rect.adjusted(0, offset.y(), offset.x(), 0)
        elif mode == 'bl':
            rect = rect.adjusted(offset.x(), 0, 0, offset.y())
        elif mode == 'br':
            rect = rect.adjusted(0, 0, offset.x(), offset.y())
        elif mode == 'tm':
            rect = rect.adjusted(0, offset.y(), 0, 0)
        elif mode == 'bm':
            rect = rect.adjusted(0, 0, 0, offset.y())
        elif mode == 'lm':
            rect = rect.adjusted(offset.x(), 0, 0, 0)
        elif mode == 'rm':
            rect = rect.adjusted(0, 0, offset.x(), 0)
        
        self.setRect(rect.normalized().toRect().toRectF())
        self.updateHandles()

    def mousePressEvent(self, event):
        if Qt.KeyboardModifier.ControlModifier not in event.modifiers():
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)  
        self.start_pos = event.pos()
        self.mouse_press_rect = self.rect()
        self.resize_mode = self.handleAt(event.pos())
        if self.resize_mode:
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resize_mode:
            self.interactiveResize(event.pos())
        elif self.start_pos:
            new_pos = self.pos() + event.pos() - self.start_pos
            self.setPos(new_pos.toPoint().toPointF())
        else:
            super().mouseMoveEvent(event)
        self.crop_overlay.setCropSelection(self.mapRectToScene(self.rect()))

    def mouseReleaseEvent(self, event):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)  
        self.resize_mode = None
        self.start_pos = None
        self.update()

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.setPen(QPen(QColor(0, 0, 0), .5, Qt.PenStyle.SolidLine, join = Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(QBrush(QColor(255, 255, 255), Qt.BrushStyle.SolidPattern))
        for handle in self.handles.values():
            painter.drawRect(handle)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()