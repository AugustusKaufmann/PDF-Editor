import os
import fitz  # PyMuPDF
import logging
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QScrollArea, QWidget, QGridLayout, QLabel, QFrame, QDialogButtonBox, QRadioButton, QButtonGroup, QMessageBox)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from functools import partial

from widgets import DraggableLabel


class RearrangePagesDialog(QDialog):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.initUI()

    def initUI(self):
        try:
            self.setWindowTitle('Rearrange Pages')
            self.setGeometry(200, 200, 800, 600)

            layout = QVBoxLayout(self)
            self.setLayout(layout)

            self.grid_layout = QGridLayout()
            self.pages_widgets = []

            pdf_document = fitz.open(self.pdf_path)
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))  # Scale down content for better visibility
                qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)

                page_label = DraggableLabel(dialog=self)
                page_label.setPixmap(pixmap)
                page_label.setObjectName(str(page_num))
                page_label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
                page_label.setLineWidth(2)
                page_label.setFixedSize(200, 260)  # Increased size for better visibility
                page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Add the page label to a vertical layout with a label showing the page number
                page_layout = QVBoxLayout()
                page_layout.addWidget(page_label)
                page_number_label = QLabel(f"Page {page_num + 1}")
                page_number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                page_layout.addWidget(page_number_label)

                page_widget = QWidget()
                page_widget.setLayout(page_layout)
                page_widget.setObjectName(str(page_num))

                self.pages_widgets.append(page_widget)
                self.grid_layout.addWidget(page_widget, page_num // 4, page_num % 4)

            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_content = QWidget()
            scroll_content.setLayout(self.grid_layout)
            scroll_area.setWidget(scroll_content)

            layout.addWidget(scroll_area)

            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            button_box.accepted.connect(self.accept)
            button_box.rejected.connect(self.reject)
            layout.addWidget(button_box)
        except Exception as e:
            logging.error(f"Failed to initialize UI: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to initialize UI: {e}')

    def get_new_order(self):
        try:
            return [int(self.grid_layout.itemAt(i).widget().objectName()) for i in range(self.grid_layout.count())]
        except Exception as e:
            logging.error(f"Failed to get new order: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to get new order: {e}')

    def swapWidgets(self, source_index, target_index):
        try:
            if source_index != target_index:
                widget = self.pages_widgets.pop(source_index)
                self.pages_widgets.insert(target_index, widget)

                # Clear the grid layout
                for i in reversed(range(self.grid_layout.count())):
                    widget_to_remove = self.grid_layout.itemAt(i).widget()
                    self.grid_layout.removeWidget(widget_to_remove)
                    widget_to_remove.setParent(None)

                # Rebuild the grid layout with the new order
                for index, widget in enumerate(self.pages_widgets):
                    self.grid_layout.addWidget(widget, index // 4, index % 4)
        except Exception as e:
            logging.error(f"Failed to swap widgets: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to swap widgets: {e}')

class EncryptionOptionsDialog(QDialog):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.change_password_selected = False
        self.decrypt_selected = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Encryption Options')
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout(self)

        self.change_password_button = QRadioButton("Change Password")
        self.decrypt_button = QRadioButton("Decrypt PDF")

        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.change_password_button)
        self.button_group.addButton(self.decrypt_button)

        layout.addWidget(self.change_password_button)
        layout.addWidget(self.decrypt_button)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        if self.change_password_button.isChecked():
            self.change_password_selected = True
        elif self.decrypt_button.isChecked():
            self.decrypt_selected = True
        super().accept()

class MergePDFsDialog(QDialog):
    def __init__(self, open_pdfs, parent=None):
        super().__init__(parent)
        self.open_pdfs = open_pdfs
        self.selected_pdfs = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Merge PDFs')
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.grid_layout = QGridLayout()
        self.preview_labels = []

        for i, pdf_path in enumerate(self.open_pdfs):
            pdf_document = fitz.open(pdf_path)
            page = pdf_document.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))  # Scale down content for better visibility
            qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            preview_label = QLabel()
            preview_label.setPixmap(pixmap)
            preview_label.setObjectName(pdf_path)
            preview_label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
            preview_label.setLineWidth(2)
            preview_label.setFixedSize(200, 260)
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.mousePressEvent = partial(self.toggleSelection, pdf_path=pdf_path)

            page_layout = QVBoxLayout()
            page_layout.addWidget(preview_label)
            page_number_label = QLabel(f"{i + 1}")
            page_number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_layout.addWidget(page_number_label)

            page_widget = QWidget()
            page_widget.setLayout(page_layout)
            page_widget.setObjectName(str(i))

            self.preview_labels.append(page_widget)
            self.grid_layout.addWidget(page_widget, i // 4, i % 4)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(self.grid_layout)
        scroll_area.setWidget(scroll_content)

        layout.addWidget(scroll_area)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def toggleSelection(self, event, pdf_path):
        if pdf_path in self.selected_pdfs:
            self.selected_pdfs.remove(pdf_path)
        else:
            self.selected_pdfs.append(pdf_path)
        self.updateSelections()

    def updateSelections(self):
        for i, pdf_path in enumerate(self.open_pdfs):
            for label in self.preview_labels:
                if label.objectName() == str(i):
                    preview_label = label.findChild(QLabel)
                    if pdf_path in self.selected_pdfs:
                        order = self.selected_pdfs.index(pdf_path) + 1
                        preview_label.setText(f"{order}")
                    else:
                        preview_label.setText("")

    def get_selected_pdfs(self):
        return self.selected_pdfs

class SplitPDFDialog(QDialog):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.selected_pages = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Split PDF')
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.grid_layout = QGridLayout()
        self.page_labels = []

        pdf_document = fitz.open(self.pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))  # Scale down content for better visibility
            qimage = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)

            page_label = QLabel()
            page_label.setPixmap(pixmap)
            page_label.setObjectName(str(page_num))
            page_label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
            page_label.setLineWidth(2)
            page_label.setFixedSize(200, 260)
            page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_label.mousePressEvent = partial(self.toggleSelection, page_num=page_num)

            page_layout = QVBoxLayout()
            page_layout.addWidget(page_label)
            page_number_label = QLabel(f"Page {page_num + 1}")
            page_number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_layout.addWidget(page_number_label)

            page_widget = QWidget()
            page_widget.setLayout(page_layout)
            page_widget.setObjectName(str(page_num))

            self.page_labels.append(page_widget)
            self.grid_layout.addWidget(page_widget, page_num // 4, page_num % 4)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(self.grid_layout)
        scroll_area.setWidget(scroll_content)

        layout.addWidget(scroll_area)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def toggleSelection(self, event, page_num):
        if page_num in self.selected_pages:
            self.selected_pages.remove(page_num)
        else:
            self.selected_pages.append(page_num)
        self.updateSelections()

    def updateSelections(self):
        for i, page_widget in enumerate(self.page_labels):
            page_label = page_widget.findChild(QLabel)
            if int(page_widget.objectName()) in self.selected_pages:
                order = self.selected_pages.index(int(page_widget.objectName())) + 1
                page_label.setText(f"{order}")
            else:
                page_label.setText("")

    def get_selected_pages(self):
        return self.selected_pages
