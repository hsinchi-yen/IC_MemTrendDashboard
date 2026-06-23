# IC_MemTrendDashboard — Action Plan List

> **使用說明**：每個 ACTION 為最小可交付單元，可由 AI Agent 獨立讀取並執行。  
> 每個 ACTION 包含：Context（背景）、Spec（規格）、Acceptance Criteria / Tests（驗收條件）、Implementation Steps（實作步驟）。  
> 請依序執行，除非 ACTION 明確標注「可並行」。  
> 所有程式碼寫入專案根目錄：`c:\Users\lance.tn\AI Project\IC_MemTrendDashboard\`

---

## 總覽

| Action ID | 名稱 | Phase | 類型 | 依賴 |
|---|---|---|---|---|
| ACTION-001 | 專案目錄結構建立 | P0 | Setup | — |
| ACTION-002 | 資料源驗證腳本 — 台股 (FinMind) | P0 | Validation | ACTION-001 |
| ACTION-003 | 資料源驗證腳本 — 美股 (FinMind/Stooq/AlphaVantage) | P0 | Validation | ACTION-001 |
| ACTION-004 | 資料源驗證腳本 — 日股 (Stooq/yfinance) | P0 | Validation | ACTION-001 |
| ACTION-005 | 資料源驗證腳本 — 韓股 (yfinance/Stooq) | P0 | Validation | ACTION-001 |
| ACTION-006 | 資料源驗證腳本 — TrendForce/DRAMeXchange 公開快照 | P0 | Validation | ACTION-001 |
| ACTION-007 | 資料源可用性報告產生 | P0 | Report | ACTION-002~006 |
| ACTION-008 | Docker Compose 基礎建設 | P1 | Infrastructure | ACTION-001 |
| ACTION-009 | PostgreSQL Schema 建立 | P1 | Database | ACTION-008 |
| ACTION-010 | FastAPI 專案骨架與設定 | P1 | Backend | ACTION-008 |
| ACTION-011 | Instruments 主檔資料匯入 | P1 | Data | ACTION-009 |
| ACTION-012 | 台股日線抓取 Job | P1 | Ingestion | ACTION-009,010 |
| ACTION-013 | 美股日線抓取 Job | P1 | Ingestion | ACTION-009,010 |
| ACTION-014 | 日股日線抓取 Job | P1 | Ingestion | ACTION-009,010 |
| ACTION-015 | 韓股日線抓取 Job | P1 | Ingestion | ACTION-009,010 |
| ACTION-016 | DRAM/NAND 公開快照抓取 Job | P1 | Ingestion | ACTION-009,010 |
| ACTION-017 | 每日 01:00 背景排程 (APScheduler) | P1 | Scheduler | ACTION-012~016 |
| ACTION-018 | 手動更新 API 端點 | P1 | API | ACTION-012~016 |
| ACTION-019 | 資料新鮮度健康檢查 API | P1 | API | ACTION-017,018 |
| ACTION-020 | 基礎查詢 API 端點 | P1 | API | ACTION-009,010 |
| ACTION-021 | Trend Metrics 計算 Job | P1 | Analytics | ACTION-012~016 |
| ACTION-022 | 牛熊分數計算引擎 | P1 | Analytics | ACTION-021 |
| ACTION-023 | 前端專案骨架 (React+Vite+TypeScript) | P2 | Frontend | ACTION-008 |
| ACTION-024 | 全域設計系統與深色主題 | P2 | Frontend | ACTION-023 |
| ACTION-025 | 頂部狀態列元件 | P2 | Frontend | ACTION-024 |
| ACTION-026 | 動態發光牛熊溫度計元件 | P2 | Frontend | ACTION-024 |
| ACTION-027 | 五維雷達圖元件 | P2 | Frontend | ACTION-024 |
| ACTION-028 | 大趨勢圖元件 (lightweight-charts) | P2 | Frontend | ACTION-024 |
| ACTION-029 | 報價熱力表元件 | P2 | Frontend | ACTION-024 |
| ACTION-030 | 股票追蹤表元件 | P2 | Frontend | ACTION-024 |
| ACTION-031 | 懸浮資訊卡 (Sparkline Tooltip) 元件 | P2 | Frontend | ACTION-030 |
| ACTION-032 | 領先/落後排行榜元件 | P2 | Frontend | ACTION-024 |
| ACTION-033 | 資料來源狀態與更新進度元件 | P2 | Frontend | ACTION-018,019 |
| ACTION-034 | Web UI 查詢頁 | P2 | Frontend | ACTION-020 |
| ACTION-035 | 指標說明頁與 ⓘ Tooltip | P2 | Frontend | ACTION-024 |
| ACTION-036 | RWD 手機版佈局 (底部導覽列 + Swipeable Cards) | P2 | Frontend | ACTION-023~034 |
| ACTION-037 | 微動畫與流暢轉場系統 | P2 | Frontend | ACTION-024 |
| ACTION-038 | 告警規則 CRUD API | P3 | Backend | ACTION-009,010 |
| ACTION-039 | 告警觸發引擎 | P3 | Backend | ACTION-022,038 |
| ACTION-040 | Telegram Bot 推播整合 | P3 | Backend | ACTION-039 |
| ACTION-041 | Line Notify 推播整合 | P3 | Backend | ACTION-039 |
| ACTION-042 | Email 推播整合 | P3 | Backend | ACTION-039 |
| ACTION-043 | 每日收盤摘要推送 Job | P3 | Scheduler | ACTION-040,041 |
| ACTION-044 | 相關性矩陣計算 Job | P3 | Analytics | ACTION-021 |
| ACTION-045 | 相關性矩陣 UI 元件 | P3 | Frontend | ACTION-044 |
| ACTION-046 | PWA Manifest 與離線快取 | P4 | Mobile | ACTION-023~036 |
| ACTION-047 | Capacitor Android 專案建立 | P4 | Mobile | ACTION-046 |
| ACTION-048 | LLM 新聞摘要抓取 Job | P5 | AI | ACTION-009,010 |
| ACTION-049 | 歷史事件標記 CRUD 與圖表 Overlay | P5 | AI+Frontend | ACTION-028,048 |
| ACTION-050 | 簡單歷史回測 Widget | P5 | Analytics | ACTION-021,022 |
| ACTION-051 | 產業鏈節點圖 (Node Graph) | P5 | Frontend | ACTION-020 |

---

## PHASE 0 — 資料源驗證與代號確認

---

### ACTION-001：專案目錄結構建立

**Context**  
整個 IC_MemTrendDashboard 系統的根目錄結構，後續所有 ACTION 都在此基礎上建立。需要清楚分層 backend、frontend、scripts、docs、tests 等目錄。

**Spec**  
在 `c:\Users\lance.tn\AI Project\IC_MemTrendDashboard\` 下建立以下目錄與基礎設定檔：

```
IC_MemTrendDashboard/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── jobs/
│   │   └── db/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── (由 ACTION-023 建立)
├── scripts/
│   ├── phase0_validation/
│   └── data_import/
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

**Acceptance Criteria / Tests**  
- [ ] 所有目錄已建立，無缺漏。
- [ ] `.env.example` 包含以下變數鍵（值留空）：`FINMIND_TOKEN`、`ALPHA_VANTAGE_KEY`、`TELEGRAM_BOT_TOKEN`、`TELEGRAM_CHAT_ID`、`LINE_NOTIFY_TOKEN`、`SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASS`、`DATABASE_URL`、`LLM_API_KEY`。
- [ ] `.gitignore` 包含：`.env`、`__pycache__/`、`*.pyc`、`node_modules/`、`dist/`、`*.log`。
- [ ] `README.md` 包含：專案簡介、各 Phase 說明、如何啟動 (docker-compose up)。

**Implementation Steps**  
1. 建立上述所有目錄。
2. 建立 `.env.example` 並列出所有環境變數鍵。
3. 建立 `.gitignore`。
4. 建立 `README.md` 含基本說明。
5. 建立 `backend/__init__.py` 與 `backend/app/__init__.py`（空檔）。

---

### ACTION-002：資料源驗證腳本 — 台股 (FinMind)

**Context**  
Phase 0 核心任務：驗證 FinMind API 是否能覆蓋所有台股記憶體/模組/控制 IC/封測/材料/設備追蹤標的，並取得最近 1 年日線。

**Spec**  
建立 `scripts/phase0_validation/validate_tw_finmind.py`：
- 使用環境變數 `FINMIND_TOKEN`。
- 待驗證台股代號清單（硬編碼於腳本中）：
  - 核心記憶體：`2408`、`2344`、`6770`、`3006`、`2337`、`8299`、`2451`、`3260`、`4967`、`5289`、`8271`、`8088`
  - 控制 IC/IP：`8054`、`6104`、`3529`、`3661`
  - 封測/測試/載板：`6239`、`8150`、`2449`、`6257`、`8110`、`3711`、`3264`、`6515`、`6510`、`6223`、`6683`、`3037`、`3189`、`8046`
  - 設備/材料：`6488`、`5483`、`3532`、`3680`、`3131`、`3583`、`6196`、`2404`、`5434`
- 對每個代號呼叫 FinMind `TaiwanStockPrice`，查詢最近 252 交易日資料（date 從今天往前 1 年）。
- 記錄每個代號：`status`（success/fail）、`row_count`（取得筆數）、`last_date`（最新資料日期）、`error_msg`（若失敗）。
- 輸出 JSON 報告至 `scripts/phase0_validation/results/tw_finmind_result.json`。
- 加入速率限制：每次請求間隔至少 0.5 秒；若收到 HTTP 402 立即停止並記錄。

**Acceptance Criteria / Tests**  
- [ ] 腳本可以 `python validate_tw_finmind.py` 執行（需在 `.env` 設定 `FINMIND_TOKEN`）。
- [ ] 若 Token 未設定，腳本輸出清楚錯誤訊息並結束，而非拋出未處理例外。
- [ ] 輸出 JSON 格式正確：`{"generated_at": "...", "total": N, "success": N, "fail": N, "results": [...]}`。
- [ ] 速率限制有效：實際請求間隔 >= 0.5 秒（可用 log timestamp 驗證）。
- [ ] 若代號不存在（FinMind 回傳空資料），`status` 標記為 `no_data` 而非 `success`。

**Implementation Steps**  
1. 建立 `scripts/phase0_validation/results/` 目錄。
2. 安裝依賴：`requests`、`python-dotenv`（加入 `requirements.txt`）。
3. 撰寫腳本，使用 `TaiwanStockPrice` dataset，parameters: `data_id=<代號>&start_date=<1年前>&end_date=<今天>`。
4. 加入 retry 機制（最多 3 次，指數退避）。
5. 輸出 JSON 報告。

---

### ACTION-003：資料源驗證腳本 — 美股 (FinMind/Stooq/AlphaVantage)

**Context**  
驗證美股記憶體與供應鏈標的的資料源覆蓋率。美股需同時測試三個來源並比較。

**Spec**  
建立 `scripts/phase0_validation/validate_us_stocks.py`：
- 待驗證美股代號：`MU`、`SNDK`、`WDC`、`SIMO`、`RMBS`、`MRVL`、`AVGO`、`CDNS`、`SNPS`、`AMAT`、`LRCX`、`KLAC`、`TER`、`FORM`、`COHU`、`AMKR`、`ENTG`、`MKSI`、`ONTO`、`ACLS`、`VECO`、`PLAB`、`STX`、`PSTG`
- 對每個代號分別測試：
  - **FinMind** `USStockPrice`（Bearer token）
  - **Stooq** CSV 下載（`https://stooq.com/q/d/l/?s=<symbol>.us&i=d`）
  - **Alpha Vantage** TIME_SERIES_DAILY（`apikey` 環境變數 `ALPHA_VANTAGE_KEY`）
- 記錄每個來源：`status`、`row_count`、`last_date`、`latency_ms`、`error_msg`。
- 輸出 `scripts/phase0_validation/results/us_stocks_result.json`。
- Alpha Vantage 免費 key 每分鐘限 5 次，腳本需自動限速（每次間隔 12 秒）。

