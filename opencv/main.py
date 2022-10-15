import cv2

# 首先读取config文件，第一行代表当前已经储存的人名个数，接下来每一行是（id，name）标签和对应的人名
id_dict = {}  # 字典里存的是id——name键值对
Total_face_num = 999  # 已经被识别有用户名的人脸个数,


def init():  # 将config文件内的信息读入到字典中
    f = open('config.txt')
    global Total_face_num
    Total_face_num = int(f.readline())

    for i in range(int(Total_face_num)):
        line = f.readline()
        id_name = line.split(' ')
        id_dict[int(id_name[0])] = id_name[1]
    f.close()


init()

# 加载OpenCV人脸检测分类器Haar
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# 准备好识别方法LBPH方法
recognizer = cv2.face.LBPHFaceRecognizer_create()

# 打开标号为0的摄像头
camera = cv2.VideoCapture(0)  # 摄像头
success, img = camera.read()  # 从摄像头读取照片
W_size = 0.1 * camera.get(3)
H_size = 0.1 * camera.get(4)  # 获取视频流的帧的高和宽


def scan_face():
    # 使用之前训练好的模型
    for i in range(Total_face_num):  # 每个识别器都要用
        i += 1
        yml = str(i) + ".yml"
        print("本次:" + yml)  # 调试信息
        recognizer.read(yml)

        ave_poss = 0
        for times in range(10):  # 每个识别器扫描十遍
            times += 1
            cur_poss = 0
            global success
            global img

            success, img = camera.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 识别人脸
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.2, minNeighbors=5, minSize=(int(W_size), int(H_size)))
            # 进行校验
            for (x, y, w, h) in faces:
                # 调用分类器的预测函数，接收返回值标签和置信度
                idnum, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                conf = confidence
                # 计算出一个检验结果

                if 15 > conf > 0:
                    cur_poss = 1  # 表示可以识别
                elif 60 > conf > 35:
                    cur_poss = 1  # 表示可以识别
                else:
                    cur_poss = 0  # 表示不可以识别

            ave_poss += cur_poss

        if ave_poss >= 5:  # 有一半以上识别说明可行则返回
            return i

    return 0  # 全部过一遍还没识别出说明无法识别


def f_scan_face_thread():
    # 使用之前训练好的模型
    # recognizer.read('aaa.yml')
    print('\n开始刷脸')
    ans = scan_face()
    if ans == 0:
        print("最终结果：无法识别")

    else:
        ans_name = "最终结果：" + str(ans) + id_dict[ans]
        print(ans_name)


while 1:
    f_scan_face_thread()
