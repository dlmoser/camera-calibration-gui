import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import os
import glob
from PIL import Image
import numpy as np
import time
import threading

from cam_video_stream import CamStream
from camera_calibration.camera_calibrator import ChessboardCalibrator


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
        print("dc", dc)
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
        print("K", K)
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
        print("aaa", selected_flag_list)
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

        ctk.CTkButton(master=self, text="Start Calibration", command = self.start_calibration).grid(row=1, column=0, padx=5, pady=5, sticky="ews")



    def start_calibration(self):

        def calibration_thread():
            self.calibration_inst.init_object_and_image_points()
            for image_path in self.master.master.image_preview_frame.images_in_folder:

                print(image_path)
                ret, img = self.calibration_inst.find_chessboard_corners_in_image(image_path)

                self.master.master.image_box_frame.set_display_image(img)
                time.sleep(0.1)

            self.calibration_inst.calculate_calibration_matrix()

            for image_path in self.master.master.image_preview_frame.images_in_folder:

                print(image_path)
                img = self.calibration_inst.undistort_image(image_path)

                self.master.master.image_box_frame.set_display_image(img)
                time.sleep(0.1)

            


        threading.Thread(target=calibration_thread).start()

        # def find_all_chessboard_corners():
        #     # try:
        #     print("lala")
        #     image_path = next(image_path_iter)
        #     ret, img = self.calibration_inst.find_chessboard_corners_in_image(image_path)
        #     self.master.image_box_frame.set_display_image(img)
        #     # except StopIteration:
        #     #     print("next function should be called here")
        #     #     return
            
        #     self.after(50, find_all_chessboard_corners)

        # image_path_iter = iter(self.master.image_preview_frame.images_in_folder)

        # find_all_chessboard_corners()

        # print("end function")
          
            
        # for image_path in self.master.image_preview_frame.images_in_folder:

        #     print(image_path)
        #     ret, img = self.calibration_inst.find_chessboard_corners_in_image(image_path)

        #     self.master.image_box_frame.set_display_image(img)
        #     time.sleep(1)

        # self.calibration_inst.start_normal_calibration(self.master.image_preview_frame.images_in_folder)   



class MyTabView(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        self.add("Normal")
        self.add("Fisheye")

        self.grid_rowconfigure((0), weight=1)
        self.grid_columnconfigure((0), weight=1)

        # add widgets on tabs
        self.label = ctk.CTkLabel(master=self.tab("Normal"))
        self.label.grid(row=0, column=0, padx=20, pady=10)




class LeftSettingBox(ctk.CTkTabview):
    def __init__(self, master, calibration_inst, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.calibration_inst = calibration_inst

        # create tabs
        self.add("Normal")
        self.add("Fisheye")




        # # add widgets on tabs
        # self.label = ctk.CTkLabel(master=self.tab("Normal"))
        # self.label.grid(row=0, column=0, padx=0, pady=0)


        # MyTabView(master=self, bg_color = "transparent").grid(row=0, column=0, padx=0, pady=0, sticky="ewns")

        # self.grid_rowconfigure((0,1), weight=0)
        # self.grid_rowconfigure((4), weight=1)
        # self.grid_columnconfigure((0), weight=1)

        # ctk.CTkLabel(master=self, text="Select Calibrator").grid(row=0, column=0, padx=5, pady=5, sticky="ewn")


        # self.calibrator_selector = ctk.CTkComboBox(master=self,values=calibration_inst.get_calibrator_list()) #, command=self.cam_inst.cam_changed)
        # self.calibrator_selector.grid(row=1, column=0, padx=5, pady=5, sticky="ewn")

     
        self.tab("Normal").grid_rowconfigure((0), weight=1)
        self.tab("Normal").grid_columnconfigure((0), weight=1)

        self.normal_calibration_frame = NormalCalibrationFrame(master = self.tab("Normal"), calibration_inst = self.calibration_inst, fg_color = "transparent")
        self.normal_calibration_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ewns")


    def set_image_box_frame(self, image_box_frame):
        self.image_box_frame = image_box_frame

    def set_preview_frame(self, image_preview_frame):
        self.image_preview_frame = image_preview_frame



class ImagePreviewFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, orientation="horizontal", **kwargs)
        self.master = master
        self.image_labels = []

        self.check_for_images_in_folder()

    def check_for_images_in_folder(self):
        try:
            self.images_in_folder = sorted(glob.glob(os.path.join(self.master.master.selected_image_save_folder, "*.png")))
            # check if we need to update the image preview
            if len(self.image_labels) != len(self.images_in_folder):
                self.update_image_preview()
        except:
            pass

        self.after(1000, self.check_for_images_in_folder)


    def update_image_preview(self):
        for label in self.image_labels:
            label["img_label"].destroy()
        self.image_labels = []
        for i, image_path in enumerate(self.images_in_folder):
            reference_height = 100
            img = Image.open(image_path)
            display_img = ctk.CTkImage(dark_image=img, size=(img.width/img.height*reference_height, reference_height))
            img_label = ctk.CTkLabel(master=self, text="")
            img_label.grid(row=0, column=i, padx=5, pady=5)
            img_label.configure(image=display_img)

            button = ctk.CTkButton(master=img_label, text="x", width=15, height=15, command = lambda current_elem=image_path: self.remove_image(current_elem))
            button.place(relx=1.0, rely=0.0, anchor="ne")
            
            self.image_labels.append({"img_label": img_label, "img_path": image_path})


    def remove_image(self, img_path):
        print("remove_image", img_path)
        os.remove(img_path)
        self.images_in_folder = sorted(glob.glob(os.path.join(self.master.master.selected_image_save_folder, "*.png")))
        self.update_image_preview()


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
        print("resize")
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
        
        self.image_preview_frame = ImagePreviewFrame(master=self, height=100)
        self.image_preview_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")

        # add the image box frame instance to settings so the we can display the calibration process
        self.left_setting_box.set_image_box_frame(self.image_box_frame)

        # add the image preview frame to settings so we can get the image elements
        self.left_setting_box.set_preview_frame(self.image_preview_frame)
