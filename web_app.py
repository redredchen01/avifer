import streamlit as st
import os
import tempfile
import shutil
from pathlib import Path
import time
import threading
import json

try:
    from PIL import Image
    import piexif
except ImportError:
    Image = None
    piexif = None

# 配置頁面
st.set_page_config(
    page_title="AVIF批量轉換工具",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定義CSS
st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
    }
    .progress-container {
        margin: 1rem 0;
    }
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 標題
st.markdown(
    """
<div class="main-header">
    <h1>🖼️ AVIF批量轉換工具</h1>
    <p>高效、安全的本地圖片格式轉換工具</p>
</div>
""",
    unsafe_allow_html=True,
)

# 側邊欄配置
st.sidebar.header("⚙️ 轉換設置")

# 質量設置
quality = st.sidebar.slider(
    "壓縮質量",
    min_value=1,
    max_value=100,
    value=80,
    help="較高的質量會產生較大的文件，但圖片效果更好",
)

# 速度設置
speed = st.sidebar.slider(
    "編碼速度",
    min_value=1,
    max_value=10,
    value=6,
    help="較高的速度會降低壓縮效率，但轉換更快",
)

# 並發設置
concurrent = st.sidebar.slider(
    "並發處理數", min_value=1, max_value=8, value=4, help="同時處理的圖片數量"
)

# 支持的格式
supported_formats = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"]

# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 上傳圖片")

    # 文件上傳
    uploaded_files = st.file_uploader(
        "選擇圖片文件",
        type=["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"],
        accept_multiple_files=True,
        help="支持多種圖片格式，可一次選擇多個文件",
    )

    # 或者拖拽上傳目錄
    st.markdown("---")
    st.subheader("📂 選擇目錄")

    upload_dir = st.text_input(
        "輸入目錄路徑",
        placeholder="/path/to/your/images",
        help="輸入包含圖片的目錄路徑",
    )

    if st.button("掃描目錄", key="scan_dir"):
        if upload_dir and os.path.exists(upload_dir):
            # 掃描目錄中的圖片文件
            image_files = []
            for root, dirs, files in os.walk(upload_dir):
                for file in files:
                    if any(file.lower().endswith(fmt) for fmt in supported_formats):
                        image_files.append(os.path.join(root, file))

            if image_files:
                st.session_state.directory_files = image_files
                st.success(f"找到 {len(image_files)} 個圖片文件")
            else:
                st.warning("目錄中沒有找到支持的圖片文件")
        else:
            st.error("目錄不存在或路徑無效")

