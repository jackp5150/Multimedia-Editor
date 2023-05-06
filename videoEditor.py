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

from timeline import Timeline
from bluearrow import BlueArrow



import random

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
        self.setFixedSize(1200, 900)
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

        # Styling square buttons
        square_buttons = [QPushButton(self) for _ in range(5)]
        for button in square_buttons:
            button.setFixedSize(40, 40)  # Increase the size of the buttons
            button.setStyleSheet("""
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
        square_buttons_layout = QHBoxLayout()
        square_buttons_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        for button in square_buttons:
            button.setFixedSize(30, 30)
            button.setStyleSheet(
                'QPushButton {'
                '    background-color: #3498db;'
                '    color: white;'
                '    font: bold 14px;'
                '    padding: 6px;'
                '    border: none;'
                '}'
                'QPushButton:hover {'
                '    background-color: #2980b9;'
                '}'
            )


        # Instantiating plus button and importing it
        plus_button = QPushButton(self)
        plus_button.setFixedSize(40, 40)
        plus_button.setIcon(QIcon("plus_icon.png"))
        plus_button.setIconSize(QSize(24, 24))
        plus_button.setStyleSheet(
            'QPushButton {'
            '    background-color: #3498db;'
            '    color: white;'
            '    font: bold 14px;'
            '    padding: 6px;'
            '    border-radius: 20px;'  # Add border-radius for a circular shape
            '}'
            'QPushButton:hover {'
            '    background-color: #2980b9;'
            '}'
        )

        # Instantiating plus button
        hbox_plus_button = QHBoxLayout()
        hbox_plus_button.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        hbox_plus_button.addWidget(plus_button)
        hbox_plus_button.insertSpacerItem(0, QSpacerItem(60, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

        # Instantiating window layout organizer
        vbox = QVBoxLayout()
        vbox.addLayout(hbox_controls)
        vbox.addSpacing(30)

        # Instantiating square buttons
        hbox_square_buttons = QHBoxLayout()
        for button in square_buttons:
            hbox_square_buttons.addWidget(button)
        hbox_square_buttons.setSpacing(7) 
        vbox.addLayout(hbox_square_buttons)
        # vbox.addSpacing(10)

        # # Instantiating timeline
        # self.timeline = Timeline(self)
        # self.timeline.setFixedHeight(int(self.height() / 6))
        # vbox.addWidget(self.timeline, stretch=1)  # Add the QHBoxLayout for the plus button to the QVBoxLayout

        # Creating layout for the media itself
        self.videoWidget = QtMultimediaWidgets.QVideoWidget(self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.videoWidget.setFixedSize(1000, 600)  # Increase the size of the videoWidget

        # vbox.addSpacing(10)
        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Add expanding spacer above hbox_video
        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Add expanding spacer below hbox_video
        hbox_video = QHBoxLayout()
        hbox_video.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))  # Add expanding spacer to the left of videoWidget
        hbox_video.addWidget(self.videoWidget)
        hbox_video.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))  # Add expanding spacer to the right of videoWidget

        vbox.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Add expanding spacer above hbox_video
        vbox.addLayout(hbox_video)
        vbox.addStretch(1)



        # Adding the plus button
        vbox.addLayout(hbox_plus_button)
        vbox.addSpacing(10)

        # Adding the timeline
        self.timeline = Timeline(self)
        self.timeline.setFixedHeight(int(self.height() / 6))
        vbox.addWidget(self.timeline, stretch=1)

        # Connecting everything
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.positionChanged.connect(self.timeline.move_arrow_while_playing)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.stateChanged.connect(self.toggle_play_pause_button)

        # Adding more stuff
        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)


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
