import cv2
import numpy as np
import time



class ChessboardCalibrator():
    calibrator_list = ["normal", "fisheye"]

    def __init__(self, chessboard_patter = (9,6), claibration_mode = "normal"):
        self.chessboard_pattern = chessboard_patter
        self.init_object_and_image_points()
        self.chessboard_patter = chessboard_patter
        self.calibration_mode = claibration_mode


    def get_calibrator_list(self):
        return self.calibrator_list

    def init_object_and_image_points(self):
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        self.objp = np.zeros((self.chessboard_pattern[0]*self.chessboard_pattern[1],3), np.float32)
        self.objp[:,:2] = np.mgrid[0:self.chessboard_pattern[0],0:self.chessboard_pattern[1]].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images.
        self.objpoints = [] # 3d point in real world space
        self.imgpoints = [] # 2d points in image plane.


    def set_calibrator_mode(self, mode):
        self.calibration_mode = mode
        if mode == "normal":
            self.normal_calibration_inst = NormalCalibrator()
        elif mode == "fisheye":
            print("fisheye not implemented yet")
        else:
            print("unknown calibration mode")


    def find_chessboard_corners_in_image(self, image_path):
        img = cv2.imread(image_path)
        self.img_shapexy = img.shape[:2][::-1]
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray_img, self.chessboard_patter)

        # If found, add object points, image points (after refining them)
        if ret == True:
            self.objpoints.append(self.objp)
            corners2 = cv2.cornerSubPix(gray_img, corners, (11,11), (-1,-1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            self.imgpoints.append(corners2)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, self.chessboard_patter, corners2, ret)

        return ret, img


    def calculate_calibration_matrix(self):
        if self.calibration_mode == "normal":
            self.map1, self.map2 = self.normal_calibration_inst.calculate_calibration_matrix(self.objpoints, self.imgpoints, self.img_shapexy)


    def undistort_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.remap(img, self.map1, self.map2, cv2.INTER_LINEAR)
        return img


    # def start_normal_calibration(self, img_path_list):
    #     print("img_path_list", img_path_list)

    
        
    # for img_path in img_path_list:
    #     img = cv2.imread(img_path)
    #     gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # ret, corners = cv2.findChessboardCorners(gray_img, corner_layout)

        # # If found, add object points, image points (after refining them)
        # if ret == True:
        #     objpoints.append(objp)
        #     corners2 = cv2.cornerSubPix(gray_img, corners, (11,11), (-1,-1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        #     imgpoints.append(corners2)
        #     # Draw and display the corners
        #     cv2.drawChessboardCorners(img, corner_layout, corners2, ret)
        #     cv2.imshow('img', img)
        #     cv2.waitKey(50)


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
    

                         
    def __init__(self):
        self.selected_calibration_flags = 0

    def get_available_flags_names(self):
        return list(self.calibration_flag_dict.keys())
    

    def set_calibration_flags(self, select_flag_list):
        for flag_sting in select_flag_list:
            if flag_sting in self.get_available_flags_names():
                self.selected_calibration_flags += self.calibration_flag_dict[flag_sting]
            else:
                print("Warning: flag {} not known".format(flag_sting))


    def calculate_calibration_matrix(self, objpoints, imgpoints, img_shapexy):
        self.img_shape_xy = img_shapexy
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
