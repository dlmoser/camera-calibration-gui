import numpy as np
import customtkinter as ctk
import setting_manager as sm
from tkinter import filedialog
import os
import glob
from PIL import Image

class ColorSweep():
    def __init__(self, start_color, end_color):
        self.start_color = np.array(start_color)
        self.end_color = np.array(end_color)
        self.d = self.start_color
        self.k = self.end_color-self.start_color
        
    def get_color(self, x):
        return self.d + x*self.k
    
    def get_color_hex(self, x):
        c = self.get_color(x).astype(int).tolist()
        return '#%02X%02X%02X' % (c[0],c[1],c[2])
    


class LoadingAnimation(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.x = 0

        self.cs = ColorSweep([255,255,255], [0,0,255])
        # ctk.CTkLabel(master=self, text="Loading...").pack(side="left", fill="x", expand=1, padx=5, pady=5)

        self.center_frame = ctk.CTkFrame(master=self, fg_color="transparent", height=100, width=200, corner_radius=10)
        self.center_frame.pack(expand=1, padx=5, pady=5)

        ctk.CTkLabel(master=self.center_frame, text = "Loading...", height=30, width=27, corner_radius=20).grid(row=0, column=0, padx=10, pady=10)

        self.animation_frame = ctk.CTkFrame(master=self.center_frame, fg_color="transparent", height=100, width=200, corner_radius=10)
        self.animation_frame.grid(row=1, column=0, padx=10, pady=10)

        self.loading_ball_list = []
        for i in range(10):
            lading_ball = ctk.CTkFrame(master=self.animation_frame, fg_color="#ffffff", height=10, width=10, corner_radius=10)
            lading_ball.grid(row=1, column=i, padx=10, pady=10)
            self.loading_ball_list.append(lading_ball)

        self.animate()

    def animate(self):
        self.x += 0.01
        if self.x > 1:
            self.x = 0
        x_array = (np.linspace(0,1,len(self.loading_ball_list))+self.x)%1
        color_array = [self.cs.get_color_hex(x) for x in x_array]
        for elem in self.loading_ball_list:
            elem.configure(fg_color=color_array.pop())
        self.after(10, self.animate)


        


class SelectSaveFolderFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.grid_rowconfigure((0), weight=2)
        self.grid_rowconfigure((0,1,2,3), weight=1)
        # self.grid_rowconfigure((), weight=2)
        self.grid_columnconfigure((0), weight=0)
        self.grid_columnconfigure((1), weight=5)

        ctk.CTkButton(master=self, text="Select Image Save Folder",  height=10, command=self.select_image_save_folder).grid(row=0, column=0, columnspan=2, padx=10, pady=(15,0), sticky="news")

        ctk.CTkLabel(master=self, text="Folder: ", height=20).grid(row=1, column=0, padx=10, pady=(10,0), sticky="nws")
        self.selected_save_folder_label = ctk.CTkLabel(master=self, height=15)
        self.selected_save_folder_label.grid(row=1, column=1, padx=10, pady=0, sticky="nws")

        
        ctk.CTkLabel(master=self, text="Image Number: ", height=20).grid(row=2, column=0, padx=10, pady=(0,10), sticky="nws")
        ctk.CTkLabel(master=self, textvariable = sm.setting_dict["number_of_images_in_folder"], height=15).grid(row=2, column=1, padx=10, pady=(0,10), sticky="w")


        # trace when selected_image_save_folder variable is changed to adapt the label and the save button mode
        sm.setting_dict["selected_image_save_folder"].trace('w', self.write_image_folder_variable)

        self.write_image_folder_variable()


    def write_image_folder_variable(self, *args):
        selected_folder = sm.setting_dict["selected_image_save_folder"].get()
        if os.path.isdir(selected_folder):
            print("split folder", os.path.split(selected_folder))
            self.selected_save_folder_label.configure(text=os.path.split(selected_folder)[-1])
            # selected_folder = self.master.master.selected_image_save_folder.set(selected_folder)
        else:
            self.selected_save_folder_label.configure(text="-")

    
    def select_image_save_folder(self):
        sm.setting_dict["selected_image_save_folder"].set(filedialog.askdirectory())




class ImagePreviewFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, orientation="horizontal", **kwargs)
        self.master = master
        self.image_labels = []

        self.check_for_images_in_folder()

    def check_for_images_in_folder(self):
        try:
            self.images_in_folder = sorted(glob.glob(os.path.join(sm.setting_dict["selected_image_save_folder"].get(), "*.png")))
            sm.setting_dict["number_of_images_in_folder"].set(len(self.images_in_folder))
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
        self.images_in_folder = sorted(glob.glob(os.path.join(sm.setting_dict["selected_image_save_folder"].get(), "*.png")))
        self.update_image_preview()