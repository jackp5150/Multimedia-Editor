import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QSlider, QStyle, QSizePolicy, QFrame, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QUrl, QDir, QSize, QRectF, QPointF
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtGui import QIcon, QPalette, QImage, QBrush, QMouseEvent, QPixmap
from PyQt5 import QtMultimediaWidgets
from PyQt5.QtGui import QPainter


class Timeline(QGraphicsView):
    def __init__(self, parent=None):
        super(Timeline, self).__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.TextAntialiasing)

    def display_frames(self, frames):
        self.scene().clear()
        for i, frame in enumerate(frames):
            pixmap = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pixmap)
            item.setPos(QPointF(i * (pixmap.width() + 2), 0))
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
        command = f"ffmpeg -i {video_path} -vf fps={frame_rate} frame_%04d.png"
        os.system(command)
        frames = []
        for file in sorted(os.listdir()):
            if file.startswith("frame_") and file.endswith(".png"):
                frame = QImage(file)
                frames.append(frame)
                os.remove(file)
        return frames

    def initUI(self):
        self.setWindowTitle("Video Editor")
        self.setFixedSize(900, 500)
        self.setWindowIcon(QIcon('icon.png'))

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QImage("background.jpg")))
        self.setPalette(palette)

        self.mediaPlayer.setVideoOutput(QtMultimediaWidgets.QVideoWidget(self))

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

        videoLayout = QVBoxLayout()
        videoWidget = QtMultimediaWidgets.QVideoWidget(self)
        videoLayout.addWidget(videoWidget)
        vbox.addLayout(videoLayout)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        self.timeline = Timeline(self)
        vbox.addWidget(self.timeline)

        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)




    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath(), "Video Files (*.mp4 *.avi *.mkv *.wmv *.mov *.flv *.webm)", options=options)
        if fileName != '':
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.mediaPlayer.setPlaylist(self.playlist)
            self.mediaPlayer.pause()  # pause the video to show the first frame
            frames = self.generate_frames(fileName)
            self.timeline.display_frames(frames)
            self.mediaPlayer.play()

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


