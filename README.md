# PDF Editor

## Overview
This PDF Editor application allows users to perform various operations on PDF files such as merging, splitting, rearranging pages, and encryption. The application is built using Python and PyQt6 and uses the PyMuPDF library for PDF manipulation.

## Features
- **Open PDF Files**: Open and view multiple PDF files in tabs.
- **Merge PDFs**: Merge multiple PDF files into a single PDF.
- **Split PDF**: Split a PDF file into multiple files by selecting specific pages.
- **Rearrange Pages**: Rearrange the pages within a PDF file.
- **Encrypt PDF**: Encrypt a PDF file with a password and change the password or decrypt it.
- **Zoom Functionality**: Zoom in and out of PDF pages for better readability.

## Installation
To run the application, simply download the executable from the `dist` folder and run it. You do not need to install any dependencies.

## Usage
### Running the Application
1. Download the executable from the `dist` folder.
2. Double-click the executable to start the PDF Editor application.

### Application Features
1. **Open PDF Files**
   - Press `Ctrl+O` to open a PDF file.
2. **Merge PDFs**
   - Open multiple PDF files and use the "Merge PDFs" option from the Tools menu to merge them.
3. **Split PDF**
   - Open a PDF file and use the "Split PDF" option from the Tools menu to split it by selecting pages.
4. **Rearrange Pages**
   - Open a PDF file and use the "Rearrange Pages" option from the Tools menu to rearrange the pages.
5. **Encrypt PDF**
   - Open a PDF file and use the "Encrypt PDF" option from the Tools menu to set a password. You can also change the password or decrypt the PDF.
6. **Zoom Functionality**
   - Use the zoom slider to zoom in and out of the PDF pages.

## File Structure
    project-root/
    │
    ├── dialogs.py # Contains dialog classes for rearrange, merge, split, and encryption options
    ├── widgets.py # Contains custom widget classes and PDF viewer widget creation
    ├── pdf_editor.py # Main PDF Editor application logic
    ├── main.py # Entry point for the application
    ├── README.md # This readme file
    └── dist/ # Folder containing the executable file

## Logging
The application logs various events and errors to `pdf_editor.log`. You can check this file for detailed logs.

## Contributing
If you would like to contribute to this project, please fork the repository and create a pull request with your changes. Ensure that your code follows the coding standards and is well-documented.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