**Acceptance Criteria / Tests**  
- [ ] 三個來源各自獨立測試，單一來源失敗不影響其他來源的測試繼續執行。
- [ ] Stooq 測試不需任何 API key 即可獨立執行（純 HTTP GET CSV）。
- [ ] Alpha Vantage 限速有效：若 `ALPHA_VANTAGE_KEY` 未設定，跳過此來源並標注 `skipped`。
- [ ] 輸出 JSON 包含三個來源的比較摘要，例如哪些代號 Stooq 有但 FinMind 無。

**Implementation Steps**  
1. 撰寫三個獨立的資料源抓取函式。
2. 整合到主流程，對每個代號依序測試三個來源。
3. 產生比較報告。

---

### ACTION-004：資料源驗證腳本 — 日股 (Stooq/yfinance)

**Context**  
驗證日股核心記憶體（Kioxia `285A.T`）與設備/材料觀察股的資料源可用性。

**Spec**  
建立 `scripts/phase0_validation/validate_jp_stocks.py`：
- 待驗證代號（Stooq 格式）：`285a.jp`、`6857.jp`、`8035.jp`、`7735.jp`、`6146.jp`、`6920.jp`、`6361.jp`、`7731.jp`、`7751.jp`、`6728.jp`、`6590.jp`、`3436.jp`、`4063.jp`、`4004.jp`、`4186.jp`、`4901.jp`、`7741.jp`、`4062.jp`、`7911.jp`、`7912.jp`、`4401.jp`、`4088.jp`
- 測試來源：Stooq CSV（`https://stooq.com/q/d/l/?s=<symbol>&i=d`）、yfinance（ticker = `<代號>.T`）
- 記錄：`status`、`row_count`、`last_date`、`currency`、`error_msg`
- 輸出 `scripts/phase0_validation/results/jp_stocks_result.json`

**Acceptance Criteria / Tests**  
- [ ] Kioxia `285A.T` 若 Stooq 無資料，自動嘗試 yfinance，並在報告中標注「需 yfinance 備援」。
- [ ] 日股代號格式轉換正確（Stooq 用小寫 `.jp`，yfinance 用 `.T`）。
- [ ] 輸出報告標示哪些標的「無法取得」，建議手動匯入 CSV。

**Implementation Steps**  
1. 撰寫 Stooq CSV 和 yfinance 兩個抓取函式。
2. 日股代號格式轉換輔助函式。
3. 執行驗證並輸出報告。

---

### ACTION-005：資料源驗證腳本 — 韓股 (yfinance/Stooq)

**Context**  
驗證韓股核心記憶體（Samsung `005930.KS`、SK hynix `000660.KS`）與設備/材料/封測觀察股可用性。

**Spec**  
建立 `scripts/phase0_validation/validate_kr_stocks.py`：
- 待驗證代號（yfinance 格式）：`005930.KS`、`000660.KS`、`240810.KQ`、`319660.KQ`、`031980.KQ`、`084370.KQ`、`095610.KQ`、`222800.KQ`、`095340.KQ`、`058470.KQ`、`067310.KQ`、`036540.KQ`、`033640.KQ`、`131290.KQ`、`092870.KQ`、`357780.KQ`、`005290.KQ`、`014680.KS`、`104830.KQ`、`092070.KQ`、`093370.KS`
- 測試來源：yfinance、Stooq（代號需轉換為 `<num>.kr` 格式）
- 輸出 `scripts/phase0_validation/results/kr_stocks_result.json`

**Acceptance Criteria / Tests**  
- [ ] Samsung 和 SK hynix 至少一個來源能取得最近 1 年日線（此為最低通過門檻）。
- [ ] 報告中標注建議使用的首選來源（依覆蓋率與穩定性）。

---

### ACTION-006：資料源驗證腳本 — TrendForce/DRAMeXchange 公開快照

**Context**  
驗證 DRAMeXchange 公開頁面可抓取哪些報價品項，並確認資料格式與更新頻率。

**Spec**  
建立 `scripts/phase0_validation/validate_memory_quotes.py`：
- 目標 URL：`https://www.dramexchange.com/`
- 嘗試抓取頁面並解析以下表格（若存在）：
  - DRAM Spot Price（DDR4、DDR5、LPDDR5 等）
  - NAND Flash Spot Price（TLC/MLC wafer、SSD、eMMC 等）
  - Module Spot Price
  - Wafer Spot Price
- 對每個表格，記錄：`table_name`、`columns`（欄位名稱）、`row_count`（品項數量）、`sample_data`（前 2 筆）、`last_update`（若頁面有標示）。
- 加入 `User-Agent` 模擬瀏覽器、請求間隔 >= 3 秒。
- 輸出 `scripts/phase0_validation/results/memory_quotes_result.json`。
- 若頁面需 JavaScript 動態渲染（BeautifulSoup 抓不到資料），在報告中標注「需 Playwright」並列出所需元素。

**Acceptance Criteria / Tests**  
- [ ] 腳本執行後輸出 JSON，明確列出哪些表格可靜態抓取、哪些需 Playwright。
- [ ] 若完全無法解析，輸出`"status": "requires_manual_or_playwright"`，不拋出未處理例外。
- [ ] User-Agent 設定正確（模擬 Chrome 最新版本）。

---

### ACTION-007：資料源可用性報告產生

**Context**  
整合 ACTION-002 到 ACTION-006 的所有驗證結果，產生一份 Markdown 格式的「資料源可用性報告」。

**Spec**  
建立 `scripts/phase0_validation/generate_report.py`：
- 讀取 `results/` 目錄下所有 `*_result.json`。
- 產生 `docs/data_source_report.md`，包含：
  1. **執行摘要**：各市場標的總數、成功/失敗/需備援數量
  2. **台股覆蓋率表格**：代號、名稱、Tier、FinMind 狀態、最新資料日
  3. **美股三來源比較表格**：代號、FinMind、Stooq、AlphaVantage 各自狀態
  4. **日股覆蓋率表格**：代號、Stooq 狀態、yfinance 狀態、建議來源
  5. **韓股覆蓋率表格**：代號、yfinance 狀態、Stooq 狀態、建議來源
  6. **記憶體報價快照狀態**：各表格名稱、可抓狀態、欄位、是否需 Playwright
  7. **行動建議**：哪些標的需手動 CSV、哪些建議捨棄、哪些需付費授權

**Acceptance Criteria / Tests**  
- [ ] 報告 Markdown 格式正確（表格對齊、標題層次清楚）。
- [ ] 「行動建議」區段清楚列出需要人工介入的項目。
- [ ] 腳本即使部分 `result.json` 不存在，仍可正常產生報告（缺失來源標注 `not_run`）。

---

## PHASE 1 — MVP 資料管線

---

### ACTION-008：Docker Compose 基礎建設

**Context**  
建立整個系統的容器化基礎，讓 PostgreSQL、Backend API 和 Web UI 可以用單一指令啟動。

**Spec**  
建立 `docker-compose.yml`，包含以下服務：

```yaml
services:
  db:
    image: postgres:16-alpine
    environment: (從 .env 讀取 POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)
    ports: ["5432:5432"]
    volumes: ["postgres_data:/var/lib/postgresql/data"]
    healthcheck: (pg_isready)

  backend:
    build: ./backend
    ports: ["3000:3000"]
    environment: (DATABASE_URL 等從 .env 讀取)
    depends_on: db (condition: service_healthy)

  frontend:
    build: ./frontend
    ports: ["8510:8510"]
    depends_on: backend
```

同時建立 `backend/Dockerfile`（基於 `python:3.12-slim`，安裝 requirements.txt，啟動 uvicorn）。

在 `.env.example` 加入：`POSTGRES_DB=memdash`、`POSTGRES_USER=memdash`、`POSTGRES_PASSWORD=<your_pw>`。

**Acceptance Criteria / Tests**  
- [ ] `docker-compose up -d db` 成功啟動 PostgreSQL，`docker-compose exec db pg_isready` 回傳 `accepting connections`。
- [ ] `docker-compose up -d backend` 成功啟動（健康檢查通過後），`curl http://localhost:3000/health` 回傳 `{"status": "ok"}`。
- [ ] 資料庫 volume `postgres_data` 正確建立，重啟容器後資料不遺失。
- [ ] `.env` 機密不寫入 Dockerfile 或 docker-compose.yml（皆從環境變數讀取）。

**Implementation Steps**  
1. 撰寫 `docker-compose.yml`。
2. 撰寫 `backend/Dockerfile`。
3. 建立最簡 FastAPI app（只有 `/health` 端點），確認容器啟動正常。
4. 更新 `.env.example` 加入 PostgreSQL 相關變數。

---

### ACTION-009：PostgreSQL Schema 建立

**Context**  
建立完整的資料庫 schema，這是所有資料管線和 API 的基礎。使用 Alembic 管理 migration，確保 schema 版本可控。

**Spec**  
安裝：`sqlalchemy`、`alembic`、`asyncpg`（加入 `backend/requirements.txt`）。

建立以下資料表（使用 SQLAlchemy ORM 定義於 `backend/app/models/`）：

**`instruments`**
```sql
id SERIAL PRIMARY KEY,
ticker VARCHAR(20) NOT NULL,
market VARCHAR(10) NOT NULL,  -- TW/US/JP/KR
name VARCHAR(100),
name_en VARCHAR(100),
tier VARCHAR(5) NOT NULL,  -- A/B/C
supply_chain_tag VARCHAR(50),  -- memory-maker/nand-controller/...
currency VARCHAR(5),
is_active BOOLEAN DEFAULT TRUE,
score_weight DECIMAL(5,4) DEFAULT 0,
score_only_observe BOOLEAN DEFAULT FALSE,
created_at TIMESTAMPTZ DEFAULT NOW(),
UNIQUE(ticker, market)
```

**`equity_prices`**
```sql
id BIGSERIAL PRIMARY KEY,
instrument_id INT REFERENCES instruments(id),
trade_date DATE NOT NULL,
open DECIMAL(18,6),
high DECIMAL(18,6),
low DECIMAL(18,6),
close DECIMAL(18,6),
volume BIGINT,
source VARCHAR(20),  -- finmind/stooq/alphavantage/manual
created_at TIMESTAMPTZ DEFAULT NOW(),
UNIQUE(instrument_id, trade_date)
```

**`memory_quotes`**
```sql
id BIGSERIAL PRIMARY KEY,
product VARCHAR(50) NOT NULL,  -- DDR5-4800/NAND-TLC-wafer/...
category VARCHAR(20) NOT NULL,  -- DRAM/NAND/SSD/eMMC
price_type VARCHAR(20),  -- spot/contract/module/wafer
price_high DECIMAL(12,6),
price_low DECIMAL(12,6),
price_avg DECIMAL(12,6),
change_pct DECIMAL(8,4),
currency VARCHAR(5) DEFAULT 'USD',
unit VARCHAR(20),  -- USD/Gb, USD/piece
source VARCHAR(30),
snapshot_date DATE NOT NULL,
fetched_at TIMESTAMPTZ DEFAULT NOW(),
UNIQUE(product, price_type, snapshot_date)
```

**`trend_metrics`**
```sql
id BIGSERIAL PRIMARY KEY,
instrument_id INT REFERENCES instruments(id),
as_of_date DATE NOT NULL,
period VARCHAR(5) NOT NULL,  -- 1D/1W/1M/3M/6M/1Y
change_pct DECIMAL(8,4),
change_abs DECIMAL(18,6),
direction VARCHAR(10),  -- up/flat/down
momentum DECIMAL(8,4),
ma_state JSONB,  -- {ma20: above/below, ma60: ..., ma120: ..., ma240: ...}
volatility DECIMAL(8,4),
hi_lo_flag JSONB,  -- {1M_high: bool, 3M_high: bool, ...}
streak INT,
acceleration DECIMAL(8,4),
normalized_index DECIMAL(10,4),
narrative TEXT,
computed_at TIMESTAMPTZ DEFAULT NOW(),
UNIQUE(instrument_id, as_of_date, period)
```

