from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QBrush, QPainter, QImage, QPixmap
from bluearrow import BlueArrow
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


class Timeline(QGraphicsView):
    def __init__(self, video_editor, parent=None):
        super().__init__(parent)
        self.video_editor = video_editor
        self.playing = False
        self.arrow_position = 0
        self.timer = None
        self.setScene(QGraphicsScene(self))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.TextAntialiasing)

        brush = QBrush(Qt.black)  # changed the background color to black
        self.setBackgroundBrush(brush)

        self.setFrameStyle(QFrame.NoFrame)  # removed the frame around the timeline

    def move_arrow(self, dx):
        arrow = [item for item in self.scene().items() if isinstance(item, BlueArrow)][0]
        new_pos = arrow.x() + dx
        arrow.setPos(QPointF(new_pos, -arrow.pixmap().height()))

    def move_arrow_while_playing(self, position):
        video_duration = self.video_editor.mediaPlayer.duration()
        if video_duration == 0:
            return
        arrow_position = (position / video_duration) * (self.scene().width() - 1)
        self.move_arrow(arrow_position - self.arrow_position)
        self.arrow_position = arrow_position



    def start_arrow_movement(self):
        self.arrow_position = 0
        self.playing = True



    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.timeline.stop()
        else:
            self.playing = True
            self.mediaPlayer.play()
            # self.timeline.play()



    def next_frame(self):
        # Advance to the next frame
        self.current_frame += 1

        # Stop the timer if all frames have been played
        if self.current_frame == len(self.scene().items()):
            self.stop()
            return

        # Move the blue arrow to the next frame
        item = self.scene().items()[self.current_frame]
        x_offset = item.data(Qt.UserRole)
        # self.move_arrow(x_offset)

        # Update the video position based on the current frame
        video_duration = self.video_editor_window.mediaPlayer.duration()
        frame_duration = round(500 / self.frame_rate)  # in milliseconds
        video_position = int(self.current_frame * frame_duration)
        self.video_editor_window.setPosition(video_position)



    def stop(self):
        # Set the playing flag to False
        self.playing = False

        # Stop the timer if it is running
        if self.timer is not None and self.timer.isActive():
            self.timer.stop()




    def display_frames(self, frames, frame_rate):
        self.frame_rate = frame_rate
        self.scene().clear()
        width = self.width()
        height = self.height() / 2
        frame_count = len(frames)
        if frame_count == 0:
            return
        frame_width = int((width + frame_count - 1) / frame_count)
        x_offset = 0
        for frame in frames:
            pixmap = QPixmap.fromImage(frame).scaled(frame_width, int(height))
            item = QGraphicsPixmapItem(pixmap)
            item.setPos(QPointF(x_offset, 0))
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            item.setFlag(QGraphicsItem.ItemIsMovable, True)
            item.setData(Qt.UserRole, x_offset)
            item.setScale(1.0)
            item.setOpacity(1.0)
            x_offset += frame_width
            self.scene().addItem(item)
        blue_arrow = BlueArrow(self.parent().parent(), self, None)
        self.scene().addItem(blue_arrow)  # Update this line

        self.setSceneRect(QRectF(self.scene().itemsBoundingRect()))