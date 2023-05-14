import customtkinter as ctk
from tkinter import filedialog
import glob
import os
import numpy as np
from PIL import Image
import time
import tkinter as tk
import setting_manager


from image_recording_frame import ImageRecordingFrame
from calibration_frame import CalibrationFrame
from display_frame import DisplayFrame
from cam_video_stream import CamStream
from custom_widgets import LoadingAnimation


# Supported themes: green, dark-blue, blue
ctk.set_appearance_mode("dark")




class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        setting_manager.init_setting_dict()

        self.geometry("900x600")
        self.title("Camera Calibration App")
        self.minsize(600, 400)

        # folder where calibration images are saved
        # the variable is on top level to share it between recording and calibration frames
        self.selected_image_save_folder = tk.StringVar(value="No Folder Selected")
  

        self.grid_rowconfigure((0), weight=0)
        self.grid_rowconfigure((1), weight=1)
        self.grid_columnconfigure((0), weight=1)

        self.top_frame = ctk.CTkFrame(self, height=50)
        self.top_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nsew")
        
        self.top_frame.grid_columnconfigure((0,1,2), weight=1)
        self.image_record_mode_button = ctk.CTkButton(master=self.top_frame, text="Image Recording Mode", command = lambda: self.set_main_mode("image_record_mode"))
        self.image_record_mode_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        # self.image_record_mode_button.configure(state="disabled")
        # self.image_record_mode_button.configure(fg_color="grey")
        self.calibration_mode_button = ctk.CTkButton(master=self.top_frame, text="Calibration Mode", command = lambda: self.set_main_mode("calibration_mode"))
        self.calibration_mode_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.calibration_mode_button.configure(fg_color="transparent")

        self.display_mode_button = ctk.CTkButton(master=self.top_frame, text="Display Mode", command = lambda: self.set_main_mode("display_mode"))
        self.display_mode_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.display_mode_button.configure(fg_color="transparent")


        self.main_frame = ImageRecordingFrame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # self.main_frame = CalibrationFrame(self)
        # self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # self.DEVELOP_CALIBRATION_MODE()


    def DEVELOP_CALIBRATION_MODE(self):
        self.set_main_mode("calibration_mode")

        self.main_frame = CalibrationFrame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")



    def set_main_mode(self, mode):
        try:
            self.main_frame.destroy()
        except:
            pass
        if mode == "image_record_mode":
            self.main_frame = ImageRecordingFrame(self)
            self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            self.image_record_mode_button.configure(fg_color = ['#3B8ED0', '#1F6AA5'])
            self.calibration_mode_button.configure(fg_color="transparent")
            self.display_mode_button.configure(fg_color = "transparent")

        elif mode == "calibration_mode":
            self.main_frame = CalibrationFrame(self)
            self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            self.image_record_mode_button.configure(fg_color = 'transparent')
            self.calibration_mode_button.configure(fg_color=['#3B8ED0', '#1F6AA5'])
            self.display_mode_button.configure(fg_color = "transparent")

        elif mode == "display_mode":
            self.main_frame = DisplayFrame(self)
            self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            self.image_record_mode_button.configure(fg_color = 'transparent')
            self.calibration_mode_button.configure(fg_color='transparent')
            self.display_mode_button.configure(fg_color = ['#3B8ED0', '#1F6AA5'])





# # Create App class
# class App(ctk.CTk):
#     # Layout of the GUI will be written in the init itself
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Sets the title of our window to "App"
#         self.title("Calibration App")   
#         # Dimensions of the window will be 200x200
#         self.geometry("900x600") 

#         self.columnconfigure(1, weight=1)
#         self.rowconfigure(0, weight=1)

#         left_frame = ctk.CTkFrame(self, width=300, height=400)
#         left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="N")


if __name__ == "__main__":
    app = App()
    app.mainloop()  # Runs the app
     