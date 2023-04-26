# Handwritten Text Annotation Tool

This is an Electron-based tool for annotating handwritten text in images that have been cropped from a form. The tool allows annotators to input what is written in the image and record if the image contains English or Nepali handwritten text. In case of Nepali handwritten text, the tool provides a way to write in Nepali using a text romanizer with a list of suggestions. Users can also click on one of the suggestions to replace the English word with the selected suggested word. The tool allows annotators to delete and crop images and store annotated data in CSV format or a database.

## Shortcuts

The tool supports the following keyboard shortcuts:

- Ctrl+Shift+Right Arrow: Go to the next image
- Ctrl+Shift+Left Arrow: Go to the previous image
- Ctrl+s: Save the current annotation
- Ctrl+o: Select a folder containing the images to annotate
- Ctrl+t: Toggle Nepali input mode

These shortcuts can be modified in the code to suit individual preferences.

## Installation

To install the tool, clone this repository and run the following commands:

```
yarn
yarn start
```

This will install the necessary dependencies and start the application.

## Usage

To use the tool, follow these steps:

1. Click on the "Select Folder" button to choose the folder containing the images to annotate.
2. Use the keyboard shortcuts to navigate through the images and annotate them.
3. Click on the "Save" button to save the annotations.
4. The annotated data will be stored in CSV format or a database.
