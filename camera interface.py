import cv2

cam = cv2.VideoCapture(0)


while True:

    a, img = cam.read()
    
    cv2.imshow("Frame", img)
    key = cv2.waitKey(1)
    print(key)
    if(key == ord('q')):

        cv2.imwrite("imag1.png",img)
        break

cam.release()
cv2.destroyAllWindows()
