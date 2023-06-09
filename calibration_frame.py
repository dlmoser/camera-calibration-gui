import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox
import os
import glob
from PIL import Image
import numpy as np
import time
import json
import threading
import setting_manager as sm


from cam_video_stream import CamStream
from camera_calibration.camera_calibrator import ChessboardCalibrator
from custom_widgets import SelectSaveFolderFrame, ImagePreviewFrame


class DistortionCoefficients(ctk.CTkFrame):
    def __init__(self, master, calibration_inst, **kwargs):
        super().__init__(master, **kwargs)

        self.calibration_inst = calibration_inst
        self.init_distortion_coefficients()

        self.grid_rowconfigure((0), weight=0)
        self.grid_columnconfigure((0), weight=1)
        # self.grid_columnconfigure((\0,1,2,3,4,5,6,7,8,9,10,11,12), weight=1)


        switch_var = ctk.StringVar(value="off")
        def switch_event():
            print("switch toggled, current value:", switch_var.get())

            if switch_var.get() == "on":
                # frame_setting_main = ctk.CTkFrame(master=self, fg_color="transparent")
                self.frame_setting_main.grid(row=1, column=0, padx=5, pady=0, sticky="we")
                self.set_distortion_coefficients()
            else:
                self.frame_setting_main.grid_forget()
                self.calibration_inst.normal_calibration_inst.set_camera_matrix(None)


        switch_1 = ctk.CTkSwitch(master=self, text="Set Distortion Coefficients", command=switch_event, variable=switch_var, onvalue="on", offvalue="off")
        switch_1.grid(row=0, column=0, padx=5, pady=(0,4),sticky="w", columnspan=3)

        self.frame_setting_main = ctk.CTkFrame(master=self, fg_color="transparent")

        self.frame_setting_main.grid_columnconfigure((0,1,2), weight=1)
        self.frame_setting_main.grid_rowconfigure((0), weight=1)

        for idx, (key, v) in enumerate(sorted(self.dc.items())):

            frame_elem = ctk.CTkFrame(master=self.frame_setting_main, fg_color="transparent")
            frame_elem.grid(row=int(idx/2), column=idx%2, padx=5, pady=0, sticky="we")
            frame_elem.grid_columnconfigure((0,1,2), weight=1)

            ctk.CTkLabel(master=frame_elem, text=v["name"], font=(None, 11), height=15).grid(row=0, column=0, padx=0, pady=0, sticky="ew")
            ctk.CTkLabel(master=frame_elem, text="=", font=(None, 11), height=15).grid(row=0, column=1, padx=0, pady=0, sticky="ew")
            k = ctk.CTkEntry(master=frame_elem, width = 40, height = 15, fg_color = "transparent", corner_radius=0 , font=(None, 10))
            k.grid(row=0, column=2, padx=0, pady=0, sticky="ew")
            k.configure(validate='focusout', validatecommand=(self.register(self.validate_entry), '%P', "%W", key), textvariable = v["value"])


    def validate_entry(self, value, widget_name, K_key):
        try:
            value = float(value)
        except:
            print("value error")
            # self.K[K_key]["value"].set("0.0")
            widget = self.nametowidget(widget_name)
            self.after_idle(lambda: self.dc[K_key]["value"].set("0.0"))
            return False
        self.after_idle(lambda: self.set_distortion_coefficients())
        return True

    def init_distortion_coefficients(self):
        self.dc = {"c01": {"name": "k1", "value": tk.StringVar(value="0.0")},
                "c02": {"name": "k2", "value": tk.StringVar(value="0.0")},
                "c03": {"name": "p1", "value": tk.StringVar(value="0.0")},
                "c04": {"name": "p2", "value": tk.StringVar(value="0.0")},
                "c05": {"name": "k3", "value": tk.StringVar(value="0.0")},
                "c06": {"name": "k4", "value": tk.StringVar(value="0.0")},
                "c07": {"name": "k5", "value": tk.StringVar(value="0.0")},
                "c08": {"name": "k6", "value": tk.StringVar(value="0.0")},
                "c09": {"name": "s1", "value": tk.StringVar(value="0.0")},
                "c10": {"name": "s2", "value": tk.StringVar(value="0.0")},
                "c11": {"name": "s3", "value": tk.StringVar(value="0.0")},
                "c12": {"name": "s4", "value": tk.StringVar(value="0.0")},
                "c13": {"name": "tx", "value": tk.StringVar(value="0.0")},
                "c14": {"name": "ty", "value": tk.StringVar(value="0.0")}}
        self.set_distortion_coefficients()
                      

    def set_distortion_coefficients(self):
        dc = np.zeros((14))
        for idx, (k, v) in enumerate(sorted(self.dc.items())):
            dc[idx] = float(v["value"].get())
        self.calibration_inst.normal_calibration_inst.set_distortion_coefficients(dc)



