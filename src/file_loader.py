import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class FileLoader:
    def __init__(self, application):
        self._app = application

    @staticmethod
    def load_image(file_path):
        """Loads an image file and returns it as a tkinter PhotoImage object."""
        try:
            image = Image.open(file_path)
            tk_image = ImageTk.PhotoImage(image)
            return tk_image
        except FileNotFoundError:
            ##print(f"File not found: {file_path}")
            return None
        except Exception as e:
            ##print(f"Error loading image: {e}")
            return None

    @staticmethod
    def open_file_dialog():
        """Opens a file dialog to select a file."""
        return filedialog.askopenfilename(
            filetypes=[("OBJ Files", "*.obj"), ("All Files", "*.*")]
        )

    @staticmethod
    def save_file_dialog():
        """Opens a file dialog to select a location to save the file."""
        return filedialog.asksaveasfilename(
            defaultextension=".obj",
            filetypes=[("OBJ Files", "*.obj"), ("All Files", "*.*")]
        )
