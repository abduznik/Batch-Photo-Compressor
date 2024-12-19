import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ExifTags
import os
from datetime import datetime

def select_files_or_folder():
    global selected_files
    selected_files = []
    choice = file_or_folder.get()

    if choice == "files":
        selected_files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
        )
    elif choice == "folder":
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                        selected_files.append(os.path.join(root, file))

    if selected_files:
        files_label.config(text=f"{len(selected_files)} file(s) selected")
    else:
        files_label.config(text="No files selected")

def compress_images():
    if not selected_files:
        messagebox.showwarning("No Files Selected", "Please select files or a folder to compress.")
        return

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    # Create a new folder with the current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_folder = os.path.join(output_folder, f"compressed_{timestamp}")
    os.makedirs(new_folder, exist_ok=True)

    for file in selected_files:
        try:
            with Image.open(file) as img:
                # Auto Orient
                if auto_orient_var.get():
                    try:
                        for orientation in ExifTags.TAGS.keys():
                            if ExifTags.TAGS[orientation] == 'Orientation':
                                break
                        exif = img._getexif()
                        if exif is not None:
                            orientation = exif.get(orientation)
                            if orientation == 3:
                                img = img.rotate(180, expand=True)
                            elif orientation == 6:
                                img = img.rotate(270, expand=True)
                            elif orientation == 8:
                                img = img.rotate(90, expand=True)
                    except Exception as e:
                        print(f"Auto-orientation failed for {file}: {e}")

                # Ensure image is in RGB mode
                img = img.convert("RGB")
                filename = os.path.basename(file)
                output_path = os.path.join(new_folder, os.path.splitext(filename)[0] + "_compressed.jpg")

                # Save with compression if selected
                if compress_var.get():
                    img.save(output_path, "JPEG", quality=60)
                else:
                    img.save(output_path, "JPEG", quality=100)
        except Exception as e:
            messagebox.showerror("Error", f"Error processing {file}: {e}")

    messagebox.showinfo("Success", f"Images processed and saved to {new_folder}.")

# GUI Setup
root = tk.Tk()
root.title("Image Processor")
root.geometry("500x350")
root.config(bg="#333")  # Dark theme background

selected_files = []

# GUI Elements
tk.Label(root, text="Select Files or Folder and Options", bg="#333", fg="#FFF").pack(pady=10)

# File/Folder selection options
file_or_folder = tk.StringVar(value="files")
tk.Radiobutton(root, text="Select Files", variable=file_or_folder, value="files", bg="#333", fg="#FFF", selectcolor="#555", command=select_files_or_folder).pack()
tk.Radiobutton(root, text="Select Folder", variable=file_or_folder, value="folder", bg="#333", fg="#FFF", selectcolor="#555", command=select_files_or_folder).pack()

files_label = tk.Label(root, text="No files selected", fg="#0F0", bg="#333")
files_label.pack(pady=5)

# Checkboxes for options
compress_var = tk.BooleanVar(value=True)
auto_orient_var = tk.BooleanVar(value=False)

tk.Checkbutton(root, text="Enable Compression (Medium, 60%)", variable=compress_var, bg="#333", fg="#FFF", selectcolor="#555").pack()
tk.Checkbutton(root, text="Auto Orient Images", variable=auto_orient_var, bg="#333", fg="#FFF", selectcolor="#555").pack()

compress_button = tk.Button(root, text="Process Images", command=compress_images, bg="#444", fg="#FFF", activebackground="#555", activeforeground="#FFF")
compress_button.pack(pady=20)

root.mainloop()
