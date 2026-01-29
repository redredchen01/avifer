# AVIF批量轉換工具 - Web界面

## 🌟 功能特點

- **🖼️ 現代化Web界面**: 基於Streamlit構建的直觀用戶界面
- **📁 拖拽上傳**: 支持文件和目錄拖拽上傳
- **⚡ 實時轉換**: 集成Node.js高性能轉換引擎
- **📊 進度監控**: 實時顯示轉換進度和統計信息
- **🎛️ 參數調整**: 可調質量、速度、並發數等參數
- **🔒 本地處理**: 所有轉換都在本地進行，保護隱私

## 🚀 快速啟動

### 方法1: 使用啟動腳本（推薦）

```bash
./start_web.sh
```

### 方法2: 手動啟動

```bash
# 1. 激活虛擬環境
source web-env/bin/activate

# 2. 啟動Streamlit
streamlit run web_app.py --server.port 8501
```

### 方法3: 使用Python腳本

```bash
python3 start_web.py
```

## 📱 界面功能

### 🎛️ 側邊欄配置
- **壓縮質量**: 1-100（默認80）
- **編碼速度**: 1-10（默認6）
- **並發處理數**: 1-8（默認4）

### 📁 文件上傳區域
- **單文件上傳**: 支持多選
- **目錄掃描**: 輸入路徑批量掃描
- **支持格式**: JPG, PNG, WebP, GIF, BMP, TIFF

### 📊 轉換統計
- 總文件數
- 成功/失敗統計
- 原始大小 vs 轉換後大小
- 壓縮率計算

### 🔄 轉換過程
- 實時進度條
- 當前處理文件狀態
- 錯誤信息顯示

## 🛠️ 技術架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │  Python Bridge  │    │   Node.js       │
│   Web UI        │◄──►│  converter.py   │◄──►│   converter.js  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    用戶界面              Python邏輯處理           高性能圖片轉換
```

### 核心組件

1. **web_app.py** - Streamlit主界面
2. **converter_bridge.py** - Python到Node.js橋接
3. **src/converter.js** - Node.js轉換引擎
4. **src/batch.js** - 批量處理邏輯

## 📦 依賴安裝

### Python依賴
```bash
# 創建虛擬環境
python3 -m venv web-env
source web-env/bin/activate

# 安裝依賴
pip install streamlit pillow
```

### Node.js依賴
```bash
npm install
```

## 🎯 使用流程

1. **啟動應用**: 運行啟動腳本
2. **打開瀏覽器**: 訪問 http://localhost:8501
3. **上傳文件**: 拖拽或選擇圖片文件
4. **調整參數**: 設置質量、速度等參數
5. **開始轉換**: 點擊轉換按鈕
6. **查看結果**: 查看轉換統計和下載文件

## 🔧 故障排除

### 常見問題

1. **端口被佔用**
   ```bash
   # 檢查端口使用情況
   lsof -i :8501
   
   # 使用其他端口
   streamlit run web_app.py --server.port 8502
   ```

2. **依賴缺失**
   ```bash
   # 重新安裝依賴
   pip install -r requirements.txt
   npm install
   ```

3. **轉換失敗**
   - 檢查Node.js是否正確安裝
   - 確認Sharp庫可用
   - 查看控制台錯誤信息

### 調試模式

```bash
# 啟用詳細日誌
streamlit run web_app.py --logger.level debug
```

## 📈 性能優化

- **並發處理**: 根據CPU核心數調整並發數
- **質量設置**: 平衡質量和文件大小
- **內存管理**: 大文件分批處理

## 🔒 安全說明

- ✅ 所有處理都在本地進行
- ✅ 文件不會上傳到外部服務器
- ✅ 轉換完成後臨時文件自動清理
- ✅ 支持用戶自定義輸出路徑

## 📄 許可證

MIT License - 詳見 [LICENSE](LICENSE) 文件