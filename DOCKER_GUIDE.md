# IC MemTrendDashboard — Docker 快速啟動指南

## 前置要求

1. **Docker Desktop for Windows**
   - 下載: https://www.docker.com/products/docker-desktop
   - 安裝後需要重啟電腦
   - 確認 Docker 已啟動（右下角系統托盤可見 Docker 圖示）

2. **.env 環境配置檔**
   - 複製 `.env.example` 為 `.env`
   - 基本配置已預設（資料庫使用 Docker 內部服務)
   - 可選配置：股票 API Keys (FinMind, AlphaVantage)

3. **連接埠可用**
   - Port 3000 (backend API)
   - Port 5432 (PostgreSQL database)
   - Port 8510 (frontend dev server)

## 啟動方式

### 方式 1：雙擊 run-docker.cmd（推薦 ✓）
1. 導航到專案根目錄
2. 雙擊 **run-docker.cmd** 檔案
3. 會自動檢查 Docker、建立容器、啟動服務
4. 按 Enter 開始啟動
5. 等待日誌顯示 "Application startup complete"

### 方式 2：手動 Docker Compose
```bash
cd c:\Users\lance.tn\AI Project\IC_MemTrendDashboard
docker-compose up --build
```

### 方式 3：後台運行
```bash
docker-compose up -d
```

## 服務存取

服務啟動後，可在以下位置訪問：

- **前端儀表板**: http://localhost:8510
  - React 開發伺服器（熱更新）
  - 自動代理 API 到 localhost:3000

- **後端 API**: http://localhost:3000
  - 所有 API 端點

- **API 文檔**: http://localhost:3000/docs
  - Swagger UI 互動文檔
  - 可直接測試 API

- **資料庫**: localhost:5432
  - PostgreSQL 連線字串:
    ```
    postgresql://memdash:changeme@localhost:5432/memdash
    ```

## 停止服務

- **終端中**: 按 Ctrl+C
- **清理所有容器與卷**: 
  ```bash
  docker-compose down -v
  ```

## 常見問題

### Q1: "Docker not found" 錯誤
**A**: Docker Desktop 未安裝或未在 PATH 中。
- 確認 Docker Desktop 已安裝: https://www.docker.com/products/docker-desktop
- 重啟終端後重試

### Q2: "Docker daemon not running"
**A**: Docker 後台程序未啟動。
- 開啟 Docker Desktop 應用程式
- 等待 Docker 完全啟動（可能需要 30 秒）
- 重新執行 run-docker.cmd

### Q3: "Port already in use" 錯誤
**A**: 其他程序已佔用該連接埠。
- 檢查是否有先前未清理的容器
  ```bash
  docker ps -a
  docker rm <container_id>
  ```
- 或修改 docker-compose.yml 中的連接埠

### Q4: 前端無法連接到後端 API
**A**: 代理配置問題。
- 確認 backend 容器正在運行: `docker ps`
- 檢查 vite.config.ts 中的代理設定
- 在瀏覽器開發者工具查看網路標籤

### Q5: 資料庫連線失敗
**A**: PostgreSQL 容器未完全啟動。
- 等待 5-10 秒並重新整理頁面
- 檢查日誌: `docker logs <postgres_container_id>`

## 資料初始化

首次啟動後，資料庫預設為空。要匯入測試資料：

1. **進入 backend 容器**:
   ```bash
   docker exec -it <backend_container_id> bash
   ```

2. **執行 Phase 0 驗證**:
   ```bash
   python scripts/phase0_validation/validate_tw_finmind.py
   python scripts/phase0_validation/validate_us_stocks.py
   python scripts/phase0_validation/validate_jp_stocks.py
   python scripts/phase0_validation/validate_kr_stocks.py
   python scripts/phase0_validation/validate_memory_quotes.py
   python scripts/phase0_validation/generate_report.py
   ```

3. **或執行完整 ingestion 流程**:
   ```bash
   python -m app.jobs.run_all
   ```

## 測試檢查清單

- [ ] 前端頁面正常載入 (http://localhost:8510)
- [ ] 所有儀表板小工具可見（TopBar, Charts, Tables）
- [ ] API 文檔可訪問 (http://localhost:3000/docs)
- [ ] 後端 health check 通過: GET /api/health
- [ ] 資料庫連線正常
- [ ] 圖表數據正確顯示（使用演示數據或真實數據）

## 調試技巧

### 查看容器日誌
```bash
# 後端日誌
docker logs -f <backend_container_id>

# 前端日誌（如果使用 npm 容器）
docker logs -f <frontend_container_id>

# 資料庫日誌
docker logs -f <db_container_id>
```

### 進入容器 Shell
```bash
# Backend (Python)
docker exec -it <backend_container_id> bash

# Database (PostgreSQL)
docker exec -it <db_container_id> psql -U memdash -d memdash
```

### 重建容器
```bash
# 移除舊容器並重建
docker-compose down
docker-compose up --build
```

## 開發工作流

### 修改 Frontend 代碼
- 編輯 `frontend/src/` 中的檔案
- 開發伺服器會自動重新載入 (HMR)
- 無需重啟容器

### 修改 Backend 代碼
- 編輯 `backend/app/` 中的檔案
- 需要手動重啟後端容器:
  ```bash
  docker-compose restart backend
  ```

### 修改資料庫 Schema
- 使用 Alembic 管理遷移
- 編輯 `backend/alembic/versions/` 中的遷移檔案
- 執行遷移:
  ```bash
  docker exec -it <backend_container_id> alembic upgrade head
  ```

## 生產部署提示

當準備部署到生產時，考慮：

1. 使用環境特定的配置 (.env.production)
2. 配置完整的 HTTPS/SSL
3. 使用強密碼修改所有預設密碼
4. 設定合適的 CORS 政策
5. 配置適當的日誌記錄和監控
6. 使用數據庫備份和恢復策略

---

**祝您使用愉快！有任何問題歡迎回報。**