class CameraMatrix(ctk.CTkFrame):
    def __init__(self, master, calibration_inst, **kwargs):
        super().__init__(master, **kwargs)

        self.calibration_inst = calibration_inst
        self.init_camnera_matrix()

        self.grid_rowconfigure((0,1), weight=1)
        self.grid_columnconfigure((0,1,2), weight=0)

        switch_var = ctk.StringVar(value="off")
        def switch_event():
            print("switch toggled, current value:", switch_var.get())

            if switch_var.get() == "on":
                # frame_setting_main = ctk.CTkFrame(master=self, fg_color="transparent")
                self.frame_setting_main.grid(row=1, column=0, padx=5, pady=0, sticky="w")
                self.set_camera_matrix()
            else:
                self.frame_setting_main.grid_forget()
                self.calibration_inst.normal_calibration_inst.set_camera_matrix(None)


        switch_1 = ctk.CTkSwitch(master=self, text="Set Camera Matrix", command=switch_event, variable=switch_var, onvalue="on", offvalue="off")
        switch_1.grid(row=0, column=0, padx=5, pady=(0,4),sticky="w", columnspan=3)

        # ctk.CTkLabel(master=self, text="Set Camera Matrix", height=20).grid(row=0, column=0, padx=5, pady=(0,4),sticky="w", columnspan=3)

        self.frame_setting_main = ctk.CTkFrame(master=self, fg_color="transparent")
        # self.frame_setting_main.grid(row=1, column=0, padx=5, pady=0, sticky="w")

        frame_label = ctk.CTkFrame(master=self.frame_setting_main, fg_color="transparent")
        frame_label.grid(row=1, column=0, padx=(5,0), pady=(0,10))

        frame_label.grid_rowconfigure((0,1,2), weight=1)
        frame_label.grid_columnconfigure((0,1,2), weight=1)
        

        # display camera matrix entry names
        for idx, (k, v) in enumerate(sorted(self.K.items())):
            ctk.CTkLabel(master=frame_label, text=v["name"], font=(None, 10), height=20, width = 20).grid(row=int((idx)/3), column=(idx)%3, padx=0, pady=0)

        ctk.CTkLabel(master=self.frame_setting_main, text="=").grid(row=1, column=1, padx=10, pady=(0,10), sticky="ns")

        frame_entry = ctk.CTkFrame(master=self.frame_setting_main, fg_color="transparent")
        frame_entry.grid(row=1, column=2, padx=0, pady=(0,10))

        frame_entry.grid_rowconfigure((0,1,2), weight=1)
        frame_entry.grid_columnconfigure((0,1,2), weight=1)

        # create entry fields to get camera matrix values
        for idx, (key, v) in enumerate(sorted(self.K.items())):
            k = ctk.CTkEntry(master=frame_entry, width=40, height = 20, fg_color = "transparent", corner_radius=0 , font=(None, 10))
            k.grid(row=int((idx)/3), column=(idx)%3, padx=0, pady=0)
            k.configure(validate='focusout', validatecommand=(self.register(self.validate_entry), '%P', "%W", key), textvariable = self.K[key]["value"])


    def validate_entry(self, value, widget_name, K_key):
        try:
            value = float(value)
        except:
            print("value error")
            # self.K[K_key]["value"].set("0.0")
            widget = self.nametowidget(widget_name)
            self.after_idle(lambda: self.K[K_key]["value"].set("0.0"))
            return False
        self.after_idle(lambda: self.set_camera_matrix())
        
        return True
 
    def init_camnera_matrix(self):
        #TODO maybe save and reload camera matrix

        self.K = {"a1": {"name": "fx", "value": tk.StringVar(value="0.0")},
                "a2": {"name": "0", "value": tk.StringVar(value="0.0")},
                "a3": {"name": "cx", "value": tk.StringVar(value="0.0")},
                "a4": {"name": "0", "value": tk.StringVar(value="0.0")},
                "a5": {"name": "fy", "value": tk.StringVar(value="0.0")},
                "a6": {"name": "cy", "value": tk.StringVar(value="0.0")},
                "a7": {"name": "0", "value": tk.StringVar(value="0.0")},
                "a8": {"name": "0", "value": tk.StringVar(value="0.0")},
                "a9": {"name": "1", "value": tk.StringVar(value="0.0")}}
        self.set_camera_matrix()
            

    def set_camera_matrix(self):
        K = np.zeros((3,3))
        for idx, (k, v) in enumerate(sorted(self.K.items())):
            K[int(idx/3), idx%3] = float(v["value"].get())
        self.calibration_inst.normal_calibration_inst.set_camera_matrix(K)



