from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import win32clipboard as win32cb # Copy Pasting Functionality (LOOK INTO DEFAULT pyqt6 clipboard features)
import win32api
from io import BytesIO
import os

# TEMP FIX (Might not be temp?)
from PIL import Image

from BISDebug import DebugWindow # Debugging
def debug_update(name, value):
    pass


CF_FILENAMEW = win32cb.RegisterClipboardFormat('FileNameW')
CF_PNG       = win32cb.RegisterClipboardFormat('PNG')
CF_TEXT      = win32cb.CF_TEXT
CF_DIBV5     = win32cb.CF_DIBV5

def convert_dib_to_png_bytes(dib_data: bytes) -> bytes:
    # Open the DIBV5 data using Pillow
    with BytesIO(dib_data) as input_stream:
        pil_image = Image.open(input_stream)

        # Save the image to a PNG format in memory
        with BytesIO() as output_stream:
            pil_image.save(output_stream, format="PNG")
            png_data = output_stream.getvalue()

    return png_data

class MainWindow(QMainWindow):
    variable_change = pyqtSignal(str, object) # Debugging
    def __init__(self):
        super().__init__()

        # Debugging
        self.debug_window = DebugWindow()
        self.variable_change.connect(self.debug_window.update_variable)
        self.debug_window.show()
        #

        self.setWindowTitle("Better Image Software : ALPHA")
        init_window_w, init_window_h = 750, 750 
        display_w = win32api.GetSystemMetrics(0)
        display_h = win32api.GetSystemMetrics(1)

        print(display_w, display_h)
        self.setGeometry(int((display_w/2)-(init_window_w/2)), int((display_h/2)-(init_window_h/2)), init_window_w, init_window_h)

        self.centralWidget = CentralWidget()
        self.setCentralWidget(self.centralWidget)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.button_open_file = QAction("&Open File  (Ctrl + O)")
        self.button_open_file.triggered.connect(self.dialog_open_file)
        self.file_menu.addAction(self.button_open_file)

    def __setattr__(self, name, value): # Debugging __setattr__ Updates tracked variables in DebugWindow when updated.
        debug_update(name, value)
        super().__setattr__(name, value)    

    def dialog_open_file(self):
        dialog = QFileDialog()
        file, _ = dialog.getOpenFileName(self, "Select an Image", filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)") #Update later to be generated from an array
        if file:
            self.centralWidget.view.setImage(file)

    def keyPressEvent(self, event: QKeyEvent | None): # Switch to a dict for better organization and faster lookup
        if event.key() == Qt.Key.Key_Escape:
            QApplication.quit()
        elif event.key() == Qt.Key.Key_F11:
            self.centralWidget.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
            window.showNormal() if window.isFullScreen() else window.showFullScreen()
            self.centralWidget.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_O:
            self.dialog_open_file()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_C:
            print("KeyBind [CTRL+C] -> Copy")
            self.copy()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            print("KeyBind [CTRL+V] -> Paste")
            self.paste()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            print("KeyBind [CTRL+S] -> Save")
            self.save()
        elif event.key() == Qt.Key.Key_1:
            print("KeyBind [1] -> toggleCrop")
            if self.centralWidget.view.image:
                self.centralWidget.view.toggleCrop()
        elif event.key() == Qt.Key.Key_2:
            print("KeyBind [2] -> print crop_selection.rect()")
            if self.centralWidget.view.crop_selection:
                print(self.centralWidget.view.crop_selection.rect())
        return super().keyPressEvent(event)
    
    def copy(self):
        return
        img = self.centralWidget.view.pixmap.toImage()
        buffer = QByteArray()  # Create a QByteArray buffer
        qbuffer = QBuffer(buffer)  # Wrap the QByteArray in a QBuffer
        qbuffer.open(QIODevice.OpenModeFlag.ReadWrite)  # Open the buffer for writing

        # Save the QImage to the QBuffer as a PNG
        img.save(qbuffer, "PNG")

        # Get the byte data from the buffer
        image_bytes = buffer.data()
        print(image_bytes)

    def paste(self):
        print("PASTING")
        win32cb.OpenClipboard()
        if win32cb.IsClipboardFormatAvailable(CF_PNG): # CF_PNG -> 49341
            print('CF_PNG')
            cb_data = win32cb.GetClipboardData(CF_PNG) #Bytes
            self.centralWidget.view.setImage(cb_data)

        ###FIX for img copied from web
        elif win32cb.IsClipboardFormatAvailable(CF_DIBV5): # CF_DIBV5 -> 17
            print('CF_DIBV5')
            cb_data = win32cb.GetClipboardData(CF_DIBV5) #Bytes
            cb_data = convert_dib_to_png_bytes(cb_data) #TEMP FIX CONVERT DIBV5 BYTES TO PNG BYTES
            self.centralWidget.view.setImage(cb_data)

        elif win32cb.IsClipboardFormatAvailable(CF_FILENAMEW): # CF_FILENAMEW -> 49159
            print('CF_FILENAMEW')
            cb_data = win32cb.GetClipboardData(CF_FILENAMEW)
            img_path = cb_data.decode('utf-16le').rstrip('\x00') #Windows' internal APIs use UTF-16LE and trailing \x00 for null terminator
            self.centralWidget.view.setImage(img_path)

        elif win32cb.IsClipboardFormatAvailable(CF_TEXT): # CF_TEXT -> 1
            print('CF_TEXT')
            cb_data = win32cb.GetClipboardData(CF_TEXT)
            img_path = cb_data.decode('utf-8')
            if os.path.exists(img_path):
                self.centralWidget.view.setImage(img_path)
        win32cb.CloseClipboard()

    def save(self):
        """
        Problem to solve (Many):
        Going to tackle this problem later as it is very complex.
        Current problem is dealing with all the different image types and flexibility of compression/metadata/quality
        Image Formats Defaults should be stored like so:
        https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#png-saving
        PNG -> PNG : max compression | metadata (y|n)
        JPG -> JPG : Quality 100
        """
        img = self.centralWidget.view.pixmap.toImage()
        print(type(img))

        buffer = QBuffer()
        buffer.setData(QByteArray())  # Initialize the buffer with an empty byte array
        buffer.open(QBuffer.OpenModeFlag.WriteOnly)
        
        # Save QImage to the buffer in PNG format (you can change format)
        img.save(buffer, "PNG")
        
        # Get the raw image data from the buffer
        byte_data = buffer.data()

        # Convert byte data to a bytes-like object that Pillow can work with
        pil_image = Image.open(BytesIO(byte_data))
        # pil_image.save('output_image.webp', format='WebP', lossless = True, quality = 100)
        pil_image.save('output.png', format='PNG', optimize = True)
    
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
    
    def __setattr__(self, name, value): # Debugging
        debug_update(name, value)
        super().__setattr__(name, value)
        
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

    def __setattr__(self, name, value): # Debugging
        debug_update(name, value)
        super().__setattr__(name, value)

    def setImage(self, data : str | bytes): #img is a str filepath or bytes of img data
        """
        Currently converting filepath to bytes in function. 
        Should be out of prior responsibility: fix later.
        """
        self.is_cropping = False #?
        self.zoom_level = 1.0
        self.resetTransform()
        self.scene.clear()
        self.pixmap = QPixmap()
        if isinstance(data, str):
            with open(data, "rb") as image_file:
                data = image_file.read()
                print('convert')
        if isinstance(data, bytes):
            self.pixmap.loadFromData(data)
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
        # print('scaleView')
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


    #Drag and Drop
    """
    For some reason QDragEnterEvent, dragLeaveEvent, dragMoveEvent
    need to be present for dropEvent to function.
    Additionally, QDragEnterEvent needs to be present; not dragEnterEvent.
    Something to look into later
    """
    def QDragEnterEvent(self, event):
        pass
    def dragLeaveEvent(self, event):
        pass
    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        print("DROPEVENT")
        data = event.mimeData()
        print(data.text()) #Add functionality to get images from drag and drop from web (ie requests)
        if url := data.urls():
            url = url[0]
            self.setImage(url.toString().split('///')[1]) #url is formatted 'file:///C:/....image.ext'

    #Drag and Drop

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
        #path.setFillRule(Qt.FillRule.OddEvenFill) #Might be commented due to being default rule
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
    
def debug_update(name, value):
    window.variable_change.emit(name, value)
    print(name, value)

app.exec()