# 記憶體報價趨勢追蹤儀錶板 - 功能與 UI 強化計畫 (Improve Plan)

基於原有的 `implement_plan.md`，本計畫旨在進一步提升系統的「專業分析能力 (功能面)」與「使用者體驗 (UI/UX 面)」，將儀錶板從單純的數據展示工具，升級為具備主動洞察與頂級視覺體驗的現代化金融科技終端。

---

## 1. 功能面強化 (Functionality Enhancements)

### 1.1 主動式告警與推播系統 (Proactive Alerting)
*   **閾值觸發通知**：允許設定特定指標的自動告警，例如：
    *   DRAM 現貨價單日跌幅 > 3%
    *   NAND Wafer 價格突破季線
    *   總體牛熊分數跨越 60 分 (轉為偏牛) 或跌破 40 分 (轉為偏熊)
*   **多渠道整合推播**：整合 Line Notify、Telegram Bot 或 Email。除了警報外，也可設定每日台股/美股收盤後，自動推送「記憶體市場單日摘要」。

### 1.2 AI 新聞情緒與事件疊加 (AI Sentiment & Event Overlays)
*   **LLM 財報與新聞摘要**：後端串接 LLM API (如 Gemini 或 OpenAI)，每日自動抓取並摘要大廠 (Micron, SK Hynix, WD) 的新聞、財報會議逐字稿，提取與「記憶體供需、資本支出」相關的關鍵字與情緒偏向。
*   **歷史事件標註圖表 (Event Overlays)**：在歷史趨勢圖上自動或手動標記重大產業事件（如「三星宣佈減產」、「Kioxia 停電事件」、「AI PC 需求爆發」）。將價格走勢與現實事件重疊，大幅提升覆盤與研究的直覺性。

### 1.3 進階數據分析與連動性 (Advanced Analytics & Correlation)
*   **即時相關性矩陣 (Correlation Matrix)**：計算個別股票（如群聯、威剛）與 NAND/DRAM 報價之間的滾動相關係數。幫助使用者一眼看出哪些標的對報價最敏感，或是發現「落後補漲」與「提前反應」的標的。
*   **簡單歷史回測 (Backtesting Widget)**：提供基礎的回測視覺化。例如：「若在牛熊分數大於 60 時買入 Tier A 股票籃子，持有 1 個月的期望報酬與勝率為何？」增加儀錶板的實戰參考價值。

### 1.4 產業鏈資金流向節點圖 (Supply Chain Node Graph)
*   **動態視覺化供應鏈**：有別於單純的表格，使用節點關聯圖 (Node Graph) 畫出「上游矽晶圓/設備」->「原廠製造」->「控制IC/模組」->「終端應用」。
*   **熱區高亮**：將各節點依據當前股價漲跌幅以紅綠顏色高亮，以類似熱力圖的方式呈現，一眼就能看出目前資金或景氣落在哪個產業環節。

---

## 2. UI/UX 體驗強化 (UI/UX Enhancements)

### 2.1 現代化與尊榮感視覺設計 (Modern Premium Aesthetics)
*   **預設深色模式 (Dark Mode by Default)**：採用玻璃擬物化 (Glassmorphism)、深色背景配合細緻的漸層與高反差霓虹強調色（如上漲用亮翠綠，下跌用鮮警紅）。打造類似 Bloomberg Terminal 的專業感與現代化 Web3 產品的科技感。
*   **微動畫與流暢轉場 (Micro-interactions)**：在切換時間維度 (1W/1M/1Y)、切換分頁、或是數據更新時，加入平滑的過渡動畫 (如數字跳動效果)，避免畫面生硬切換，提升產品精緻度。

### 2.2 專業級互動圖表 (Professional Interactive Charting)
*   **升級圖表引擎**：除了 ECharts，建議核心趨勢圖整合 TradingView 的 `lightweight-charts`。提供極度滑順的縮放、平移體驗，並允許在記憶體指數上直接疊加技術指標 (如 MA均線、RSI、MACD)。
*   **圖中圖與懸浮資訊卡 (Contextual Tooltips)**：當滑鼠懸停在表格中的股票代號或報價品項時，自動彈出包含該項目「近 30 天走勢迷你圖 (Sparkline)」及「簡單介紹」的資訊卡，大幅減少使用者點擊與頁面跳轉的次數。

### 2.3 高度客製化的版面佈局 (Customizable Dashboard)
*   **模組化 Widget 拖曳**：每個數據區塊（報價熱力表、股票追蹤表、排行榜）設計為獨立 Widget。允許使用者自由拖曳排列版面，並將個人化佈局儲存於 LocalStorage，滿足不同關注焦點的需求。

### 2.4 具象化的牛熊分數呈現 (Visualized Bull/Bear Indicator)
*   **動態發光溫度計 (Glowing Gauge)**：將 0-100 的總分設計成具備動態發光效果的儀表板。分數極端時（如強熊或強牛），周圍帶有呼吸燈效果，視覺化市場的「狂熱」或「冰冷」程度。
*   **五維雷達圖 (Radar Chart)**：將牛熊分數的五個組成維度（報價動能、股票動能、廣度、波動、相對強弱）以雷達圖展開。一眼就能辨識當前市場是「基本面報價驅動」還是單純「股市資金驅動」。

### 2.5 行動裝置優先的最佳化 (Mobile-First Optimization)
*   **行動端專屬導覽列**：針對 Android PWA / APK，在底部加入固定式導覽列 (Bottom Navigation Bar) 快速切換「總覽、報價、個股、設定」。
*   **滑動式資料卡片**：在手機版螢幕空間有限的情況下，將擁擠的橫向表格轉換為可左右滑動的「資訊卡 (Swipeable Cards)」，大幅提升單手操作的便利性與閱讀體驗。

---

## 3. 實作階段調整建議 (Phase Adjustments)

若要將上述強化項目融入，原實作計畫的 Phase 階段可做以下擴充：

*   **Phase 2 擴充 (UI 升級)**：
    *   前端基礎建設直接導入深色主題系統 (Dark Theme)。
    *   實作動態牛熊溫度計與五維雷達圖。
    *   在主要報價圖表中評估引入 `lightweight-charts`。
*   **Phase 3 擴充 (告警與進階分析)**：
    *   加入 Line / Telegram 推播 API 串接。
    *   實作個股與報價的相關性矩陣計算 (Correlation Matrix)。
*   **新增 Phase 5 (AI 與進階洞察)**：
    *   導入 LLM 新聞摘要與財報情緒分析。
    *   實作歷史事件疊加圖表 (Event Overlays)。
    *   實作產業鏈資金流向節點圖 (Node Graph)。
