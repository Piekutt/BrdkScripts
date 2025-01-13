import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

BALLOT_BOX = "\u2610"
BALLOT_BOX_WITH_X = "\u2612"

def peek_folder(folder):
    pattern = r"[a-zA-Z0-9_]*\.(page|dialog)$"
    try:
        no_page = True
        for path, subdirs, files in os.walk(folder):
            if len(subdirs) > 0:
                return True
            for name in files:
                if re.fullmatch(pattern, name):
                    no_page = False
        return no_page
    except PermissionError as e:
        print(f"PermissionError: {e}")
        return True

def sort_folders(folder):
    pattern = r"[a-zA-Z0-9_]*\.pkg$"
    try:
        for path, subdirs, files in os.walk(folder):
            for name in files:
                if re.fullmatch(pattern, name):
                    with open(os.path.join(path, name), 'r+', encoding='utf-8') as f:
                        lines = f.readlines()
                        list_dict = {}
                        start_index, end_index = None, None

                        for i, line in enumerate(lines):
                            if "<Objects>" in line:
                                start_index = i
                            if "<Object Type=" in line:
                                obj_type = re.search(r'(?<=<Object\sType=\")\w+', line).group(0)
                                if 'Reference="true' in line:
                                    obj_name = re.search(r'\w+(?=\\Package\.pkg)|\w+(?=\\<\/Object>)|\w+\.\w+(?=<\/Object)', line).group(0)
                                else:
                                    obj_name = re.search(r'(?<=\>)(.+)(?=<)', line).group(0)
                                list_dict[obj_name] = [obj_type, line]
                            if "</Objects>" in line:
                                end_index = i
                                sorted_list = dict(sorted(list_dict.items(), key=lambda s: s[0].lower()))

                                f.seek(0)
                                f.truncate()
                                f.writelines(lines[:start_index + 1])
                                for key in sorted_list.keys():
                                    if sorted_list[key][0] == "Folder":
                                        f.write(sorted_list[key][1])
                                for key in sorted_list.keys():
                                    if sorted_list[key][0] == "Package":
                                        f.write(sorted_list[key][1])
                                for key in sorted_list.keys():
                                    if sorted_list[key][0] not in {"Package", "Folder"}:
                                        f.write(sorted_list[key][1])
                                f.writelines(lines[end_index:])
        print("Sorting completed successfully.")
    except Exception as e:
        print(f"Error during folder sorting: {e}")

class TtkCheckList(ttk.Treeview):
    def __init__(self, master=None, width=480, separator='.', unchecked=BALLOT_BOX, checked=BALLOT_BOX_WITH_X, **kwargs):
        ttk.Treeview.__init__(self, master, **kwargs)
        self._separator = separator
        self._unchecked = unchecked
        self._checked = checked
        self.column('#0', width=width, stretch=tk.YES)
        self.bind("<Button-1>", self._item_click, True)

    def _item_click(self, event):
        x, y = event.x, event.y
        element = self.identify("element", x, y)
        if element == "text":
            iid = self.identify_row(y)
            self.toggle(iid)

    def toggle(self, iid):
        text = self.item(iid, "text")
        checked = text[-1] == self._checked
        status = self._unchecked if checked else self._checked
        self.item(iid, text=text[:-1] + status)

class FolderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Checkbox App")
        self.root.geometry('500x300')
        self.folder = None

        style = ttk.Style()
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map("Treeview", background=[("selected", "blue")])

        self.folder_frame = tk.Frame(root)
        self.folder_frame.pack()

        self.browse_button = tk.Button(self.folder_frame, text="Browse Folders", command=self.browse_folders)
        self.browse_button.pack()

        self.start_button = tk.Button(self.folder_frame, text="Start", command=self.start_action)
        self.start_button.pack()

        self.tree = TtkCheckList(root)
        self.tree.pack()

    def browse_folders(self):
        self.folder = filedialog.askdirectory()
        if not self.folder:
            messagebox.showwarning("Warning", "No folder selected!")
            return
        self.tree.delete(*self.tree.get_children())
        self.add_folder_recursive("", self.folder)

    def add_folder_recursive(self, parent_id, folder):
        folder_name = os.path.basename(folder)
        item_id = f"{parent_id}.{folder_name}" if parent_id else folder_name
        self.tree.insert(parent_id, 'end', iid=item_id, text=folder_name + " " + BALLOT_BOX)
        for sub_dir in os.listdir(folder):
            sub_folder_path = os.path.join(folder, sub_dir)
            if os.path.isdir(sub_folder_path):
                self.add_folder_recursive(item_id, sub_folder_path)

    def get_full_path(self, item):
        path_parts = []
        while item:
            text = self.tree.item(item, "text").split(" ")[0]
            path_parts.insert(0, text)
            item = self.tree.parent(item)
        
        root_folder_name = os.path.basename(self.folder)
        if path_parts[0] == root_folder_name:
            path_parts.pop(0)
        relative_path = os.path.join(*path_parts)
        full_path = os.path.abspath(os.path.join(self.folder, relative_path))
        return full_path

    def start_action(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "Please select a folder before starting.")
            return

        for item in selected_items:
            full_path = self.get_full_path(item)
            if os.path.isdir(full_path):
                print(f"Sorting folder: {full_path}")  # Til debugging
                sort_folders(full_path)
            else:
                messagebox.showwarning("Warning", f"Selected item '{full_path}' is not a valid folder.")
        
        messagebox.showinfo("Success", "Folders sorted successfully!")



if __name__ == "__main__":
    root = tk.Tk()
    app = FolderApp(root)
    root.mainloop()
