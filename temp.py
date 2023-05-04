# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QComboBox, QHBoxLayout
# from PyQt5.QtCore import QTimer
# import sys
# from converter import png_files_to_pdf

# class FileConverterApp(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle("File Converter")
#         self.setFixedSize(600, 300)

#         self.setStyleSheet("""
#             QPushButton {
#                 background-color: #3498db;
#                 color: white;
#                 font: bold 14px;
#                 padding: 6px;
#                 border: none;
#             }
#             QPushButton:hover {
#                 background-color: #2980b9;
#             }
#             QLabel {
#                 font: 12px;
#             }
#             QComboBox {
#                 padding: 4px;
#                 font: 12px;
#             }
#         """)

#         layout = QVBoxLayout()

#         type_layout = QHBoxLayout()
#         self.from_type_label = QLabel("Convert this type:")
#         type_layout.addWidget(self.from_type_label)
#         self.from_type_dropdown = QComboBox()
#         self.from_type_dropdown.addItems(["PDF", "PNG", "JPEG", "WEBP", "MP3", "MP4", "XML", "JSON", "DOCX", "SVG", "PPTX"])
#         type_layout.addWidget(self.from_type_dropdown)
#         self.from_type_dropdown.currentIndexChanged.connect(self.update_to_type_dropdown)

#         self.to_type_label = QLabel("to this type:")
#         type_layout.addWidget(self.to_type_label)
#         self.to_type_dropdown = QComboBox()
#         self.to_type_dropdown.addItems(["PDF", "PNG", "JPEG", "WEBP", "MP3", "MP4", "XML", "JSON", "DOCX", "SVG", "PPTX"])
#         type_layout.addWidget(self.to_type_dropdown)
#         layout.addLayout(type_layout)

#         self.select_button = QPushButton("Select Files")
#         self.select_button.clicked.connect(self.select_files)
#         layout.addWidget(self.select_button)

#         self.files_label = QLabel("")
#         layout.addWidget(self.files_label)

#         self.convert_button = QPushButton("Convert")
#         self.convert_button.clicked.connect(self.convert_to_pdf)
#         layout.addWidget(self.convert_button)

#         self.confirmation_label = QLabel("")
#         layout.addWidget(self.confirmation_label)

#         central_widget = QWidget()
#         central_widget.setLayout(layout)
#         self.setCentralWidget(central_widget)

#     def select_files(self):
#         selected_type = self.from_type_dropdown.currentText().lower()
#         options = QFileDialog.Options()
#         options |= QFileDialog.ReadOnly
#         self.files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", f"{selected_type.upper()} Files (*.{selected_type})", options=options)
#         self.files_label.setText(", ".join(self.files))

#     def convert_to_pdf(self):
#         if not self.files:
#             print("No files selected.")
#             return

#         for file in self.files:
#             output_pdf = file.rsplit(".", 1)[0] + ".pdf"
#             png_files_to_pdf([file], output_pdf)
#             print(f"PDF saved to: {output_pdf}")

#         self.files_label.setText("")
#         self.confirmation_label.setText("Files converted successfully.")
#         QTimer.singleShot(2000, self.clear_confirmation_label)

#     def clear_confirmation_label(self):
#         self.confirmation_label.setText("")

#     def update_to_type_dropdown(self):
#         from_type = self.from_type_dropdown.currentText()
#         self.to_type_dropdown.clear()

#         if from_type in ["JPEG", "PDF", "PNG", "SVG", "DOCX"]:
#             self.to_type_dropdown.addItems(["PDF", "PNG", "JPEG", "WEBP", "MP3", "MP4", "XML", "JSON", "DOCX", "SVG", "PPTX"])
#         elif from_type in ["XML", "JSON"]:
#             self.to_type_dropdown.addItems(["XML", "JSON"])
#         elif from_type == "MP4":
#             self.to_type_dropdown.addItems(["MP3"])
#         elif from_type == "PPTX":
#             self.to_type_dropdown.addItems(["PDF"])

# def main():
#     app = QApplication(sys.argv)
#     converter_app = FileConverterApp()
#     converter_app.show()
#     sys.exit(app.exec_())

# if __name__ == "main":
#     main()
