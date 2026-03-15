# 台師大教室使用率系統

盤點**綜合大樓、教育大樓、科工大樓**的教室，分析**哪些時段有在使用**與**空間使用率**。

## 資料說明

- `data/buildings.yaml`：三棟大樓基本資料
- `data/rooms.csv`：教室清單（棟別、容量、類型）
- `data/schedule_mock.csv`：排課／使用紀錄（mock）。欄位：`room_id`, `day_of_week`(1=週一), `slot_start`, `slot_end`, `course_or_usage`

時段編碼：slot 1 = 08:00–09:00，2 = 09:00–10:00，…，14 = 21:00–22:00。一週以週一～五、每天 14 節計算，每間教室可排課總節數 = 70 節/週。

## 使用率定義

- **教室使用率** = 該教室一週內「被使用的節數」÷ 70
- **大樓使用率** = 該棟所有教室「被使用節數加總」÷「該棟可排課節數加總」

## 執行方式

```bash
pip install -r requirements.txt
streamlit run app.py
```

儀表板提供：大樓總覽、時段熱力圖、教室使用率表、單一教室使用時段明細。

## 放到網路上（含 Google Sites 嵌入）

### 1. 部署到 Streamlit Community Cloud（免費）

1. 把此專案推到 **GitHub**（新建 repo，上傳所有檔案含 `data/`、`requirements.txt`、`app.py`）。
2. 打開 [share.streamlit.io](https://share.streamlit.io)，用 GitHub 登入。
3. 選「New app」→ 選你的 repo、branch、主檔 `app.py` → Deploy。
4. 完成後會得到一個網址，例如：`https://xxx.streamlit.app`。

### 2. 在 Google Sites 裡顯示

1. 在 Google Sites 編輯頁面，新增 **「嵌入」** 區塊（插入 → 嵌入網址）。
2. 網址填你部署好的 Streamlit 網址（例如 `https://xxx.streamlit.app`）。
3. 儲存後，訪客在 Google Sites 頁面就能看到儀表板。

注意：若嵌入後被擋（X-Frame 限制），可在 Streamlit Cloud 的 App 設定裡檢查；本專案已設 `enableCORS = false`，多數情況下可嵌入。

---

## 接真實資料

將實際排課匯出為與 `schedule_mock.csv` 相同欄位（`room_id`, `day_of_week`, `slot_start`, `slot_end`, `course_or_usage`），覆蓋或新增檔案後，由 `load_schedule()` 改為讀取該檔即可。
