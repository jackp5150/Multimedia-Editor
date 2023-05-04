import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSlider, QStyle, QSizePolicy, QFrame, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QUrl, QDir, QSize, QRectF, QPointF
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtGui import QIcon, QPalette, QImage, QBrush, QMouseEvent, QPixmap
from PyQt5 import QtMultimediaWidgets
from PyQt5.QtGui import QPainter
from moviepy.editor import VideoFileClip
import random



class Timeline(QGraphicsView):
    def __init__(self, parent=None):
        super(Timeline, self).__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.TextAntialiasing)
        
        brush = QBrush(Qt.gray)
        self.setBackgroundBrush(brush)

    def display_frames(self, frames):
        self.scene().clear()
        scale_factor = 0.1  # Adjust this value to change the size of the frames in the timeline
        spacing = .1  # Adjust this value to change the spacing between the frames
        for i, frame in enumerate(frames):
            pixmap = QPixmap.fromImage(frame).scaledToWidth(int(frame.width() * scale_factor))
            item = QGraphicsPixmapItem(pixmap)
            item.setPos(QPointF(i * (pixmap.width() + spacing), 0))
            self.scene().addItem(item)
        self.setSceneRect(QRectF(self.scene().itemsBoundingRect()))




class VideoEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.playlist = QMediaPlaylist()
        self.mediaPlayer.setPlaylist(self.playlist)
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
        self.setFixedSize(1200, 800)  # Increased the window size
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

        self.positionSlider = QSlider(Qt.Horizontal, self)
        self.positionSlider.setFixedWidth(300)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.timeLabel = QLabel(self)
        self.timeLabel.setFixedWidth(60)
        self.timeLabel.setStyleSheet("color: white")

        self.durationLabel = QLabel(self)
        self.durationLabel.setFixedWidth(60)
        self.durationLabel.setStyleSheet("color: white")

        hbox1 = QHBoxLayout()
        hbox1.addWidget(openButton)
        hbox1.addSpacing(10)
        hbox1.addWidget(playButton)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.positionSlider)
        hbox2.addWidget(self.timeLabel)
        hbox2.addWidget(self.durationLabel)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.videoWidget = QtMultimediaWidgets.QVideoWidget(self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.videoWidget.setFixedSize(800, 450)  # Set a fixed size for the video widget
        vbox.addWidget(self.videoWidget)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        self.timeline = Timeline(self)
        vbox.addWidget(self.timeline, stretch=1)

        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)







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
            frames = self.generate_frames_moviepy(fileName)
            self.timeline.display_frames(frames)

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
        else:
            self.mediaPlayer.play()

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

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()


