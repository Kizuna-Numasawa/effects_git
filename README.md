# Fukuwarai-Effect

## 概要
カメラの映像から顔のランドマークをリアルタイムで検出し、その顔のパーツを用いて福笑いをプレイするプログラムです。
MediaPipeとOpenCVを使用しています。
口を開いた状態でfukuwarai.pyを実行してください。口を閉じたら、上から降ってくるパーツが停止します。
次のパーツが降ってくるまでに口を開いてください。
全てのパーツの処理が終了すると結果を画像でimgに出力します。


## 動作環境
- OS: Windows 11 / Linux
- Python: 3.12.9
- OpenCV: 4.11.0.86

## インストール手順

```bash
git clone https://github.com/Kizuna-Numasawa/effects_git.git
cd effects_git
pip install -r requirements.txt

Dockerの場合
docker build -t hand-tracker .
docker run -it --device=/dev/video0 hand-tracker

##　別途ダウンロード
リンク先のlearned_modelsフォルダをダウンロードしてください。
ダウンロードしたフォルダをeffectsフォルダにコピペし、fukuwarai.pyを実行してください
https://drive.google.com/drive/u/2/folders/1AsS9qoXDdg31NaElCOnm_dafh9-5-h6m
