#!/bin/bash

# 啟動Streamlit Web界面的腳本

echo "🖼️  AVIF批量轉換工具 - Web界面啟動"
echo "=========================================="

# 檢查虛擬環境
if [ ! -d "web-env" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv web-env
fi

# 激活虛擬環境
echo "🔄 激活虛擬環境..."
source web-env/bin/activate

# 安裝依賴
echo "📦 檢查依賴..."
pip install streamlit pillow > /dev/null 2>&1

# 檢查Node.js依賴
if [ ! -d "node_modules" ]; then
    echo "📦 安裝Node.js依賴..."
    npm install
fi

# 啟動Streamlit
echo "🚀 啟動Web界面..."
echo "📍 請在瀏覽器中打開: http://localhost:8501"
echo "⏹️  按 Ctrl+C 停止服務"
echo ""

streamlit run web_app.py --server.port 8501 --server.address localhost --browser.gatherUsageStats false