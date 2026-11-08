# 素振りカウンター

剣道の素振りを、スマホの内カメラで正面から撮影して自動で数えるWebアプリ。

- 公開URL：https://superduperohiolife-lgtm.github.io/suburi-counter/
- 骨格推定：MediaPipe Pose（@mediapipe/pose）をHTMLに同梱
- 声かけのセリフ：`src/template.html` の `VOICE` を編集

## ビルド

```
npm i @mediapipe/pose
python3 src/build.py node_modules/@mediapipe/pose   # src/suburi_counter.html を出力
cp src/suburi_counter.html index.html
```

main へ push すると GitHub Actions で Pages にデプロイされる。
