# 🎨 XML Style Attribute Editor

This is a Flask-based web application that allows users to upload `.styles` XML files, inspect their attributes, queue changes to specific attribute values (especially useful for color attributes), and download the modified file.

## 🚀 Features

- Upload `.styles` XML files.
- Automatically extract and list all unique attributes and their values.
- Interactive UI to:
  - Select an attribute.
  - Choose an old value.
  - Define a new value (with color preview support).
- Queue multiple changes.
- Apply all changes and download the modified file.

## 🛠️ Requirements

- Python 3.x
- Flask

Install dependencies:

```bash
pip install flask
```

## 🧪 Running the App

python app.py


Then open your browser and go to: http://127.0.0.1:5000

## 📄 How It Works

Upload: Start by uploading a .styles XML file via the homepage.
Inspect & Modify: The app parses the XML, extracts attributes, and lets you queue changes.
Apply Changes: Once satisfied, apply all changes and download the updated file.
## 🖼️ UI Highlights

Built with Bootstrap 5 for responsive design.
Color preview for attributes related to color.
Dynamic dropdowns and color pickers for intuitive editing.
## ⚠️ Notes

Only .styles files are accepted.
The app uses Flask sessions to track changes during a session.
## 📃 License

This project is open-source and free to use under the MIT License.