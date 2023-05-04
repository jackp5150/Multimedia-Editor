from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QLineEdit, QMessageBox
from PyQt5.QtCore import QTimer, QUrl

import sys
from converter import (png_files_to_pdf, pdf_to_png, pdf_to_jpeg, png_to_jpeg, extract_audio_from_youtube,
                       webp_to_pdf, webp_to_png, webp_to_jpeg, json_to_xml, xml_to_json, strip_audio_from_mp4,
                       jpeg_to_pdf)
from videoEditor import VideoEditorWindow



# .\myenv\Scripts\activate

class FileConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.files = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Converter")
        self.setFixedSize(600, 300)

        self.setStyleSheet("""
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
            QLabel {
                font: 12px;
            }
            QComboBox {
                padding: 4px;
                font: 12px;
            }
        """)

        layout = QVBoxLayout()

        type_layout = QHBoxLayout()
        self.from_type_label = QLabel("Convert this type:")
        type_layout.addWidget(self.from_type_label)
        self.from_type_dropdown = QComboBox()
        self.from_type_dropdown.addItems(["PDF", "PNG", "JPEG", "MP4", "XML", "JSON", "Youtube"])
        type_layout.addWidget(self.from_type_dropdown)
        self.from_type_dropdown.currentIndexChanged.connect(self.update_to_type_dropdown)

        self.to_type_label = QLabel("to this type:")
        type_layout.addWidget(self.to_type_label)
        self.to_type_dropdown = QComboBox()
        self.to_type_dropdown.addItems(["PDF", "PNG", "JPEG", "MP3", "XML", "JSON"])
        type_layout.addWidget(self.to_type_dropdown)
        layout.addLayout(type_layout)

        self.select_button = QPushButton("Select Files")
        self.select_button.clicked.connect(self.select_files)
        layout.addWidget(self.select_button)

        self.youtube_url_input = QLineEdit()
        self.youtube_url_input.setPlaceholderText("Enter YouTube URL")
        self.youtube_url_input.hide()
        layout.addWidget(self.youtube_url_input)


        self.files_label = QLabel("")
        layout.addWidget(self.files_label)

        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert_files)

        layout.addWidget(self.convert_button)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.video_editor_button = QPushButton("Video Editor")
        self.video_editor_button.clicked.connect(self.show_video_editor)
        layout.addWidget(self.video_editor_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_video_editor(self):
        self.video_editor_window = VideoEditorWindow()
        self.video_editor_window.show()

    def select_files(self):
        selected_type = self.from_type_dropdown.currentText().lower()
        if selected_type == "youtube":
            return
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            self.files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", f"{selected_type.upper()} Files (*.{selected_type})", options=options)
        self.files_label.setText(", ".join(self.files))

    def convert_files(self):
        from_type = self.from_type_dropdown.currentText().lower()
        if from_type == "youtube":
            youtube_url = self.youtube_url_input.text()
            if not youtube_url:
                print("No YouTube URL entered.")
                return
            self.files = [youtube_url]

        if not self.files:
            print("No files selected.")
            return

        to_type = self.to_type_dropdown.currentText().lower()

        for file in self.files:
            output_file = file.rsplit(".", 1)[0] + f".{to_type}"

            if from_type == "png" and to_type == "pdf":
                png_files_to_pdf([file], output_file)
            elif from_type == "pdf" and to_type == "png":
                pdf_to_png(file, output_file)
            elif from_type == "webp" and to_type == "jpeg":
                webp_to_jpeg(file, output_file)
            elif from_type == "webp" and to_type == "png":
                webp_to_png(file, output_file)
            elif from_type == "webp" and to_type == "pdf":
                webp_to_pdf(file, output_file)
            elif from_type == "json" and to_type == "xml":
                json_to_xml(file, output_file)
            elif from_type == "xml" and to_type == "json":
                xml_to_json(file, output_file)
            elif from_type =="youtube" and to_type == "mp3":
                if not self.is_valid_youtube_url(self.files[0]):
                    QMessageBox.warning(self, "Invalid YouTube URL", "The provided YouTube URL is not valid.")
                else:
                    extract_audio_from_youtube(file, output_file)
            elif from_type == "pdf" and to_type == "jpeg":
                pdf_to_jpeg(file, output_file)
            elif from_type == "png" and to_type == "jpeg":
                png_to_jpeg(file, output_file)
            elif from_type == "mp4" and to_type == "mp3":
                strip_audio_from_mp4(file, output_file)
            elif from_type == "jpeg" and to_type == "pdf":
                jpeg_to_pdf([file], output_file)

            
            # Add more conditions for other conversion functions
            # ...
            else:
                print(f"No conversion function available for {from_type.upper()} to {to_type.upper()}")
                continue

            print(f"File saved to: {output_file}")

        self.files_label.setText("")
        self.status_label.setText("Files converted successfully.\nFile saved to: " + output_file)
        QTimer.singleShot(7000, self.clear_status_label)


    def clear_status_label(self):
        self.status_label.setText("")


    def update_to_type_dropdown(self):
        from_type = self.from_type_dropdown.currentText()
        self.to_type_dropdown.clear()

        if from_type == "JPEG":
            self.to_type_dropdown.addItems(["PDF", "PNG"])

        elif from_type == "PDF":
            self.to_type_dropdown.addItems(["JPEG", "PNG"])

        elif from_type == "PNG":
            self.to_type_dropdown.addItems(["PDF", "JPEG"])

        elif from_type in ["XML", "JSON"]:
            self.to_type_dropdown.addItems(["XML", "JSON"])

        elif from_type == "MP4":
            self.to_type_dropdown.addItems(["MP3"])

        if from_type == "Youtube":
            self.youtube_url_input.show()
            self.to_type_dropdown.addItems(["MP3"])
        else:
            self.youtube_url_input.hide()

        # ... (rest of the method)

        
    def is_valid_youtube_url(self, url):
        if 'youtube' not in url:
            return False
        
        parsed_url = QUrl(url)
        if not parsed_url.isValid():
            return False
        
        return True



def main():
    app = QApplication(sys.argv)
    converter_app = FileConverterApp()
    converter_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

