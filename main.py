import sys
import logging
from PyQt6.QtWidgets import QApplication
from pdf_editor import PDFEditor

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='pdf_editor.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        editor = PDFEditor()
        editor.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.critical(f"Application failed to start: {e}")
        print(f"Application failed to start: {e}")
