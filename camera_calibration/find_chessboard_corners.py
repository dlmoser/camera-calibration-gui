import cv2
import numpy as np
import time
import glob




class NormalCalibrator():

    calibration_flag_dict = {"USE_INTRINSIC_GUESS": cv2.CALIB_USE_INTRINSIC_GUESS,
                                "FIX_PRINCIPAL_POINT": cv2.CALIB_FIX_PRINCIPAL_POINT,
                                "FIX_ASPECT_RATIO": cv2.CALIB_FIX_ASPECT_RATIO,
                                "ZERO_TANGENT_DIST": cv2.CALIB_ZERO_TANGENT_DIST,
                                "FIX_K1": cv2.CALIB_FIX_K1,
                                "FIX_K2": cv2.CALIB_FIX_K2,
                                "FIX_K3": cv2.CALIB_FIX_K3,
                                "FIX_K4": cv2.CALIB_FIX_K4,
                                "FIX_K5": cv2.CALIB_FIX_K5,
                                "FIX_K6": cv2.CALIB_FIX_K6,
                                "RATIONAL_MODEL": cv2.CALIB_RATIONAL_MODEL,
                                "THIN_PRISM_MODEL": cv2.CALIB_THIN_PRISM_MODEL,
                                "FIX_S1_S2_S3_S4": cv2.CALIB_FIX_S1_S2_S3_S4,
                                "TILTED_MODEL": cv2.CALIB_TILTED_MODEL,
                                "FIX_TAUX_TAUY": cv2.CALIB_FIX_TAUX_TAUY}
    

                         
    def __init__(self, img_shapeyx):
        self.selected_calibration_flags = 0
        self.img_shape_xy = img_shapeyx[::-1]

    def get_available_flags_names(self):
        return list(self.calibration_flag_dict.keys())
    

    def set_calibration_flags(self, select_flag_list):
        for flag_sting in select_flag_list:
            if flag_sting in self.get_available_flags_names():
                self.selected_calibration_flags += self.calibration_flag_dict[flag_sting]
            else:
                print("Warning: flag {} not known".format(flag_sting))


    def calculate_calibration_matrix(self, objpoints, imgpoints):
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(objpoints, 
                                                                                    imgpoints,
                                                                                    self.img_shape_xy, 
                                                                                    None, 
                                                                                    None, 
                                                                                    flags=self.selected_calibration_flags)
        
        self.Knew, self.ROI = cv2.getOptimalNewCameraMatrix(self.mtx, 
                                                            self.dist, 
                                                            self.img_shape_xy,
                                                            1, 
                                                            self.img_shape_xy)
        
    
        self.map1, self.map2 = cv2.initUndistortRectifyMap(self.mtx, 
                                                           self.dist, 
                                                           None, 
                                                           self.Knew, 
                                                           self.img_shape_xy, 
                                                           cv2.CV_16SC2)
        
        return self.map1, self.map2



class ChessboardCalibrator():

    def __init__(self, chessbord_patter = (9,6), claibration_mode = "normal"):
        self.chessboard_pattern = chessbord_patter
        self.init_object_and_image_points()
        
        self.calibration_mode = claibration_mode


    def init_object_and_image_points(self):
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((self.chessboard_pattern[0]*self.chessboard_pattern[1],3), np.float32)
        objp[:,:2] = np.mgrid[0:self.chessboard_pattern[0],0:self.chessboard_pattern[1]].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images.
        self.objpoints = [] # 3d point in real world space
        self.imgpoints = [] # 2d points in image plane.

    # for img_path in img_path_list:
    #     img = cv2.imread(img_path)
    #     gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #     ret, corners = cv2.findChessboardCorners(gray_img, corner_layout)

    #     # If found, add object points, image points (after refining them)
    #     if ret == True:
    #         objpoints.append(objp)
    #         corners2 = cv2.cornerSubPix(gray_img, corners, (11,11), (-1,-1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
    #         imgpoints.append(corners2)
    #         # Draw and display the corners
    #         cv2.drawChessboardCorners(img, corner_layout, corners2, ret)
    #         cv2.imshow('img', img)
    #         cv2.waitKey(50)


