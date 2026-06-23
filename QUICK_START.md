# IC MemTrendDashboard — 快速啟動指南

## 📋 前置要求

1. **Docker Desktop for Windows** 已安裝並運行
   - 下載: https://www.docker.com/products/docker-desktop
   - 確認右下角系統托盤有 Docker 圖示

2. **.env 文件** (會自動建立)
   - 如果不存在，系統會自動從 `.env.example` 複製

3. **連接埠可用**
   - Port 3000 (Backend)
   - Port 5432 (Database) 
   - Port 8510 (Frontend)

## 🚀 啟動方式 (3 選 1)

### 方式 1️⃣: 雙擊 run-docker.cmd (最簡單)
1. 導航到專案根目錄
2. **雙擊** `run-docker.cmd` 檔案
3. 命令行會自動檢查前置條件並啟動 Docker
4. 等待看到 "Application startup complete" 訊息

### 方式 2️⃣: PowerShell 執行 (更智能)
```powershell
# 在 PowerShell 中執行
.\run-docker.ps1

# 或指定執行策略
PowerShell -ExecutionPolicy Bypass -File .\run-docker.ps1
```

### 方式 3️⃣: 手動 Docker Compose (高階用戶)
```bash
docker-compose up --build
```

## ✅ 驗證服務已啟動

當看到以下訊息表示成功啟動：
```
uvicorn.error    | INFO:     Application startup complete
```

服務訪問地址：
| 服務 | 網址 |
|------|------|
| **前端儀表板** | http://localhost:8510 |
| **後端 API** | http://localhost:3000 |
| **API 互動文檔** | http://localhost:3000/docs |
| **資料庫** | localhost:5432 |

## ⏹️ 停止服務

- **終端中**: 按 `Ctrl+C`
- **清理所有容器**: `docker-compose down -v`

## 🔧 常見問題

### Q: "Docker daemon not running"
**A**: Docker Desktop 未啟動
- 開啟 Docker Desktop 應用程式
- 等待右下角圖示出現
- 重新執行啟動腳本

### Q: "port already in use"
**A**: 該連接埠被其他程序占用
- 檢查是否有先前的容器未停止: `docker ps`
- 停止容器: `docker stop <container_id>`
- 或修改 `docker-compose.yml` 中的連接埠

### Q: cmd 視窗執行後立即關閉
**A**: 可能有錯誤訊息閃過
- 改用 PowerShell: `.\run-docker.ps1` (會顯示彩色錯誤訊息)
- 或手動執行: `docker-compose up --build` (看完整日誌)

### Q: 前端無法連接後端
**A**: API 代理配置問題
- 確認後端容器正在運行: `docker ps`
- 檢查 vite.config.ts 代理設定
- 瀏覽器開發者工具 (F12) 查看網路請求

### Q: 資料庫連線失敗
**A**: PostgreSQL 未完全啟動
- 等待 10-15 秒重新整理
- 檢查日誌: `docker logs -f <db_container_id>`

## 📊 開發工作流

### 修改前端代碼
- 編輯 `frontend/src/` 中的檔案
- 開發伺服器會自動重新載入 (HMR)
- 不需重啟容器

### 修改後端代碼
- 編輯 `backend/app/` 中的檔案
- 需手動重啟後端容器:
  ```bash
  docker-compose restart backend
  ```

### 查看即時日誌
```bash
# 所有容器日誌
docker-compose logs -f

# 特定容器
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

## 📝 檔案結構參考

```
IC_MemTrendDashboard/
├── run-docker.cmd          # ← 雙擊啟動 (Windows cmd)
├── run-docker.ps1          # ← PowerShell 啟動腳本
├── docker-compose.yml      # Docker 容器編排配置
├── .env                    # 環境變數 (自動生成)
├── .env.example            # 環境變數範本
├── backend/                # FastAPI 應用
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React 應用
│   ├── src/
│   ├── package.json
│   └── Dockerfile
└── DOCKER_GUIDE.md         # 詳細 Docker 指南
```

## 🎯 首次啟動提示

1. 第一次運行會下載 Docker 映像 (~500MB)，可能需要 3-5 分鐘
2. PostgreSQL 初始化可能需要 10-20 秒
3. 如果看到 "Connection refused"，等待後重新整理瀏覽器
4. 前端會顯示演示數據直到後端完全初始化

---

**成功啟動後，就可以在 http://localhost:8510 查看儀表板了！** 🎉
