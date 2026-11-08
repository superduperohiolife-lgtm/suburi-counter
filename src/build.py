"""素振りカウンターのビルド

使い方:
  python3 build.py <node_modules/@mediapipe/pose> single  → suburi_counter.html（全部入り1ファイル・ローカル用）
  python3 build.py <node_modules/@mediapipe/pose> pages <出力dir>
      → index.html + mp/（モデル類）+ sw.js + manifest.webmanifest（GitHub Pages用）
"""
import base64, hashlib, json, pathlib, shutil, sys

ROOT = pathlib.Path(__file__).parent
POSE = pathlib.Path(sys.argv[1])
MODE = sys.argv[2] if len(sys.argv) > 2 else "single"

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
pose_js = (POSE / "pose.js").read_text(encoding="utf-8")


def write(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")


if MODE == "single":
    tags = [f'<script type="application/x-asset" data-name="{n}" data-mime="{m}">'
            f'{base64.b64encode((POSE / n).read_bytes()).decode()}</script>' for n, m in ASSETS]
    html = (tpl.replace("<script>/*__POSE_JS__*/</script>",
                        "<script>" + pose_js.replace("</script", "<\\/script") + "</script>")
               .replace("/*__ASSETS__*/", "\n".join(tags))
               .replace("<!--__MANIFEST__-->", "")
               .replace("__POSE_VERSION__", version))
    out = ROOT / "suburi_counter.html"
    write(out, html)
    print(out, f"{out.stat().st_size/1e6:.1f} MB")

elif MODE == "pages":
    dist = pathlib.Path(sys.argv[3])
    (dist / "mp").mkdir(parents=True, exist_ok=True)
    for n, _ in ASSETS + [("pose.js", "")]:
        shutil.copy(POSE / n, dist / "mp" / n)
    html = (tpl.replace("<script>/*__POSE_JS__*/</script>", '<script src="mp/pose.js"></script>')
               .replace("/*__ASSETS__*/", "")
               .replace("<!--__MANIFEST__-->",
                        '<link rel="manifest" href="manifest.webmanifest">\n'
                        '<link rel="icon" href="icon-192.png" type="image/png">\n'
                        '<link rel="apple-touch-icon" href="apple-touch-icon.png">')
               .replace("__POSE_VERSION__", version))
    write(dist / "index.html", html)

    for icon in ("icon-512.png", "icon-192.png", "icon-maskable-512.png", "icon-maskable-192.png", "apple-touch-icon.png"):
        shutil.copy(ROOT / icon, dist / icon)
    write(dist / "manifest.webmanifest", json.dumps({
        "name": "素振りカウンター", "short_name": "素振り", "start_url": "./", "scope": "./",
        "display": "standalone", "orientation": "portrait",
        "background_color": "#0b1a2e", "theme_color": "#0b1a2e",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                  # Android は maskable を優先し、白い円の背景なしで全面に表示する
                  {"src": "icon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
                  {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
    }, ensure_ascii=False, indent=2))

    shell = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png",
             "icon-maskable-192.png", "icon-maskable-512.png", "apple-touch-icon.png"]
    files = shell + [f"mp/{n}" for n, _ in ASSETS] + ["mp/pose.js"]
    # 内容のハッシュをキャッシュ名に入れ、更新時に自動で入れ替える
    h = hashlib.sha256(b"sw-v2")  # SWの処理を変えたらここも変える
    for f in sorted(p for p in dist.rglob("*") if p.is_file() and p.name != "sw.js"):
        h.update(f.read_bytes())
    cache = "suburi-" + h.hexdigest()[:10]
    sw = f"""// 素振りカウンター Service Worker（build.py が生成）
// 画面のファイルだけ先に保存し、モデル類はページが取得したときに保存する（二重ダウンロード防止）
const CACHE = "{cache}";
const SHELL = {json.dumps(shell)};
const MODELS = {json.dumps(files[len(shell):])};
self.addEventListener("install", e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
}});
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
  // 初回はページが先にモデルを読み込むため、ブラウザのHTTPキャッシュ経由で後追い保存する
  caches.open(CACHE).then(async c => {{
    for (const f of MODELS){{ if (!(await c.match(f))) {{ try{{ await c.add(f); }}catch(err){{}} }} }}
  }});
}});
self.addEventListener("fetch", e => {{
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.open(CACHE).then(async c => {{
    const hit = await c.match(req, {{ ignoreSearch: true }});
    if (hit) return hit;
    const res = await fetch(req);
    if (res.ok) c.put(req, res.clone());
    return res;
  }}));
}});
"""
    write(dist / "sw.js", sw)
    total = sum(p.stat().st_size for p in dist.rglob("*") if p.is_file())
    print(dist, f"{total/1e6:.1f} MB", cache)
else:
    sys.exit("MODE は single か pages")