**`market_scores`**
```sql
id BIGSERIAL PRIMARY KEY,
score_date DATE NOT NULL UNIQUE,
total_score DECIMAL(6,3),
quote_momentum_score DECIMAL(6,3),
equity_momentum_score DECIMAL(6,3),
breadth_score DECIMAL(6,3),
risk_score DECIMAL(6,3),
relative_strength_score DECIMAL(6,3),
status VARCHAR(20),  -- strong-bear/bear/neutral/bull/strong-bull
narrative JSONB,  -- 各子分數說明
computed_at TIMESTAMPTZ DEFAULT NOW()
```

**`source_runs`**
```sql
id BIGSERIAL PRIMARY KEY,
source_name VARCHAR(50) NOT NULL,
trigger VARCHAR(20) NOT NULL,  -- startup/manual/scheduled_0100
started_at TIMESTAMPTZ,
finished_at TIMESTAMPTZ,
status VARCHAR(20),  -- running/success/fail/partial
rows_fetched INT DEFAULT 0,
error_msg TEXT,
metadata JSONB
```

**`refresh_jobs`**
```sql
id BIGSERIAL PRIMARY KEY,
job_id UUID DEFAULT gen_random_uuid(),
trigger VARCHAR(20) NOT NULL,
started_at TIMESTAMPTZ DEFAULT NOW(),
finished_at TIMESTAMPTZ,
status VARCHAR(20) DEFAULT 'running',
progress JSONB,  -- {total: N, done: N, current_source: "..."}
lock_key VARCHAR(100) UNIQUE,
success_count INT DEFAULT 0,
fail_count INT DEFAULT 0
```

**`alert_rules`** (Phase 3，但先建立 schema)
```sql
id SERIAL PRIMARY KEY,
rule_name VARCHAR(100),
instrument_id INT REFERENCES instruments(id),
metric VARCHAR(50),  -- total_score/dram_spot_1d/...
condition VARCHAR(10),  -- gt/lt/cross_up/cross_down
threshold DECIMAL(12,4),
channel VARCHAR(20),  -- telegram/line/email
is_active BOOLEAN DEFAULT TRUE,
created_at TIMESTAMPTZ DEFAULT NOW()
```

**`alert_events`** (Phase 3，但先建立 schema)
```sql
id BIGSERIAL PRIMARY KEY,
rule_id INT REFERENCES alert_rules(id),
triggered_at TIMESTAMPTZ DEFAULT NOW(),
metric_value DECIMAL(12,4),
notify_status VARCHAR(20),  -- sent/failed/skipped
notify_response TEXT
```

**Acceptance Criteria / Tests**  
- [ ] `alembic upgrade head` 成功執行，所有表格建立無錯誤。
- [ ] 各表格的 UNIQUE constraint 正確（不允許重複 ticker+market、不允許同日同品項同 source 重複報價）。
- [ ] `instrument_id` 外鍵在 `equity_prices` 和 `trend_metrics` 上有索引（查詢效能）。
- [ ] 測試：插入一筆 instrument，再插入同一 ticker+market，應觸發 unique violation。
- [ ] 測試：插入 equity_prices 不存在的 instrument_id，應觸發 FK violation。

**Implementation Steps**  
1. 安裝依賴，設定 alembic。
2. 定義所有 SQLAlchemy models。
3. 產生 initial migration。
4. 執行 migration 並驗證表格。
5. 撰寫簡單的 Python 測試腳本驗證 constraints。

---

### ACTION-010：FastAPI 專案骨架與設定

**Context**  
建立 FastAPI 應用骨架，包含設定管理、資料庫連線、dependency injection、錯誤處理與基礎端點。

**Spec**  
在 `backend/app/` 下建立：

**`config.py`**（使用 pydantic-settings）：
```python
class Settings(BaseSettings):
    DATABASE_URL: str
    FINMIND_TOKEN: str = ""
    ALPHA_VANTAGE_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    LINE_NOTIFY_TOKEN: str = ""
    LLM_API_KEY: str = ""
    DATA_FRESHNESS_THRESHOLD_HOURS_STOCK: int = 12
    DATA_FRESHNESS_THRESHOLD_HOURS_QUOTE: int = 24
```

**`main.py`**：
- FastAPI app 初始化
- CORS 設定（允許 `http://localhost:8510`）
- 路由前綴：`/api`
- 啟動事件：初始化 DB 連線 pool
- 全域例外處理：500 回傳 `{"error": "internal_server_error", "detail": "..."}`

**`db/database.py`**：
- async SQLAlchemy engine (`asyncpg`)
- `get_db()` dependency

**基礎端點**（於 `routers/health.py`）：
- `GET /health` → `{"status": "ok", "version": "0.1.0", "db": "connected"}`

**`requirements.txt`** 包含：`fastapi`、`uvicorn[standard]`、`sqlalchemy[asyncio]`、`asyncpg`、`alembic`、`pydantic-settings`、`python-dotenv`、`httpx`、`requests`、`beautifulsoup4`、`lxml`、`apscheduler`

**Acceptance Criteria / Tests**  
- [ ] `uvicorn app.main:app --reload --port 3000` 正常啟動，無 import 錯誤。
- [ ] `GET /health` 回傳 `{"status": "ok"}` 且 HTTP 200。
- [ ] 若 `DATABASE_URL` 設定錯誤，啟動時立即報錯並給出明確提示（非執行期才崩潰）。
- [ ] CORS：`curl -H "Origin: http://localhost:8510" http://localhost:3000/health` 包含 `Access-Control-Allow-Origin` header。
- [ ] FastAPI 自動產生的 `/docs`（Swagger UI）可正常開啟。

**Implementation Steps**  
1. 建立 `config.py`、`database.py`、`main.py`、`routers/health.py`。
2. 設定 CORS middleware。
3. 設定 lifespan 事件初始化資料庫連線。
4. 撰寫 `/health` 端點，含 DB ping。

---

### ACTION-011：Instruments 主檔資料匯入

**Context**  
將所有追蹤標的（台股、美股、日股、韓股及所有 Tier 分類）的 master data 匯入 `instruments` 表格，作為所有後續資料操作的基礎。

**Spec**  
建立 `scripts/data_import/instruments_seed.py`：
- 從 `scripts/data_import/instruments_seed.json` 讀取標的清單。
- 使用 upsert（ON CONFLICT DO UPDATE）寫入 `instruments` 表格。
- 標的清單涵蓋所有在 `final_implement_plan.md` 第 1.2 節列出的標的，含：
  - `ticker`、`market`（TW/US/JP/KR）、`name`（中文）、`name_en`（英文）
  - `tier`（A/B/C）、`supply_chain_tag`（memory-maker / nand-controller / module-brand / equipment / material / backend-test / substrate / downstream-storage 等）
  - `currency`（TWD/USD/JPY/KRW）、`is_active`（true）
  - `score_weight`（Tier A 核心標的給予高權重，Tier C 給 0）
  - `score_only_observe`（Tier C 標的設為 true）

同時建立 `GET /api/instruments` 端點，支援：
- Query params：`market`、`tier`、`tag`、`is_active`
- 回傳 JSON 陣列

**Acceptance Criteria / Tests**  
- [ ] `python instruments_seed.py` 執行後，`SELECT COUNT(*) FROM instruments` 回傳正確總數（台股+美股+日股+韓股所有標的）。
- [ ] 重複執行腳本不產生重複資料（upsert 有效）。
- [ ] `GET /api/instruments?market=TW&tier=A` 只回傳台股 Tier A 標的。
- [ ] `GET /api/instruments?tag=memory-maker` 只回傳記憶體原廠標的。
- [ ] 每個標的的 `tier` 和 `supply_chain_tag` 填寫正確（人工確認清單）。

**Implementation Steps**  
1. 手動建立 `instruments_seed.json`，逐一填入所有標的資料（依照 final_implement_plan.md 清單）。
2. 撰寫 seed 腳本（upsert 邏輯）。
3. 建立 `GET /api/instruments` 端點與對應 router。
4. 撰寫 pytest 測試 API 回傳格式與過濾邏輯。

---

### ACTION-012：台股日線抓取 Job

**Context**  
從 FinMind 抓取所有台股標的的股票日線資料，存入 `equity_prices` 表格。支援增量更新（只抓最後成功日期之後的資料）。

**Spec**  
建立 `backend/app/jobs/ingest_tw_stocks.py`：

```python
async def ingest_tw_stocks(trigger: str = "manual") -> dict:
    """
    1. 建立 source_run 記錄 (status=running)
    2. 查詢 instruments 表格，取得所有 market=TW, is_active=True 的標的
    3. 對每個標的：
       a. 查詢 equity_prices 最後資料日期 (last_date)
       b. 若 last_date 為空，從今天往前 365 天開始抓
       c. 呼叫 FinMind TaiwanStockPrice API (start_date=last_date+1, end_date=today)
       d. upsert 資料到 equity_prices (source='finmind')
       e. 更新 source_run 進度
    4. 更新 source_run (status=success/fail/partial)
    5. 回傳統計資訊
    """
```

設計要求：
- 速率限制：每次請求間隔 >= 0.5 秒。
- 每個標的最多 retry 3 次，指數退避（1s, 2s, 4s）。
- 若 HTTP 402（額度用完），立即停止所有請求，標記本次 run 為 `quota_exceeded`，後續標的跳過。
- 單一標的失敗不中斷整體 job（記錄 error，繼續下個標的）。
- 使用 asyncio 非同步執行，但對 FinMind 的實際 HTTP 請求需受速率限制（不可並行打爆 API）。

**Acceptance Criteria / Tests**  
- [ ] 執行後 `source_runs` 新增一筆記錄，`status` 正確（`success`/`partial`/`fail`）。
- [ ] `equity_prices` 表格有新增資料，且 `source='finmind'`。
- [ ] 重複執行不產生重複資料（upsert 有效）。
- [ ] 增量更新有效：已有 2024-01-01 資料，再次執行應只抓 2024-01-02 至今。
- [ ] 模擬 HTTP 402：job 應立即停止並在 `source_runs.error_msg` 寫入 `quota_exceeded`。
- [ ] pytest mock 測試：mock FinMind API 回傳，驗證 upsert 邏輯正確。

**Implementation Steps**  
1. 建立 FinMind API client (`backend/app/services/finmind_client.py`)。
2. 建立 `ingest_tw_stocks.py` job function。
3. 撰寫 pytest 測試（mock API + 測試 DB upsert）。

---

### ACTION-013：美股日線抓取 Job

**Context**  
從多個來源抓取美股日線，依 Phase 0 驗證結果選擇最佳來源，並設置備援切換邏輯。

**Spec**  
建立 `backend/app/jobs/ingest_us_stocks.py`：
- 來源優先順序：FinMind `USStockPrice` → Stooq CSV → Alpha Vantage（Alpha Vantage 因每分鐘 5 次限制，只作最後備援）。
- 對每個美股標的：先嘗試 FinMind，若失敗改用 Stooq，若再失敗才用 Alpha Vantage。
- Alpha Vantage 使用限速：請求間隔 >= 12 秒。
- Stooq URL：`https://stooq.com/q/d/l/?s=<symbol>.us&i=d`（下載 CSV）。
- 其餘設計與 ACTION-012 相同（增量更新、retry、source_runs 記錄）。

**Acceptance Criteria / Tests**  
- [ ] MU（Micron）日線資料可成功抓取並存入。
- [ ] 模擬 FinMind 失敗時，自動切換到 Stooq。
- [ ] `equity_prices` 的 `source` 欄位正確記錄實際使用的來源（`finmind`/`stooq`/`alphavantage`）。
- [ ] Alpha Vantage 限速有效（測試模式下可用 mock 驗證）。

---

### ACTION-014：日股日線抓取 Job

**Context**  
從 Stooq 和 yfinance 抓取日股標的日線，處理日股特有的代號格式。

**Spec**  
建立 `backend/app/jobs/ingest_jp_stocks.py`：
- 來源優先順序：Stooq CSV → yfinance。
- Stooq 日股代號格式：`<code>.jp`（例如 `285a.jp`）；yfinance 格式：`<code>.T`。
- 特別注意 Kioxia `285A.T`：需先用 Stooq 抓，若無資料改用 yfinance。
- 其他設計與 ACTION-012 相同。

