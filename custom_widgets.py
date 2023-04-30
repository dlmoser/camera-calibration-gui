import numpy as np
import customtkinter as ctk


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


        
