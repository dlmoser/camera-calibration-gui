import customtkinter as ctk
from tkinter import filedialog
import glob
import os
import numpy as np

from image_recording_frame import ImageRecordingFrame



# Supported themes: green, dark-blue, blue
ctk.set_appearance_mode("dark")




class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("900x600")
        self.title("Camera Calibration App")
        self.minsize(600, 400)

        self.grid_rowconfigure((0), weight=0)
        self.grid_rowconfigure((1), weight=1)
        self.grid_columnconfigure((0), weight=1)

        self.top_frame = ctk.CTkFrame(self, height=50)
        self.top_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nsew")
        self.image_record_mode_button = ctk.CTkButton(master=self.top_frame, text="Image Recording Mode", command = lambda: self.set_main_mode("image_record_mode"))
        self.image_record_mode_button.pack(side="left", fill="x", expand=1, padx=5, pady=5)
        self.image_record_mode_button.configure(state="disabled")
        self.image_record_mode_button.configure(fg_color="grey")
        self.calibration_mode_button = ctk.CTkButton(master=self.top_frame, text="Calibration Mode", command = lambda: self.set_main_mode("calibration_mode"))
        self.calibration_mode_button.pack(side="right", fill="x", expand=1, padx=5, pady=5)
        # self.image_record_mode_button.configure(state="disabled")
        # self.image_record_mode_button.configure(fg_color="grey")

        self.main_frame = ImageRecordingFrame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


    def set_main_mode(self, mode):
        try:
            self.main_frame.destroy()
        except:
            pass
        if mode == "image_record_mode":
            self.main_frame = ImageRecordingFrame(self)
            self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            self.image_record_mode_button.configure(state="disabled")
            self.image_record_mode_button.configure(fg_color="grey")
            self.calibration_mode_button.configure(state = "normal") 
            self.calibration_mode_button.configure(fg_color = ['#3B8ED0', '#1F6AA5'])

        elif mode == "calibration_mode":
            self.main_frame = ctk.CTkFrame(self)
            self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
            self.calibration_mode_button.configure(state="disabled")
            self.calibration_mode_button.configure(fg_color="grey")
            self.image_record_mode_button.configure(state = "normal") 
            self.image_record_mode_button.configure(fg_color = ['#3B8ED0', '#1F6AA5'])




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
     