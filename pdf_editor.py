import os
import logging
from pymupdf import pymupdf
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QFileDialog, QMessageBox, QInputDialog, QLineEdit,
                             QDialog, QLabel, QVBoxLayout, QWidget, QPushButton)
from PyQt6.QtGui import (QAction)
from PyQt6.QtCore import Qt

from dialogs import (RearrangePagesDialog, EncryptionOptionsDialog, MergePDFsDialog, SplitPDFDialog)
from widgets import create_pdf_viewer_widget

class PDFEditor(QMainWindow):
    count = 0
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Editor')
        self.setGeometry(100, 100, 1200, 800)

        # Create a central widget for the welcome screen
        self.central_widget = self.create_central_widget()
        self.setCentralWidget(self.central_widget)

        # Create tab widget for opened PDFs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.tabs.setVisible(False)  # Hide the tabs initially

        # Create actions for the menu bar and toolbar
        self.create_actions()
        self.create_menu_bar()

    def create_central_widget(self):
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)

        welcome_label = QLabel("Ctrl + O to get started")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = welcome_label.font()
        font.setPointSize(13)
        font.setBold(True)
        welcome_label.setFont(font)

        #open_button = QPushButton("Open")
        #open_button.setFont(font)
        #open_button.clicked.connect(self.openFile)
        #open_button.setFixedWidth(200)

        central_layout.addWidget(welcome_label)
        #central_layout.addSpacing(0)
        #central_layout.addWidget(open_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return central_widget

    def create_actions(self):
        self.openFileAction = QAction('Open', self)
        self.openFileAction.setShortcut('Ctrl+O')
        self.openFileAction.triggered.connect(self.openFile)

        self.saveAsFileAction = QAction('Save As', self)
        self.saveAsFileAction.triggered.connect(self.saveAsFile)

        self.mergeFilesAction = QAction('Merge PDFs', self)
        self.mergeFilesAction.triggered.connect(self.mergeFiles)

        self.splitFileAction = QAction('Split PDF', self)
        self.splitFileAction.triggered.connect(self.splitFile)

        self.encryptFileAction = QAction('Encrypt PDF', self)
        self.encryptFileAction.triggered.connect(self.encryptFile)

        self.rearrangeFileAction = QAction('Rearrange Pages', self)
        self.rearrangeFileAction.triggered.connect(self.rearrangeFile)

    def create_menu_bar(self):
        menubar = self.menuBar()
        if len(menubar.children()) < 2:
            fileMenu = menubar.addMenu('File')
            fileMenu.addAction(self.openFileAction)
            fileMenu.addAction(self.saveAsFileAction)

            editMenu = menubar.addMenu('Tools')
            editMenu.addAction(self.mergeFilesAction)
            editMenu.addAction(self.splitFileAction)
            editMenu.addAction(self.encryptFileAction)
            editMenu.addAction(self.rearrangeFileAction)

        # Set menubar stylesheet for hover effect
            menubar.setStyleSheet("""
                QMenuBar::item {
                    background: transparent;
                }
                QMenuBar::item:selected {
                    background: #1e81b0;
                }
                QMenu::item:selected {
                    background: #1e81b0;
                }
            """)

    def openFile(self):
        try:
            fileName, _ = QFileDialog.getOpenFileName(self,
                                                      'Open File',
                                                      os.path.expanduser('~'),
                                                      'PDF Files (*.pdf);;All Files (*)',
                                                      )
            if fileName:
                if not self.tabs.isVisible():
                    self.setCentralWidget(self.tabs)
                    self.tabs.setVisible(True)

                pdf_document = pymupdf.open(fileName)
                if pdf_document.is_encrypted:
                    password, ok = QInputDialog.getText(self, 'Password Required', 'Enter password:',
                                                        QLineEdit.EchoMode.Password)
                    if ok and not pdf_document.authenticate(password):
                        QMessageBox.critical(self, 'Error', 'Incorrect password.')
                        return

                pdfWidget = create_pdf_viewer_widget(fileName, pdf_document)
                pdfWidget.pdf_path = fileName  # Store the pdf_path for later use
                self.tabs.addTab(pdfWidget, fileName.split('/')[-1])
                self.tabs.setCurrentWidget(pdfWidget)
        except Exception as e:
            logging.error(f"Failed to open PDF file: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to open PDF file: {e}')

    def closeTab(self, index):
        try:
            #widget = self.tabs.widget(index)

            #widget.deleteLater()
            if self.tabs.count() == 1:
                self.initUI()
                #self.tabs.widget(index).deleteLater()
            else:
                self.tabs.removeTab(index)
        except Exception as e:
            logging.error(f"Failed to close tab: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to close tab: {e}')

    def saveAsFile(self):
        try:
            current_widget = self.tabs.currentWidget()
            if current_widget:
                pdf_path = current_widget.pdf_path
                new_pdf_path, _ = QFileDialog.getSaveFileName(self, 'Save As', pdf_path, 'PDF Files (*.pdf)')
                if new_pdf_path:
                    pdf_document = pymupdf.open(pdf_path)
                    pdf_document.save(new_pdf_path)
                    pdf_document.close()
                    QMessageBox.information(self, 'Success', f'PDF has been saved as {new_pdf_path}.')
        except Exception as e:
            logging.error(f"Failed to save file as: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to save file as: {e}')

    def mergeFiles(self):
        try:
            if self.tabs.count() < 2:
                QMessageBox.warning(self, 'Merge PDFs', 'You need to open at least two PDFs to merge.')
                return

            open_pdfs = [self.tabs.widget(i).pdf_path for i in range(self.tabs.count())]
            dialog = MergePDFsDialog(open_pdfs, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_pdfs = dialog.get_selected_pdfs()
                if len(selected_pdfs) < 2:
                    QMessageBox.warning(self, 'Merge PDFs', 'You need to select at least two PDFs to merge.')
                    return
                self.apply_merge(selected_pdfs)
        except Exception as e:
            logging.error(f"Failed to merge files: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to merge files: {e}')

    def apply_merge(self, pdf_paths):
        try:
            merged_pdf = pymupdf.open()
            for pdf_path in pdf_paths:
                pdf_document = pymupdf.open(pdf_path)
                merged_pdf.insert_pdf(pdf_document)
            merged_pdf_path = os.path.join(os.path.dirname(pdf_paths[0]), "merged.pdf")
            merged_pdf.save(merged_pdf_path)
            merged_pdf.close()
            self.open_new_created(merged_pdf_path)
            QMessageBox.information(self, 'Success', f'PDFs have been merged and saved as {merged_pdf_path}.')
        except Exception as e:
            logging.error(f"Failed to apply merge: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to apply merge: {e}')

    def splitFile(self):
        try:
            current_widget = self.tabs.currentWidget()
            if current_widget:
                pdf_path = current_widget.pdf_path
                dialog = SplitPDFDialog(pdf_path, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_pages = dialog.get_selected_pages()
                    if not selected_pages:
                        QMessageBox.warning(self, 'Split PDF', 'You need to select at least one page to split.')
                        return
                    self.apply_split(pdf_path, selected_pages)
        except Exception as e:
            logging.error(f"Failed to split file: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to split file: {e}')

    def apply_split(self, pdf_path, selected_pages):
        try:
            pdf_document = pymupdf.open(pdf_path)
            split_pdf = pymupdf.open()
            for page_num in selected_pages:
                split_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            split_pdf_path = os.path.join(os.path.dirname(pdf_path), "split.pdf")
            split_pdf.save(split_pdf_path)
            split_pdf.close()
            self.open_new_created(split_pdf_path)
            QMessageBox.information(self, 'Success', f'PDF has been split and saved as {split_pdf_path}.')
        except Exception as e:
            logging.error(f"Failed to apply split: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to apply split: {e}')

    def encryptFile(self):
        try:
            current_widget = self.tabs.currentWidget()
            if current_widget:
                pdf_path = current_widget.pdf_path
                pdf_document = pymupdf.open(pdf_path)
                if pdf_document.is_encrypted:
                    QMessageBox.information(self, 'Encrypt PDF', 'The PDF is already encrypted.')
                    self.showEncryptionOptions(pdf_path)
                else:
                    self.setPassword(pdf_path)
        except Exception as e:
            logging.error(f"Failed to encrypt file: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to encrypt file: {e}')

    def setPassword(self, pdf_path):
        try:
            password, ok = QInputDialog.getText(self, 'Set Password', 'Enter password:', QLineEdit.EchoMode.Password)
            if ok and password:
                pdf_document = pymupdf.open(pdf_path)
                new_pdf_path = os.path.splitext(pdf_path)[0] + "_encrypted.pdf"
                pdf_document.save(new_pdf_path, encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw=password,
                                  user_pw=password)
                pdf_document.close()
                self.open_new_created(new_pdf_path)
                QMessageBox.information(self, 'Success',
                                        f'PDF has been encrypted successfully and saved as {new_pdf_path}.')
        except Exception as e:
            logging.error(f"Failed to set password: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to set password: {e}')

    def changePassword(self, pdf_path):
        try:
            old_password, ok = QInputDialog.getText(self, 'Change Password', 'Enter current password:',
                                                    QLineEdit.EchoMode.Password)
            if ok and old_password:
                pdf_document = pymupdf.open(pdf_path)
                if not pdf_document.authenticate(old_password):
                    QMessageBox.critical(self, 'Error', 'Current password is incorrect.')
                    return

                new_password, ok = QInputDialog.getText(self, 'Set New Password', 'Enter new password:',
                                                        QLineEdit.EchoMode.Password)
                if ok and new_password:
                    new_pdf_path = os.path.splitext(pdf_path)[0] + "_newpassword.pdf"
                    pdf_document.save(new_pdf_path, encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw=new_password,
                                      user_pw=new_password)
                    pdf_document.close()
                    self.open_new_created(new_pdf_path)
                    QMessageBox.information(self, 'Success',
                                            f'Password has been changed successfully and saved as {new_pdf_path}.')
        except Exception as e:
            logging.error(f"Failed to change password: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to change password: {e}')

    def decryptPDF(self, pdf_path):
        try:
            password, ok = QInputDialog.getText(self, 'Decrypt PDF', 'Enter current password:',
                                                QLineEdit.EchoMode.Password)
            if ok and password:
                pdf_document = pymupdf.open(pdf_path)
                if not pdf_document.authenticate(password):
                    QMessageBox.critical(self, 'Error', 'Current password is incorrect.')
                    return
                new_pdf_path = os.path.splitext(pdf_path)[0] + "_decrypted.pdf"
                pdf_document.save(new_pdf_path, encryption=pymupdf.PDF_ENCRYPT_NONE)
                pdf_document.close()
                self.open_new_created(new_pdf_path)
                QMessageBox.information(self, 'Success',
                                        f'PDF has been decrypted successfully and saved as {new_pdf_path}.')
        except Exception as e:
            logging.error(f"Failed to decrypt PDF: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to decrypt PDF: {e}')

    def showEncryptionOptions(self, pdf_path):
        try:
            dialog = EncryptionOptionsDialog(pdf_path, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if dialog.change_password_selected:
                    self.changePassword(pdf_path)
                elif dialog.decrypt_selected:
                    self.decryptPDF(pdf_path)
        except Exception as e:
            logging.error(f"Failed to show encryption options: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to show encryption options: {e}')

    def rearrangeFile(self):
        try:
            current_widget = self.tabs.currentWidget()
            if current_widget:
                dialog = RearrangePagesDialog(current_widget.pdf_path, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_order = dialog.get_new_order()

                    # Apply the new order and save to a new file
                    self.apply_new_order(current_widget.pdf_path, new_order)

                    QMessageBox.information(self, 'Success', 'PDF pages rearranged and saved successfully.')
        except Exception as e:
            logging.error(f"Failed to rearrange file: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to rearrange file: {e}')

    def apply_new_order(self, pdf_path, new_order):
        try:
            # Open the original PDF document
            original_pdf = pymupdf.open(pdf_path)

            # Create a new PDF document
            new_pdf = pymupdf.open()

            # Insert pages from the original PDF to the new PDF in the new order
            for i in new_order:
                new_pdf.insert_pdf(original_pdf, from_page=i, to_page=i)

            # Save the new PDF to the same directory with a new name
            new_pdf_path = os.path.splitext(pdf_path)[0] + "_reordered.pdf"
            new_pdf.save(new_pdf_path, garbage=4)
            new_pdf.close()

            # Close the original PDF document
            original_pdf.close()

            self.open_new_created(new_pdf_path)

            logging.info(f"Reordered PDF saved as: {new_pdf_path}")

        except Exception as e:
            logging.error(f"Failed to apply new order: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to apply new order: {e}')

    def open_new_created(self, fileName):
                if fileName:
                    if not self.tabs.isVisible():
                        self.setCentralWidget(self.tabs)
                        self.tabs.setVisible(True)

                    pdf_document = pymupdf.open(fileName)
                    if pdf_document.is_encrypted:
                        password, ok = QInputDialog.getText(self, 'Password Required', 'Enter password:',
                                                            QLineEdit.EchoMode.Password)
                        if ok and not pdf_document.authenticate(password):
                            QMessageBox.critical(self, 'Error', 'Incorrect password.')
                            return

                    pdfWidget = create_pdf_viewer_widget(fileName, pdf_document)
                    pdfWidget.pdf_path = fileName  # Store the pdf_path for later use
                    self.tabs.addTab(pdfWidget, fileName.split('/')[-1])
                    self.tabs.setCurrentWidget(pdfWidget)