**Acceptance Criteria / Tests**  
- [ ] Kioxia（`285A`）日線可成功抓取。
- [ ] Advantest（`6857`）日線可成功抓取。
- [ ] 日股資料的 `currency` 欄位存為 `JPY`（instruments 表格中需確認）。

---

### ACTION-015：韓股日線抓取 Job

**Context**  
從 yfinance 和 Stooq 抓取韓股日線資料。

**Spec**  
建立 `backend/app/jobs/ingest_kr_stocks.py`：
- 來源優先順序：yfinance → Stooq。
- yfinance 韓股代號格式：`<code>.KS`（KRX 主板）或 `<code>.KQ`（KOSDAQ）。
- 其他設計與 ACTION-012 相同。

**Acceptance Criteria / Tests**  
- [ ] Samsung（`005930.KS`）和 SK hynix（`000660.KS`）日線可成功抓取。
- [ ] 韓股資料的 `currency` 欄位存為 `KRW`。

---

### ACTION-016：DRAM/NAND 公開快照抓取 Job

**Context**  
每日從 DRAMeXchange 公開頁面抓取記憶體報價快照，存入 `memory_quotes` 表格。

**Spec**  
建立 `backend/app/jobs/ingest_memory_quotes.py`：
- 依照 ACTION-006 的驗證結果，抓取可靜態解析的報價表格。
- 若靜態解析失敗（需 Playwright），使用 Playwright headless 模式（`playwright install chromium`）。
- 每個品項以 upsert 存入 `memory_quotes`（以 `product + price_type + snapshot_date` 為 unique key）。
- `snapshot_date` 設為抓取當日 (UTC+8 台北時間)。
- 加入手動匯入備援：支援讀取 `scripts/data_import/manual_quotes.csv`（欄位：`product`、`price_type`、`price_avg`、`snapshot_date`）。

**Acceptance Criteria / Tests**  
- [ ] 至少抓到 DRAM Spot（DDR4 或 DDR5）一筆資料。
- [ ] 至少抓到 NAND Wafer Spot 一筆資料。
- [ ] `memory_quotes` 中同一品項同一日只有一筆（upsert 有效）。
- [ ] 手動匯入 CSV 功能可用：`python ingest_memory_quotes.py --from-csv manual_quotes.csv`。
- [ ] 若 DRAMeXchange 完全無法抓取（網路問題），`source_runs.status` 為 `fail`，不拋出未處理例外。

---

### ACTION-017：每日 01:00 背景排程 (APScheduler)

**Context**  
設置每天台北時間 01:00 自動執行所有資料抓取 job 的排程，讓系統在無人介入的情況下持續累積歷史資料。

**Spec**  
在 `backend/app/main.py` 的 lifespan 事件中初始化 APScheduler：

```python
scheduler = AsyncIOScheduler(timezone="Asia/Taipei")
scheduler.add_job(
    run_all_ingestion_jobs,
    CronTrigger(hour=1, minute=0),
    id="daily_ingestion",
    replace_existing=True,
    max_instances=1  # 避免重疊執行
)
```

建立 `backend/app/jobs/run_all.py`（`run_all_ingestion_jobs` function）：
1. 取得或建立 `refresh_jobs` lock（`lock_key='daily_ingestion'`）。
2. 若已有 `running` 狀態的 lock，跳過本次執行（log 警告）。
3. 依序執行：台股 → 美股 → 日股 → 韓股 → 記憶體報價 → trend metrics 計算 → 牛熊分數計算。
4. 更新 `refresh_jobs` 狀態與進度。
5. 釋放 lock。

**Acceptance Criteria / Tests**  
- [ ] 排程在台北時間 01:00 觸發（可用 `scheduler.get_job("daily_ingestion").next_run_time` 驗證）。
- [ ] 同時觸發兩次（手動 + 排程），只有一個執行（lock 有效）。
- [ ] `refresh_jobs` 表格有正確的 lock_key、started_at、finished_at 記錄。
- [ ] 若其中一個 job 失敗，仍繼續執行後續 jobs（fail_count 遞增，不中斷整體流程）。

---

### ACTION-018：手動更新 API 端點

**Context**  
提供手動觸發更新的 API，讓 Web UI 和 Android app 的「更新」按鈕可以呼叫。

**Spec**  
建立 `backend/app/routers/refresh.py`：

```
POST /api/refresh
  → 觸發 run_all_ingestion_jobs（背景 asyncio.create_task）
  → 若已有 running job，回傳 HTTP 409 + {"error": "job_already_running", "job_id": "..."}
  → 否則回傳 HTTP 202 + {"job_id": "...", "status": "started", "trigger": "manual"}

GET /api/refresh/status
  → 回傳最近 refresh_jobs 記錄
  → {"job_id": "...", "status": "running/success/fail", "progress": {...}, "started_at": "...", "finished_at": "..."}

GET /api/refresh/status/{job_id}
  → 回傳特定 job 的詳細狀態
```

**Acceptance Criteria / Tests**  
- [ ] `POST /api/refresh` 成功觸發 job，回傳 202 和 job_id。
- [ ] 在 job running 期間再次 `POST /api/refresh`，回傳 409。
- [ ] `GET /api/refresh/status` 回傳最近 job 的進度，`progress.current_source` 正確反映正在抓取的來源。
- [ ] job 完成後 `GET /api/refresh/status` 的 `status` 變為 `success` 或 `fail`。
- [ ] pytest 測試所有端點的 HTTP status code 和 response schema。

---

### ACTION-019：資料新鮮度健康檢查 API

**Context**  
提供 Web UI 和 Android app 開啟時的資料新鮮度檢查，讓 UI 可以判斷是否需要提示更新。

**Spec**  
建立 `GET /api/refresh/health` 端點：
```json
{
  "overall_status": "fresh|stale|critical",
  "equity_prices": {
    "last_updated": "2026-06-23T18:30:00+08:00",
    "hours_since_update": 3.5,
    "is_stale": false,
    "threshold_hours": 12
  },
  "memory_quotes": {
    "last_updated": "2026-06-22T18:30:00+08:00",
    "hours_since_update": 25.1,
    "is_stale": true,
    "threshold_hours": 24
  },
  "last_scheduler_run": {
    "started_at": "...",
    "status": "success",
    "job_id": "..."
  }
}
```
- `overall_status`：若所有資料都新鮮 → `fresh`；有任一過期 → `stale`；超過 2 倍門檻 → `critical`。

**Acceptance Criteria / Tests**  
- [ ] 剛完成更新後，`overall_status` 為 `fresh`。
- [ ] 模擬 equity_prices 最後更新超過 12 小時，回傳 `stale`。
- [ ] 超過 24 小時，回傳 `critical`。
- [ ] pytest 測試三種狀態轉換邏輯。

---

### ACTION-020：基礎查詢 API 端點

**Context**  
提供前端所需的核心資料查詢 API，涵蓋股票日線、記憶體報價、供應鏈分類與牛熊分數的查詢與篩選。

**Spec**  
建立以下端點（`backend/app/routers/`）：

```
GET /api/instruments               ← ACTION-011 已建立
GET /api/prices/{ticker}           ← 股票日線
  query: market, start_date, end_date, period(1W/1M/3M/6M/1Y)
  response: [{date, open, high, low, close, volume}]

GET /api/quotes                    ← 記憶體報價
  query: category(DRAM/NAND/SSD), product, start_date, end_date
  response: [{product, category, price_type, price_avg, change_pct, snapshot_date}]

GET /api/score                     ← 牛熊分數
  query: start_date, end_date
  response: [{score_date, total_score, status, narrative, sub_scores}]

GET /api/score/latest              ← 最新牛熊分數
GET /api/trend_metrics/{ticker}    ← 趨勢指標
  query: market, period, as_of_date
```

所有查詢 API 需支援：
- 分頁（`page`、`page_size`，預設 page_size=100）。
- 回傳 `total_count` 與 `data` 兩層結構。
- 無資料時回傳空陣列（非 404）。

另建立查詢頁專用端點：
```
GET /api/query/stock_table
  query: market, tier, tag, date_from, date_to, sort_by, sort_order, search
  → 整合 instruments + equity_prices + trend_metrics，一次回傳完整股票表格資料
  → 支援 CSV 匯出 (Accept: text/csv)
```

**Acceptance Criteria / Tests**  
- [ ] `GET /api/prices/MU?market=US&period=1Y` 回傳 MU 最近 1 年日線（JSON 格式正確）。
- [ ] `GET /api/quotes?category=DRAM` 回傳所有 DRAM 報價快照。
- [ ] `GET /api/query/stock_table?market=TW&tier=A` 回傳台股 Tier A 的完整資料。
- [ ] CSV 匯出：`Accept: text/csv` header 時回傳正確的 CSV 格式。
- [ ] 分頁正確：第 2 頁不重複第 1 頁資料。
- [ ] pytest 測試所有端點，包含邊界條件（空結果、超出範圍的日期）。

---

### ACTION-021：Trend Metrics 計算 Job

**Context**  
從 `equity_prices` 和 `memory_quotes` 計算所有標的的多期間趨勢指標，存入 `trend_metrics` 表格。這是牛熊分數計算的基礎。

**Spec**  
建立 `backend/app/jobs/compute_trend_metrics.py`：

對每個 instrument（股票）和每個報價品項，計算以下 period 的指標：`1D`、`1W`、`1M`、`3M`、`6M`、`1Y`。

**計算規格**：
- `change_pct`：`(P_today - P_base) / P_base * 100`
  - 1D: base = 前 1 個交易日
  - 1W: base = 前 5 個交易日
  - 1M: base = 前 21 個交易日
  - 3M: base = 前 63 個交易日
  - 6M: base = 前 126 個交易日
  - 1Y: base = 前 252 個交易日
- `direction`：`change_pct > 0.5` → `up`；`change_pct < -0.5` → `down`；其餘 → `flat`
- `ma_state`：計算 20/60/120/240 日移動平均，每個均線記錄 `above`/`below`
- `volatility`：期間內日報酬的年化標準差（`std(daily_returns) * sqrt(252)`）
- `hi_lo_flag`：現價是否為 1M/3M/6M/1Y 最高或最低
- `streak`：連續上漲或下跌天數（正值 = 連漲，負值 = 連跌）
- `normalized_index`：以 1 年前為基準 100，今日相對指數
- `momentum`：`change_pct_1M * 0.5 + change_pct_3M * 0.3 + (ma_above_count / 4 * 100) * 0.2`（-100 到 +100 分）

對 `memory_quotes` 專屬：
- `spot_contract_spread`：同品項 spot 與 contract 的價差百分比（若兩者都存在）

upsert 存入 `trend_metrics`（以 `instrument_id + as_of_date + period` 為 key）。

**Acceptance Criteria / Tests**  
- [ ] 執行後 `trend_metrics` 有資料，且每個 instrument × 每個 period 各一筆。
- [ ] `change_pct` 計算正確：手動驗算 MU 的 1W 報酬，與 API 回傳值一致（誤差 < 0.01%）。
- [ ] `ma_state` 正確：若現價高於 20 日均線，`ma_state.ma20 = "above"`。
- [ ] `streak` 正確：若最後 5 天連漲，`streak = 5`。
- [ ] 重複計算不產生重複列（upsert 有效）。
- [ ] pytest 單元測試：使用模擬價格序列驗證每個計算函式的輸出。

---

### ACTION-022：牛熊分數計算引擎

**Context**  
整合多維度指標計算 0-100 的記憶體市場牛熊總分，並存入 `market_scores`。分數需可解釋，能展開各子分數與說明。

**Spec**  
建立 `backend/app/jobs/compute_market_score.py`：

```
score = 50
  + quote_momentum_score * 0.40
  + equity_momentum_score * 0.25
  + breadth_score * 0.10
  + risk_score_adj * 0.15   (risk 分數為負面因子，越高風險越扣分)
  + relative_strength_score * 0.10
```

**各子分數計算規格**：

1. **`quote_momentum_score` (記憶體報價動能，-50~+50)**
   - 取 DRAM（DDR4/DDR5 spot avg）和 NAND（wafer spot avg）的 1W/1M/3M 加權 change_pct
   - 權重：1W=20%, 1M=50%, 3M=30%
   - 加分：均線方向向上加分，新高旗標加分
   - 轉換到 -50~+50 範圍

