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

使用 `pan_authorized.mp4` 搭配 `--intent static` 會得到 FAIL；改成 `--intent authorized_camera` 會得到 NEEDS_REVIEW，讓你確認運鏡是否符合原定意圖。

## 如何理解結果

- PASS：抽樣的特徵位移沒有超過門檻，不等於人物一定沒有出框。
- FAIL：超過預設 8% 畫面寬度；主體自身移動也可能造成誤判，需要看原片。
- NEEDS_REVIEW：刻意運鏡或特徵不足，需要人工檢查。
- 結束碼 0 也可能是 NEEDS_REVIEW，串接自動流程時請同時檢查 `status` 與 `gate`。

這不是人臉偵測器、防手震工具或影片生成器。8% 是本專案的篩選政策，不是經過通用資料集驗證的品質標準。完整用法、限制與貢獻方式見 [英文首頁](../README.md)。
