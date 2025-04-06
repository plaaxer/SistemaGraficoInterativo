import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk

class FileLoader:
    def __init__(self):
        pass

    def load_obj(self, file_path):
        """Loads a .obj file and returns its content as a list of lines."""
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            return lines
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error loading .obj file: {e}")
            return None

    @staticmethod
    def load_image(file_path):
        """Loads an image file and returns it as a tkinter PhotoImage object."""
        try:
            image = Image.open(file_path)
            tk_image = ImageTk.PhotoImage(image)
            return tk_image
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error loading image: {e}")
            return None