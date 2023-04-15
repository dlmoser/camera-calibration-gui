import cv2
import numpy as np
import time




def find_chessboard_corners(img):
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

if __name__ == "__main__":
    img_path = "/Users/davidmoser/Downloads/test_save_folder/image_004.png"

    img = cv2.imread(img_path)
    img = find_chessboard_corners(img)

    cv2.imshow("aaa", img)
    cv2.waitKey(0)