2. **`equity_momentum_score` (核心記憶體股票動能，-50~+50)**
   - 只納入 Tier A 標的與 score_only_observe=false 標的
   - 各標的的 `momentum` 分數加權平均（以 `score_weight` 為權重）
   - 轉換到 -50~+50 範圍

3. **`breadth_score` (供應鏈廣度，0~+50)**
   - 計算 Tier A/B 記憶體相關股票中，站上 20D 均線的比例 (P20) 和站上 60D 均線的比例 (P60)
   - `breadth_raw = P20 * 0.4 + P60 * 0.6`
   - 轉換到 0~+50 範圍

4. **`risk_score_adj` (波動與回撤，-30~0)**
   - 計算 Tier A 籃子的 1M 波動（年化標準差）和最大回撤
   - 波動越高、回撤越大則扣分越多（負值）
   - 轉換到 -30~0 範圍

5. **`relative_strength_score` (相對強弱，-25~+25)**
   - 計算記憶體股票籃子相對大盤指數（Nasdaq/TAIEX/KOSPI）的超額報酬
   - 轉換到 -25~+25 範圍

**狀態映射**：
- 0-20: `strong-bear`
- 21-40: `bear`
- 41-60: `neutral`
- 61-80: `bull`
- 81-100: `strong-bull`

**Narrative（白話說明）**：
自動生成說明文字，例如：
```json
{
  "summary": "記憶體市場偏牛（62分），DRAM 現貨月漲 12% 為主要驅動力",
  "quote": "DDR5 spot 1M +12%，NAND wafer 1M -3%",
  "equity": "Tier A 股票 78% 站上 60 日均線",
  "risk": "月波動率偏低 (15%)，最大回撤 -8%",
  "relative": "記憶體籃子 1M 超額 Nasdaq +5%"
}
```

**Acceptance Criteria / Tests**  
- [ ] 計算結果存入 `market_scores` 表格，欄位完整。
- [ ] 總分在 0-100 範圍內（不得超出）。
- [ ] 在所有 DRAM 報價為正向、股票全部站上均線的測試資料下，分數應 > 60（偏牛）。
- [ ] 在報價全線下跌、股票全部跌破均線的測試資料下，分數應 < 40（偏熊）。
- [ ] `narrative` JSON 格式正確，summary 包含總分與主要驅動因子。
- [ ] pytest 單元測試：各子分數函式的邊界條件測試。

---

## PHASE 2 — 一頁式 Dashboard（含 UI 升級）

---

### ACTION-023：前端專案骨架 (React + Vite + TypeScript)

**Context**  
建立前端應用的基礎，使用 React 18 + Vite + TypeScript 組合，配置開發環境、路由與 API 客戶端。

**Spec**  
在 `frontend/` 目錄下使用 Vite 初始化 React TypeScript 專案：

```bash
cd frontend && npx create-vite . --template react-ts
```

安裝核心依賴：
- `react-router-dom@6`（頁面路由）
- `@tanstack/react-query@5`（API 狀態管理與快取）
- `axios`（HTTP 客戶端）
- `echarts` + `echarts-for-react`（基礎圖表）
- `lightweight-charts@4`（TradingView 核心趨勢圖）
- `react-beautiful-dnd` 或 `@dnd-kit/core`（Widget 拖曳）
- `date-fns`（日期處理）

設定：
- `vite.config.ts`：dev server port = 8510，API proxy → `http://localhost:3000`。
- `src/api/client.ts`：axios 實例，baseURL = `/api`，統一錯誤處理。
- `src/api/hooks/`：使用 React Query 封裝各 API 呼叫的 custom hooks。
- 路由（React Router）：
  - `/`：主 Dashboard 頁
  - `/query`：Web UI 查詢頁
  - `/indicators`：指標說明頁

**Acceptance Criteria / Tests**  
- [ ] `npm run dev` 在 port 8510 啟動，瀏覽器可開啟。
- [ ] API proxy 有效：`fetch('/api/health')` 在瀏覽器中正確打到 `http://localhost:3000/health`。
- [ ] TypeScript 嚴格模式（`strict: true`）開啟，無 type error。
- [ ] 路由正確：`/`、`/query`、`/indicators` 各自渲染不同頁面（暫時放 placeholder）。
- [ ] `npm run build` 可成功建置（無 build error）。

---

### ACTION-024：全域設計系統與深色主題

**Context**  
建立整個 Dashboard 的視覺設計基礎：深色主題、色彩系統、字型、間距、玻璃擬物化效果與微動畫基礎。這是後續所有 UI 元件的依賴。

**Spec**  
建立 `frontend/src/styles/`：

**`theme.css`（CSS 自訂屬性）**：
```css
:root {
  /* 背景 */
  --bg-primary: #0a0e1a;      /* 深海軍藍底色 */
  --bg-secondary: #111827;    /* 卡片底色 */
  --bg-glass: rgba(255,255,255,0.04);  /* 玻璃效果 */
  --bg-glass-border: rgba(255,255,255,0.08);
  
  /* 強調色 */
  --color-bull: #00e676;       /* 上漲翠綠 */
  --color-bear: #ff1744;       /* 下跌警紅 */
  --color-neutral: #90a4ae;    /* 持平灰 */
  --color-accent: #7c3aed;     /* 主色調（紫霓虹）*/
  --color-accent-glow: rgba(124,58,237,0.3);
  
  /* 文字 */
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #475569;
  
  /* 間距與圓角 */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 20px;
  
  /* 動畫 */
  --transition-fast: 150ms ease;
  --transition-base: 300ms ease;
  --transition-slow: 500ms ease;
}
```

**Glassmorphism 卡片共用樣式**：
```css
.glass-card {
  background: var(--bg-glass);
  border: 1px solid var(--bg-glass-border);
  backdrop-filter: blur(16px);
  border-radius: var(--radius-lg);
  padding: 20px;
}
```

**字型**：引入 Google Fonts `Inter`（body）和 `JetBrains Mono`（數字/代號）。

**數字跳動動畫 hook**：建立 `useSmoothCounter(targetValue, duration)` hook，讓數字在更新時平滑過渡。

**顏色工具函式** (`src/utils/colorUtils.ts`)：
- `getChangeColor(pct: number): string`：正值回傳 `--color-bull`，負值 `--color-bear`，零 `--color-neutral`。
- `getHeatmapColor(pct: number, maxAbs: number): string`：依熱力圖色階回傳 rgba 色值。

**Acceptance Criteria / Tests**  
- [ ] 網頁背景為深色（`#0a0e1a`）。
- [ ] 卡片有玻璃擬物化效果（backdrop-filter blur 可見）。
- [ ] `getChangeColor(5)` 回傳綠色、`getChangeColor(-3)` 回傳紅色。
- [ ] `useSmoothCounter` hook：數值從 0 → 62 時，瀏覽器中可見平滑遞增動畫（約 500ms）。
- [ ] 數字欄位使用 JetBrains Mono 等寬字型。

---

### ACTION-025：頂部狀態列元件

**Context**  
Dashboard 最頂部的高信息密度狀態列，顯示總牛熊分數、各指標快速摘要、期間切換按鈕與最後更新時間。

**Spec**  
建立 `frontend/src/components/TopBar/TopBar.tsx`：

**佈局（水平排列）**：
```
[品牌名/LOGO] [牛熊分數Badge] [DRAM指標] [NAND指標] [股票籃子指標] [spacer] [期間切換] [更新時間] [更新按鈕]
```

**各部分規格**：
- **牛熊分數 Badge**：大字體顯示分數（如 `62`），旁邊小字狀態（`偏牛`），依狀態變色（強牛=亮綠發光，強熊=亮紅發光）。
- **DRAM/NAND/股票指標**：各顯示「指標名 + 箭頭 + 變化率」，例如 `DRAM ↑ +3.2%`，顏色依漲跌。
- **期間切換**：Button group（`1W | 1M | 3M | 6M | 1Y`），選中狀態高亮，切換時觸發全域 context 更新（影響所有圖表與表格的顯示期間）。
- **更新時間**：小字顯示「最後更新：HH:MM」，若資料過期顯示警示色。
- **更新按鈕**：按下觸發 `POST /api/refresh`，loading 狀態顯示旋轉動畫，完成後顯示成功/失敗。

**全域 Period Context**：
建立 `src/context/PeriodContext.tsx`，提供當前選擇的 period 給所有子元件。

**Acceptance Criteria / Tests**  
- [ ] 頂部狀態列在 1440px 桌機寬度下一行顯示，不換行。
- [ ] 切換期間按鈕後，`PeriodContext.period` 變更（可用 React DevTools 驗證）。
- [ ] 更新按鈕 loading 期間不可重複點擊（disabled 狀態）。
- [ ] 牛熊 Badge 分數 > 80 時，有 CSS glow 效果（`box-shadow` 帶顏色）。

---

### ACTION-026：動態發光牛熊溫度計元件

**Context**  
以視覺化儀表盤形式呈現 0-100 牛熊總分，讓使用者一眼感受市場溫度。包含動態發光與呼吸燈效果。

**Spec**  
建立 `frontend/src/components/BullBearGauge/BullBearGauge.tsx`：
- 使用 ECharts Gauge 圖表（`series[0].type = 'gauge'`）。
- 色段：0-20 紅色漸層、21-40 橘紅、41-60 灰藍、61-80 綠、81-100 亮翠綠。
- 中心顯示大字分數 + 下方狀態文字（`強熊 / 偏熊 / 中性 / 偏牛 / 強牛`）。
- 指針平滑動畫：分數更新時，指針以 800ms 動畫移動到新位置。
- **呼吸燈效果**：當分數 < 20 或 > 80 時，元件外框有 CSS `@keyframes pulse-glow` 動畫，發光顏色對應紅/綠。

**Props**：
```typescript
interface BullBearGaugeProps {
  score: number;         // 0-100
  status: string;        // strong-bull / bull / neutral / bear / strong-bear
  narrative?: {          // 可展開的說明
    summary: string;
    quote: string;
    equity: string;
    risk: string;
    relative: string;
  };
  onExpand?: () => void; // 點擊展開詳情
}
```

**Acceptance Criteria / Tests**  
- [ ] 分數從 0 變為 75 時，指針動畫平滑（不閃跳）。
- [ ] 分數 85 時，元件外框可見呼吸燈（肉眼可見 pulse 效果）。
- [ ] 分數 15 時，外框呼吸燈為紅色。
- [ ] 分數 55 時，無呼吸燈（只有靜態外框）。
- [ ] 點擊元件，`onExpand` 被呼叫。

---

### ACTION-027：五維雷達圖元件

**Context**  
以五維雷達圖展開牛熊分數的五個組成維度，讓使用者一眼看出市場當前的動力結構。

**Spec**  
建立 `frontend/src/components/RadarChart/ScoreRadarChart.tsx`：
- 使用 ECharts Radar 圖。
- 五個維度：`報價動能`、`股票動能`、`供應鏈廣度`、`風險（反向）`、`相對強弱`。
- 每個維度 0-100 分（子分數標準化到 0-100）。
- 填充區域用半透明漸層（accent 紫色）。
- 懸停於某個頂點時，顯示該維度的 narrative 說明文字（Tooltip）。

**Props**：
```typescript
interface ScoreRadarChartProps {
  scores: {
    quote_momentum: number;
    equity_momentum: number;
    breadth: number;
    risk_inverse: number;      // 100 - risk_penalty（風險越低分越高）
    relative_strength: number;
  };
  narrative: Record<string, string>;
}
```

**Acceptance Criteria / Tests**  
- [ ] 雷達圖渲染五個軸，標籤可讀。
- [ ] 五個維度都很高時（>80），填充區域接近完整圓形。
- [ ] 懸停軸點顯示對應的 narrative 說明。
- [ ] 分數更新時，填充區域有平滑過渡動畫。

---

### ACTION-028：大趨勢圖元件 (lightweight-charts)

**Context**  
核心趨勢圖，使用 TradingView lightweight-charts 顯示記憶體報價指數與股票籃子指數的歷史走勢，支援縮放、技術指標與歷史事件標注。

