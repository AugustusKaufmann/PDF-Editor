import fitz  # PyMuPDF
import logging
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QLabel, QSplitter, QTableWidget,
                             QTableWidgetItem, QHeaderView, QSlider, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QImage, QPixmap, QDrag


def create_pdf_viewer_widget(pdf_path, pdf_document):
    try:
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        widget.pdf_path = pdf_path  # Store the pdf_path in the widget

        # Splitter to divide the PDF view and the controls
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Scroll area for PDF content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        pdf_pages = [pdf_document.load_page(i) for i in range(len(pdf_document))]

        pdf_labels = []
        for page in pdf_pages:
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))  # Scale down the content
            qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            label = QLabel()
            label.setPixmap(pixmap)
            pdf_labels.append(label)
            scroll_layout.addWidget(label)

            hbox = QHBoxLayout()
            hbox.addStretch(1)
            hbox.addWidget(label)
            hbox.addStretch(1)
            scroll_layout.addLayout(hbox)

        if len(pdf_pages) == 0:
            error_label = QLabel("No pages found in PDF.")
            scroll_layout.addWidget(error_label)

        splitter.addWidget(scroll_area)

        # Right side layout for metadata, zoom slider, and page navigation input
        right_layout = QVBoxLayout()

        # Metadata table
        metadata_table = QTableWidget(10, 1)
        metadata_table.setHorizontalHeaderLabels(["Value"])
        metadata_table.setVerticalHeaderLabels(["producer", "format", "encryption", "author", "modDate",
                                                "keywords", "title", "creationDate", "creator", "subject"])
        metadata = pdf_document.metadata
        fields = ["producer", "format", "encryption", "author", "modDate", "keywords", "title", "creationDate",
                  "creator", "subject"]
        for i, field in enumerate(fields):
            metadata_table.setItem(i, 0, QTableWidgetItem(metadata.get(field, '')))

        metadata_table.horizontalHeader().setStretchLastSection(True)
        metadata_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        metadata_table.setFixedHeight(300)  # Set a fixed height for the metadata table

        right_layout.addWidget(metadata_table)

        # Spacer to increase space between metadata table and other controls
        right_layout.addSpacing(20)

        # Zoom slider
        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setMinimum(1)
        zoom_slider.setMaximum(5)
        zoom_slider.setValue(1)
        zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        zoom_slider.setTickInterval(1)
        zoom_slider.setFixedWidth(200)  # Set a fixed width for the zoom slider
        zoom_slider.setToolTip("Zoom in and out of the PDF")  # Add tooltip
        right_layout.addWidget(zoom_slider)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Set the initial sizes of the splitter to achieve the 70%/30% ratio
        splitter.setSizes([800, 400])

        layout.addWidget(splitter)

        def zoom_pdf():
            try:
                scale_factor = zoom_slider.value()
                for i, page in enumerate(pdf_pages):
                    pix = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))
                    qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimage)
                    pdf_labels[i].setPixmap(pixmap)
            except Exception as e:
                logging.error(f"Failed to zoom PDF: {e}")
                QMessageBox.critical(widget, 'Error', f'Failed to zoom PDF: {e}')

        zoom_slider.valueChanged.connect(zoom_pdf)

        return widget
    except Exception as e:
        logging.error(f"Failed to create PDF viewer widget: {e}")
        QMessageBox.critical(widget, 'Error', f'Failed to create PDF viewer widget: {e}')

class DraggableLabel(QLabel):
    def __init__(self, parent=None, dialog=None):
        super().__init__(parent)
        self.dialog = dialog
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(str(self.objectName()))
                drag.setMimeData(mime_data)
                drag.exec(Qt.DropAction.MoveAction)
        except Exception as e:
            logging.error(f"Failed in mousePressEvent: {e}")
            QMessageBox.critical(self, 'Error', f'Failed in mousePressEvent: {e}')

    def dragEnterEvent(self, event):
        try:
            if event.mimeData().hasText():
                event.acceptProposedAction()
        except Exception as e:
            logging.error(f"Failed in dragEnterEvent: {e}")
            QMessageBox.critical(self, 'Error', f'Failed in dragEnterEvent: {e}')

    def dragMoveEvent(self, event):
        try:
            if event.mimeData().hasText():
                event.acceptProposedAction()
        except Exception as e:
            logging.error(f"Failed in dragMoveEvent: {e}")
            QMessageBox.critical(self, 'Error', f'Failed in dragMoveEvent: {e}')

    def dropEvent(self, event):
        try:
            if event.mimeData().hasText():
                source_widget = event.source()
                if source_widget:
                    source_index = int(source_widget.objectName())
                    target_index = int(self.objectName())
                    event.setDropAction(Qt.DropAction.MoveAction)
                    event.accept()
                    self.dialog.swapWidgets(source_index, target_index)
        except Exception as e:
            logging.error(f"Failed in dropEvent: {e}")
            QMessageBox.critical(self, 'Error', f'Failed in dropEvent: {e}')
