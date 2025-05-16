from flask import Flask, request, render_template, send_file, redirect, url_for, session
import os
import xml.etree.ElementTree as ET

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and file.filename.endswith('.styles'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        tree = ET.parse(filepath)
        root = tree.getroot()
        attributes = {}
        for elem in root.iter():
            for attr, value in elem.attrib.items():
                attributes.setdefault(attr, set()).add(value)
        attributes = {k: sorted(list(v)) for k, v in attributes.items()}

        session['filename'] = file.filename
        session['attributes'] = attributes
        session['changes'] = []

        return render_template('searchreplace.html', filename=file.filename, attributes=attributes, changes=[])
    return 'Invalid file format. Please upload a .styles file.'

@app.route('/add_change', methods=['POST'])
def add_change():
    attribute = request.form['attribute']
    old_value = request.form['old_value']
    new_value = request.form['new_value']

    changes = session.get('changes', [])
    changes.append({'attribute': attribute, 'old_value': old_value, 'new_value': new_value})
    session['changes'] = changes

    return render_template('searchreplace.html', filename=session['filename'], attributes=session['attributes'], changes=changes)

@app.route('/replace', methods=['POST'])
def replace():
    filename = session['filename']
    changes = session['changes']

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    tree = ET.parse(filepath)
    root = tree.getroot()

    for change in changes:
        for elem in root.iter():
            if elem.get(change['attribute']) == change['old_value']:
                elem.set(change['attribute'], change['new_value'])

    ET.register_namespace('', "http://www.br-automation.com/iat2015/styles/engineering/v1")

    modified_path = os.path.join(UPLOAD_FOLDER, f'modified_{filename}')
    tree.write(modified_path, encoding='utf-8', xml_declaration=True)
    return send_file(modified_path, as_attachment=True)

@app.route('/remove_change/<int:index>', methods=['POST'])
def remove_change(index):
    changes = session.get('changes', [])
    if 0 <= index < len(changes):
        changes.pop(index)
        session['changes'] = changes
    return render_template('searchreplace.html', filename=session['filename'], attributes=session['attributes'], changes=changes)

if __name__ == '__main__':
    app.run(debug=True)