**Spec**  
建立 `frontend/src/components/TrendChart/TrendChart.tsx`：

使用 `lightweight-charts` 建立圖表：
- **左軸（LineSeries）**：標準化 DRAM/NAND 報價指數（normalized_index，基準日=100）。
- **右軸（LineSeries）**：記憶體股票籃子指數。
- **可切換疊加**：按鈕組（`DRAM | NAND | 股票 | 全部`），切換時 smooth 更新圖表 series。
- **技術指標疊加**（可選顯示）：MA20（黃）、MA60（橘）、MA120（紅）。
- **歷史事件標記**（Event Overlays，Phase 5 介面預留）：
  - 使用 `createSeriesMarker` 在時間軸上標記重大事件（圓形標記 + 懸停顯示事件說明）。
  - 現階段支援手動硬編碼測試事件，Phase 5 再串接 API。
- **十字準線**：滑動時顯示精確的日期與數值。
- **Range selector**：圖表下方提供 1M / 3M / 6M / 1Y / ALL 快速選擇。

**Acceptance Criteria / Tests**  
- [ ] 圖表可渲染，x 軸為日期，y 軸為數值。
- [ ] 滾輪縮放和拖曳功能正常。
- [ ] 切換「DRAM / NAND / 股票 / 全部」後，圖表 series 正確更新（非閃爍）。
- [ ] 懸停顯示十字準線與對應日期、數值。
- [ ] MA20 疊加線可切換顯示/隱藏。

---

### ACTION-029：報價熱力表元件

**Context**  
以熱力矩陣方式呈現各記憶體報價品項的多期間漲跌，讓使用者一眼看出哪個品項、哪個期間最強或最弱。

**Spec**  
建立 `frontend/src/components/QuoteHeatmap/QuoteHeatmap.tsx`：

**表格結構**（行 = 品項，列 = 期間）：

| 品項 | 1D | 1W | 1M | 3M | 6M | 1Y |
|---|---|---|---|---|---|---|
| DDR5 spot | +0.5% | +4.2% | +12.1% | ... | ... | ... |
| DDR4 spot | -0.1% | +1.0% | +3.2% | ... | ... | ... |
| NAND TLC wafer | ... | ... | ... | ... | ... | ... |

**視覺規格**：
- 每個格子背景色依 `getHeatmapColor(pct, maxAbs)` 填充（正綠負紅，色深依幅度）。
- 格子內顯示百分比數字，顏色為白（深色背景）或黑（淺色背景），確保對比度。
- 懸停格子時顯示 Tooltip：品項全名 + 期間定義 + 變化率 + 30 日 Sparkline 迷你圖。
- 點擊品項名稱 → 展開品項詳情圖（modal 或 slide-in panel）。

**期間說明 Tooltip**（ⓘ 按鈕觸發）：
每個期間欄標題旁有 ⓘ 圖示，懸停顯示期間定義說明（例如「1M = 相對約 21 個交易日前的漲跌幅」）。

**Acceptance Criteria / Tests**  
- [ ] 表格正確渲染所有品項 × 期間組合。
- [ ] 最高漲幅格子背景最深綠，最高跌幅最深紅（視覺熱力圖效果）。
- [ ] 懸停格子，Tooltip 在 200ms 內出現（不閃爍）。
- [ ] 點擊品項名稱，詳情圖出現。
- [ ] ⓘ Tooltip 顯示期間說明文字。

---

### ACTION-030：股票追蹤表元件

**Context**  
按市場分組顯示所有追蹤股票的關鍵指標，包含各期間報酬、均線狀態與相對強弱。

**Spec**  
建立 `frontend/src/components/StockTable/StockTable.tsx`：

**表格欄位**：
`代號 | 名稱 | 最新價 | 1D | 1W | 1M | 3M | 1Y | 成交量 | 均線狀態 | 動能 | 趨勢徽章`

**市場分組**：使用 Tab 或 Accordion 分組：`全部 | 美股 | 韓股 | 台股(核心) | 台股(觀察)`

**趨勢徽章（Trend Badge）**：
- 依 `direction`、`momentum`、`streak` 自動生成，例如：
  - `📈 月線上升・趨勢轉強`（direction=up, momentum>30, streak>3）
  - `⚠️ 週線急跌・留意`（1W change < -5%）
  - `➡️ 年線盤整`（direction=flat）
- 徽章顏色：上升系列=綠，下跌系列=紅，中性=灰。

**均線狀態 Bar**：
用 4 個小點（20D/60D/120D/240D）表示站上/跌破狀態，亮綠=站上，暗紅=跌破。

**排序**：點擊欄位標題可排序（預設依 1M 報酬降序）。

**Acceptance Criteria / Tests**  
- [ ] 表格渲染，欄位齊全。
- [ ] 市場 Tab 切換後只顯示對應市場股票。
- [ ] 點擊「1M」欄標題，表格依 1M 報酬排序。
- [ ] 趨勢徽章對應規則正確（連漲 3 天且 1W 正 → `📈 週線上升`）。
- [ ] 均線 4 點顯示正確（站上 20D 但跌破 60D → 第 1 點亮第 2 點暗）。

---

### ACTION-031：懸浮資訊卡 (Sparkline Tooltip) 元件

**Context**  
滑鼠懸停在股票代號或報價品項時，彈出包含 30 日走勢迷你圖與簡介的資訊卡，減少使用者點擊跳轉。

**Spec**  
建立 `frontend/src/components/SparklineTooltip/SparklineTooltip.tsx`：
- 使用 Floating UI 或自訂 Portal 定位（避免被父元素 overflow:hidden 裁切）。
- 資訊卡內容：
  - 股票代號 + 名稱（中文）+ 市場
  - Tier 標籤（A/B/C）+ 供應鏈分類標籤
  - 30 日走勢 Sparkline（使用 ECharts line 圖，無軸，僅顯示線條與面積）
  - 最新收盤價 + 1D 漲跌幅
- 出現/消失動畫：fade + slight upward movement（200ms）。
- 延遲顯示：hover 後 300ms 才出現（避免快速滑過觸發）。
- 資料由 React Query 懶加載（首次 hover 才 fetch，之後快取）。

**Acceptance Criteria / Tests**  
- [ ] Hover 股票代號 300ms 後，資訊卡出現在代號旁邊（不被遮蔽）。
- [ ] 資訊卡快速移出後立即消失（無殘影）。
- [ ] Sparkline 正確顯示最近 30 日趨勢（上漲為綠色區域，下跌為紅色）。
- [ ] 資料懶加載：第一次 hover 後觸發 API 請求，第二次 hover 使用快取（Network tab 驗證）。

---

### ACTION-032：領先/落後排行榜元件

**Context**  
顯示當前期間內表現最佳和最差的報價品項與股票，並標注異常波動。

**Spec**  
建立 `frontend/src/components/LeaderBoard/LeaderBoard.tsx`：

分為三個子列表：
1. **報價 Top Movers**：依當前期間 change_pct 排序，顯示前 5 名上漲和前 5 名下跌。
2. **股票 Top Movers**：同上，但只針對 Tier A 股票。
3. **異常波動提示**：1D 漲跌幅 > 5% 的標的，標注 `⚠️ 異常波動`。

每列顯示：排名、代號/品項名、變化率（帶顏色箭頭）、Sparkline（7 日）。

排行榜依 `PeriodContext.period` 動態更新（切換期間後 re-sort）。

**Acceptance Criteria / Tests**  
- [ ] 排行榜依當前期間正確排序（切換到 1Y 後重新排序）。
- [ ] 異常波動標注正確出現（當日漲跌 > 5%）。
- [ ] 7 日 Sparkline 正確顯示。

---

### ACTION-033：資料來源狀態與更新進度元件

**Context**  
讓使用者清楚知道資料的新鮮度、各資料源狀態，以及手動更新的進度。

**Spec**  
建立 `frontend/src/components/DataStatus/DataStatus.tsx`：
- 從 `GET /api/refresh/health` 取得新鮮度資訊。
- 從 `GET /api/refresh/status` 取得最近 job 狀態。
- 顯示：
  - 整體狀態指示燈（🟢 Fresh / 🟡 Stale / 🔴 Critical）
  - 各資料源最後更新時間（股票、報價）
  - 每日 01:00 排程最後執行結果（成功/失敗）
  - 若有 job 執行中：顯示進度條 + 當前正在抓取的來源
  - 「立即更新」按鈕
- 若 `overall_status === 'stale'`，頂部顯示橘色提示橫幅（不遮擋主要內容）。
- 輪詢：job 執行中時每 3 秒 polling `GET /api/refresh/status`（完成後停止）。

**Acceptance Criteria / Tests**  
- [ ] 整體狀態燈隨 API 回傳正確切換顏色。
- [ ] 更新按鈕觸發 API 請求，按下後按鈕進入 loading 狀態。
- [ ] job 執行中時，進度條有動畫，current_source 文字更新。
- [ ] job 完成後停止輪詢（不繼續發請求）。

---

### ACTION-034：Web UI 查詢頁

**Context**  
提供完整的資料查詢介面，讓使用者可以篩選、排序、搜尋資料，並匯出 CSV。

**Spec**  
建立 `frontend/src/pages/QueryPage/QueryPage.tsx`（路由：`/query`）：

**篩選面板（左側 / 頂部）**：
- 市場多選（TW / US / JP / KR）
- Tier 多選（A / B / C）
- 供應鏈分類多選（下拉選單，從 `GET /api/instruments` 動態取得所有 tag）
- 日期區間選擇（start_date / end_date）
- 資料源狀態（全部 / 成功 / 失敗）
- 代號或名稱搜尋（text input，即時篩選）

**資料表格**：
- 呼叫 `GET /api/query/stock_table`，顯示完整股票資料表。
- 欄位：代號、名稱、市場、Tier、最新價、各期間報酬、均線狀態。
- 欄位點擊排序（正/反序切換）。
- 虛擬化捲動（`@tanstack/react-virtual`），支援大量資料不卡頓。

**匯出功能**：
- 「匯出 CSV」按鈕：下載當前篩選結果的 CSV（呼叫 API 帶 `Accept: text/csv`）。

**Acceptance Criteria / Tests**  
- [ ] 篩選市場=US，表格只顯示美股資料。
- [ ] 搜尋 "MU"，表格只顯示包含 "MU" 的代號或名稱。
- [ ] 點擊「1M 報酬」欄排序，資料正確重排。
- [ ] 點擊「匯出 CSV」，瀏覽器下載一個有效的 .csv 檔案，內容與表格一致。
- [ ] 500 筆資料時，表格捲動流暢（FPS > 30）。

---

### ACTION-035：指標說明頁與 ⓘ Tooltip

**Context**  
集中說明所有指標的定義、計算方式與解讀指引，同時在各元件中加入 ⓘ 懸停說明。

**Spec**  
建立 `frontend/src/pages/IndicatorsPage/IndicatorsPage.tsx`（路由：`/indicators`）：

頁面結構（Accordion 展開）：
- **期間定義**：1D/1W/1M/3M/6M/1Y 各期間的交易日計算方式。
- **趨勢指標**：change_pct / direction / momentum / ma_state / hi_lo_flag / streak / acceleration 各自的定義 + 計算公式 + 解讀範例。
- **牛熊分數**：總分計算公式 + 五個子分數說明。
- **熱力圖色階**：顏色深度對應的幅度範圍說明。

建立 `frontend/src/components/InfoTooltip/InfoTooltip.tsx`（ⓘ 通用說明元件）：
- `<InfoTooltip text="說明文字" />` 渲染一個 ⓘ 圖示，懸停顯示說明氣泡。
- 供 QuoteHeatmap、StockTable 等元件的欄位標題使用。

**Acceptance Criteria / Tests**  
- [ ] `/indicators` 頁面可正常開啟，所有 Accordion 可展開/收合。
- [ ] InfoTooltip 組件在其他元件中使用後，ⓘ 懸停顯示正確說明文字。
- [ ] 所有指標均有清楚的中文說明（人工確認內容品質）。

---

### ACTION-036：RWD 手機版佈局（底部導覽列 + Swipeable Cards）

**Context**  
針對行動裝置（Android PWA/APK）優化 Dashboard 佈局，加入底部導覽列和滑動式資料卡片。

