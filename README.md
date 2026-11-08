# 素振りカウンター

剣道の素振り（上下・正面素振り）を、スマホの内カメラで正面から撮影して自動で数えるWebアプリ。

- 公開URL：https://superduperohiolife-lgtm.github.io/suburi-counter/
- 判定：MediaPipe Pose で手首が鼻より上→肩付近まで下がったら1本
- 音声：1本ごとに効果音、20本ごと（設定で10/50）に端末の読み上げ
- オフライン：初回表示後は Service Worker のキャッシュでネットなしでも起動

## ファイル構成

| パス | 内容 |
|---|---|
| `src/template.html` | アプリ本体（UI・判定・音声）。声かけのセリフは `VOICE` を編集 |
| `src/build.py` | ビルド。`pages`＝Pages用、`single`＝全部入り1ファイル |
| `.github/workflows/pages.yml` | main への push で自動ビルド＆デプロイ |

## ローカルビルド

```
npm install
python3 src/build.py node_modules/@mediapipe/pose pages _site    # Pages用
python3 src/build.py node_modules/@mediapipe/pose single         # src/suburi_counter.html（1ファイル版）
```
