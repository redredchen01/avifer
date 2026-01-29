import zipfile
import tempfile
import shutil
from pathlib import Path
import time


class DownloadUtils:
    """下載工具類"""

    @staticmethod
    def create_download_zip(output_dir, zip_name="converted_images.zip"):
        """創建包含轉換後文件的ZIP壓縮包"""
        try:
            output_path = Path(output_dir)
            if not output_path.exists():
                return None

            # 查找所有AVIF文件
            avif_files = list(output_path.glob("**/*.avif"))

            if not avif_files:
                return None

            # 創建臨時ZIP文件
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
            temp_zip.close()

            with zipfile.ZipFile(temp_zip.name, "w", zipfile.ZIP_DEFLATED) as zipf:
                for avif_file in avif_files:
                    # 計算相對路徑以保持目錄結構
                    arcname = avif_file.relative_to(output_path)
                    zipf.write(avif_file, arcname)

            return temp_zip.name

        except Exception as e:
            print(f"創建ZIP文件失敗: {str(e)}")
            return None

    @staticmethod
    def get_file_list(output_dir):
        """獲取轉換後文件列表"""
        try:
            output_path = Path(output_dir)
            avif_files = list(output_path.glob("**/*.avif"))

            file_list = []
            for avif_file in avif_files:
                relative_path = avif_file.relative_to(output_path)
                file_size = avif_file.stat().st_size

                file_list.append(
                    {
                        "path": str(relative_path),
                        "name": avif_file.name,
                        "size": file_size,
                        "size_kb": file_size / 1024,
                    }
                )

            return sorted(file_list, key=lambda x: x["path"])

        except Exception as e:
            print(f"獲取文件列表失敗: {str(e)}")
            return []

    @staticmethod
    def get_conversion_summary(output_dir):
        """獲取轉換摘要信息"""
        try:
            output_path = Path(output_dir)
            avif_files = list(output_path.glob("**/*.avif"))

            if not avif_files:
                return None

            total_size = sum(f.stat().st_size for f in avif_files)
            total_size_mb = total_size / (1024 * 1024)

            # 統計目錄結構
            directories = set()
            for f in avif_files:
                directories.add(f.parent.relative_to(output_path))

            return {
                "file_count": len(avif_files),
                "total_size_mb": total_size_mb,
                "directory_count": len(directories),
                "directories": list(directories),
            }

        except Exception as e:
            print(f"獲取轉換摘要失敗: {str(e)}")
            return None


# Streamlit特定的UI函數
def create_streamlit_ui():
    """創建Streamlit UI組件"""
    try:
        import streamlit as st

        return st
    except ImportError:
        return None


def show_file_preview(output_dir, max_files=10):
    """顯示轉換後文件的預覽"""
    st = create_streamlit_ui()
    if not st:
        return

    try:
        file_list = DownloadUtils.get_file_list(output_dir)

        if not file_list:
            st.info("沒有轉換後的文件可預覽")
            return

        st.subheader("📋 轉換後文件預覽")

        # 限制顯示的文件數量
        display_files = file_list[:max_files]

        for i, file_info in enumerate(display_files):
            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                # 文件序號
                st.write(f"**{i + 1}.**")

            with col2:
                # 文件信息
                st.write(f"📄 `{file_info['path']}`")
                st.write(f"📏 大小: {file_info['size_kb']:.1f} KB")

            with col3:
                # 單文件下載按鈕（需要實現）
                st.write("📁")

        # 如果文件超過顯示限制，顯示提示
        if len(file_list) > max_files:
            st.info(f"還有 {len(file_list) - max_files} 個文件未顯示，請使用批量下載")

    except Exception as e:
        st.error(f"文件預覽失敗: {str(e)}")


def provide_download_link(zip_path, link_text="📥 下載轉換後的文件"):
    """提供下載鏈接"""
    st = create_streamlit_ui()
    if not st:
        return False

    if zip_path and Path(zip_path).exists():
        try:
            with open(zip_path, "rb") as f:
                zip_data = f.read()

            st.download_button(
                label=link_text,
                data=zip_data,
                file_name="converted_avif_images.zip",
                mime="application/zip",
                key="download_button",
            )

            # 清理臨時文件
            Path(zip_path).unlink(missing_ok=True)
            return True

        except Exception as e:
            st.error(f"下載準備失敗: {str(e)}")
            return False
    else:
        st.warning("沒有找到轉換後的文件")
        return False
