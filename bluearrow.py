from PyQt5.QtWidgets import QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QBrush, QPainter, QImage, QPixmap
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSlider, QStyle, QSizePolicy, QFrame, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSpacerItem
from PyQt5.QtCore import Qt, QUrl, QDir, QSize, QRectF, QPointF
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtGui import QIcon, QPalette, QImage, QBrush, QMouseEvent, QPixmap
from PyQt5 import QtMultimediaWidgets
from PyQt5.QtGui import QPainter
from moviepy.editor import VideoFileClip
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from PyQt5.QtCore import QTimer

class BlueArrow(QGraphicsPixmapItem):
    def __init__(self, video_editor, timeline, parent=None):
        super().__init__(parent)
        self.video_editor = video_editor
        self.timeline = timeline
        arrow = QImage("blue_arrow.png")  # Update the path to your arrow image file
        arrow = arrow.scaledToHeight(32)
        self.setPixmap(QPixmap.fromImage(arrow))

        # Set the arrow position above the timeline with the center of the arrow above the first frame
        self.setPos(QPointF(-self.pixmap().width() / 2, -self.pixmap().height()))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            self.update_video_position(value.x())
        return super().itemChange(change, value)

    def update_video_position(self, x):
        num_images = len(self.timeline.scene().items()) - 1  # Subtract 1 to exclude the BlueArrow item
        video_duration = self.video_editor.mediaPlayer.duration()
        video_position = int((x / (self.timeline.scene().width() - self.pixmap().width())) * video_duration)
        self.video_editor.setPosition(video_position)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            # Calculate the new x position while keeping the y position constant
            new_pos = event.scenePos()
            x = new_pos.x()
            x = min(max(x, 0), self.timeline.scene().width() - self.pixmap().width())

            # Update arrow position and video position
            self.setPos(QPointF(x, -self.pixmap().height()))
            self.update_video_position(x)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self.timeline.playing:
            return
        if event.button() == Qt.LeftButton:
            self.drag_start_x = event.pos().x()
            self.drag_start_y = event.pos().y()
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.timeline.playing:
            return
        if event.button() == Qt.LeftButton:
            event.accept()