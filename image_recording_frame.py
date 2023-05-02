import customtkinter as ctk
from tkinter import filedialog
import os
import glob
from PIL import Image
import numpy as np
import threading


from cam_video_stream import CamStream
from camera_calibration.find_chessboard_corners import find_and_draw_chessboard_corners
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

        ctk.CTkLabel(master=self, text="Detect Calibration Object").grid(row=2, column=0, padx=5, pady=5, sticky="ewn")
        self.master.calibration_detector_selector = ctk.CTkComboBox(master=self,values=["No Detector", "Chessboard"])
        self.master.calibration_detector_selector.grid(row=3, column=0, padx=5, pady=5, sticky="ewn")


        ctk.CTkButton(master=self, text="Select Image Save Folder", command=self.select_image_save_folder).grid(row=4, column=0, padx=5, pady=5, sticky="ews")
        self.selected_save_folder_label = ctk.CTkLabel(master=self, text="")
        self.selected_save_folder_label.grid(row=5, column=0, padx=5, pady=5, sticky="ewn")

        # trace when selected_image_save_folder variable is changed to adapt the label and the save button mode
        self.master.master.selected_image_save_folder.trace('w', self.write_image_folder_variable)


        self.save_image_button = ctk.CTkButton(master=self, text="Save Image", command=self.save_image)
        self.save_image_button.grid(row=6, column=0, padx=5, pady=5, sticky="ews")
        self.save_image_button.configure(state="disabled")
        self.save_image_button.configure(fg_color="grey")

        # call the function once to set the init value
        self.write_image_folder_variable()


    def write_image_folder_variable(self, *args):
        selected_folder = self.master.master.selected_image_save_folder.get()
        if os.path.isdir(selected_folder):
            self.selected_save_folder_label.configure(text=os.path.split(selected_folder)[-1])
            # selected_folder = self.master.master.selected_image_save_folder.set(selected_folder)
            self.save_image_button.configure(state = "normal") 
            self.save_image_button.configure(fg_color = ['#3B8ED0', '#1F6AA5'])
        else:
            self.selected_save_folder_label.configure(text="No Folder Selected")
            self.save_image_button.configure(state="disabled")
            self.save_image_button.configure(fg_color="grey")


    def select_image_save_folder(self):
        folder_selected = filedialog.askdirectory()
        print("folder selected: ", folder_selected)    
        self.master.master.selected_image_save_folder.set(folder_selected)

        
    def save_image(self):
        def save_image_thread():
            images_in_folder = self.get_images_in_folder()
            if len(images_in_folder) == 0:
                image_name = "image_001.png"
            else:
                last_image = images_in_folder[-1]
                last_image_name = os.path.split(last_image)[-1]
                last_image_number = int(last_image_name.split("_")[-1].split(".")[0])
                new_image_number = last_image_number + 1
                image_name = "image_{:03d}.png".format(new_image_number)

            img_save_path = os.path.join(self.master.master.selected_image_save_folder.get(), image_name)
            print("Save Image: ", img_save_path)
            Image.fromarray(self.cam_inst.frame.copy()).save(img_save_path)
        threading.Thread(target=save_image_thread).start()
        print("here")
        

    def get_images_in_folder(self):
        return sorted(glob.glob(os.path.join(self.master.master.selected_image_save_folder.get(), "*.png")))




class ImageBoxFrame(ctk.CTkFrame):
    def __init__(self, cam_inst, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.cam_inst = cam_inst
        self.current_size = None

        self.bind('<Configure>', self.resizer)

        self.current_frame = Image.fromarray(np.ones((100,int(100*1.25)), np.uint8)*255)

        self.image_label = ctk.CTkLabel(self, text = "")
        self.image_label.pack(fill = "both", expand = True, anchor="center")

        self.update_image()

    def update_image(self):
        if self.current_size is not None:
            if "No Detector" == self.master.calibration_detector_selector.get():
                frame = self.cam_inst.frame.copy()
            elif "Chessboard" == self.master.calibration_detector_selector.get():
                frame = find_and_draw_chessboard_corners(self.cam_inst.frame.copy())
            self.current_frame = Image.fromarray(frame)
            display_frame = ctk.CTkImage(dark_image = self.current_frame, size=self.current_size)
            self.image_label.configure(image=display_frame)
        self.after(30, self.update_image)



    def resizer(self, e):
        print("resize")
        self.current_size = (e.width,e.height)
        img = ctk.CTkImage(dark_image=self.current_frame, size=self.current_size)
        self.image_label.configure(image=img)


        

class ImagePreviewFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, orientation="horizontal", **kwargs)
        self.master = master
        self.image_labels = []

        self.check_for_images_in_folder()


    def check_for_images_in_folder(self):
        try:
            self.images_in_folder = sorted(glob.glob(os.path.join(self.master.master.selected_image_save_folder.get(), "*.png")))
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
        os.remove(img_path)
        self.images_in_folder = sorted(glob.glob(os.path.join(self.master.master.selected_image_save_folder.get(), "*.png")))
        self.update_image_preview()




class ImageRecordingFrame(ctk.CTkFrame):
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
        
        ImagePreviewFrame(master=self, height=100).grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")
    
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


