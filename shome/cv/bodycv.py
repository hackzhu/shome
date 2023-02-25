#!/usr/bin/env python
import cv2


def main():
    i = 0
    camera = cv2.VideoCapture('/home/zhu/sync/code/shome/test/body/9.mp4')
    classfier = cv2.CascadeClassifier("haarcascades/haarcascade_upperbody.xml")
    while camera.isOpened():
        success, frame = camera.read()
        if success:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            bodys = classfier.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 150))
            for body in bodys:
                x, y, w, h = body
                cv2.rectangle(frame, (x - 10, y - 10),
                              (x + w + 10, y + h + 10), (0, 255, 0), 1)
                print(i)
                i += 1
            cv2.imshow('frame', frame)

            k = cv2.waitKey(1)
            if k == 27:
                cv2.destroyAllWindows()
                break


if __name__ == '__main__':
    main()
