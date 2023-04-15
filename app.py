import customtkinter as ctk
from tkinter import filedialog
import glob
import os
from PIL import Image
import numpy as np

from cam_video_stream import CamStream
from camera_calibration.find_chessboard_corners import find_chessboard_corners


# Supported themes: green, dark-blue, blue
ctk.set_appearance_mode("dark")


class LeftSettingBox(ctk.CTkFrame):
    def __init__(self, cam_inst, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.cam_inst = cam_inst

        self.master.selected_save_folder = None

        self.grid_rowconfigure((0,1), weight=0)
        self.grid_rowconfigure((4), weight=1)
        self.grid_columnconfigure((0), weight=1)

        ctk.CTkLabel(master=self, text="Select Camera").grid(row=0, column=0, padx=5, pady=5, sticky="ewn")

        available_cams, selected_cam = self.cam_inst.scan_for_available_cameras()
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
        self.selected_save_folder_label = ctk.CTkLabel(master=self, text="No Folder Selected")
        self.selected_save_folder_label.grid(row=5, column=0, padx=5, pady=5, sticky="ewn")

        
        self.save_image_button = ctk.CTkButton(master=self, text="Save Image", command=self.save_image)
        self.save_image_button.grid(row=6, column=0, padx=5, pady=5, sticky="ews")
        self.save_image_button.configure(state="disabled")
        self.save_image_button.configure(fg_color="grey")


    def select_image_save_folder(self):
        folder_selected = filedialog.askdirectory()
        print("folder selected: ", folder_selected)    
        if folder_selected == "":
            self.master.selected_save_folder = None
            self.selected_save_folder_label.configure(text="No Folder Selected")
            print("write error dialog")

            # disable save button
            self.save_image_button.configure(state="disabled")
            self.save_image_button.configure(fg_color="grey")
        else:
            self.selected_save_folder_label.configure(text=os.path.split(folder_selected)[-1])
            self.master.selected_save_folder = folder_selected

            # enable save button 
            self.save_image_button.configure(state = "normal") 
            self.save_image_button.configure(fg_color = ['#3B8ED0', '#1F6AA5'])
        
    def save_image(self):
        print("get_images_in_folder", self.get_images_in_folder())
        images_in_folder = self.get_images_in_folder()
        if len(images_in_folder) == 0:
            image_name = "image_001.png"

        else:
            last_image = images_in_folder[-1]
            last_image_name = os.path.split(last_image)[-1]
            last_image_number = int(last_image_name.split("_")[-1].split(".")[0])
            new_image_number = last_image_number + 1
            image_name = "image_{:03d}.png".format(new_image_number)
            print("image_name", image_name)

        Image.fromarray(self.cam_inst.frame).save(os.path.join(self.master.selected_save_folder, image_name))
        

    def get_images_in_folder(self):
        return sorted(glob.glob(os.path.join(self.master.selected_save_folder, "*.png")))




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
                frame = find_chessboard_corners(self.cam_inst.frame.copy())
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
            self.images_in_folder = sorted(glob.glob(os.path.join(self.master.selected_save_folder, "*.png")))
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
        self.images_in_folder = sorted(glob.glob(os.path.join(self.master.selected_save_folder, "*.png")))
        self.update_image_preview()




class ImageRecordingFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.cam_inst = CamStream()

        self.grid_rowconfigure((0), weight=4)
        self.grid_rowconfigure((1), weight=1)
        self.grid_columnconfigure((0), weight=1)
        self.grid_columnconfigure((1), weight=4)

        self.image_box_frame = ImageBoxFrame(master=self, cam_inst=self.cam_inst)
        self.image_box_frame.grid(row=0, column=1, padx=(0,10), pady=10, sticky="nsew")

        self.left_setting_box = LeftSettingBox(master=self, cam_inst=self.cam_inst)
        self.left_setting_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ImagePreviewFrame(master=self, height=100).grid(row=1, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")

    def button_callback(self):
        self.textbox.insert("insert", self.combobox.get() + "\n")

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
     