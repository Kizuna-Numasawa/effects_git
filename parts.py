import cv2
import numpy as np

fall_y = 0                  ##落下中のパーツの左端のy軸上での位置
                            # #fall関数内に書くと、繰り返しで毎回初期化されるため、グローバル変数にしている
winkedPointsList = []


def extract_part_image(frame, part_points):
    x,y,w,h = cv2.boundingRect(part_points)     ##boundingRect()：輪郭を囲む最小の矩形のこと
    mask = np.zeros_like(frame[:, :, 0])
    cv2.fillPoly(mask, [part_points], 255)      ##fillPoly()：指定したポリゴンの内部を塗りつぶす。→maskのpart_pointsの内部を白で塗りつぶす
    part_img = cv2.bitwise_and(frame, frame, mask=mask)
    return part_img[y:y+h, x:x+w], x, y

def mask(frame, img, fall_y, x0):
    ##合成
    ###マスクを作って、背景画像はマスク部分を消し、パーツ画像はマスク以外の部分を消す
    ###マスクで処理した背景画像とパーツ画像を合成する
    ###最後に、合成した画像をframe画像の適した位置に合成する
    h, w = img.shape[:2]
    frame_result = frame
    pastePosition = frame[fall_y:fall_y+h, x0:x0+w]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)       ##閾値マスク。グラースケール値が10以上で白。未満で黒
    mask_not = cv2.bitwise_not(mask)

    pastePosition = cv2.bitwise_and(pastePosition, pastePosition, mask=mask_not)
    pasteImg = cv2.bitwise_and(img, img, mask=mask)       ##bitwise_add()：同じ画像を2回渡すと、マスクで指定された部分だけが「残る」
    pasted_img = cv2.add(pastePosition, pasteImg)                   ##背景画像とパーツ画像を合成
    frame_result[fall_y:fall_y+h, x0:x0+w] = pasted_img             ##さらに、frame画像の適した位置に合成

    return frame_result, fall_y

def maskPoints(frame, smoothed_face, points, fall_y, x0):
    ##合成
    ###マスクを作って、背景画像はマスク部分を消し、パーツ画像はマスク以外の部分を消す
    ###マスクで処理した背景画像とパーツ画像を合成する
    ###最後に、合成した画像をframe画像の適した位置に合成する
    img, _, _ = extract_part_image(frame, points)
    h, w = img.shape[:2]
    frame_result = smoothed_face
    pastePosition = smoothed_face[fall_y:fall_y+h, x0:x0+w]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)       ##閾値マスク。グラースケール値が10以上で白。未満で黒
    mask_not = cv2.bitwise_not(mask)

    pastePosition = cv2.bitwise_and(pastePosition, pastePosition, mask=mask_not)
    pasteImg = cv2.bitwise_and(img, img, mask=mask)       ##bitwise_add()：同じ画像を2回渡すと、マスクで指定された部分だけが「残る」
    pasted_img = cv2.add(pastePosition, pasteImg)                   ##背景画像とパーツ画像を合成
    frame_result[fall_y:fall_y+h, x0:x0+w] = pasted_img             ##さらに、frame画像の適した位置に合成

    return frame_result, fall_y

def fall(frame, img, x0, waiting):       ##x0はextract_part_imageの出力で得た、顔面上でのパーツのx軸の位置
    global fall_y
    if img is None or img.size == 0:
        return frame, fall_y
    fall_speed = 10              ##落下速度（1フレームで何マス落ちるか）
    h, w = img.shape[:2]
    y = fall_y                  ##yが0の地点（frameの一番上）から落とすために代入

    if waiting:                         ##時間経過中は落下させずにそのまま返す
        return frame, fall_y
    
    if y + h < frame.shape[0] - 15:  ##☆frameの一番下（frame.shape[0]）にパーツが到達していないか
        fall_y += fall_speed
    else:
        fall_y = 0              ##画面下に着いたら画面上に戻す

    return mask(frame, img, fall_y, x0)

##ウインクで固定するパーツと、そのx座標y座標を大域変数のリストに追加
def addPointsList(start_idx, end_idx, x0):
    global winkedPointsList, fall_y
    winkedPointsList.append((start_idx, end_idx, fall_y, x0))
    fall_y = 0

def winkedFrame(frame, smoothed_face, parts):
    for start, end, fall_y, x0 in winkedPointsList:
        current_points = parts[start:end]
        smoothed_face, _ = maskPoints(frame, smoothed_face, current_points, fall_y, x0)
    return smoothed_face