**Spec**  
使用 CSS Media Query (`@media (max-width: 768px)`)：

**底部導覽列**（`frontend/src/components/BottomNav/BottomNav.tsx`）：
- 固定在螢幕底部。
- 四個 Tab：`總覽 (🏠) | 報價 (💾) | 個股 (📊) | 設定 (⚙️)`。
- 點擊各 Tab 捲動到對應區塊（`id` anchor）或切換頁面。
- 只在 `max-width: 768px` 顯示，桌機版隱藏。

**Swipeable Cards**：
- 在手機版，將股票追蹤表（StockTable）改為可左右滑動的卡片。
- 每張卡片顯示：代號、名稱、最新價、1D 漲跌、趨勢徽章、7 日 Sparkline。
- 使用 CSS `scroll-snap` 實現滑動效果。

**桌機版佈局**：
- `display: grid; grid-template-columns: 1fr 1fr;`（大螢幕兩欄）。
- `max-width: 768px` 改為單欄。

**Acceptance Criteria / Tests**  
- [ ] 在 375px 寬度（iPhone SE）下，底部導覽列正確顯示在最底部，主內容不被遮蔽（加 padding-bottom）。
- [ ] 在 1440px 桌機寬度下，底部導覽列不顯示。
- [ ] Swipeable Cards 在手機模擬器下可正常左右滑動。
- [ ] 滑動到最後一張卡片後，不繼續滑動（scroll-snap 邊界正確）。

---

### ACTION-037：微動畫與流暢轉場系統

**Context**  
為整個 Dashboard 加入協調一致的微動畫，提升精緻感與互動反饋。

**Spec**  
建立 `frontend/src/styles/animations.css`：

```css
/* 元件淡入 */
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up {
  animation: fade-in-up var(--transition-base) ease both;
}

/* 呼吸燈（牛熊 Gauge 用）*/
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 8px currentColor; }
  50% { box-shadow: 0 0 24px currentColor, 0 0 48px currentColor; }
}

/* 數字更新閃爍 */
@keyframes value-flash {
  0% { opacity: 1; }
  30% { opacity: 0.4; }
  100% { opacity: 1; }
}
```

**轉場時機規格**：
- Dashboard 首次載入：各 Widget 依序（stagger）淡入（每個延遲 50ms）。
- 期間切換（1W/1M/...）：所有數值以 `value-flash` 閃爍一次表示已更新。
- 更新按鈕完成後：狀態燈以 `fade-in-up` 更新。
- Tooltip 出現/消失：`fade-in-up`（出現）+ `fade-out`（消失）200ms。

建立 `useMountAnimation(delay: number)` hook，自動在元件掛載時應用進場動畫。

**Acceptance Criteria / Tests**  
- [ ] 首次進入 Dashboard，各卡片從下方淡入，有時差（stagger）效果。
- [ ] 切換期間後，所有數字短暫閃爍（可肉眼感受）。
- [ ] 所有動畫尊重 `prefers-reduced-motion` media query（accessibility）：若使用者設定減少動畫，所有動畫停用。

---

## PHASE 3 — 評分、告警與進階分析

---

### ACTION-038：告警規則 CRUD API

**Context**  
提供告警規則的新增、查詢、更新、停用 API，讓使用者可以設定當特定指標觸發特定條件時自動通知。

**Spec**  
建立 `backend/app/routers/alerts.py`：

```
GET    /api/alerts/rules            → 查詢所有告警規則
POST   /api/alerts/rules            → 新增告警規則
PATCH  /api/alerts/rules/{id}       → 更新規則（含啟用/停用）
DELETE /api/alerts/rules/{id}       → 刪除規則

GET    /api/alerts/events           → 查詢告警觸發歷史
  query: rule_id, start_date, end_date, status
```

**告警規則 Schema**（`POST /api/alerts/rules` body）：
```json
{
  "rule_name": "DRAM 現貨單日大跌",
  "metric": "dram_spot_1d_change",
  "condition": "lt",
  "threshold": -3.0,
  "channel": "telegram",
  "is_active": true
}
```

支援的 `metric` 值：
- `total_score`（牛熊總分）
- `dram_spot_1d_change`（DRAM 現貨單日變化率）
- `nand_wafer_ma_cross`（NAND Wafer 突破季線）
- `stock_1d_change.<ticker>`（特定股票單日漲跌）

支援的 `condition`：`gt`、`lt`、`cross_up`、`cross_down`。

**Acceptance Criteria / Tests**  
- [ ] `POST /api/alerts/rules` 建立規則後，`GET /api/alerts/rules` 可查到。
- [ ] 規則的 `is_active` 可透過 `PATCH` 切換。
- [ ] 不合法的 `metric` 或 `condition` 值，回傳 422（Validation Error）。
- [ ] pytest 測試所有 CRUD 端點。

---

### ACTION-039：告警觸發引擎

**Context**  
定期（每日資料更新後）評估所有啟用中的告警規則，若條件觸發則發出通知。

**Spec**  
建立 `backend/app/jobs/evaluate_alerts.py`：
- 在 `run_all_ingestion_jobs` 完成後自動執行。
- 對每個 `is_active=True` 的告警規則：
  1. 從 `market_scores`、`trend_metrics`、`memory_quotes` 取得對應指標最新值。
  2. 判斷條件是否觸發（`gt`/`lt`/`cross_up`/`cross_down`）。
  3. 若觸發，呼叫對應渠道的推播函式（ACTION-040/041/042）。
  4. 寫入 `alert_events`（含觸發值、推播結果）。
- `cross_up`/`cross_down` 需比較「昨日」與「今日」的值是否越過 threshold。

**Acceptance Criteria / Tests**  
- [ ] 建立規則「total_score lt 40」，模擬分數從 45 → 35 → 觸發告警，`alert_events` 有一筆記錄。
- [ ] 同一規則連續觸發兩天，`alert_events` 有兩筆記錄（每次都通知）。
- [ ] `cross_up` 規則：分數昨天 38、今天 42（閾值 40）→ 觸發；昨天 42、今天 45 → 不觸發（未越過）。
- [ ] 推播失敗（網路錯誤），`alert_events.notify_status` = `failed`，但不影響其他規則繼續評估。

---

### ACTION-040：Telegram Bot 推播整合

**Context**  
串接 Telegram Bot API，發送告警通知和每日摘要。

**Spec**  
建立 `backend/app/services/telegram_notifier.py`：
```python
async def send_telegram(message: str) -> bool:
    """
    使用 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 環境變數
    呼叫 https://api.telegram.org/bot<token>/sendMessage
    message 支援 Markdown format
    失敗時 retry 2 次，回傳 True/False
    """
```

告警訊息格式（Markdown）：
```
🔔 *記憶體儀錶板告警*
規則：DRAM 現貨單日大跌
觸發值：-3.8%（閾值：< -3.0%）
時間：2026-06-23 18:30 台北時間
[查看儀錶板](http://localhost:8510)
```

**Acceptance Criteria / Tests**  
- [ ] 若 `TELEGRAM_BOT_TOKEN` 或 `TELEGRAM_CHAT_ID` 未設定，函式回傳 `False` 並 log warning，不拋出例外。
- [ ] 模擬 Telegram API 超時，retry 2 次後回傳 `False`。
- [ ] （整合測試）設定有效 token，發送測試訊息後 Telegram 確實收到（人工驗證）。

---

### ACTION-041：Line Notify 推播整合

**Context**  
串接 Line Notify API，作為 Telegram 的替代推播渠道。

**Spec**  
建立 `backend/app/services/line_notifier.py`：
```python
async def send_line(message: str) -> bool:
    """
    使用 LINE_NOTIFY_TOKEN 環境變數
    POST https://notify-api.line.me/api/notify
    message = "記憶體儀錶板告警\n規則：...\n觸發值：..."
    """
```

**Acceptance Criteria / Tests**  
- 同 ACTION-040，測試無效 token 時的優雅降級。

---

### ACTION-042：Email 推播整合

**Context**  
串接 SMTP 發送告警 Email，使用 HTML 格式呈現豐富的每日摘要。

**Spec**  
建立 `backend/app/services/email_notifier.py`：
- 使用 `smtplib` 或 `aiosmtplib`。
- 環境變數：`SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASS`、`ALERT_EMAIL_TO`。
- 告警 Email：純文字 + HTML 兩份（multipart/alternative）。
- HTML 模板：紅/綠標題、規則說明表格、連結按鈕。

**Acceptance Criteria / Tests**  
- [ ] SMTP 設定有效時，Email 成功發送（人工確認收件匣）。
- [ ] SMTP 設定無效時，函式回傳 `False`，不拋出未處理例外。

---

### ACTION-043：每日收盤摘要推送 Job

**Context**  
在每天美股收盤後（台北時間約 05:00 或 06:00，夏令/冬令時間不同），自動推送當日記憶體市場摘要到指定渠道。

**Spec**  
在 APScheduler 加入第二個定時任務（台北時間 05:30）：

呼叫 `send_daily_summary()`：
1. 取得最新 `market_scores`（今日牛熊分數與 narrative）。
2. 取得今日 Top Movers（DRAM/NAND 報價最大漲跌）。
3. 取得 Tier A 股票今日表現（前 3 強、前 3 弱）。
4. 組合成摘要訊息，發送到所有已設定渠道（Telegram / Line / Email）。

摘要格式（Telegram Markdown 範例）：
```
📊 *記憶體市場日報 2026-06-23*
────────────────
牛熊評分：62分（偏牛）↑ 昨日+3分
DRAM 綜合：月漲 +12%
NAND 綜合：月跌 -3%
────────────────
📈 今日強勢：
  MU +4.2% | 南亞科 +3.1%
📉 今日弱勢：
  Samsung -1.2%
────────────────
[完整儀錶板](http://localhost:8510)
```

**Acceptance Criteria / Tests**  
- [ ] 05:30 排程正確設定（驗證 next_run_time）。
- [ ] 訊息內容包含牛熊分數、DRAM/NAND 摘要、強弱個股。
- [ ] 若 `market_scores` 沒有今日資料，摘要標注「今日資料尚未更新」，仍正常發送。
- [ ] 所有推播渠道的 token 未設定時，跳過對應渠道（不中斷）。

---

### ACTION-044：相關性矩陣計算 Job

**Context**  
計算個股（尤其是 Tier B 模組廠、控制 IC 廠）與 DRAM/NAND 報價之間的滾動相關係數，讓使用者發現「報價敏感股」與「落後補漲」標的。

**Spec**  
建立 `backend/app/jobs/compute_correlation.py`：

**計算規格**：
- 對每個 Tier A/B 股票，計算其 close price 日報酬與以下報價的日報酬的滾動相關係數：
  - DRAM DDR4 spot（`memory_quotes` 中 `product like 'DDR4%'`）
  - DRAM DDR5 spot
  - NAND TLC wafer spot
- 滾動窗格：`60` 和 `120` 個交易日。
- 相關係數範圍：-1 到 +1，0.7 以上視為高度相關，0.3 以下視為低度相關。

結果存入 `correlation_matrix` 表格（需在 ACTION-009 schema 中已建立）。

**Acceptance Criteria / Tests**  
- [ ] 計算結果存入 DB，每個（股票, 報價品項, 窗格）三元組有一筆最新資料。
- [ ] MU 與 DRAM DDR4 報價的 60 日相關係數應明顯為正（預期 > 0.5，人工確認）。
- [ ] 若某股票的報價資料不足 60 筆，該窗格的相關係數標記為 `null`。

---

### ACTION-045：相關性矩陣 UI 元件

**Context**  
以熱力圖矩陣視覺化個股與報價的相關係數，讓使用者快速找出敏感標的。

**Spec**  
建立 `frontend/src/components/CorrelationMatrix/CorrelationMatrix.tsx`：

- 行 = 股票（Tier A/B）
- 列 = 報價品項（DDR4/DDR5/NAND TLC 等）
- 格子顏色：1 = 深藍、0 = 白、-1 = 深紅（雙向熱力圖）
- 格子顯示係數數值（小字）
- 懸停 Tooltip：顯示「股票名稱 vs 報價品項，60 日相關係數 0.78，表示兩者趨勢高度正相關」
- 欄位切換：`60 日 | 120 日` 視窗切換

