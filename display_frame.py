import customtkinter as ctk
from tkinter import filedialog
import json
import os
from PIL import Image
import numpy as np
import threading
import setting_manager as sm


from cam_video_stream import CamStream
from camera_calibration.camera_calibrator import RemapCalibrator
from custom_widgets import LoadingAnimation


class LeftSettingBox(ctk.CTkFrame):
    def __init__(self, cam_inst, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.cam_inst = cam_inst


        self.grid_rowconfigure((0,1), weight=0)
        self.grid_rowconfigure((4), weight=1)
        self.grid_columnconfigure((0), weight=1)

        ctk.CTkLabel(master=self, text="Select Camera").grid(row=0, column=0, padx=5, pady=5, sticky="ewn")

        available_cams, selected_cam = self.cam_inst.get_available_cameras()
        self.camera_selector = ctk.CTkComboBox(master=self,values=[elem[0] for elem in available_cams], command=self.cam_inst.cam_changed)
        self.camera_selector.grid(row=1, column=0, padx=5, pady=5, sticky="ewn")

        # set the default cam
        default_cam = available_cams[selected_cam][0]
        self.camera_selector.set(default_cam)
        self.cam_inst.cam_changed(default_cam)

        # ctk.CTkLabel(master=self, text="").grid(row=2, column=0, padx=5, pady=5, sticky="ewn")
        # self.master.calibration_detector_selector = ctk.CTkComboBox(master=self,values=["No Detector", "Chessboard"])
        # self.master.calibration_detector_selector.grid(row=3, column=0, padx=5, pady=5, sticky="ewn")

        ctk.CTkButton(master=self, text="Load Calibration Parameter", command=self.load_calibration_parameter).grid(row=2, column=0, padx=5, pady=5, sticky="ewn")
        self.calibration_parameter_label = ctk.CTkLabel(master=self, text="no calibration file")
        self.calibration_parameter_label.grid(row=4, column=0, padx=5, pady=5, sticky="ewn")

        # trace when calibration_file_path variable is changed to adapt the label and the save button mode
        sm.setting_dict["calibration_file_path"].trace('w', self.write_calibration_file_path)
        # call once for initialization
        self.write_calibration_file_path()


    def write_calibration_file_path(self, *args):
        file_path = sm.setting_dict["calibration_file_path"].get()
        try:
            self.calibration_parameter_label.configure(text=os.path.split(file_path)[-1])
        except:
            self.calibration_parameter_label.configure(text="no calibration file")


    def load_calibration_parameter(self):
        file_path = filedialog.askopenfilename(initialdir=sm.setting_dict["selected_image_save_folder"].get(), title="Select Calibration Parameter File", filetypes=[("Calibration Parameter", "*.json")])
        sm.setting_dict["calibration_file_path"].set(file_path)
        self.calibration_parameter_label.configure(text=os.path.split(file_path)[-1])



class ImageBoxFrame(ctk.CTkFrame):
    def __init__(self, cam_inst, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.cam_inst = cam_inst
        self.current_size = None
        self.remap_calibrator_inst = None

        self.bind('<Configure>', self.resizer)

        self.current_frame = Image.fromarray(np.ones((100,int(100*1.25)), np.uint8)*255)

        self.image_label = ctk.CTkLabel(self, text = "")
        self.image_label.pack(fill = "both", expand = True, anchor="center")

        # trace when calibration_file_path variable is changed to adapt the label and the save button mode
        sm.setting_dict["calibration_file_path"].trace('w', self.write_calibration_file_path)
        # call once for initialization
        self.write_calibration_file_path()

        self.update_image()

    def write_calibration_file_path(self, *args):
        file_path = sm.setting_dict["calibration_file_path"].get()
        if file_path != "":
            print("file_path", file_path)
            with open(file_path, "r") as f:
                calibration_parameter = json.load(f)
            self.remap_calibrator_inst = RemapCalibrator(calibration_parameter["map1"], calibration_parameter["map2"])



    def update_image(self):
        if self.current_size is not None:
            if self.remap_calibrator_inst is not None:
                frame = self.remap_calibrator_inst.undistort_image(self.cam_inst.frame.copy())
            else:
                frame = self.cam_inst.frame.copy()
            self.current_frame = Image.fromarray(frame)
            display_frame = ctk.CTkImage(dark_image = self.current_frame, size=self.current_size)
            self.image_label.configure(image=display_frame)
        self.after(30, self.update_image)



    def resizer(self, e):
        print("resize")
        self.current_size = (e.width,e.height)
        img = ctk.CTkImage(dark_image=self.current_frame, size=self.current_size)
        self.image_label.configure(image=img)




class DisplayFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.create_loading_frame()

        self.camera_init_thread()

        self.create_image_recording_frame_when_cam_init_is_finished()


    def create_loading_frame(self):
        self.loading_frame = LoadingAnimation(self)
        self.loading_frame.pack(fill="both", expand=True)

    def camera_init_thread(self):
        self.cam_inst = None
        def init_cam():
            self.cam_inst = CamStream()
        threading.Thread(target=init_cam).start()

    def create_image_recording_frame(self):
        try:
            self.loading_frame.destroy()
        except:
            pass
        self.grid_rowconfigure((0), weight=4)
        self.grid_rowconfigure((1), weight=1)
        self.grid_columnconfigure((0), weight=1)
        self.grid_columnconfigure((1), weight=4)

        self.image_box_frame = ImageBoxFrame(master=self, cam_inst=self.cam_inst)
        self.image_box_frame.grid(row=0, column=1, padx=(0,10), pady=10, sticky="nsew")

        self.left_setting_box = LeftSettingBox(master=self, cam_inst=self.cam_inst)
        self.left_setting_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    
    def create_image_recording_frame_when_cam_init_is_finished(self):
        if self.cam_inst is not None:
            self.create_image_recording_frame()
        else:
            self.after(100, self.create_image_recording_frame_when_cam_init_is_finished)

    def destroy(self):
        print("destroy ImageRecordingFrame")
        if self.cam_inst is not None:
            self.cam_inst.stop_stream()
        return super().destroy()