class normal_calibrater():
    calibration_flags = ['USE_INTRINSIC_GUESS', 'FIX_PRINCIPAL_POINT', 'FIX_ASPECT_RATIO',  'ZERO_TANGENT_DIST', 'FIX_K1', 'FIX_K2', 'FIX_K3',
                         'FIX_K4', 'FIX_K5', 'FIX_K6', 'RATIONAL_MODEL', 'THIN_PRISM_MODEL', 'FIX_S1_S2_S3_S4', 'TILTED_MODEL', 'FIX_TAUX_TAUY']
    new_camera_matrix_args = {
        'R': [0, 0, 0], 'new_size': ['i_r', 'i_c'], 'alpha': 0.5, "new_shift": [0, 0]}

    def __init__(self, images):
        super().__init__(images)
        self.new_camera_matrix_args = fisheye_calibrater.new_camera_matrix_args.copy()

    def set_calibration_flags(self, select_flag_list):
        if self.status < 0:
            return
        try:
            for cf, sfl in zip(self.calibration_flags, select_flag_list):
                if sfl == True:
                    self.selected_calibraiton_flags += eval('cv2.CALIB_' + cf)
        except Exception as e:
            self.status = -1
            print("Error in set_calibration_flags: {}".format(e))

    def set_new_cameramatrix_settings(self, select_setting_list):
        if self.status < 0:
            return
        try:
            self.new_camera_matrix_args['R'] = Rrpy(
                roll=float(select_setting_list['R']['roll']), pitch=float(select_setting_list['R']['pitch']), yaw=float(select_setting_list['R']['yaw']), mode='degree')
            if select_setting_list['new_size']['row'] == 'i_r':
                self.new_camera_matrix_args['new_size'][1] = self.img_shape_flip[1]
            else:
                self.new_camera_matrix_args['new_size'][1] = int(
                    select_setting_list['new_size']['row'])
            if select_setting_list['new_size']['column'] == 'i_c':
                self.new_camera_matrix_args['new_size'][0] = self.img_shape_flip[0]
            else:
                self.new_camera_matrix_args['new_size'][0] = int(
                    select_setting_list['new_size']['column'])

            self.new_camera_matrix_args['new_size'] = tuple(self.new_camera_matrix_args['new_size'])
            self.new_camera_matrix_args['alpha'] = float(select_setting_list['alpha'])
        except Exception as e:
            self.status = -1
            print("Error in set_new_cameramatrix_settings: {}".format(e))

    def calc_calibration_matrix(self):
        try:
            self.init_parameter()
            self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(
                self.objpoints, self.imgpoints, self.img_shape_flip, None, None, flags=self.selected_calibraiton_flags)

            self.Knew, self.ROI = cv2.getOptimalNewCameraMatrix(
                self.mtx, self.dist, self.img_shape_flip, self.new_camera_matrix_args['alpha'], self.img_shape_flip)

            self.map1, self.map2 = cv2.initUndistortRectifyMap(
                self.mtx, self.dist, self.new_camera_matrix_args['R'], self.Knew, self.new_camera_matrix_args['new_size'], cv2.CV_16SC2)
        except Exception as e:
            self.status = -4
            print("Error in calc_calibration_matrix: {}".format(e))



def find_and_draw_chessboard_corners(img):
    print("img.shape", img.shape)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img_shape = gray.shape[:2]
    # gray = cv2.resize(gray, (int(img_shape[1]/2), int(img_shape[0]/2)))
    print("gray.shape", gray.shape)
    t1 = time.time()
    ret, corners = cv2.findChessboardCorners(gray, (9,6),flags=cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    t2 = time.time()
    print("delta time", t2-t1, ret)
    if ret == True:
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (9,6), corners,ret)

    return img

def find_chessboard_corners(img_path_list, corner_layout = (9,6)):

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((9*6,3), np.float32)
    objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.




    for img_path in img_path_list:
        img = cv2.imread(img_path)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray_img, corner_layout)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray_img, corners, (11,11), (-1,-1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            imgpoints.append(corners2)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, corner_layout, corners2, ret)
            cv2.imshow('img', img)
            cv2.waitKey(50)



    calibration_inst = NormalCalibrator(img_shapeyx=img.shape[:2])
    flag_list = calibration_inst.get_available_flags_names()
    # calibration_inst.set_calibration_flags(flag_list)
    map1, map2 = calibration_inst.calculate_calibration_matrix(objpoints=objpoints, imgpoints=imgpoints)

    for img_path in img_path_list:
        print("remap")
        img = cv2.imread(img_path)
        img = cv2.remap(img, map1, map2, cv2.INTER_LINEAR)
        cv2.imshow('img', img)
        cv2.waitKey(0)


if __name__ == "__main__":
    
    import customtkinter, tkinter

    app = customtkinter.CTk()
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    # create scrollable textbox
    tk_textbox = tkinter.Text(app, highlightthickness=0)
    tk_textbox.grid(row=0, column=0, sticky="nsew")

    # create CTk scrollbar
    ctk_textbox_scrollbar = customtkinter.CTkScrollbar(app, command=tk_textbox.yview)
    ctk_textbox_scrollbar.grid(row=0, column=1, sticky="ns")

    # connect textbox scroll event to CTk scrollbar
    tk_textbox.configure(yscrollcommand=ctk_textbox_scrollbar.set)

    app.mainloop()


    # img_path = "/Users/davidmoser/Downloads/test_save_folder/*.png"

    # img_path_list = sorted(glob.glob(img_path))

    # find_chessboard_corners(img_path_list)

    # print("len img", len(img_path_list))
    # print(img_path_list)
    # img = cv2.imread(img_path)
    # img = find_chessboard_corners(img)

    # cv2.imshow("aaa", img)
    # cv2.waitKey(0)
