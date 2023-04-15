import os

# import the necessary packages
import threading
import cv2
import time
import glob
import PIL
from PIL import Image, ImageTk
import numpy as np


class CamStream:
    def __init__(self):

        self.stream = None
        self.stop_all = False
        self.available_cams = []
        self.selected_cam = None
        self.set_fake_frame()
    

    def cam_changed(self, select_cam_name):
        self.stop_stream()
        for cam_name, idx in self.available_cams:
            if cam_name == select_cam_name:
                self.selected_cam = idx
        self.start_stream()


    def scan_for_available_cameras(self):
        # scan the first 10 idx and check if there is a camera behind
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cam_name = f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}[px], {int(cap.get(cv2.CAP_PROP_FPS))}[fps]"
                self.available_cams.append([cam_name, i])
        # select the first cam as default
        if len(self.available_cams) >= 1:
            self.selected_cam = 0
        return self.available_cams, self.selected_cam

    def create(self):
        try:
            self.stream = cv2.VideoCapture(self.selected_cam)
            flag, _ = self.stream.read()
            if flag == False:
                raise
            print("CAMSTREAM: {} detected".format(self.selected_cam))
            time.sleep(1)
            return self
        except:
            print("WARNING: CAMSTREAM: {} seems not to work".format(self.selected_cam))
            return None

    def display_image(self):
        if self.stream == None:
            self.stream = cv2.VideoCapture(self.selected_cam)
        _, frame  = self.stream.read()
        	# Convert image from one color space to other
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        render = numpy_to_tkimg(image)

        self.img_label.photo_image = render

	    # Configure image in the label
        self.img_label.configure(image=render)
        self.img_label.image = render
        self.img_label.update()
        self.img_label.after(10, self.display_image)


    def start_stream(self):
        print("start stream loop")
        self.stop_all = False
        self.stream_thread = threading.Thread(target=self.stream_loop)
        self.stream_thread.start()
        time.sleep(1)

    def stream_loop(self):
        self.create()
        while True:
            if self.stop_all == True:
                break
            _, frame = self.stream.read()

            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)    
        self.stream.release()
        self.stream = None
        self.set_fake_frame()

    def stop_stream(self):
        try:
            self.stop_all = True
            self.stream_thread.join()
            print("stopped stream thread")
        except:
            pass

    def set_fake_frame(self):
        self.frame = np.ones((100,int(100*1.25), 3), np.uint8)

    def get_resolution(self):
        cam1_res = (self.stream.get(cv2.CAP_PROP_FRAME_WIDTH),
                    self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return cam1_res

    def set_resolution(self, resolution):
        width, height = resolution
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def grap_frame(self):
        self.retval_g = self.stream.grab()

    def retrieve_frame(self):
        self.retval_r, self.frame = self.stream.retrieve()

    def read_frame(self):
        (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def set_h264(self):
        codec = 1196444237.0  # MJPG
        codec = 844715353.0  # YUY2
        self.stream.set(cv2.CAP_PROP_FOURCC, codec)

    def print_all_infos(self):
        print('cv2.CAP_PROP_POS_MSEC: {}'.format(self.stream.get(cv2.CAP_PROP_POS_MSEC)))
        print('cv2.CAP_PROP_POS_FRAMES: {}'.format(self.stream.get(cv2.CAP_PROP_POS_FRAMES)))
        print('cv2.CAP_PROP_POS_AVI_RATIO: {}'.format(self.stream.get(cv2.CAP_PROP_POS_AVI_RATIO)))
        print('cv2.CAP_PROP_FRAME_WIDTH: {}'.format(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print('cv2.CAP_PROP_FRAME_HEIGHT: {}'.format(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print('cv2.CAP_PROP_FPS: {}'.format(self.stream.get(cv2.CAP_PROP_FPS)))
        print('cv2.CAP_PROP_FOURCC: {}'.format(self.stream.get(cv2.CAP_PROP_FOURCC)))
        print('cv2.CAP_PROP_FRAME_COUNT: {}'.format(self.stream.get(cv2.CAP_PROP_FRAME_COUNT)))
        print('cv2.CAP_PROP_FORMAT: {}'.format(self.stream.get(cv2.CAP_PROP_FORMAT)))
        print('cv2.CAP_PROP_MODE: {}'.format(self.stream.get(cv2.CAP_PROP_MODE)))
        print('cv2.CAP_PROP_BRIGHTNESS: {}'.format(self.stream.get(cv2.CAP_PROP_BRIGHTNESS)))
        print('cv2.CAP_PROP_CONTRAST: {}'.format(self.stream.get(cv2.CAP_PROP_CONTRAST)))
        print('cv2.CAP_PROP_SATURATION: {}'.format(self.stream.get(cv2.CAP_PROP_SATURATION)))
        print('cv2.CAP_PROP_HUE: {}'.format(self.stream.get(cv2.CAP_PROP_HUE)))
        print('cv2.CAP_PROP_GAIN: {}'.format(self.stream.get(cv2.CAP_PROP_GAIN)))
        print('cv2.CAP_PROP_EXPOSURE: {}'.format(self.stream.get(cv2.CAP_PROP_EXPOSURE)))
        print('cv2.CAP_PROP_CONVERT_RGB: {}'.format(self.stream.get(cv2.CAP_PROP_CONVERT_RGB)))
    #    print('cv2.CAP_PROP_WHITE_BALANCE_U: {}'.format(
    #        self.stream.get(cv2.CAP_PROP_WHITE_BALANCE_U)))
    #    print('cv2.CAP_PROP_WHITE_BALANCE_V: {}'.format(
    #        self.stream.get(cv2.CAP_PROP_WHITE_BALANCE_V)))
        print('cv2.CAP_PROP_ISO_SPEED: {}'.format(self.stream.get(cv2.CAP_PROP_ISO_SPEED)))
        print('cv2.CAP_PROP_BUFFERSIZE: {}'.format(self.stream.get(cv2.CAP_PROP_BUFFERSIZE)))


def test():
    cam = CamStream().create()
    print(cam.get_resolution())
    cam.print_all_infos()


def numpy_to_tkimg(img_npy):
    img = PIL.Image.fromarray(img_npy)
    return ImageTk.PhotoImage(image=img)


if __name__ == '__main__':
    cam = CamStream()
    cam.scan_for_available_cameras()
    print("available_cams", cam.available_cams)