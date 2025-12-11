import time
from picamera2 import Picamera2

# カメラの初期化
picam2 = Picamera2()

# カメラを起動して、画質調整のために2秒待つ
picam2.start()
time.sleep(2)

# 写真を撮って保存
picam2.capture_file("test.jpg")

# 終了
picam2.stop()
print("撮影完了: test.jpg")