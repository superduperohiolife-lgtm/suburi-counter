"""template.html に @mediapipe/pose 一式を base64 で埋め込み、単一HTMLを出力する"""
import base64, json, pathlib, sys

ROOT = pathlib.Path(__file__).parent
POSE = pathlib.Path(sys.argv[1])  # node_modules/@mediapipe/pose
OUT = ROOT / "suburi_counter.html"

ASSETS = [
    ("pose_solution_packed_assets_loader.js", "text/javascript"),
    ("pose_solution_simd_wasm_bin.js", "text/javascript"),
    ("pose_solution_simd_wasm_bin.wasm", "application/wasm"),
    ("pose_solution_simd_wasm_bin.data", "application/octet-stream"),
    ("pose_solution_packed_assets.data", "application/octet-stream"),
    ("pose_web.binarypb", "application/octet-stream"),
    ("pose_landmark_lite.tflite", "application/octet-stream"),
]

tpl = (ROOT / "template.html").read_text(encoding="utf-8")
version = json.loads((POSE / "package.json").read_text())["version"]
pose_js = (POSE / "pose.js").read_text(encoding="utf-8").replace("</script", "<\\/script")

tags = []
for name, mime in ASSETS:
    b64 = base64.b64encode((POSE / name).read_bytes()).decode()
    tags.append(f'<script type="application/x-asset" data-name="{name}" data-mime="{mime}">{b64}</script>')

html = (tpl.replace("/*__POSE_JS__*/", pose_js)
           .replace("/*__ASSETS__*/", "\n".join(tags))
           .replace("__POSE_VERSION__", version))
OUT.write_text(html, encoding="utf-8", newline="\n")
print(OUT, f"{OUT.stat().st_size/1e6:.1f} MB")
