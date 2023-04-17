import customtkinter as ctk
from tkinter import filedialog
import os
import glob
from PIL import Image
import numpy as np
import time
import threading

from cam_video_stream import CamStream
from camera_calibration.camera_calibrator import ChessboardCalibrator


class CameraMatrix(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure((0,1,2), weight=1)
        self.grid_columnconfigure((0,1,2), weight=1)

        for i in range(3):
            for j in range(3):
                k = ctk.CTkEntry(master=self, placeholder_text="1.23", width=40, height=20, fg_color = "transparent", corner_radius=0 , font=(None, 10))
                k.grid(row=i, column=j, padx=0, pady=0, sticky="n")


class NormalCalibrationFrame(ctk.CTkFrame):
    def __init__(self, master, calibration_inst, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.calibration_inst = calibration_inst

        self.grid_rowconfigure((0,1,2,3), weight=1)
        self.grid_columnconfigure((0), weight=1)




        ctk.CTkLabel(master=self, text="Select Calibration Settings").grid(row=0, column=0, padx=5, pady=5, sticky="ewn")

        ctk.CTkLabel(master=self, text="Set Camera Matrix").grid(row=1, column=0, padx=0, pady=0, sticky="ewn")


        CameraMatrix(master=self).grid(row=2, column=0, padx=0, pady=0, sticky="n")

        scroll_frame = ctk.CTkScrollableFrame(master=self, height=100, fg_color="transparent")
        scroll_frame.grid(row=3, column=0, padx=0, pady=0, sticky="we")

        scroll_frame.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16), weight=5)
        scroll_frame.grid_columnconfigure((0), weight=0)


        self.calibration_checkbox_list = []
        for idx, setting_name in enumerate(self.calibration_inst.normal_calibration_inst.get_available_flags_names()):
            checkbox = ctk.CTkCheckBox(master=scroll_frame, text=setting_name, checkbox_width = 12, checkbox_height=12, font=(None,11), command = self.set_calibration_flags)
            checkbox.grid(row=idx, column=0, padx=0, pady=0, sticky="ewn")
            self.calibration_checkbox_list.append([setting_name, checkbox])

        
        ctk.CTkButton(master=self, text="Start Calibration", command = self.start_calibration).grid(row=4, column=0, padx=5, pady=5, sticky="ewn")


    def set_calibration_flags(self):
        selected_flag_list = [elem[0] for elem in self.calibration_checkbox_list if elem[1].get() == True]
        self.calibration_inst.normal_calibration_inst.set_calibration_flags(selected_flag_list)

    def start_calibration(self):

        def calibration_thread():
            for image_path in self.master.image_preview_frame.images_in_folder:

                print(image_path)
                ret, img = self.calibration_inst.find_chessboard_corners_in_image(image_path)

                self.master.image_box_frame.set_display_image(img)
                time.sleep(0.1)

            self.calibration_inst.calculate_calibration_matrix()

            for image_path in self.master.image_preview_frame.images_in_folder:

                print(image_path)
                img = self.calibration_inst.undistort_image(image_path)

                self.master.image_box_frame.set_display_image(img)
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




class LeftSettingBox(ctk.CTkFrame):
    def __init__(self, master, calibration_inst, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.calibration_inst = calibration_inst

        self.grid_rowconfigure((0,1), weight=0)
        self.grid_rowconfigure((4), weight=1)
        self.grid_columnconfigure((0), weight=1)

        ctk.CTkLabel(master=self, text="Select Calibrator").grid(row=0, column=0, padx=5, pady=5, sticky="ewn")


        self.calibrator_selector = ctk.CTkComboBox(master=self,values=calibration_inst.get_calibrator_list()) #, command=self.cam_inst.cam_changed)
        self.calibrator_selector.grid(row=1, column=0, padx=5, pady=5, sticky="ewn")

        self.calibration_inst.set_calibrator_mode(self.calibrator_selector.get())

        self.normal_calibration_frame = NormalCalibrationFrame(master = self, calibration_inst = self.calibration_inst, height=100)
        self.normal_calibration_frame.grid(row=2, column=0, padx=0, pady=0, sticky="ewn")


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
        self.left_setting_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.image_preview_frame = ImagePreviewFrame(master=self, height=100)
        self.image_preview_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")

        # add the image box frame instance to settings so the we can display the calibration process
        self.left_setting_box.set_image_box_frame(self.image_box_frame)

        # add the image preview frame to settings so we can get the image elements
        self.left_setting_box.set_preview_frame(self.image_preview_frame)