class NormalCalibrationSettings(ctk.CTkFrame):
    def __init__(self, master, calibration_inst, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.calibration_inst = calibration_inst

        self.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17), weight=5)
        self.grid_columnconfigure((0), weight=1)

        ctk.CTkLabel(master=self, text="Set Calibration Flags", height=20).grid(row=0, column=0, padx=5, pady=(0,4),sticky="w", columnspan=3)

        self.calibration_checkbox_list = []
        for idx, setting_name in enumerate(self.calibration_inst.normal_calibration_inst.get_available_flags_names()):
            checkbox = ctk.CTkCheckBox(master=self, text=setting_name, checkbox_width = 12, checkbox_height=12, font=(None,11), command = self.set_calibration_flags)
            checkbox.grid(row=idx+1, column=0, padx=5, pady=0, sticky="ewn")
            self.calibration_checkbox_list.append([setting_name, checkbox])

    def set_calibration_flags(self):
        
        selected_flag_list = [elem[0] for elem in self.calibration_checkbox_list if elem[1].get() == True]
        print("selected_flag_list", selected_flag_list)
        self.calibration_inst.normal_calibration_inst.set_calibration_flags(selected_flag_list)



class NormalCalibrationFrame(ctk.CTkFrame):
    def __init__(self, master, calibration_inst, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.calibration_inst = calibration_inst

        self.calibration_inst.set_calibrator_mode("normal")

        self.grid_rowconfigure((0), weight=1)
        self.grid_columnconfigure((0), weight=1)

        scroll_frame = ctk.CTkScrollableFrame(master=self, fg_color="transparent")
        scroll_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ewns")

        scroll_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17), weight=5)
        scroll_frame.grid_columnconfigure((0), weight=1)

        CameraMatrix(master=scroll_frame, calibration_inst = calibration_inst).grid(row=0, column=0, padx=0, pady=0, sticky="ew")

        DistortionCoefficients(master=scroll_frame, calibration_inst = calibration_inst).grid(row=1, column=0, padx=0, pady=(5, 0), sticky="ew")

        NormalCalibrationSettings(master=scroll_frame, calibration_inst=self.calibration_inst).grid(row=2, column=0, padx=0, pady=5, sticky="ew")

        ctk.CTkButton(master=self, text="Start Calibration", command = self.start_calibration).grid(row=1, column=0, padx=10, pady=5, sticky="ews")

        self.save_calibration_parameter_button = ctk.CTkButton(master=self, text="Save Calibration Parameter", command = self.save_calibration_parameter)
        self.save_calibration_parameter_button.grid(row=2, column=0, padx=10, pady=5, sticky="ews")
        self.save_calibration_parameter_button.configure(state="disabled")


    def save_calibration_parameter(self):
        calibration_dict = self.calibration_inst.normal_calibration_inst.get_calibration_parameter()
        files = [('Calibration Parameter', '*.json')]
        file = filedialog.asksaveasfile(initialdir=sm.setting_dict["selected_image_save_folder"].get(), filetypes = files, defaultextension = files)
        with open(file.name, "w") as f:
            json.dump(calibration_dict, f, indent=4)
        sm.setting_dict["calibration_file_path"].set(file.name)
        

    def start_calibration(self):

        def calibration_thread():
            self.calibration_inst.init_object_and_image_points()
            for image_path in self.master.master.image_preview_frame.images_in_folder:

                print(image_path)
                ret, img = self.calibration_inst.find_chessboard_corners_in_image(image_path)

                self.master.master.image_box_frame.set_display_image(img)
                time.sleep(0.1)

            try:
                self.calibration_inst.calculate_calibration_matrix()
            except Exception as e:
                messagebox.showerror('Python Error', e)

            for image_path in self.master.master.image_preview_frame.images_in_folder:

                print(image_path)
                img = self.calibration_inst.undistort_image(image_path)

                self.master.master.image_box_frame.set_display_image(img)
                time.sleep(0.1)

            self.save_calibration_parameter_button.configure(state="normal")
        threading.Thread(target=calibration_thread).start()



