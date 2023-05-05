import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSlider, QStyle, QSizePolicy, QFrame, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSpacerItem
from PyQt5.QtCore import Qt, QUrl, QDir, QSize, QRectF, QPointF
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtGui import QIcon, QPalette, QImage, QBrush, QMouseEvent, QPixmap
from PyQt5 import QtMultimediaWidgets
from PyQt5.QtGui import QPainter
from moviepy.editor import VideoFileClip
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from PyQt5.QtCore import QTimer



import random



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








class VideoEditorWindow(QMainWindow):
    def __init__(self):
        super(VideoEditorWindow, self).__init__()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.playlist = QMediaPlaylist()
        self.mediaPlayer.setPlaylist(self.playlist)
        self.timeline = Timeline(self)
        self.initUI()
    
    def generate_frames(self, video_path):
    # You can change the frame_rate to get more or less frames
        frame_rate = 1
        command = f'ffmpeg -i "{video_path}" -vf fps={frame_rate} frame_%04d.png'
        os.system(command)
        frames = []
        for file in sorted([f for f in os.listdir() if f.startswith("frame_") and f.endswith(".png")], key=lambda x: int(x.split("_")[1].split(".")[0])):
            if file.startswith("frame_") and file.endswith(".png"):
                frame = QImage(file)
                frames.append(frame)
                os.remove(file)
        return frames

    def initUI(self):
        self.setWindowTitle("Video Editor")
        self.setFixedSize(1200, 800)
        self.setWindowIcon(QIcon('icon.png'))

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QImage("background.jpg")))
        self.setPalette(palette)

        openButton = QPushButton('Open', self)
        openButton.setFixedWidth(80)
        openButton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font: bold 14px;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        openButton.clicked.connect(self.openFile)

        playButton = QPushButton(self)
        playButton.setFixedSize(24, 24)
        playButton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font: bold 14px;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        playButton.clicked.connect(self.play)
        self.playButton = playButton
        self.mediaPlayer.stateChanged.connect(self.toggle_play_pause_button)



        self.positionSlider = QSlider(Qt.Horizontal, self)
        self.positionSlider.setFixedWidth(300)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.durationLabel = QLabel(self)
        self.durationLabel.setStyleSheet("color: white")


        self.timeLabel = QLabel(self)
        self.timeLabel.setStyleSheet("color: white")

        hbox_main_controls = QHBoxLayout()
        hbox_main_controls.addWidget(openButton)
        hbox_main_controls.addSpacing(10)
        hbox_main_controls.addWidget(playButton)
        hbox_main_controls.addSpacing(10)
        hbox_main_controls.addWidget(self.timeLabel)
        hbox_main_controls.addSpacing(10)
        hbox_main_controls.addWidget(self.positionSlider)


        hbox_controls = QHBoxLayout()
        hbox_controls.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        hbox_controls.addLayout(hbox_main_controls)
        hbox_controls.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.videoWidget = QtMultimediaWidgets.QVideoWidget(self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.videoWidget.setFixedSize(800, 450)

        hbox_video = QHBoxLayout()
        hbox_video.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        hbox_video.addWidget(self.videoWidget)
        hbox_video.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_controls)
        vbox.addSpacing(10)
        vbox.addLayout(hbox_video)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        self.timeline = Timeline(self)
        self.timeline.setFixedHeight(int(self.height() / 6))
        vbox.addWidget(self.timeline, stretch=1)

        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.positionChanged.connect(self.timeline.move_arrow_while_playing)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.stateChanged.connect(self.toggle_play_pause_button)


    def toggle_play_pause_button(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))




    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie", QDir.homePath(), "Videos (*.mp4 *.avi *.wmv)", options=options)
        if fileName != '':
            self.playlist.clear()
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playlist.setCurrentIndex(0)
            self.mediaPlayer.play()

            # Extract frames and display them in the timeline
            frame_rate = 2
            frames = self.generate_frames_moviepy(fileName, frame_rate)
            self.timeline.display_frames(frames, frame_rate)
            self.timeline.start_arrow_movement()


    def generate_frames_moviepy(self, video_path, frame_rate=2):
        clip = VideoFileClip(video_path)
        frames = []
        step = max(int(1/frame_rate), 1)  # Fix for the step value in the range() function
        for t in range(0, int(clip.duration), step):
            frame = clip.get_frame(t)
            qimage = QImage(frame.tobytes(), frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            frames.append(qimage)
        return frames




    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.timeline.playing = False
        else:
            self.mediaPlayer.play()
            self.timeline.playing = True


    def stop_playing(self):
        self.playing = False


    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        self.timeLabel.setText(self.timeFormat(position))

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        self.durationLabel.setText(self.timeFormat(duration))

    def timeFormat(self, duration):
        duration /= 1000
        minutes = int(duration / 60)
        seconds = int(duration % 60)
        return f"{minutes}:{seconds:02d}"

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.timeline.playing:
            return
        new_pos = event.scenePos()
        x = new_pos.x()
        x = min(max(x, 0), self.timeline.scene().width() - self.pixmap().width())
        self.setPos(QPointF(x, 0))
        self.timeline.update_video_position(x)
