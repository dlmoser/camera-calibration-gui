import tkinter as tk

def init_setting_dict():
    global setting_dict
    setting_dict = {
        "number_of_images_in_folder": tk.DoubleVar(),
        "selected_image_save_folder": tk.StringVar(value="/Users/davidmoser/Downloads/test_save_folder"),
        "calibration_file_path": tk.StringVar()
    }
# class SettingManager():
#     def __init__(self):
#         self.setting_dict = {"image_save_path": None}


#     def set_setting(self, image_save_path):
#         self.image_save_path = path