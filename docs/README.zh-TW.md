# Camera Motion Language：發布前檢查 AI 影片的非預期位移

這是本機 Python 命令列工具與選用的代理技能。它量測整體影像特徵位移，協助篩選本來應該固定鏡頭的影片；不需要 API 金鑰、GPU 或 Hermes。

## Windows 快速開始

先安裝 Python 3.10 以上與 Git：

```powershell
git clone https://github.com/leonininder/camera-motion-language.git
cd camera-motion-language
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/measure_frame_drift.py --video golden_clips/static_hold.mp4 --intent static
```

預期看到 `status=PASS` 與 `gate=ENFORCE`。內附影片是 **OpenCV 合成測試素材**，不是 AI 模型的真實生成成果。把 `--video` 改成自己的 MP4 或 MOV 即可測試。

較稀疏的舊素材 `pan_authorized.mp4` 現在因幾何一致性不足回傳 NEEDS_REVIEW／exit 2。可執行 `scripts/evaluate_regressions.py --output regression-results.json` 重現紋理平移與往返位移的 FAIL 對照。

## 如何理解結果

- PASS：預設逐幀檢查的特徵位移沒有超過門檻，不等於人物一定沒有出框。
- FAIL：超過預設 8% 畫面寬度；主體自身移動也可能造成誤判，需要看原片。
- NEEDS_REVIEW：刻意運鏡或特徵不足，需要人工檢查。
- 結束碼 0 也可能是 NEEDS_REVIEW，串接自動流程時請同時檢查 `status` 與 `gate`。

這不是人臉偵測器、防手震工具或影片生成器。8% 是本專案的篩選政策，不是經過通用資料集驗證的品質標準。完整用法、限制與貢獻方式見 [英文首頁](../README.md)。

## 自動流程與逐幀模式

```powershell
.\.venv\Scripts\python.exe scripts/measure_frame_drift.py --video golden_clips/static_hold.mp4 --format json --require-pass --all-frames
```

`--require-pass` 只在 PASS／ENFORCE 回傳 exit 0。JSON 的 `approved` 只代表位移代理政策通過，不是整支影片可發布的保證。預設就是逐幀檢查（`--all-frames` 可明示）；`--sample-frames N` 是較快預覽，即使抽樣位移很低也只回 NEEDS_REVIEW、不自動放行；仍不能區分攝影機與主體。四段公開授權動畫試片目前都要求人工複查，尚不能宣稱真實 AI 影片準確率。詳見[機器契約](MACHINE_CONTRACT.md)及[評估結果](../benchmarks/README.md)。