class LeftSettingBox(ctk.CTkTabview):
    def __init__(self, master, calibration_inst, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.calibration_inst = calibration_inst

        # create tabs
        self.add("Normal")
        self.add("Fisheye")

     
        self.tab("Normal").grid_rowconfigure((0), weight=1)
        self.tab("Normal").grid_columnconfigure((0), weight=1)

        self.normal_calibration_frame = NormalCalibrationFrame(master = self.tab("Normal"), calibration_inst = self.calibration_inst, fg_color = "transparent")
        self.normal_calibration_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ewns")


    def set_image_box_frame(self, image_box_frame):
        self.image_box_frame = image_box_frame

    def set_preview_frame(self, image_preview_frame):
        self.image_preview_frame = image_preview_frame





class ImageBoxFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.current_size = None
        
        self.bind('<Configure>', self.resizer)

        self.current_frame = Image.fromarray(np.ones((100,int(100*1.25)), np.uint8)*0)

        self.image_label = ctk.CTkLabel(self, text = "")
        self.image_label.pack(fill = "both", expand = True, anchor="center")

        self.update_image()


    def set_display_image(self, image):
        self.current_frame = Image.fromarray(image)

    def update_image(self):
        if self.current_size is not None:
            display_frame = ctk.CTkImage(dark_image = self.current_frame, size=self.current_size)
            self.image_label.configure(image=display_frame)
        self.after(30, self.update_image)


    def resizer(self, e):
        self.current_size = (e.width,e.height)
        img = ctk.CTkImage(dark_image=self.current_frame, size=self.current_size)
        self.image_label.configure(image=img)



class CalibrationFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.calibration_inst = ChessboardCalibrator()

        self.grid_rowconfigure((0), weight=4)
        self.grid_rowconfigure((1), weight=0)
        self.grid_columnconfigure((0), weight=1)
        self.grid_columnconfigure((1), weight=4)

        self.image_box_frame = ImageBoxFrame(master=self)
        self.image_box_frame.grid(row=0, column=1, padx=(0,10), pady=10, sticky="nsew")

        self.left_setting_box = LeftSettingBox(master=self, calibration_inst = self.calibration_inst)
        self.left_setting_box.grid(row=0, column=0, padx=10, pady=(0,10), sticky="nsew")
        
        self.select_save_folder_frame = SelectSaveFolderFrame(master=self)
        self.select_save_folder_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")

        self.image_preview_frame = ImagePreviewFrame(master=self, height=100)
        self.image_preview_frame.grid(row=1, column=1, padx=(0,10), pady=(0,10), sticky="nsew")

        # add the image box frame instance to settings so the we can display the calibration process
        self.left_setting_box.set_image_box_frame(self.image_box_frame)

        # add the image preview frame to settings so we can get the image elements
        self.left_setting_box.set_preview_frame(self.image_preview_frame)
