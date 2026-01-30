import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from typing import List, Tuple
from pathlib import Path
from PIL import Image, ExifTags, UnidentifiedImageError
import os
from datetime import datetime
import argparse
from tqdm import tqdm

selected_files: List[str] = []

# Helper function for validation
def check_range(value) -> int:
    i_value = int(value)
    if i_value < 1 or i_value > 100:
        raise argparse.ArgumentTypeError(f'{value} is invalid. Please choose an integer between 1 and 100.')
    return i_value

def select_files_or_folder() -> None:
    global selected_files
    choice = file_or_folder.get()

    if choice == "files":
        files: Tuple[str, ...] = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
        )
        selected_files = list(files)
    elif choice == "folder":
        folder: str = filedialog.askdirectory(title="Select Folder")
        if folder:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                        selected_files.append(os.path.join(root, file))

    if selected_files:
        files_label.config(text=f"{len(selected_files)} file(s) selected")
    else:
        files_label.config(text="No files selected")

def compress_images() -> None:
    if not selected_files:
        messagebox.showwarning("No Files Selected", "Please select files or a folder to compress.")
        return

    output_folder: str = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    # Create a new folder with the current date and time
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_folder: str = os.path.join(output_folder, f"compressed_{timestamp}")
    os.makedirs(new_folder, exist_ok=True)

    # Setup Progress Bar
    progress_bar['value'] = 0
    progress_bar['maximum'] = len(selected_files)

    # Get the format selected by the user
    selected_format = format_var.get()

    for file in tqdm(selected_files, desc="Compressing", unit="img"):
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

                # Handle Transparency
                if selected_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                    # Ensure image is in RGB mode
                    img = img.convert("RGB")
                
                # Determine File Extension
                filename: str = os.path.basename(file)
                file_root: Path = os.path.splitext(filename)[0]
                
                if selected_format == 'JPEG':
                    ext = '.jpg'
                else:
                    ext = f'.{selected_format.lower()}'

                output_path: str = os.path.join(new_folder, f"{file_root}_compressed.{ext}")

                # Save with compression if selected
                quality_val = args.quality if compress_var.get() else 100
                img.save(output_path, format=selected_format, quality=quality_val)

        # Catch specific errors and Log instead of stopping
        except (UnidentifiedImageError, IOError) as e:
            print(f'Warning: Skipped invalid file {file}. Reason: {e}')
            continue
        except Exception as e:
            messagebox.showerror("Error", f"Error processing {file}: {e}")
        
        # Update GUI
        progress_bar['value'] += 1
        root.update_idletasks()  # to keep the window awake

    messagebox.showinfo("Success", f"Images processed and saved to {new_folder}.")


# Setup CLI Argument Parser
parser = argparse.ArgumentParser(description='Image Processor CLI/GUI')

# Define --quality argument with the custom validation type
parser.add_argument(
    '--quality',
    type=check_range,
    default=60,
    help='Compression quality (1-100)',
)

# Parse arguments
args = parser.parse_args()

# GUI Setup
root = tk.Tk()
root.title("Image Processor")
root.geometry("500x350")
root.config(bg="#333")  # Dark theme background

# GUI Elements
tk.Label(root, text="Select Files or Folder and Options", bg="#333", fg="#FFF").pack(pady=10)

# File/Folder selection options
file_or_folder = tk.StringVar(value="files")
tk.Radiobutton(root, text="Select Files", variable=file_or_folder, value="files", bg="#333", fg="#FFF", selectcolor="#555", command=select_files_or_folder).pack()
tk.Radiobutton(root, text="Select Folder", variable=file_or_folder, value="folder", bg="#333", fg="#FFF", selectcolor="#555", command=select_files_or_folder).pack()

files_label = tk.Label(root, text="No files selected", fg="#0F0", bg="#333")
files_label.pack(pady=5)

# Output Format Selection
format_label = tk.Label(root, text="Output Format:", bg="#333", fg="#FFF")
format_label.pack()

format_var = tk.StringVar(value="JPEG")
format_menu = ttk.Combobox(root, textvariable=format_var, state="readonly")
format_menu["values"] = ["JPEG", "PNG", "WEBP"]
format_menu.pack(pady=5)

# Checkboxes for options
compress_var = tk.BooleanVar(value=True)
auto_orient_var = tk.BooleanVar(value=False)

tk.Checkbutton(root, text="Enable Compression (Medium, 60%)", variable=compress_var, bg="#333", fg="#FFF", selectcolor="#555").pack()
tk.Checkbutton(root, text="Auto Orient Images", variable=auto_orient_var, bg="#333", fg="#FFF", selectcolor="#555").pack()

compress_button = tk.Button(root, text="Process Images", command=compress_images, bg="#444", fg="#FFF", activebackground="#555", activeforeground="#FFF")
compress_button.pack(pady=20)

# Progress Bar Widget
progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(pady=10)

root.mainloop()
