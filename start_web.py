#!/usr/bin/env python3
"""
啟動腳本 - 運行Streamlit Web界面
"""

import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """檢查並安裝必要的依賴"""
    print("🔍 檢查依賴...")

    # 檢查Node.js依賴
    if not (Path("node_modules") / ".bin").exists():
        print("📦 安裝Node.js依賴...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )

    # 檢查Node.js模塊
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 請先安裝Node.js")
        sys.exit(1)

    print("✅ 依賴檢查完成")


def start_streamlit():
    """啟動Streamlit應用"""
    print("🚀 啟動Streamlit應用...")

    # 設置Streamlit配置
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "localhost"

    # 啟動Streamlit
    try:
        subprocess.run(
            [
                "streamlit",
                "run",
                "web_app.py",
                "--server.port",
                "8501",
                "--server.address",
                "localhost",
                "--browser.gatherUsageStats",
                "false",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit未安裝，正在安裝...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "streamlit"], check=True
        )
        start_streamlit()


if __name__ == "__main__":
    print("🖼️  AVIF批量轉換工具 - Web界面")
    print("=" * 40)

    # 檢查依賴
    check_dependencies()

    # 啟動應用
    start_streamlit()
