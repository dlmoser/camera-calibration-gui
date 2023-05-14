import tkinter as tk

def init_setting_dict():
    global setting_dict
    setting_dict = {
        "number_of_images_in_folder": tk.DoubleVar(),
        "selected_image_save_folder": tk.StringVar(value="/Users/davidmoser/Downloads/test_save_folder"),
        "calibration_file_path": tk.StringVar()
    }
