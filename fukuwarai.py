import cv2
import numpy as np
import time
import parts as pa
import detectBlink as db

dev = 0
waiting = False
wait_start = 0

def main():                                         ##会検出器を読み込む。正面顔の検出
    face_cascade = cv2.CascadeClassifier("./learned_models/haarcascades/haarcascade_frontalface_default.xml")
    fmdetector=cv2.face.createFacemarkLBF()         ##68点のランドマーク検出器(LBF)を作成
    fmdetector.loadModel("./learned_models/lbfmodel.yaml")     ##LBFモデルを読み込む

    cap = cv2.VideoCapture(dev)                     ##カメラ起動
    # ht  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))   ##高さ(ピクセル)を取得
    # wt  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))    ##幅(ピクセル)を取得
    # fps = cap.get(cv2.CAP_PROP_FPS)                 ##fps(フレームレート)を取得

    global waiting, wait_start
    value = 0       ##瞬きしたら落下パーツを変更するためのif-elif-else文の条件value
    value_max = 6
    parts = None
    last_part_time = 0

    while cap.isOpened():                           ##カメラが正常に開いている間、繰り返す
        ret, frame = cap.read()                     ##フレーム(1枚の画像)を取得。retは成功したかを表すブール値

        if ret:     ##もし取得成功したら......
            ##顔を検出
            faces = face_cascade.detectMultiScale(frame, 1.1, 5)    ##フレームから顔を検出。1.1倍ずつスケールを変えてスキャン、5個以上の矩形が一致したら顔と認識

            for face in faces:      ##顔を1つずつ取り出す
                if value == value_max:
                    break
                ##顔の中から68点の顔の特徴を検出
                landmarks = fmdetector.fit(frame, np.array([face]))
                _,list = landmarks
                parts = np.array(list[0][0], dtype=np.int32)
                hull = cv2.convexHull(parts)        ##下のoutline_extendedとは異なり、より大きく（ざっくり）顔全体を覆える
                # outline_extended = np.concatenate([parts[0:17], parts[26:16:-1]])       ##顔の輪郭は0~16番、26~17は眉、-1は眉を逆順で接続する指定
                ##マスク画像を作成
                mask = np.zeros(frame.shape[:2], dtype=np.uint8)        ##顔輪郭の中だけを1とする
                cv2.fillPoly(mask, [hull], 255)
                ##メディアン平滑化画像を作成
                median_filtered = cv2.medianBlur(frame, 51)
                ##輪郭内だけ平滑化画像を合成
                smoothed_face = np.where(mask[:, :, np.newaxis] == 255, median_filtered, frame)

                
                ##口、左目、右目、鼻の抽出
                ##この項目をswich文で分岐させる
                if value == 0:      ##口
                    part_points = parts[48:60]
                    part_img, x0, _ = pa.extract_part_image(frame, part_points - [0,0])
                elif value == 1:    ##左目
                    part_points = parts[36:42]
                    part_img, x0, _ = pa.extract_part_image(frame, part_points - [0,0])
                elif value == 2:    ##右目
                    part_points = parts[42:48]
                    part_img, x0, _ = pa.extract_part_image(frame, part_points - [0,0])
                elif value == 3:    ##鼻
                    part_points = parts[27:36]
                    part_img, x0, _ = pa.extract_part_image(frame, part_points - [0,0])
                elif value == 4:    ##左眉
                    part_points = parts[17:22]
                    part_img, x0, _ = pa.extract_part_image(frame, part_points - [0,0])
                elif value == 5:    ##右眉
                    part_points = parts[22:27]
                    part_img, x0, _ = pa.extract_part_image(frame, part_points - [0,0])

                ##ウインクしたパーツをsmoothed_faceに合成する
                smoothed_face = pa.winkedFrame(frame, smoothed_face, parts)

                ##落下画像を合成
                falled_frame, _= pa.fall(smoothed_face, part_img, x0, waiting)

                ##合成結果を表示
                cv2.imshow("fukuwarai", falled_frame)

        ##ウインクしたらパーツ画像が静止する
        if not waiting and parts is not None:
            if db.boolBlink(frame, parts - [0,0]):
                if time.time() - last_part_time > 2.0:      ##1.5秒以上経過していたら進める
                    # pa.addPointsList(part_points, fall_y, x0)
                    if value == 0:
                        pa.addPointsList(48, 60, x0)
                    elif value == 1:
                        pa.addPointsList(36, 42, x0)
                    elif value == 2:
                        pa.addPointsList(42, 48, x0)
                    elif value == 3:
                        pa.addPointsList(27, 36, x0)
                    elif value == 4:
                        pa.addPointsList(17, 22, x0)
                    elif value == 5:
                        pa.addPointsList(22, 27, x0)
                    waiting = True      ##待機状態に入る
                    wait_start = time.time()        ##待機開始時間を記録
                
        ##パーツ静止後、待機時間が経過したら次のパーツへ
        if waiting and (time.time() - wait_start > 2.0):
            if value != value_max:
                value += 1
            waiting = False     ##待機終了

        ##全てのパーツを合成したら、パーツの落下を停止し、写真を出力する
        if value == value_max:
            cv2.imshow("completed", falled_frame)
            cv2.imwrite("./img/completed.jpg", falled_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cap.release()

if __name__ == '__main__':
    main()