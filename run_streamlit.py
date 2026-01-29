import sys
import os

# 添加當前目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """啟動Streamlit應用"""
    try:
        import streamlit as st
        from web_app import main as app_main

        # 直接運行streamlit應用
        if __name__ == "__main__":
            import streamlit.web.cli as stcli

            sys.argv = ["streamlit", "run", "web_app.py"]
            sys.exit(stcli.main())

    except ImportError as e:
        print(f"請先安裝依賴: pip install -r requirements.txt")
        print(f"錯誤信息: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
