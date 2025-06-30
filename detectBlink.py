#[ipbk1]顔検出プログラム応用
import cv2
import numpy as np


def boolBlink(frame, parts):
    bool = 0
  #######まばたき検出#######（ドライアイなので口閉じに変更）
    # blink = abs((parts[47][1]-parts[43][1])/(parts[45][0]-parts[42][0]))
    blink = abs((parts[66][1]-parts[62][1])/(parts[54][0]-parts[48][0]))
    if blink <= 0.05:
        bool = 1
        print("eye-close(",bool,")")
    return bool