with col2:
    st.subheader("📊 轉換統計")

    # 統計信息
    if "conversion_stats" in st.session_state:
        stats = st.session_state.conversion_stats
        st.markdown(
            f"""
        <div class="stats-card">
            <h4>轉換結果</h4>
            <p>📁 總文件數: {stats.get("total", 0)}</p>
            <p>✅ 成功轉換: {stats.get("success", 0)}</p>
            <p>❌ 轉換失敗: {stats.get("failed", 0)}</p>
            <p>📦 原始大小: {stats.get("original_size_mb", 0):.2f} MB</p>
            <p>📦 轉換後大小: {stats.get("converted_size_mb", 0):.2f} MB</p>
            <p>📉 壓縮率: {stats.get("compression_ratio", 0):.2f}%</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
        <div class="stats-card">
            <h4>等待轉換...</h4>
            <p>請先上傳圖片文件或選擇目錄</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

# 轉換控制
st.markdown("---")
col3, col4 = st.columns([2, 1])

with col3:
    st.subheader("🚀 開始轉換")

    # 檢查是否有文件要轉換
    files_to_convert = []

    if uploaded_files:
        files_to_convert.extend(uploaded_files)

    if "directory_files" in st.session_state:
        files_to_convert.extend(st.session_state.directory_files)

    if files_to_convert:
        st.info(f"準備轉換 {len(files_to_convert)} 個文件")

        if st.button("開始轉換", type="primary", key="start_convert"):
            # 創建臨時目錄
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)
                output_dir = temp_dir / "output"
                output_dir.mkdir(exist_ok=True)

                # 進度條
                progress_bar = st.progress(0)
                status_text = st.empty()

                # 轉換統計
                stats = {
                    "total": len(files_to_convert),
                    "success": 0,
                    "failed": 0,
                    "original_size": 0,
                    "converted_size": 0,
                    "errors": [],
                }

                # 實際轉換過程
                from converter_bridge import convert_image_to_avif

                for i, file_info in enumerate(files_to_convert):
                    try:
                        # 更新狀態
                        filename = (
                            file_info.name
                            if hasattr(file_info, "name")
                            else os.path.basename(file_info)
                        )
                        status_text.text(f"正在轉換: {filename}")

                        # 處理上傳的文件
                        if hasattr(file_info, "name"):
                            # 保存上傳的文件到臨時位置
                            temp_input_path = temp_dir / filename
                            with open(temp_input_path, "wb") as f:
                                f.write(file_info.getvalue())
                            input_path = str(temp_input_path)
                        else:
                            input_path = file_info

                        # 生成輸出路徑
                        output_filename = filename.rsplit(".", 1)[0] + ".avif"
                        output_path = str(output_dir / output_filename)

                        # 調用轉換器
                        result = convert_image_to_avif(
                            input_path, output_path, quality, speed
                        )

                        # 更新統計
                        if "error" not in result:
                            stats["success"] += 1
                            stats["original_size"] += result.get("originalSize", 0)
                            stats["converted_size"] += result.get("convertedSize", 0)
                        else:
                            stats["failed"] += 1
                            stats["errors"].append(f"{filename}: {result['error']}")

                        # 更新進度
                        progress = (i + 1) / len(files_to_convert)
                        progress_bar.progress(progress)

                    except Exception as e:
                        stats["failed"] += 1
                        filename = (
                            file_info.name
                            if hasattr(file_info, "name")
                            else os.path.basename(file_info)
                        )
                        stats["errors"].append(f"{filename}: {str(e)}")

                        # 更新進度
                        progress = (i + 1) / len(files_to_convert)
                        progress_bar.progress(progress)

                # 計算最終統計
                if stats["original_size"] > 0:
                    stats["compression_ratio"] = (
                        (stats["original_size"] - stats["converted_size"])
                        / stats["original_size"]
                    ) * 100
                    stats["original_size_mb"] = stats["original_size"] / (1024 * 1024)
                    stats["converted_size_mb"] = stats["converted_size"] / (1024 * 1024)

                # 保存統計到session
                st.session_state.conversion_stats = stats

                # 顯示結果
                status_text.text("轉換完成！")

                if stats["failed"] == 0:
                    st.success(f"✅ 所有 {stats['success']} 個文件轉換成功！")
                else:
                    st.warning(f"⚠️ {stats['success']} 個成功，{stats['failed']} 個失敗")

                # 下載功能
                from download_utils import (
                    DownloadUtils,
                    show_file_preview,
                    provide_download_link,
                )

                st.markdown("### 📥 下載轉換後的文件")

                # 顯示轉換摘要
                summary = DownloadUtils.get_conversion_summary(str(output_dir))
                if summary:
                    st.markdown(
                        f"""
                    <div class="stats-card">
                        <h4>轉換摘要</h4>
                        <p>📁 轉換文件數: {summary["file_count"]}</p>
                        <p>📦 總大小: {summary["total_size_mb"]:.2f} MB</p>
                        <p>📂 目錄數: {summary["directory_count"]}</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                # 文件預覽
                show_file_preview(str(output_dir))

                # 批量下載
                st.markdown("### 📦 批量下載")

                if stats["success"] > 0:
                    # 創建ZIP文件
                    zip_path = DownloadUtils.create_download_zip(str(output_dir))

                    if zip_path:
                        # 提供下載鏈接
                        if provide_download_link(zip_path):
                            st.success("✅ 下載鏈接已準備就緒！")
                        else:
                            st.error("❌ 下載鏈接創建失敗")
                    else:
                        st.warning("⚠️ 沒有找到轉換後的文件")
                else:
                    st.warning("⚠️ 沒有成功轉換的文件可供下載")

    else:
        st.warning("請先上傳圖片文件或選擇包含圖片的目錄")

with col4:
    st.subheader("ℹ️ 使用說明")
    st.markdown(
        """
    <div class="stats-card">
        <h4>步驟說明</h4>
        <ol>
            <li>上傳圖片文件或選擇目錄</li>
            <li>調整轉換參數</li>
            <li>點擊開始轉換</li>
            <li>等待轉換完成</li>
            <li>下載轉換後的文件</li>
        </ol>
        
        <h4>支持格式</h4>
        <ul>
            <li>JPEG/JPG</li>
            <li>PNG</li>
            <li>WebP</li>
            <li>GIF</li>
            <li>BMP</li>
            <li>TIFF</li>
        </ul>
        
        <h4>輸出格式</h4>
        <p>AVIF（現代高效圖片格式）</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

# 頁腳
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666;'>
    <p>🔒 所有轉換都在本地進行，您的文件不會上傳到任何服務器</p>
    <p>💡 AVIF格式提供更好的壓縮率和圖片質量</p>
</div>
""",
    unsafe_allow_html=True,
)