**Acceptance Criteria / Tests**  
- [ ] 矩陣正確渲染，行列標籤可讀。
- [ ] 係數 = 1 的格子為深藍色，係數 = -1 的格子為深紅色。
- [ ] 切換 60/120 日窗格後，格子顏色更新。
- [ ] 係數為 `null` 的格子顯示「N/A」（灰色）。

---

## PHASE 4 — PWA / Android APK

---

### ACTION-046：PWA Manifest 與離線快取

**Context**  
將 Web 應用升級為 Progressive Web App，支援加入 Android 主畫面和基礎離線快取。

**Spec**  
在 `frontend/public/` 目錄建立：

**`manifest.json`**：
```json
{
  "name": "記憶體趨勢儀錶板",
  "short_name": "MemDash",
  "description": "DRAM/NAND/Flash 報價與供應鏈股票即時追蹤",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0a0e1a",
  "theme_color": "#7c3aed",
  "icons": [
    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}
  ]
}
```

建立 App Icon（192px 和 512px，深色背景 + 記憶體晶片圖示）。

**Service Worker**（使用 `vite-plugin-pwa`）：
- 快取策略：
  - Static assets（JS/CSS）：Cache First
  - `/api/instruments`：Cache First，背景更新
  - `/api/score/latest`、`/api/refresh/health`：Network First（必須即時）
- 離線時顯示「目前離線，顯示快取資料」提示橫幅。

**Acceptance Criteria / Tests**  
- [ ] 在 Chrome DevTools Application → Manifest 可看到 manifest 設定正確。
- [ ] 「加入主畫面」功能在 Android Chrome 可用。
- [ ] 網路離線時，Dashboard 仍可顯示（載入快取資料），不出現白畫面。
- [ ] Lighthouse PWA 分數 > 80。

---

### ACTION-047：Capacitor Android 專案建立

**Context**  
使用 Capacitor 將 React Web 應用封裝為 Android APK，讓使用者可安裝到 Android 裝置。

**Spec**  
在 `frontend/` 下安裝 Capacitor：

```bash
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init "MemTrendDashboard" "tw.lance.memdash" --web-dir=dist
npx cap add android
```

設定 `capacitor.config.ts`：
```typescript
{
  appId: 'tw.lance.memdash',
  appName: 'MemTrendDashboard',
  webDir: 'dist',
  server: {
    // 開發時可設定連到 localhost:3000
    url: 'http://YOUR_BACKEND_IP:3000', 
    cleartext: true  // 允許 HTTP（正式版應改 HTTPS）
  }
}
```

建立 Debug APK 的建置指令：
```bash
npm run build && npx cap sync android && cd android && ./gradlew assembleDebug
```

在 `README.md` 加入完整的 APK 建置說明。

**Acceptance Criteria / Tests**  
- [ ] `npx cap add android` 後，`android/` 目錄建立。
- [ ] `./gradlew assembleDebug` 成功產生 `app-debug.apk`。
- [ ] APK 安裝到 Android 模擬器後，可正常開啟 Dashboard（需 Backend 在同網路下執行）。

---

## PHASE 5 — AI 與進階洞察

---

### ACTION-048：LLM 新聞摘要抓取 Job

**Context**  
每日自動抓取記憶體大廠相關新聞，使用 LLM API 摘要並提取情緒與關鍵訊號，存入 `news_items` 表格。

**Spec**  
建立 `backend/app/jobs/ingest_news.py`：

**新聞抓取來源**（RSS / 公開 API）：
- Reuters Technology RSS：`https://feeds.reuters.com/reuters/technologyNews`
- Bloomberg Semiconductor（若有公開 RSS）
- 篩選關鍵字：`memory`, `DRAM`, `NAND`, `HBM`, `Micron`, `Samsung`, `SK Hynix`, `Kioxia`

**LLM 摘要規格**：
呼叫 LLM API（`LLM_API_KEY` 環境變數），Prompt：
```
你是記憶體產業分析師。以下是一篇新聞，請提取：
1. 與 DRAM/NAND/HBM 供需、報價、產能相關的關鍵訊息（2-3 條）
2. 市場情緒（bullish/neutral/bearish）
3. 關聯公司代號（從清單選擇：MU/SNDK/005930/000660/285A/2408/2344）
只輸出 JSON，格式：{"key_points": [...], "sentiment": "...", "related_tickers": [...]}

新聞標題：{title}
新聞內文：{content}
```

存入 `news_items` 表格（需在 ACTION-009 中已定義 schema）。

**Acceptance Criteria / Tests**  
- [ ] 腳本執行後，`news_items` 有資料（至少 1 筆）。
- [ ] LLM 輸出 JSON 格式正確，`sentiment` 為合法值。
- [ ] 重複抓取同一新聞 URL 不產生重複記錄（以 URL 為 unique key）。
- [ ] `LLM_API_KEY` 未設定時，新聞仍抓取並存儲（`sentiment` 和 `key_points` 為 `null`），不中斷。

---

### ACTION-049：歷史事件標記 CRUD 與圖表 Overlay

**Context**  
讓使用者可以在趨勢圖上標記重大產業事件，並讓圖表在對應日期顯示事件標記，提升歷史分析直覺性。

**Spec**  

**後端 CRUD** (`backend/app/routers/events.py`)：
```
GET    /api/events           → 查詢重大事件列表
  query: start_date, end_date, ticker
POST   /api/events           → 新增事件
PATCH  /api/events/{id}      → 修改事件
DELETE /api/events/{id}      → 刪除事件
```

事件結構（`market_events` 表格）：
```json
{
  "event_date": "2024-10-15",
  "title": "Samsung 宣佈 HBM 減產",
  "description": "Samsung 宣布因 HBM3E 良率問題，將 2024 Q4 HBM 產量削減 20%。",
  "related_tickers": ["005930", "MU", "000660"],
  "category": "supply"  // supply/demand/macro/tech
}
```

**前端 Event Overlay** (更新 `TrendChart.tsx`)：
- 從 `GET /api/events` 取得事件列表。
- 在 lightweight-charts 使用 `createSeriesMarker` 在對應日期加上標記（▲ 圖示）。
- 懸停標記時，顯示事件 Tooltip（標題 + 描述 + 相關代號）。
- 事件管理 UI（`/query` 頁面新增「事件管理」Tab）：表格 + 新增/刪除按鈕。

**Acceptance Criteria / Tests**  
- [ ] 新增事件後，趨勢圖對應日期出現標記。
- [ ] 懸停標記，Tooltip 顯示事件說明。
- [ ] 事件管理 UI 可新增和刪除事件。
- [ ] 刪除事件後，圖表標記消失（即時更新）。

---

### ACTION-050：簡單歷史回測 Widget

**Context**  
提供基礎的策略回測視覺化，讓使用者評估「依牛熊分數買賣 Tier A 籃子」的歷史表現。

**Spec**  
建立 `backend/app/routers/backtest.py`：

```
POST /api/backtest
Body: {
  "entry_condition": "score_gt_60",  // 分數超過 60 時買入
  "exit_condition": "hold_30d",      // 持有 30 天後賣出
  "start_date": "2025-01-01",
  "end_date": "2026-01-01",
  "target": "tier_a_basket"         // 買入 Tier A 籃子等權重
}
```

回傳：
```json
{
  "trades": [{
    "entry_date": "...", "entry_score": 62,
    "exit_date": "...", "return_pct": 8.5
  }],
  "summary": {
    "total_trades": 5, "win_rate": 0.60,
    "avg_return": 4.2, "max_drawdown": -8.1
  },
  "equity_curve": [{date: "...", cumulative_return: ...}]
}
```

前端 Widget（`frontend/src/components/Backtest/BacktestWidget.tsx`）：
- 表單（入場條件、持有期、日期範圍）
- 執行後顯示：equity curve 折線圖 + 勝率/平均報酬摘要卡片 + 交易明細表。

**Acceptance Criteria / Tests**  
- [ ] 後端正確計算：模擬 5 筆交易，人工驗算勝率與平均報酬一致。
- [ ] 資料不足時（日期範圍內沒有觸發信號），回傳 `{"trades": [], "summary": null}`，非 500 錯誤。
- [ ] 前端 equity curve 可正確渲染。

---

### ACTION-051：產業鏈節點圖 (Node Graph)

**Context**  
以互動式節點關聯圖呈現記憶體供應鏈的上下游關係，依當日股價漲跌幅熱力高亮各節點，讓使用者一眼看出資金聚焦在哪個產業環節。

**Spec**  
建立 `frontend/src/components/SupplyChainGraph/SupplyChainGraph.tsx`：

使用 ECharts Graph 系列（`type: 'graph'`）：

**節點結構**（依 supply_chain_tag 分層）：
- 層 1（左）：矽晶圓 / 設備 / 材料（Tier B/C 上游）
- 層 2：記憶體原廠（Tier A：Samsung, SK Hynix, Micron, Kioxia, 南亞科, 華邦電）
- 層 3：控制 IC / 模組廠（Tier A/B）
- 層 4（右）：封測 / SSD 方案商 / 下游儲存

**節點視覺**：
- 節點大小依市值或 Tier 調整（Tier A 較大）。
- 節點顏色依當日漲跌幅（正 → 綠系，負 → 紅系，中性 → 灰）。
- 節點標籤：股票代號 + 今日漲跌幅（%）。
- 懸停節點：彈出 Sparkline Tooltip（使用 ACTION-031 元件）。

**邊（edges）**：
- 代表供應鏈關係（靜態定義）。
- 邊的粗細依兩端關聯程度（固定）。

**控制**：
- 縮放 / 拖曳節點。
- 「依漲跌排色」Toggle：開啟 = 熱力圖模式；關閉 = 依 Tier 固定顏色。

**Acceptance Criteria / Tests**  
- [ ] 圖表渲染，所有節點與邊正確顯示。
- [ ] 所有 Tier A 節點顏色依當日漲跌幅正確著色（人工比對資料）。
- [ ] 懸停節點，SparklineTooltip 出現。
- [ ] 圖表可縮放，節點可拖曳重排。

---

## 附錄：測試與品質標準

每個 ACTION 完成後需滿足：
1. **單元測試**（pytest / vitest）：核心邏輯函式測試覆蓋率 > 80%。
2. **API 測試**（pytest + httpx.AsyncClient）：所有 API 端點的 happy path + 主要 error path。
3. **UI 測試**（人工目視驗證）：元件在 Chrome 1440px 和 375px 下正確渲染。
4. **不拋出未處理例外**：所有外部 API 呼叫需有 try/except，失敗時 log + 回傳明確錯誤。
5. **型別完整**：後端 Pydantic schema，前端 TypeScript interface，無 `any` 型別。

---

## 附錄：環境變數完整清單

| 變數名 | 用途 | 必填 |
|---|---|---|
| `DATABASE_URL` | PostgreSQL 連線字串 | ✅ |
| `FINMIND_TOKEN` | FinMind API Bearer Token | 台股/美股 |
| `ALPHA_VANTAGE_KEY` | Alpha Vantage API Key | 美股備援 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | Phase 3 |
| `TELEGRAM_CHAT_ID` | Telegram 目標 Chat ID | Phase 3 |
| `LINE_NOTIFY_TOKEN` | Line Notify Token | Phase 3 |
| `SMTP_HOST` | SMTP 伺服器 | Phase 3 |
| `SMTP_PORT` | SMTP 埠（通常 587） | Phase 3 |
| `SMTP_USER` | SMTP 認證帳號 | Phase 3 |
| `SMTP_PASS` | SMTP 認證密碼 | Phase 3 |
| `ALERT_EMAIL_TO` | 告警 Email 收件地址 | Phase 3 |
| `LLM_API_KEY` | LLM API Key（Gemini/OpenAI） | Phase 5 |
| `POSTGRES_DB` | PostgreSQL DB 名稱 | Docker |
| `POSTGRES_USER` | PostgreSQL 使用者 | Docker |
| `POSTGRES_PASSWORD` | PostgreSQL 密碼 | Docker |
